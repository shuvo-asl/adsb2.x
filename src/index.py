import asyncio
from core.abstracts.pipeline import StreamConsumer
from helper.config_helper import getConfig
from core.sensor_network import SensorNetwork
from core.deduplicator import Deduplicator
from core.geofilter import GeoFilter
from core.data_splitter import FlightChangeDetector,PositionChangeDetector
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

    # show_data = asyncio.create_task(open_data(deduplicator.filter()))
    show_data = OutputMonitor(deduplicator.filter(), output_char='f')

    # geo_filter = GeoFilter(deduplicator.filter())
    #
    # flightUpdate = FlightChangeDetector(geo_filter.filter())
    # positionUpdate = PositionChangeDetector(flightUpdate.data())
    #
    # sink_flight_data = OutputMonitor(flightUpdate.changes())
    # sink_position_data = OutputMonitor(positionUpdate.changes(), output_char='f')
    # sink_flight_update_data = OutputMonitor(positionUpdate.data(), output_char='f')

    await sensorNetwork.closed()
    await show_data.closed()
    # await sink_position_data.closed()
    # await sink_flight_data.closed()
    # await sink_flight_update_data.closed()

def main():
    """ Application Entry Point """
    asyncio.run(process())

if __name__ == "__main__":
    main()
