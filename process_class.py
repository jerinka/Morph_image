import multiprocessing as mp
from multiprocessing import Queue
import cv2
import time

class Worker(mp.Process):
    def __init__(self, img, q):
        print ("Init")
        self.img = img
        mp.Process.__init__(self)
        self.q = q
        
        self.count=0

    def run(self):
        while True:
            cv2.imshow('img',self.img)
            k=cv2.waitKey(30)
            if not self.q.empty():
                self.q.get()
            self.q.put([self.count])
            self.count+=1
            if k==27:
                break
        print("Stopping thread process")

if __name__=='__main__':
    img1 = cv2.imread("images/bradley_cooper.jpg")
    img2 = cv2.imread("images/jim_carrey.jpg")
    q1 = Queue(maxsize=1)
    q2 = Queue(maxsize=1)
    p1 = Worker(img1, q1)
    p2 = Worker(img2, q2)
    p1.start()
    p2.start()
    while (p1.is_alive() or p2.is_alive()):
        if not q1.empty():
            print('q1:',q1.get())
        if not q2.empty():
            print('q2:',q2.get())
        #import pdb;pdb.set_trace()
        time.sleep(1)

    print("Stoping main thread while loop")
    
    p1.join()
    p2.join()