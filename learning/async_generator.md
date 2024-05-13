# Async Generator
    
    def timed_data(data_stream):
    """Change a stream of integers to a stream of json with uti value"""
    return (json.dumps({"data": item, "uti": item / 2}) async for item in data_stream)

The expression `(json.dumps({"data": item, "uti": item / 2}) async for item in data_stream)` indeed creates an asynchronous generator object, not a regular generator. 
The async for construct is used to create an asynchronous generator, which asynchronously iterates over items yielded by data_stream.

When you use `async for`, it's a signal to Python that you're working with asynchronous iteration. 
The async for statement is used to iterate over asynchronous iterables, such as asynchronous generators, asynchronous iterators, or asynchronous iterators returned by asynchronous iterables.

So, in this case, timed_data returns an asynchronous generator object, not a regular generator object.
To consume items from this asynchronous generator, you would need to use asynchronous iteration, as shown in the previous example.