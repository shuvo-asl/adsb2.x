import json
import asyncio
from receiver import Receiver
from aircraft_list_filter import AircraftListFilter
from helper.config_helper import getConfig


async def receiver_task(sensor_url, request_period, queue):
    """Instantiate a receiver and run it as an asyncio task"""
    receiver = Receiver(sensor_url, request_period, queue)
    await receiver.process()


async def main():
    
    """ Get System Tracking Mode Status """
    tracking_mode = getConfig('sys.tracking_mode')
    if not tracking_mode:
        print("Currently Tracking Mode is Off. Press 'Enter' to wait for tracking to be enabled or 'Q' to exit.")
        choice = input()
        if choice.lower() == 'q':
            return  # Exit cleanly

    """ Instantiate receiver and run forever """
    json_queue = asyncio.Queue(100)
    
    sensors = getConfig('sensors')  # Get sensor configuration from system config
    request_period = getConfig('sys.sensor_request_period',10)

    receiver_tasks = []
    for sensor in sensors:
        task = asyncio.create_task(receiver_task(sensor['url'], request_period, json_queue))
        receiver_tasks.append(task)


    _filter = AircraftListFilter(json_queue)

    await asyncio.gather(*receiver_tasks, _filter.process())

     # Insert a NONE sentinel in the data pipeline to indicate "end of data"
    await json_queue.put(None)

if __name__ == "__main__":
    asyncio.run(main())


     