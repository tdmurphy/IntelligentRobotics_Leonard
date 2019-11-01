import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
import numpy as np
import math
from scipy import stats

pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
base_data = Twist()

#constants 
VELOCITY = 0.2
GRANULARITY = 15
DETECTING_RANGE = 1.0
base_data = Twist()

def findWall(data):
    print("Attempting to find wall")
    base_data.linear.x = VELOCITY
    if base_data.angular.z <= 0:
        base_data.angular.z = 0.4

def hardRight(data):
    print("hard right")
    base_data.angular.z = -0.6
    for(x,y) in data:
        if(x <= 0.5):
            base_data.angular.z = -1
    print(base_data.angular.z)

def defineMovement(data):
    thresholds = np.full(len(data.data), DETECTING_RANGE)
    zipped = zip(data.data, thresholds)
    increment = int(len(zipped)/(GRANULARITY/3))
    farLeftReadings = zipped[0:increment]
    midReadings = zipped[increment*2:increment*3]
    farRightReadings = zipped[increment*4:]
    frontLeftReadings = zipped[increment:increment*2]
    frontRightReadings = zipped[increment*3:increment*4]
    
    frontLeftDetecting = False
    midDetecting = False
    frontRightDetecting = False
    farRightDetecting = False
    farLeftDetecting = False

    for (x,y) in frontLeftReadings:
        if(x<=y):
            frontLeftDetecting = True

    for (x,y) in midReadings:
        if(x<=y):
            midDetecting = True

    for (x,y) in frontRightReadings:
        if(x<=y):
            rightDetecting = True
    for (x,y) in farRightReadings:
        if(x<=y):
            farRightDetecting = True
    for (x,y) in farLeftReadings:
        if(x<=y):
            farLeftDetecting = True

    if(not(midDetecting) and not(frontLeftDetecting) and not(farLeftDetecting)):
        findWall(data.data)
    elif(midDetecting):
        base_data.linear.x = 0
        if(base_data.angular.z >= 0):
            hardRight(midReadings)
   # elif(frontLeftDetecting and not(farLeftDetecting)):
   #     frontLeftDetection = False
   #     for(x,y) in frontLeftReadings:
   #         if(x <= 0.9):
   #             frontLeftDetection = True
   #     if(frontLeftDetection and base_data.angular.z != -0.4):
   #         print("Obstacle in my front left region")
   #         base_data.angular.z = -0.4
    else:
        print("Im following a wall")
        farLeftCorrection = False
        for(x,y) in farLeftReadings:
            if(x <= 0.75):
                farLeftCorrection = True

        frontLeftCorrection = False
        for(x,y) in frontLeftReadings:
            if(x <= 0.85):
                frontLeftCorrection = True
        
        print("Far L - " + str(farLeftCorrection) + " Front L - " +str(frontLeftCorrection))
        base_data.linear.x = VELOCITY/2
        if ((farLeftCorrection or frontLeftCorrection) and base_data.angular.z==0):
            base_data.angular.z = -0.3
            print("correcting course right")
        else:
            base_data.linear.x = VELOCITY
            base_data.angular.z = 0
    pub.publish(base_data)
    

def talker():
    rospy.init_node('Mover', anonymous=True)
    rospy.Subscriber('laser_reading',Float32MultiArray,defineMovement)
    # rate = rospy.Rate(10) # 10hz

    rospy.spin()
        # rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
