import asyncio
from core.abstracts.pipeline import StreamConsumer
from helper.config_helper import getConfig
from core.sensor_network import SensorNetwork
from core.deduplicator import Deduplicator
from core.geofilter import GeoFilter
from core.update_detector import FlightUpdate,PositionUpdate

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
            print(self.output_char, {k: item[k] for k in ('rx_time', 'hex', 'fli', 'squ', 'tru','state')})
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

    sensor_network = SensorNetwork(all_sensors)
    deduplicator = Deduplicator(sensor_network.data())
    geofilter = GeoFilter(deduplicator.filter())
    flightupdate = FlightUpdate(geofilter.filter())
    positionupdate = PositionUpdate(flightupdate.data())
    flight_sink = OutputMonitor(flightupdate.changes(), output_char='f')
    pos_sink = OutputMonitor(positionupdate.changes(), output_char='x')
    pipeline_sink = OutputMonitor(positionupdate.data())

    await sensor_network.closed()
    await flight_sink.closed()
    await pos_sink.closed()
    await pipeline_sink.closed()

def main():
    """ Application Entry Point """
    asyncio.run(process())

if __name__ == "__main__":
    main()
