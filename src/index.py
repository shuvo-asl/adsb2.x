import asyncio
from helper.config_helper import getConfig
from core.sensor_network import SensorNetwork
from core.deduplicator import Deduplicator
from core.geofilter import GeoFilter


async def open_data(input_stream):
    async for item in input_stream:
        print(item)


async def main():

    all_sensors = getConfig("sensors")

    sensorNetwork = SensorNetwork(all_sensors)

    deduplicator = Deduplicator(sensorNetwork.data())
    geo_filter = GeoFilter(deduplicator.filter())

    data_task = asyncio.create_task(open_data(geo_filter.filter()))

    sensor_network_task = asyncio.create_task(sensorNetwork.run())

    await asyncio.gather(data_task, sensor_network_task)


if __name__ == "__main__":
    asyncio.run(main())
