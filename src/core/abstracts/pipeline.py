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

    async def filter(self):
        """ Forward items if they meet filter criteria """
        async for item in self.input_stream:
            output_item = self.process_item(item)
            if output_item:
                yield output_item

    @abstractmethod
    def process_item(self,item):
        """ Return output item if it is fill up the deduplication criteria """

class StreamConsumer(ABC):
    """ Consume data at end of pipeline
    Self-running consumer process and close() method
    """

    def __init__(self, input_stream):
        self.input_stream = input_stream
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        """ Asyncio task to run input pipeline """
        async for item in self.input_stream:
            try:
                await self.process_item(item)
            except Exception as e:
                print(e)

    async def closed(self):
        """ Awaitable for internal task to terminate """
        await self._task

    @abstractmethod
    async def process_item(self, item):
        """ Process each incoming item """

    @abstractmethod
    async def stop(self):
        """ Indicate stopping to downstream processes """


class StreamTee(ABC):
    def __init__(self, input_stream):
        self.input_stream = input_stream

    async def data(self):
        """ Asyncio task to run input pipeline """
        async for item in self.input_stream:
            await self.process_item(item)
            yield item

        await self.finalise()

    @abstractmethod
    async def process_item(self, item):
        """ Process each incoming item """

    @abstractmethod
    async def finalise(self):
        """ Indicate stopping to downstream processes """