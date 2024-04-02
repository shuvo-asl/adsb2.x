from core.Config import Config

"""
Get Config data
"""
def getConfig(key,default=None):
    
    config = Config.getInstance()
    try:
        result = config.get(key)
        return result
    except KeyError:
        print(f"{key} not found")
        return default

