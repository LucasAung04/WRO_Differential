import cv2
import numpy as np
import time
import RPi.GPIO as GPIO

class LaneFollowingRobot:
    def __init__(self, servo_pin=17, diff_pin=18, hough_threshold=100, min_line_length=100, max_line_gap=50):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(servo_pin, GPIO.OUT)
        GPIO.setup(diff_pin, GPIO.OUT)
        self.diff_pwm = GPIO.PWM(diff_pin, 50)
        self.diff_pwm.start(0)
        self.state = "straight"  # Starting state
        self.last_corner_type = None
        
        # Initialize USB webcam (device index 0)
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Error: Unable to access the webcam.")

        self.obstacle_detected = False

    def set_servo_angle(self, angle):
        angle = max(0, min(180, angle))  # Ensure angle is within valid range
        duty_cycle = (angle / 18) + 2.5  # Convert angle to duty cycle
        self.diff_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.1)  # Delay to give servo time

    def calc_LaneCenter(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, self.hough_threshold,
                               minLineLength=self.min_line_length,
                               maxLineGap=self.max_line_gap)

        corner_points = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                corner_points.append((x1, y1))
                corner_points.append((x2, y2))

        if corner_points:
            corner_type = self.determine_corner_type(corner_points)
            self.state = "corner"
            self.last_corner_type = corner_type
            steering_angle = self.calculate_steering_angle_for_corner(corner_type)
            return (0, 0), steering_angle

        else:
            self.state = "straight"
            return (0, 0), None

    def determine_corner_type(self, corner_points):
        center_x = sum([x for x, y in corner_points]) / len(corner_points)
        center_y = sum([y for x, y in corner_points]) / len(corner_points)
        corner_types = []

        for x, y in corner_points:
            if x > center_x and y > center_y:
                corner_types.append("bottom_right")
            elif x < center_x and y > center_y:
                corner_types.append("bottom_left")
            elif x < center_x and y < center_y:
                corner_types.append("top_left")
            else:
                corner_types.append("top_right")

        if self.last_corner_type == "left":
            return "left" if "bottom_left" in corner_types or "top_left" in corner_types else "right"
        elif self.last_corner_type == "right":
            return "right" if "bottom_right" in corner_types or "top_right" in corner_types else "left"
        else:
            return "left" if "bottom_left" in corner_types or "top_left" in corner_types else "right"

    def calculate_steering_angle_for_corner(self, corner_type):
        return -25 if corner_type == "left" else 25 if corner_type == "right" else 0

    def detect_obstacle(self, frame):
        lower_green = np.array([40, 40, 40], dtype="uint8")
        upper_green = np.array([80, 255, 255], dtype="uint8")
        lower_red = np.array([160, 50, 50], dtype="uint8")
        upper_red = np.array([180, 255, 255], dtype="uint8")

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        mask_red = cv2.inRange(hsv, lower_red, upper_red)
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours_green:
            largest_green_contour = max(contours_green, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_green_contour)
            self.obstacle_detected = True
            return "left"

        if contours_red:
            largest_red_contour = max(contours_red, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_red_contour)
            self.obstacle_detected = True
            return "right"

        self.obstacle_detected = False
        return None

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: No frame captured.")
                    break

                obstacle_side = self.detect_obstacle(frame)

                if obstacle_side == "left":
                    self.set_servo_angle(120)
                elif obstacle_side == "right":
                    self.set_servo_angle(60)
                else:
                    _, steering_angle = self.calc_LaneCenter(frame)
                    if steering_angle is not None:
                        self.set_servo_angle(steering_angle + 90)

                if self.state == "straight":
                    self.diff_pwm.ChangeDutyCycle(50)
                elif self.state == "corner":
                    self.diff_pwm.ChangeDutyCycle(20)
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

# Instantiate and run the robot
robot = LaneFollowingRobot()
robot.run()
