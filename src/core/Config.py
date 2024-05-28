"""
adsb2.x/src/config.index.py 
"""
from src.config.sensors import sensors
from src.config.sys import sys_vars

class Config:
    _instance = None

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self._instance:
            raise Exception("ConfigSingleton is a Singleton class. Use getInstance() to get the instance.")
        self.data = {
            "sensors" : sensors,
            "sys" : sys_vars
        }
    
    def get(self,key):
        parseKey = key.split(".")
        
        data = None
        for item in parseKey:
            if data is not None:
                data = data[item]
            else:
                data = self.data[item]
        return data
