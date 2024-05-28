import  signal
class SingletonClass():

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'instance'):
            cls.instance = super(SingletonClass,cls).__new__(cls)
        return cls.instance



class RunControl(SingletonClass):

    def __init__(self):
        self.run = True


    def stop(self):
        self.run = False


def sigint_handler(sig,frame):
    run_control = RunControl()
    run_control.stop()

signal.signal(signal.SIGINT, sigint_handler)