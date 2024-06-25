import asyncio
import pytest
from src.core.update_detector import FlightUpdate
import random
from datetime import datetime, timedelta

def generate_random_time():
    # Get current datetime
    now = datetime.now()

    # Generate a random number of seconds (between 0 and 86400 seconds in a day)
    random_seconds = random.randint(0, 86400)

    # Calculate the random time by subtracting random_seconds from current datetime
    random_time = now - timedelta(seconds=random_seconds)

    return random_time

flight_test_data = [
    {
        "hex": 1234,
        "fli": "BG123",
        "squ": 4567,
        "uti": 12345,
        "lat": 1234,
        "lon": 1235,
        "alt": 1236,
        "sensor":"",
        "tru":"",
        "rx_time": generate_random_time()
    },
    {
        "hex": 1234,
        "fli": "BG123",
        "squ": 4567,
        "uti": 12346,
        "lat": 1234,
        "lon": 1235,
        "alt": 1236,
        "sensor":"",
        "tru":"",
        "rx_time": generate_random_time()
    },
    {
        "hex": 1235,
        "fli": "BG125",
        "squ": "",
        "uti": 12420,
        "lat": 1234,
        "lon": 1235,
        "alt": 1236,
        "sensor":"",
        "tru":"",
        "rx_time": generate_random_time()
    },
    {
        "hex": 1235,
        "fli": "BG125",
        "squ": 4567,
        "uti": 12450,
        "lat": 1234,
        "lon": 1235,
        "alt": 1236,
        "sensor":"",
        "tru":"",
        "rx_time": generate_random_time()
    }
]

async def flight_source_data():
    for item in flight_test_data:
        yield item
        await asyncio.sleep(0)  # Use await asyncio.sleep(0) instead of asyncio.sleep(0)

# Define a coroutine to run the async generator
async def run_data(update):
    async for item in update.data():
        pass
@pytest.mark.asyncio
async def test_flight_update():
    """
    Test flight update
    """
    # Create an instance of FlightUpdate and process data
    update = FlightUpdate(flight_source_data())

    data_task = asyncio.create_task(run_data(update))

    result = [item async for item in update.changes()]
    assert len(result) == 3


    #Finalize processing
    await data_task
    await update.finalise()