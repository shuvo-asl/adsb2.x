import json
import asyncio
from receiver import Receiver
from aircraft_list_filter import AircraftListFilter
from helper.config_helper import getConfig
from core.abstracts.pipeline import StreamGenerator
from Deduplicator import Deduplicator
class SensorNetwork(StreamGenerator):
    
    def __init__(self,sensor_list):
        self.json_queue = asyncio.Queue(100)
        self.tracking_mode_status = getConfig("sys.tracking_mode")
        self.sensor_list = sensor_list
        self.request_period = getConfig('sys.sensor_request_period',10)

    def before_run(self):
        if not self.tracking_mode_status:
            print("Currently Tracking Mode is Off. Press 'Enter' to wait for tracking to be enabled or 'Q' to exit.")
            choice = input()
            if choice.lower() == 'q':
                return  # Exit cleanly
    

    async def generate_tasks(self):
        rx_tasks = []
        
        for sensor in self.sensor_list:
            """Instantiate a receiver and run it as an asyncio task"""
            rx = Receiver(sensor['url'], self.request_period, self.json_queue)
            task = asyncio.create_task(rx.process())
            rx_tasks.append(task)
        
        return rx_tasks

    async def run(self):
        self.before_run()
        rx_tasks = await self.generate_tasks()
        # await self.data()
        await asyncio.gather(*rx_tasks)
        # Insert a NONE sentinel in the data pipeline to indicate "end of data"
        await self.json_queue.put(None)
    
    
    async def data(self):
        while True:
            data = await self.json_queue.get()
            yield data
