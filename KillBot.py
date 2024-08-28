import cv2

import numpy as np

import time

import RPi.GPIO as GPIO



color_ranges = {

    "red": ((0, 70, 50), (10, 255, 255)),

    "green": ((36, 25, 25), (86, 255, 255)),

    "purple": ((129, 50, 70), (158, 255, 255))

}





def detect_colors(frame):# Color detection function

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    detected_colors = []



    for color_name, (lower, upper) in color_ranges.items():

        mask = cv2.inRange(hsv, lower, upper)

        mask = cv2.erode(mask, None, iterations=2)

        mask = cv2.dilate(mask, None, iterations=2)



        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)



        for cnt in contours:

            area = cv2.contourArea(cnt)

            if area > 1000:  # Filter small areas

                detected_colors.append(color_name)

                x, y, w, h = cv2.boundingRect(cnt)

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 0), 2)

                cv2.putText(frame, color_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)





    return detected_colors



class KillBot:

    def __init__(self, servo_pin=17, diff_pin=18, hough_threshold=100, min_line_length=100, max_line_gap=50):

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(servo_pin, GPIO.OUT)

        GPIO.setup(diff_pin, GPIO.OUT)

        self.diff_pwm = GPIO.PWM(diff_pin, 50)  # Use self.diff_pwm

        self.diff_pwm.start(0)

        self.state = "straight"  # Starting state

        self.last_corner_type = None

        self.cap = cv2.VideoCapture(0)



    def set_servo_angle(self, angle):

        angle = max(0, min(180, angle))  # Ensure angle is within valid range

        duty_cycle = (angle / 18) + 2.5  # Convert angle to duty cycle (adjusted formula)



        self.diff_pwm.ChangeDutyCycle(duty_cycle)

        time.sleep(0.1)  # Delay to give servo time



    def Calc_LaneCenter(self, image):

        # Using hough transform and calculating lane center

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, 50, 150)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180,

                               self.hough_threshold,

                               minLineLength=self.min_line_length,

                               maxLineGap=self.max_line_gap)



        corner_points = []

        if lines is not None:  # Angular corner detection

            for line in lines:

                x1, y1, x2, y2 = line[0]

                corner_points.append((x1, y1))

                corner_points.append((x2, y2))

                for i in range(0, int(np.linalg.norm(np.array([x2, y2]) - np.array([x1, y1]))), 10):

                    point1 = (int(x1 + (x2 - x1) * i / np.linalg.norm(np.array([x2, y2]) - np.array([x1, y1]))), int(y1 + (y2 - y1) * i / np.linalg.norm(np.array([x2, y2]) - np.array([x1, y1]))))

                    cv2.circle(image, point1, 2, (0, 0, 255), -1)



        if corner_points:  # If there is corner

            corner_type = self.Corner_Type(corner_points)

            self.state = "corner"  # state is changed

            self.last_corner_type = corner_type

            steering_angle = self.Calc_Corner_SteerAngle(corner_type)

            return (0, 0), steering_angle  # Return Pseudo Center Lane



        else:  # Straight line

            self.state = "straight"

            return (0, 0), None



    def Corner_Type(self, corner_points):  # List of points

        center_x = sum([x for x, y in corner_points]) / len(corner_points)

        center_y = sum([y for x, y in corner_points]) / len(corner_points)

        # Determine left turning or right turning corner

        corner_types = []

        for x, y in corner_points:  # I aint documenting allthat

            if x > center_x and y > center_y:

                corner_types.append("bottom_right")

            elif x < center_x and y > center_y:

                corner_types.append("bottom_left")

            elif x < center_x and y < center_y:

                corner_types.append("top_left")

            else:

                corner_types.append("top_right")

        if self.last_corner_type == "left":

            if "bottom_left" in corner_types:

                return "left"

            elif "top_left" in corner_types:

                return "left"

            else:

                return "right"

        elif self.last_corner_type == "right":

            if "bottom_right" in corner_types:

                return "right"

            elif "top_right" in corner_types:

                return "right"

            else:

                return "left"

        else:

            if "bottom_left" in corner_types:

                return "left"

            elif "top_left" in corner_types:

                return "left"

            elif "bottom_right" in corner_types:

                return "right"

            else:

                return "right"



    def Calc_Corner_SteerAngle(self, corner_type):

        # Couldn't test, i am guesstimating here

        if corner_type == "left":

            return -25

        elif corner_type == "right":

            return 25

        else:

            return 0



    def run(self):

        try:

            while True:

                ret, frame = self.cap.read()

                if not ret:

                    break



                detected_colors = detect_colors(frame)



                if "red" in detected_colors:

                    self.set_servo_angle(60)  # Shift right

                    time.sleep(0.5)

                    self.set_servo_angle(0)  # Stop

                elif "green" in detected_colors:

                    self.set_servo_angle(120)  # Shift left

                    time.sleep(0.5)

                    self.set_servo_angle(0)  # Stop

                else:

                    lane_center, steering_angle = self.Calc_LaneCenter(frame)

                    if steering_angle is not None:

                        self.set_servo_angle(steering_angle + 90)



                if self.state == "straight":

                    self.diff_pwm.ChangeDutyCycle(50)  # Run speed

                elif self.state == "corner":

                    self.diff_pwm.ChangeDutyCycle(20)  # Slow down

                else:

                    self.diff_pwm.ChangeDutyCycle(0)



                cv2.imshow('Cam', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):

                    break



        except KeyboardInterrupt:

            print("Program stopped by user")

        finally:

            self.cap.release()

            cv2.destroyAllWindows()

            self.diff_pwm.stop()

            GPIO.cleanup()



robot = KillBot()

robot.run()

