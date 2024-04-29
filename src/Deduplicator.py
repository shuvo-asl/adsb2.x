
class Deduplicator():

    def __init__(self,input_stream):
        self.items = {}
        self.input_stream = input_stream

    async def filter(self):
        async for item in self.input_stream:
            print(item)