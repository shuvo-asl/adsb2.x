import asyncio
import pytest
from src.core.data_splitter import UpdateDetector

flight_test_data = [
    {
        "hex": 1234,
        "fli": "BG123",
        "squ": 4567,
        "uti": 12345,
        "lat": 1234,
        "lon": 1235,
        "alt": 1236
    },
    {
        "hex": 1234,
        "fli": "BG123",
        "squ": 4567,
        "uti": 12346,
        "lat": 1234,
        "lon": 1235,
        "alt": 1236
    },
    {
        "hex": 1234,
        "fli": "BG123",
        "squ": 4567,
        "uti": 12347,
        "lat": 1234,
        "lon": 1235,
        "alt": 1236
    },
    {
        "hex": 1234,
        "fli": "BG123",
        "squ": 4567,
        "uti": 12348,
        "lat": 1234,
        "lon": 1235,
        "alt": 1236
    }
]

async def flight_source_data():
    for item in flight_test_data:
        yield item
        await asyncio.sleep(0)  # Use await asyncio.sleep(0) instead of asyncio.sleep(0)

@pytest.mark.asyncio
async def test_flight_update():
    """
    Test flight update
    """
    update = UpdateDetector(flight_source_data())
    result = [item async for item in update.flight_update()]
    await update.stop()  # Ensure the stop method is called
    await update.closed()  # Await the task to ensure it has terminated
    assert len(result) == 1
    assert result[0] == flight_test_data[0]
