import asyncio
from core.abstracts.pipeline import StreamConsumer
from helper.config_helper import getConfig
from core.sensor_network import SensorNetwork
from core.deduplicator import Deduplicator
from core.geofilter import GeoFilter
from core.data_splitter import UpdateDetector
import json

async def open_data(input_stream):
    async for item in input_stream:
        print(item)

class OutputMonitor(StreamConsumer):
    """ Output progress to screen """

    def __init__(self, *args, output_char='.', **kwargs):
        super().__init__(*args, **kwargs)
        self.nb_things = 0
        self.output_char = output_char

    async def process_item(self, item):
        """ Smoke test printer to show data flow """
        if self.output_char == 'f':
            print('')
            print(self.output_char, {k: item[k] for k in ('uti', 'hex', 'fli', 'squ', 'tru','state')})
        else:
            print(self.output_char, end='')

        self.nb_things += 1
        if self.nb_things > 80:
            print('')
            self.nb_things = 0

    async def stop(self):
        pass



async def process():
    """ Core Asynchronous processing """
    all_sensors = getConfig("sensors")

    sensorNetwork = SensorNetwork(all_sensors)
    deduplicator = Deduplicator(sensorNetwork.data())

    geo_filter = GeoFilter(deduplicator.filter())
    update = UpdateDetector(geo_filter.filter())
    sink_position_data = OutputMonitor(update.position_update())
    sink_flight_data = OutputMonitor(update.flight_update(), output_char='f')

    await sensorNetwork.closed()
    await update.closed()
    await sink_position_data.closed()
    await sink_flight_data.closed()

def main():
    """ Application Entry Point """
    asyncio.run(process())

if __name__ == "__main__":
    main()
