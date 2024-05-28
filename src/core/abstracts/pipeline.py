"""
(C) ASL Systems Ltd 2024
Author: Mohammad Mehedi Hasan Shuvo
"""
import asyncio
from abc import ABC,abstractmethod

class StreamGenerator(ABC):
    """ Generate a stream of data """

    @abstractmethod
    async def data(self):
        """ Output generator """

class StreamFilter(ABC):
    """ Filter class for data pipeline """
    
    def __init__(self, input_stream):
        self.input_stream = input_stream
    
    @abstractmethod
    async def filter(self):
        """
        Get data from input stream
        Return a generator functions or
        or yield within a loop
        """

class StreamConsumer(ABC):
    """
    Consume data at end of pipeline
    Self-running consumer process and close() method
    """

    def __init__(self,input_stream):
        self.input_stream = input_stream
        self._task = asyncio.create_task(self._run())


    async def _run(self):
        async for item in self.input_stream:
            if item is None:
                break
            await self.process_item(item)

    async def closed(self):
        """ awaitable for internal task to terminate"""
        await self._task

    @abstractmethod
    async def process_item(self,item):
        pass