"""
(C) ASL Systems Ltd 2024
Author: Mohammad Mehedi Hasan(Shuvo)
"""
import json

import json
import pytest
import  asyncio
import pytest_asyncio
from src.core.deduplicator import Deduplicator

async def source_data():

    for number in range(1,60):
        await asyncio.sleep(0)
        yield number

    for number in range(20,101):
        await asyncio.sleep(0)
        yield number



def timed_data(data_stream):
    """Change a stream of integers to a stream of json with uti value"""
    return (json.dumps({"data": item, "uti": item / 2}) async for item in data_stream) #generate asynchronous generator object



# test deduplication. Output should contain only one of each number from 1-100
@pytest.mark.asyncio
async def test_deduplication():
    """Test that a stream is deduplicated"""
    deduplication = Deduplicator(timed_data(source_data()))

    # deduplicate source data
    output_data = deduplication.filter()

    # check that output has exactly one number from 1-100
    nb_items = 0
    sum_items = 0
    async for number in output_data:
        nb_items += 1
        sum_items += json.loads(number)['data']
    # assert the correct results
    assert nb_items == 100
    assert sum_items == (100 * (101)) / 2


# test aged data deletion.

STALE_CHECK_PERIOD = 1
STALE_DATA_AGE = 10


async def range_1_40():
    for item in range(1, 40):
        yield item
        await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_aged_data_deletion():
    """Test that stale data is deleted"""

    input_data = timed_data(range_1_40())
    deduplication = Deduplicator(
        input_data,
        stale_check_period=STALE_CHECK_PERIOD, stale_data_age=STALE_DATA_AGE
    )

    async for item in deduplication.filter():
        item_decode = json.loads(item)
        item_uti = item_decode["uti"]

        assert min(deduplication.items.values()) >= (
                item_uti - (STALE_CHECK_PERIOD + STALE_DATA_AGE)
        )


if __name__ == "__main__":
    test_aged_data_deletion()

# async def timed_data(data_stream):
#     async for item in data_stream:
#         data = json.dumps({"data": item, "uti": item / 2})
#         yield data

# async def print_numbers():
#     async for item in timed_data(source_data()):
#         print(item)
#
# asyncio.run(print_numbers())