# camera_check.py
# 调用摄像头实时画面，按q键退出


import cv2
import numpy as np
from utils_robot import *

move_to_top_view()
cap = cv2.VideoCapture(0)

while(True):
    ret, frame = cap.read()

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
