from core.abstracts.pipeline import StreamFilter

class GeoFilter(StreamFilter):

    def __init__(self,input_stream):
        self.input_stream = input_stream
        super().__init__(input_stream)
    
    async def filter(self):

        async for item in self.input_stream:
            yield item