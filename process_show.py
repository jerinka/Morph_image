from multiprocessing import Process, Queue
import cv2

def f(img,q):
    q.put([42, None, 'hello'])
    while True:
        cv2.imshow('img',img)
        k=cv2.waitKey(30)
        if k==27:
            break


if __name__ == '__main__':
    img = cv2.imread("images/bradley_cooper.jpg")
    q = Queue()
    p = Process(target=f, args=(img,q,))
    p2 = Process(target=f, args=(img,q,))
    p.start()
    p2.start()
    print(q.get())    # prints "[42, None, 'hello']"
    p.join()
    p2.join()