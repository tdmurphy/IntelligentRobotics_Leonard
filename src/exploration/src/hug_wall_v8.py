import rospy
from geometry_msgs.msg import Twist,Point,PoseWithCovariance,Pose
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Odometry
import numpy as np
import math
from scipy import stats

pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
base_data = Twist()

#constants 
VELOCITY = 0.2
GRANULARITY = 19
DETECTING_RANGE = 1.1
FIND_WALL_TURN = 0.35
HARD_RIGHT = -0.6
CORRECT_COURSE = -0.3
CLOSE_CORRECT_COURSE = 0.65
FAR_CORRECT_COURSE = 0.75
CORRECT_COURSE_RANGE = 0.75
base_data = Twist()
BEGUN_EXPLORATION = False
START_POSITION = None
STOP_MOVING = False
START_POSITION_BOUNDARY = 0.5
CONSIDER_STOPPING = False

def findWall(data):
    print("Attempting to find wall")
    base_data.linear.x = VELOCITY
    if base_data.angular.z <= 0:
        base_data.angular.z = FIND_WALL_TURN

def hardRight(data):
    print("hard right")
    base_data.angular.z = HARD_RIGHT
    for(x,y) in data:
        if(x <= 0.5):
            base_data.angular.z = -1
    print(base_data.angular.z)

def defineMovement(data):
    global STOP_MOVING
    global CORRECT_COURSE_RANGE
    global FAR_CORRECT_COURSE
    global CLOSE_CORRECT_COURSE
    thresholds = np.full(len(data.data), DETECTING_RANGE)
    zipped = list(zip(data.data, thresholds))
    increment = int(len(zipped)/(GRANULARITY/3))

    farLeftReadings = zipped[0:increment]
    frontLeftReadings = zipped[increment:increment*2]
    midReadings = zipped[increment*2:increment*3]
    frontRightReadings = zipped[increment*3:increment*4]
    farRightReadings = zipped[increment*4:]
    
    farLeftDetecting = False
    frontLeftDetecting = False
    midDetecting = False
    frontRightDetecting = False
    farRightDetecting = False
    frontRightCrash = False
    farRightCrash = False 

    for (x,y) in farLeftReadings:
        if(x<=y):
            farLeftDetecting = True

    for (x,y) in frontLeftReadings:
        if(x<=y):
            frontLeftDetecting = True

    for (x,y) in midReadings:
        if(x<=y):
            midDetecting = True

    for (x,y) in frontRightReadings:
        if(x<=2):
            frontRightDetecting = True

    for (x,y) in farRightReadings:
        if(x<=y):
            farRightDetecting = True

    for (x,y) in farRightReadings:
        if(x<=0.75):
            farRightCrash = True

    if(not(midDetecting) and not(frontLeftDetecting) and not(farLeftDetecting)):
        findWall(data.data)
    elif(midDetecting):
        base_data.linear.x = 0
        if(base_data.angular.z >= 0):
            hardRight(midReadings)
    elif(farRightCrash):
        if(base_data.angular.z>=0):
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

    if(frontRightDetecting):
            print("close following")
            CORRECT_COURSE_RANGE = CLOSE_CORRECT_COURSE
    else:
        print("far following")
        CORRECT_COURSE_RANGE = FAR_CORRECT_COURSE

        farLeftCorrection = False
        for(x,y) in farLeftReadings:
            if(x <= CORRECT_COURSE_RANGE):
                farLeftCorrection = True

        frontLeftCorrection = False
        for(x,y) in frontLeftReadings:
            if(x <= (CORRECT_COURSE_RANGE + 0.1)):
                frontLeftCorrection = True
        
        print("Far L - " + str(farLeftCorrection) + " Front L - " +str(frontLeftCorrection))
        base_data.linear.x = VELOCITY/2
        if ((farLeftCorrection or frontLeftCorrection) and base_data.angular.z==0):
            base_data.angular.z = CORRECT_COURSE
            print("correcting course right")
        else:
            base_data.linear.x = VELOCITY
            base_data.angular.z = 0

    if(not STOP_MOVING):
        pub.publish(base_data)
    else:
        base_data.linear.x = 0
        base_data.angular.z = 0
        pub.publish(base_data)

def determineIfComplete(data):
    global BEGUN_EXPLORATION
    global STOP_MOVING
    global START_POSITION
    global CONSIDER_STOPPING
    odomPose = data.pose.pose.position
    if(odomPose.x != 0 and odomPose.y != 0 and BEGUN_EXPLORATION == False):
        print("I have begun my exploration")
        BEGUN_EXPLORATION = True
        START_POSITION = odomPose
    elif(BEGUN_EXPLORATION ==  True):
        totalMovement = np.absolute((odomPose.x - START_POSITION.x) + (odomPose.y - START_POSITION.y))

        if(totalMovement > START_POSITION_BOUNDARY*2 and CONSIDER_STOPPING == False):
            print("I can now consider stopping")
            CONSIDER_STOPPING = True

        if(CONSIDER_STOPPING == True):
            xBoundary = np.absolute(odomPose.x - START_POSITION.x)
            yBoundary = np.absolute(odomPose.y - START_POSITION.y)

            if(xBoundary <= START_POSITION_BOUNDARY and yBoundary <= START_POSITION_BOUNDARY):
                print("I've reached my start position")
                STOP_MOVING = True

    

def talker():
    rospy.init_node('Mover', anonymous=True)
    rospy.Subscriber('laser_reading',Float32MultiArray, defineMovement)
    rospy.Subscriber('odom',Odometry, determineIfComplete)
    # rate = rospy.Rate(10) # 10hz

    rospy.spin()
        # rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass