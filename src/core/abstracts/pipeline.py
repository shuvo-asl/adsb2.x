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