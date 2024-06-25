# library modules
import asyncio
from abc import abstractmethod
from enum import Enum
from datetime import timedelta
# local modules
from src.core.abstracts.pipeline import StreamTee


class UpdateState(Enum):
    START,CONTINUE,UPDATE,END = range(4)


class UpdateDetector(StreamTee):

    """ detect changes to flights and aircraft positions """

    @classmethod
    @property
    @abstractmethod
    def CHECK_FIELDS(cls):
        raise NotImplementedError

    STATUS_FIELDS = ('hex','rx_time','sensor','tru')

    def __init__(self,*args, stale_data_age=timedelta(seconds=62), **kwargs):
        self._update_queue = asyncio.Queue(100)
        self._ref_data = {}
        self._last_check_time = None
        self._stale_data_age = stale_data_age
        super().__init__(*args)


    async def process_item(self, item):
        hex_code = item['hex']

        try:
            ref = {field: self._ref_data[hex_code][field] for field in self.CHECK_FIELDS}
            update = {field: item[field] if item[field] is not None else ref[field]
                      for field in self.CHECK_FIELDS}
        except KeyError as e:
            ref = None
            update = {field: item[field] for field in self.CHECK_FIELDS}

        if ref is None:
            update['state'] = UpdateState.START
        elif update != ref:
            update['state'] = UpdateState.UPDATE
        else:
            update['state'] = UpdateState.CONTINUE

        # Add all other status data fields
        update.update({field: item[field] for field in self.STATUS_FIELDS})

        self._ref_data[hex_code] = update

        # Output updated state if check fields have changed
        if update['state'] in (UpdateState.START, UpdateState.UPDATE):
            await self._update_queue.put(update)

        # garbage collect the reference data
        await self._check_aged_data(item['rx_time'])
    async def changes(self):
        """ Generate updates """
        while True:
            item = await self._update_queue.get()
            if item is None:
                break
            yield item

    async def finalise(self):
        """ Insert stopping sentinel to all outputs """
        await self._update_queue.put(None)

    async def _check_aged_data(self, latest_report_time):
        """ Drop stale aircraft records
        The radarcape sensors keep stale data for 1 minute """

        if self._last_check_time is None:
            self._last_check_time = latest_report_time
            return

        if latest_report_time < (self._last_check_time + timedelta(seconds=60)):
            # Only check for stale data each minute
            return

        self._last_check_time = latest_report_time
        min_age = latest_report_time - self._stale_data_age
        await self._delete_aged_data(min_age)

    async def _delete_aged_data(self, min_age):
        """ Terminate flight tracking for tacks older than min_age """
        for ac_hex in self._ref_data.copy():
            ref = self._ref_data[ac_hex]
            if ref['rx_time'] < min_age:
                ref['state'] = UpdateState.END
                await self._update_queue.put(ref)
                del self._ref_data[ac_hex]

class FlightUpdate(UpdateDetector):
    """ Detect updates to flight data """
    CHECK_FIELDS = ('fli', 'squ')

class PositionUpdate(UpdateDetector):
    """ Detect updates to position data """
    CHECK_FIELDS = ('lat', 'lon', 'alt')