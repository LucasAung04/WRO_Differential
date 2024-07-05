#Lane center
import cv2
import numpy as np

class LaneCenter:
    def CalcLC(image):
        TurnGray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        Edge=cv2.Canny(TurnGray,30,150)
        lines=cv2.HoughLinesP(Edge,1,np.pi/180 ,100, MiniLineLength=100,MaxLGap=50)
        if lines is not None:
            line_parameters=lines[:,0]
            L_line=line_parameters[np.argmin(line_parameters[:,0])]
            R_line=line_parameters[np.argmax(line_parameters[:,0])]
            
            lane_center=(L_line[0]+R_line[2])/2
            return lane_center
        else:
            return None
        
    img=cv2.imread('lane_image.jpg')
    lane_center=CalcLC(img)
    
            