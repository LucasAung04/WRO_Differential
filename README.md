# WRO_Differential

## Future Engineer attempt by SP Team Differential

We are Students from Robotics Innovation & Technology club from Singapore Polythenics. Our team consist of three members: Zeliks , Lucas and Benedict. We create our team on 4<sup>th</sup> June  2024 after our club's Annual General Meeting. In that meeting, we found out about this competitions. Let's get into the contents of our robot. 

### Team Photo
![Team Photo](TeamPic.jpg)

***Conponents we using in our robots***

*	**TB6612FNG motor driver**
*	**Differential Gear**
*	**180 servo for steering**
*	**Gear motor**
*	**Breadboard** 
*	**2 x 8 cm diameter back wheel** 
*	**2 x 5 cm diameter front wheel**
*	**Asus Webcam C3** 
*	**4 x ultrasonics sensors**
*	**9v Battery**

### Steering 

For steering, we use principles of Ackerman Steering Mechanism. The steering is connected by Tie Rod which make two wheels turn at different angles. So, it make possible for two wheels rotates at different speed which make turning smoother and accurate cornering. This method ensures that the wheels follow the ideal turning path where each obstacle are close to each other.

### Servo

The servo is integrated with a camera-based color detection module that identifies specific colors and adjusts the robot’s direction accordingly. It serveas as main role of our robots. Servo will steer the robots not to crash into wall or obstacle. When camera detact the red, it will signal the servo to turn at maximum degree to right and for green, it will turn to left and guiding the robots through the best path.

### Motor at Rear

We use TB6612FNG motor driver to run the motor. The TB6612FNG motor driver provides precise control over the motor, regulating speed and direction. It is capable of driving the motor with high efficiency and accuracy, ensuring that the differential gear system operates optimally. It can adjust the speed according to respond to different conditions. The motor driver also includes built-in protections such as thermal shutdown, overcurrent protection, and undervoltage lockout, which safeguard the motor and the overall system during operation.

### The program consists of 6 functions under the class constructor Killbot.( [KillBot.py](KillBot.py) )

The idea is to use the information captured from the frame of web cam to determine the course of direction. We apply the Hough transform to identify the border line and calculate the centre line using it. This will ensure that the bot will follow the middle of the path when facing no obstacles. To determine when to turn, we use the intersection of border lines. This is calculated under the Corner Type function. The function determines whether the corner is a left turning corner or a right turning corner.
The value returned from this function get passed through other methods to 
1. Slow down the motor driver when approaching corners
2. Set the servo angle to steer the car to turn
When the camera detects the obstacle, the frame is analysed to determine the colour of the block. This is done by defining the range of RGB values and checking the captured frame with it. The returning value from the function is passed through to determine whether to avoid to the left or right. With the information from camera, distance from the position of obstacle to position of the track border line is obtained by estimation and subsequently a new centre line to follow is derived. The bot now shifts to follow the new centre line and after the obstacle is passed, it returns to original centre line. The centre line is constantly calculated and updated per each passing frame.
The ultrasonic setup is used to aid the calculations. Four ultrasonic sensors are placed at each side of the bot. The front and back helps in calculation of positioning along the centre line. Left and right helps the bot to maintain its course through the middle of track. 
