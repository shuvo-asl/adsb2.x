import logging

import aiohttp
import json
import asyncio
import logging

"""
    Reference link for this codebase:
    https://www.pythontutorial.net/python-concurrency/python-asyncio-gather/
    
"""


class Receiver:
    def __init__(self, sensor_url, request_period, queue):
        self.sensor_url = sensor_url
        self.request_period = request_period
        self.output_queue = queue

    def _set_online_status(self, is_online:bool,note=""):
        log = logging.getLogger(__name__)
        if is_online:
            print(
                "|-----------------------------------------------------------------------|"
            )
            log.info("| " + self.sensor_url + " is online",note)
            # print("| " + self.sensor_url + " is online",note)
        else:
            # print(self.sensor_url + " is offline",note)
            log.warning("| " + self.sensor_url + " is online", note)
            print(
                "|-----------------------------------------------------------------------|"
            )

    async def receive(self):
        """Periodically pull sensor data from aircraftlist.json"""

        remote_sensor_url = "http://" + self.sensor_url + "/aircraftlist.json"

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(5)) as session:
            while True:
                try:
                    async with session.get(remote_sensor_url) as response:
                        if response.status == 200:
                            self._set_online_status(True)
                            response_text = await response.text()
                            for line in response_text[1:-2].splitlines():
                                json_line = line.strip(',')
                                json_line = json_line[0] + '"sensor":"'+self.sensor_url+'",'+json_line[1:]
                                await self.output_queue.put(json_line)
                        else:
                            self._set_online_status(False,note='200')
                except TimeoutError:
                    self._set_online_status(False,note='Timeout')
                except aiohttp.client_exceptions.ClientConnectionError:
                    self._set_online_status(False, note='Connection Error')
                await asyncio.sleep(self.request_period)
