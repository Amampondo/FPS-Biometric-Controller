import numpy as np
import cv2 as cv
import stdio
from shoot import Shooter
from magazine import Magazine
from scope import Scope
 
cap = cv.VideoCapture('prime.mp4')
cap2 = cv.VideoCapture(0)

shooter = Shooter()

load = Magazine(8*30 ,26*30)

scope = Scope(load)

isZoom = False
 
while cap.isOpened():
    ret, frame = cap.read()
    ret2 , frame2 = cap2.read()
    
    if not ret or not ret2:
        break
    
    frame2 = cv.flip(frame2,1)
    frame2 , isZoom = scope.detect(frame2)
    frame2 , isShoot = shooter.detect(frame2)

    #resizing and creating a mask
    size = 150
    frame2 = cv.resize(frame2, (size, size) )
    img2gray = cv.cvtColor(frame2, cv.COLOR_BGR2RGB) 
    ret, mask = cv.threshold(img2gray, 1, 255, cv.THRESH_BINARY)
    
    roi = frame[-size-10:-10, -size-10:-10] 
  
    # Set an index of where the mask is 
    roi[np.where(mask)] = 0
    roi += frame2 
 
    # if frame is read correctly ret is True
    if not ret or not ret2 :
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    gray = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    
    pos = 600
    if isZoom :
        load.zoom()
    if isShoot == True:
        load.increase()
        
    cap.set(cv.CAP_PROP_POS_FRAMES,load.count())
 
    cv.imshow('frame', gray)
    if cv.waitKey(10) == ord('q'):
        break
 
cap.release()
cv.destroyAllWindows()
