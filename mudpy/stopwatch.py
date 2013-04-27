from time import time

class Stopwatch:
    def __init__(self):
        self.starttime = time()
    
    def __str__(self):
        return str(time()-self.starttime)
