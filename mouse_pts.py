import cv2
import numpy as np
import threading 
import time
import os

class MousePtsThread(threading.Thread):

    def __init__(self, img, pts=[],win='MouseCallback'):
        super().__init__()
        self._stop_event = threading.Event()

        self.img = img

        if not len(pts): #if pts are not given, try to load from npy
            if os.path.isfile('pts.npy'):
                pts = np.load('pts.npy').tolist()
            else:
                pts =[]
        self.pts=pts

        # Create a black image and a window
        self.windowName = win
        self.mouse_state = None
        
        self.pt=None
        self.out_pts = []
        # bind the callback function to window
        self.cntr_indx = 0
        self.cntrs_dict = {}
        self.mouse_down = False
        self.new_mouse_down = False
        self.mouse_move = False
        # Start thread

    def CallBackFunc(self, event, x, y, flags, param):
        if event == cv2.EVENT_RBUTTONDOWN:
            if self.mouse_down == False:
                self.mouse_state = "RBUTTONDOWN"
                self.mouse_down  = True
                self.new_mouse_down = True
                self.pt = [x,y]
                print('mouse down')
                
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.mouse_down  == True:
                self.mouse_state = "MOUSEMOVE"
                self.mouse_move  = True
                self.pt = [x,y]

        elif event == cv2.EVENT_RBUTTONUP:
            self.mouse_state = "RBUTTONUP"
            self.mouse_down  = False
            self.mouse_move  = False
            print('mouse up')
    
    def stop(self):
        #cv2.destroyWindow(self.windowName)
        self._stop_event.set()

    def join(self):
        self.stop()
        super().join()

    def run(self):
        print('Thread started')
        cv2.namedWindow(self.windowName, cv2.WINDOW_GUI_NORMAL)
        cv2.setMouseCallback(self.windowName, self.CallBackFunc)
        
        b=20
        pt_ind=None
        while not self._stop_event.is_set():
            img = self.img.copy()

            if self.new_mouse_down:
                'Check if mouse click is inside a track rect'
                self.new_mouse_down=False
                match=False
                for i, pt in enumerate(self.pts):
                    if abs(pt[0]-self.pt[0]) < b and abs(pt[1]-self.pt[1])<b:
                        pt = self.pt
                        pt_ind = i
                        print("clicked inside rect:",pt_ind)
                        match=True
                        break
                if not match:
                    'Add point to pts if click is outside track rects'
                    pt_ind=None
                    self.pts.append(self.pt)
                    print('pt added:',self.pts)

            if self.mouse_move:
                'Update pt if mouse moved with Rdown'
                if pt_ind is not None:
                    self.pts[pt_ind] = self.pt
                    #print('moving:',self.pts)

            'Draw track rects'
            for i, pt in enumerate(self.pts):
                if i==pt_ind:
                    cv2.rectangle(img, (pt[0]-b,pt[1]-b), (pt[0]+b,pt[1]+b),(0,255,0),3)
                else:
                    cv2.rectangle(img, (pt[0]-b,pt[1]-b), (pt[0]+b,pt[1]+b),(255,0,0),3)
            
            cv2.imshow(self.windowName, img)
            if cv2.waitKey(20) == 27:
                cv2.destroyWindow(self.windowName)
                np.save('pts.npy',self.pts)
                break
        print("thread stopped!")

def main():
    img = cv2.imread('bradley_cooper.jpg')
    mouseobj = MousePtsThread(img)
    
    while True:
        # Mian thread logic can goes here
        time.sleep(1)
        if not(mouseobj.is_alive()):
            break
        
    # Optional, incase main while loop exited before thread exit
    if mouseobj.is_alive():
        mouseobj.stop() 
    mouseobj.join()
    print("main stopped!")
    print('Final pts:',mouseobj.pts)

    #import pdb;pdb.set_trace()

if __name__ == "__main__":
    main()
