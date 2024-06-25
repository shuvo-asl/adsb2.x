
from src.core.abstracts.pipeline import StreamFilter
import json
from datetime import datetime,timezone
class Deduplicator(StreamFilter):

    def __init__(self,input_stream,stale_check_period=60, stale_data_age=600):
        self.items = {}
        self.input_stream = input_stream
        self.stale_check_period = stale_check_period
        self.stale_data_age = stale_data_age
        self.last_check_time = 0
        super().__init__(input_stream)

    def process_item(self,item):
        output_items = None;
        if not item in self.items:

            # Store message in items and yield it to downstream processing
            item_decode = json.loads(item)
            self.items[item] = item_decode["uti"]
            rx_time = datetime.fromtimestamp(
                item_decode['uti'] + (item_decode['ns'] / 1e9),
                timezone.utc
            )
            item_decode['rx_time'] = rx_time
            output_items = item_decode

            # Delete aged items
            self.__delete_aged_item(self.items[item])

        return output_items

    def __delete_aged_item(self, latest_time):
        """ Check and delete older data"""
        # do nothing unless last checked more than stale_check_period ago
        if latest_time > self.last_check_time + self.stale_check_period:
            return
        
        self.last_check_time = latest_time

        # Calculate oldest valid data age

        min_age = latest_time - self.stale_data_age

        # Delete all items older than oldest valie data age
        for item in self.items.copy():  # iterate a copy if deleting items during iteration
            if self.items[item] < min_age:
                del self.items[item]