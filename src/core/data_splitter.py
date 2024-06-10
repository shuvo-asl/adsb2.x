import asyncio
import logging
from src.core.abstracts.pipeline import StreamConsumer
from src.core.abstracts.pipeline import StreamTee
class UpdateDetector(StreamConsumer):
    POSITION_UPDATE_FIELDS = ['lat', 'lon', 'alt']
    FLIGHT_UPDATE_FIELDS = ['fli', 'squ']
    AIRCRAFT_FIELDS = ['reg', 'typ']

    def __init__(self, *args, stale_data_age=60,stale_check_period=30, **kwargs):
        super().__init__(*args)
        self.position_queue = asyncio.Queue(100)
        self.flightdata_queue = asyncio.Queue(100)
        self.ref_data = {}
        self._last_check_time = 0
        self._stale_data_age = stale_data_age
        self._stale_check_period = stale_check_period

    async def process_item(self, item):
        try:
            ref = self.ref_data[item['hex']]
        except KeyError:
            ref = None

        if ref is None or item['uti'] > ref['uti']:
            for fields, queue in [(self.POSITION_UPDATE_FIELDS, self.position_queue),
                                  (self.FLIGHT_UPDATE_FIELDS, self.flightdata_queue)]:
                await self.update(ref, item, fields, queue)
            self.ref_data[item['hex']] = item
            await self._check_aged_data(item['uti'])

    @staticmethod
    async def update(ref, item, fields, output_queue):
        """ Output item to output_queue if fields differ from previous reports """
        item['state'] = None
        if ref is None:
            item['state'] = 'START'
        elif {k: ref[k] for k in fields} != {k: item[k] for k in fields}:
            item['state'] = 'UPDATE'
        if item['state']:
            await output_queue.put(item)

    async def position_update(self):
        while self._running:
            item = await self.position_queue.get()
            if item is None:
                break
            yield item

    async def flight_update(self):
        while self._running:
            item = await self.flightdata_queue.get()
            if item is None:
                break
            yield item

    async def finalise(self):
        """ Insert stopping sentinel to all outputs """
        for output_queue in (self.flightdata_queue, self.position_queue):
            await output_queue.put(None)
    async def stop(self):
        self._running = False
        await self.finalise()


    async def _check_aged_data(self, latest_report_time):

        """
        Update _last_check_time after every 1 minute
        Delete aged data of previous 30 seconds
        """

        if latest_report_time < (self._last_check_time + self._stale_check_period):
            return
        self._last_check_time = latest_report_time

        min_age = latest_report_time - self._stale_data_age
        await self._delete_aged_data(min_age)

    async def _delete_aged_data(self, min_age):
        """ Terminate flight tracking for tacks older than min_age """
        for ac_hex in self.ref_data.copy():
            ref = self.ref_data[ac_hex]
            if ref['uti'] < min_age:
                ref['state'] = 'END'
                await self.flightdata_queue.put(ref)
                await self.position_queue.put(ref)
                del self.ref_data[ac_hex]



class ChangeDetector(StreamTee):
    def __init__(self,input_stream,change_fields = None):
        self.ref_data = {}
        self.change_fields = change_fields
        self.output_queue = asyncio.Queue(100)
        super().__init__(input_stream)


    async def process_item(self, item):

        try:
            ref = self.ref_data[item['hex']]
            for field in self.change_fields:
                if(item[field] is not None and ref[field] != item[field]):
                    ref[item['hex']][field] = item[field]

            if self.ref_data[item['hex']] != ref:
                self.ref_data[item['hex']] = ref
                await self.output_queue.put(ref)
        except KeyError:
            self.ref_data[item['hex']] = item
            await self.output_queue.put(item)



    async def changes(self):
        while True:
            item = await self.output_queue.get()
            if item is None:
                break
            yield item
    async def finalise(self):
        await self.output_queue.put(None)


class FlightChangeDetector(ChangeDetector):
    def __init__(self,input_stream,change_stream=('fli','squ')):
        super().__init__(input_stream,change_stream)



class PositionChangeDetector(ChangeDetector):
    def __init__(self,input_stream,change_stream=('lat','lon','alt')):
        super().__init__(input_stream,change_stream)


