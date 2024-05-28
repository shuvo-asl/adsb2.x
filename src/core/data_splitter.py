import asyncio
from src.core.abstracts.pipeline import StreamConsumer
class DataSplitter():

    def __init__(self, input_stream):
        self.input_stream = input_stream
        self.update_flight_data_queue = asyncio.Queue(100)
        self.update_position_data_queue = asyncio.Queue(100)
        self.most_recent_position = {}
        self.most_recent_flight = {}



    async def processing(self):
        """
        Process input stream data
        """
        async for item in self.input_stream:

            if self.position_data_changes(item):
                await self.update_position_data_queue.put(item)

            if self.flight_data_changes(item):
                await self.update_flight_data_queue.put(item)

    def flight_data_changes(self,item):

        hex_code = item['hex']
        current_flight_data = {
            "fli" : item['fli'],
            "squ" : item['squ']
        }

        try:
            if self.most_recent_flight[hex_code] != current_flight_data:
                print(f"Flight {hex_code} data changed")
                self.most_recent_flight[hex_code] = current_flight_data
                return True;
        except KeyError as e:
            self.most_recent_flight[hex_code] = current_flight_data
            print(f"Flight {hex_code} Newly Added")
            return True

        return False;

    def position_data_changes(self,item):
        hex_code = item['hex']
        current_position_data = {
            "lat" : item['lat'],
            "lon" : item['lon'],
            "alt": item['alt']
        }
        try:
            if self.most_recent_position[hex_code] != current_position_data:
                print(f"Flight {hex_code} position data changed")
                self.most_recent_position[hex_code] = current_position_data
                return True
        except KeyError as e:
            self.most_recent_position[hex_code] = current_position_data
            print(f"Flight Position {hex_code} Newly Added")
            return True

        return False


    async def output_flight_data(self):
        while True:
            item = await self.update_flight_data_queue
            yield item

    async def output_position_data(self):
        while True:
            item = await self.update_position_data_queue.get()
            yield item

class UpdateDetector(StreamConsumer):

    POSITION_UPDATE_FIELDS = ['lat', 'lon', 'alt']
    FLIGHT_UPDATE_FIELDS = ['fli','squ']
    def __init__(self,*args, stale_data_age=30, **kwargs):
        super().__init__(*args, **kwargs)
        self.position_queue = asyncio.Queue(100)
        self.flightdata_queue = asyncio.Queue(100)
        self.ref_data = {}
        self._last_check_time = 0;
        self._stale_data_age = stale_data_age
    async def process_item(self,item):
        try:
            ref = self.ref_data[item['hex']]
        except KeyError:
            ref = None

        for fields,queue in [(self.POSITION_UPDATE_FIELDS,self.position_queue),(self.FLIGHT_UPDATE_FIELDS,self.flightdata_queue)]:
            await self.update(ref,item,fields,queue)

        self.ref_data[item['hex']] = item
        self._check_aged_data(item['uti'])

    async def update(self,ref,item,fields,output_queue):
        if ref is None or {k:ref[k] for k in fields} != {k:item[k] for k in fields}:
            await output_queue.put(item)


    async def position_update(self):
        while True:
            item = await self.position_queue.get()
            if item is None:
                break
            yield item

    async def flight_update(self):
        while True:
            item = await self.flightdata_queue.get()
            if item is None:
                break
            yield item


    async def stop(self):
        pass

    def _check_aged_data(self,latest_report_time):
        if latest_report_time < (self._last_check_time + 60):
            return
        self._last_check_time = latest_report_time

        print('checking stale aircraft tracks')
        min_age = latest_report_time - self._stale_data_age
        self._delete_aged_data(min_age)

    def _delete_aged_data(self, min_age):
        """ Terminate flight tracking for tacks older than min_age """
        for hex_code in self.ref_data.copy():
            if self.ref_data[hex_code]['uti'] < min_age:
                del self.ref_data[hex_code]
                print('d', end='')