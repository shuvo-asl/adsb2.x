import asyncio
from helper.config_helper import getConfig
from core.sensor_network import SensorNetwork
from core.deduplicator import Deduplicator
from core.geofilter import GeoFilter
from core.data_splitter import DataSplitter
import json

async def open_data(input_stream):
    async for item in input_stream:
        print(item)

async def main():
    all_sensors = getConfig("sensors")

    sensorNetwork = SensorNetwork(all_sensors)

    deduplicator = Deduplicator(sensorNetwork.data())
    geo_filter = GeoFilter(deduplicator.filter())
    splitter = DataSplitter(geo_filter.filter())

    splitter_processing_task = asyncio.create_task((splitter.processing()))
    data_task = asyncio.create_task(open_data(splitter.output_position_data()))
    sensor_network_task = asyncio.create_task(sensorNetwork.run())

    await asyncio.gather(data_task,splitter_processing_task, sensor_network_task)

if __name__ == "__main__":
    asyncio.run(main())
