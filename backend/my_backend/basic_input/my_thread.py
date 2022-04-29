import imp
from threading import Thread

class GetLogsThread(Thread):
    def __init__(self, event, id, f, machine_obj, time):
        Thread.__init__(self)
        self.stopped = event
        self.id = id
        self.f = f
        self.machine_obj = machine_obj
        self.time = time

    def run(self):
        while not self.stopped.wait(self.time):
            logs = self.f(self.machine_obj)
            print(logs)