"""
(C) ASL Systems Ltd 2024
Author: Mohammad Mehedi Hasan Shuvo
"""
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