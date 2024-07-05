import RPi.GPIO as GPIO
import time
global dist1,dist2,dist3,dist4

class ULsensor:
  
    def __init__(self):
      
        # Declare GPIO pins for ultrasonic sensors
        self.TRIG1 = 23
        self.ECHO1 = 24
        self.TRIG2 = 17
        self.ECHO2 = 27
        self.TRIG3 = 18
        self.ECHO3 = 22
        self.TRIG4 = 2
        self.ECHO4 = 3
        # Set GPIO mode to BCM
        GPIO.setmode(GPIO.BCM)
        # Set trigger pins as output and echo pins as input
        GPIO.setup(self.TRIG1, GPIO.OUT)
        GPIO.setup(self.ECHO1, GPIO.IN)
        GPIO.setup(self.TRIG2, GPIO.OUT)
        GPIO.setup(self.ECHO2, GPIO.IN)
        GPIO.setup(self.TRIG3, GPIO.OUT)
        GPIO.setup(self.ECHO3, GPIO.IN)
        GPIO.setup(self.TRIG4, GPIO.OUT)
        GPIO.setup(self.ECHO4, GPIO.IN)
    def distance(self, TRIG, ECHO):
        """
        Calculates the distance using ultrasonic sensor.
        
            TRIG: GPIO pin for the trigger.
            ECHO: GPIO pin for the echo.
        Returns:
            Distance in centimeters.
        """
        # Send a pulse to the trigger pin
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        # Measure the time taken for the echo to return
        pulse_start = time.time()
        pulse_end = time.time()
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        # Calculate the distance in centimeters
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        return distance
    def read_distances(self):
        """
        Reads distances from all four sensors and returns them as a list.
        Returns:
            A list of distances [dist1, dist2, dist3, dist4] in centimeters.
        """
        dist1 = self.distance(self.TRIG1, self.ECHO1)
        dist2 = self.distance(self.TRIG2, self.ECHO2)
        dist3 = self.distance(self.TRIG3, self.ECHO3)
        dist4 = self.distance(self.TRIG4, self.ECHO4)
        return [dist1, dist2, dist3, dist4]
    def run(self):
       
        try:
            while True:
                distances = self.read_distances()
                print("Sensor 1: {} cm".format(distances[0]))
                print("Sensor 2: {} cm".format(distances[1]))
                print("Sensor 3: {} cm".format(distances[2]))
                print("Sensor 4: {} cm".format(distances[3]))
                time.sleep(0.1)
        except KeyboardInterrupt:
            # Clean up GPIO pins when program is interrupted
            GPIO.cleanup()


sensor = ULsensor()
sensor.run()