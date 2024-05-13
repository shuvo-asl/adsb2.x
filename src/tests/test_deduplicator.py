"""
(C) ASL Systems Ltd 2024
Author: Mohammad Mehedi Hasan(Shuvo)
"""
import json

import json
import pytest
import  asyncio
import pytest_asyncio

async def source_data():
    for number in range(1,60):
        await asyncio.sleep(0)
        yield number

    for number in range(20,100):
        await asyncio.sleep(0)
        yield number



def timed_data(data_stream):
    """Change a stream of integers to a stream of json with uti value"""
    return (json.dumps({"data": item, "uti": item / 2}) async for item in data_stream) #generate asynchronous generator object

async def print_numbers():
    async for item in timed_data(source_data()):
        print(item)

asyncio.run(print_numbers())