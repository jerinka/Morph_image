import threading
import time

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(StoppableThread,self).join(*args, **kwargs)

    def run(self):
        while not self._stop_event.is_set():
            print("Still running thread!")
            time.sleep(2)
        print("thread stopped!")

if __name__=='__main__':
    threadobj = StoppableThread()
    threadobj.start()

    for i in range(2):
        print("Still running main!")
        time.sleep(2)
    
    threadobj.stop() #optional
    threadobj.join()
    print("main stopped!")