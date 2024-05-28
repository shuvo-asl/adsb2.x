import asyncio
from core.abstracts.pipeline import StreamConsumer
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
    def __init__(self,input_stream):
        self.input_stream = input_stream
        super().__init__(input_stream)
        self.position_queue = asyncio.Queue(100)
        self.flightdata_queue = asyncio.Queue(100)

    async def process_item(self,item):

        await self.update(item,self.POSITION_UPDATE_FIELDS,self.position_queue,f"{item.get('hex')} - Position")
        await self.update(item, self.FLIGHT_UPDATE_FIELDS, self.flightdata_queue,f"{item.get('hex')} - Flight")


    async def update(self,item,fields,queue,msg):
        print(msg)