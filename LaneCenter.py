import cv2
import numpy as np
import time
import RPi.GPIO as GPIO
SERVOPIN = 17  
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVOPIN, GPIO.OUT)
pwm = GPIO.PWM(SERVOPIN, 50) 
class Camera: 
    def set_servo_angle(angle):
        #angle 0-180 
        duty_cycle = (angle / 180) * (2.5 - 1) + 1
        pwm.ChangeDutyCycle(duty_cycle)
    pwm.start(1)  #cycle t
    class LaneDetector:
        def __init__(self, hough_threshold=100, min_line_length=100, max_line_gap=50):
            self.hough_threshold = hough_threshold
            self.min_line_length = min_line_length
            self.max_line_gap = max_line_gap
        def calculate_lane_center(self, image):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            # hough transform probably scuffed ask Felix later
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, self.hough_threshold, 
                                   minLineLength=self.min_line_length,
                                   maxLineGap=self.max_line_gap)
            if lines is not None:
                line_parameters = lines[:, 0]
                left_line = line_parameters[np.argmin(line_parameters[:, 0])]
                right_line = line_parameters[np.argmax(line_parameters[:, 0])]
                lane_center = (left_line[0] + right_line[2]) / 2
                return lane_center
            else:
                return None
    lane_detector = LaneDetector()  
    cap = cv2.VideoCapture(1)  
    try:
        while True:
            ret, frame = cap.read()  
            if not ret:
                break  
            lane_center = lane_detector.calculate_lane_center(frame)
            if lane_center is not None:
                steering_angle = (lane_center - frame.shape[1] / 2) * 0.1  
                steering_angle = max(-45, min(steering_angle, 45))  
                set_servo_angle(steering_angle + 90)  
            cv2.imshow('Camera Feed', frame)
            if cv2.waitKey(1) & 0xFF == ord('e'):
                break  
    except KeyboardInterrupt:
        print("Program stopped by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        pwm.stop()
        GPIO.cleanup()
            
