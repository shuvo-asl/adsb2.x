import asyncio
import logging
from src.core.abstracts.pipeline import StreamConsumer

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

        await self.update(
            ref,
            item,
            self.POSITION_UPDATE_FIELDS,
            self.output_changes,
            self.position_queue)
        await self.update(
            ref,
            item,
            self.FLIGHT_UPDATE_FIELDS,
            self.process_flight_change,
            self.flightdata_queue)
        # for fields, queue in [(self.POSITION_UPDATE_FIELDS, self.position_queue), (self.FLIGHT_UPDATE_FIELDS, self.flightdata_queue)]:
        #     await self.update(ref, item, fields, queue)

        self.ref_data[item['hex']] = item
        self._check_aged_data(item['uti'])

    async def update(self, ref, item, fields, process_changes, output_queue):
        if ref is None or {k: ref[k] for k in fields} != {k: item[k] for k in fields}:
            await process_changes(ref,item,output_queue)


    async def output_changes(self, ref,item,output_queue):
        await output_queue.put(item)

    async def process_flight_change(self, ref,item,output_queue):
        if ref is None:
            item['state'] = 'START'
            await output_queue.put(item)
        elif ref['fli'] != item['fli']:
            item['state'] = 'END'
            await output_queue.put(item)
        elif ref['squ'] != item['squ']:
            item['state'] = 'UPDATE'
            await output_queue.put(item)
        else:
            # Should never be here
            log = logging.getLogger(__name__)
            log.error("Flight data change not identified. ref:%s item:%s", ref, item)


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

    async def stop(self):
        self._running = False
        await self.position_queue.put(None)
        await self.flightdata_queue.put(None)


    def _check_aged_data(self, latest_report_time):

        """

        Update _last_check_time after every 1 minute
        Delete aged data of previous 30 seconds

        """

        if latest_report_time < (self._last_check_time + self._stale_check_period):
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