import asyncio
from helper.config_helper import getConfig
from sensor_network import SensorNetwork
from Deduplicator import Deduplicator

async def main():

    all_sensors = getConfig("sensors")
    sensorNetwork = SensorNetwork(all_sensors)
    deduplicator = Deduplicator(sensorNetwork.data()) 
    await sensorNetwork.run()
    
    

if __name__ == "__main__":
    asyncio.run(main())
