import asyncio
from src.core.abstracts.pipeline import StreamConsumer

class UpdateDetector(StreamConsumer):
    POSITION_UPDATE_FIELDS = ['lat', 'lon', 'alt']
    FLIGHT_UPDATE_FIELDS = ['fli', 'squ']

    def __init__(self, *args, stale_data_age=30, **kwargs):
        super().__init__(*args, **kwargs)
        self.position_queue = asyncio.Queue(100)
        self.flightdata_queue = asyncio.Queue(100)
        self.ref_data = {}
        self._last_check_time = 0
        self._stale_data_age = stale_data_age

    async def process_item(self, item):
        try:
            ref = self.ref_data[item['hex']]
        except KeyError:
            ref = None

        for fields, queue in [(self.POSITION_UPDATE_FIELDS, self.position_queue), (self.FLIGHT_UPDATE_FIELDS, self.flightdata_queue)]:
            await self.update(ref, item, fields, queue)

        self.ref_data[item['hex']] = item
        self._check_aged_data(item['uti'])

    async def update(self, ref, item, fields, output_queue):
        if ref is None or {k: ref[k] for k in fields} != {k: item[k] for k in fields}:
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

    async def stop(self):
        self._running = False
        await self.position_queue.put(None)
        await self.flightdata_queue.put(None)


    def _check_aged_data(self, latest_report_time):
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