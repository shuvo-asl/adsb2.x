import json

class AircraftListFilter():
    """ 
    Responsible to filter stream data
    """

    def __init__(self, input_stream):
        self.input_stream = input_stream

    async def process(self):
        while True:
            # Dequeue data from the queue
            data = await self.input_stream.get()
            print(data)

