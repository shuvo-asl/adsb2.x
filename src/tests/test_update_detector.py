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
        "uti": 12420,
        "lat": 1234,
        "lon": 1235,
        "alt": 1236
    },
    {
        "hex": 1234,
        "fli": "BG123",
        "squ": 4567,
        "uti": 12450,
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
    await update.closed()  # Await the task to ensure it has terminated
    assert len(result) == 1
    assert result[0] == flight_test_data[0]


STALE_CHECK_PERIOD = 10
STALE_DATA_AGE = 5
@pytest.mark.asyncio
async def test_aged_data_deletion():
    """ Delete Aged data """
    update = UpdateDetector(flight_source_data())
    async for item in update.flight_update():
        item_uti = item["uti"]

        # Ensure that the values in ref_data are numerical values
        min_uti_value = min(val["uti"] for val in update.ref_data.values())

        assert min_uti_value >= (item_uti - (STALE_CHECK_PERIOD + STALE_DATA_AGE))
    await update.closed()  # Await the task to ensure it has terminated
