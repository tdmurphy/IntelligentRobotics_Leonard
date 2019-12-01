import rospy
from geometry_msgs.msg import Twist, Point, PoseWithCovariance,Pose
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Odometry
import numpy as np
import math
import scipy as scp
import rrt_star

#constants
VELOCITY = 0.4
ANGULAR_VEL = 0.2
base_data = Twist()
MOVE = True
pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
DIRECTIONS = []
WAYPOINT_BOUNDARY = 0.5
ON_PATH = True
HEADING_TOLERANCE = 0.01
AVOIDING = False


def getHeading (pose, dest):
    yDist = dest[1] - pose.pose.position[1]
    xDist = dest[0] - pose.pose.position[0]
    mapAngle = math.atan(yDist/xDist)
    return mapAngle - pose.pose.angle #(????)

def detectObst():
    #need all forward detection metrics
    #noise filtering?

def avoidObst():
    #insert hug wall?

    #if ahead and or frontright: turn left
    #if frontleft: turn right

    #step forward
    #check if clear
    #veer back towards original trajectory

def checkInBoundary(p1, p2):
    xDist = sqrt(p1[0]^2 + p2[0]^2)
    yDist = sqrt(p1[1]^2 + p2[0]^2)
    
    return all(i<=WAYPOINT_BOUNDARY for i in [xDist, yDist])

def moveBot (data, current_pose, dest):

    thresholds = np.full(len(data.data), DETECTING_RANGE)
    zipped = zip(data.data, thresholds)
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

    crash = frontLeftDetecting or midDetecting or frontRightDetecting

    return False

    if MOVE:
        if crash or AVOIDING:
            if (not AVOIDING) or crash:
                base_data.linear.x=0
                if not FrontLeftDetecting or FarLeftDetecting:
                    base_data.angular.z = 0.7
                    TURNED_LEFT = True
                else:
                    base_data.angular.z = -0.7
                    TURNED_LEFT = False
                AVOIDING = TRUE
            else
                if (TURNED_LEFT and not farRightDetecting) or ((not TURNED_LEFT) and not farLeftDetecting):
                    AVOIDING = False
                    base_data.linear.x=0
                elif 
                base_data.angular.z=0
                base_data.linear.x=VELOCITY/1.5
            
            
            #avoidObst()
            ON_PATH = False

        elif not ON_PATH:
            AVOIDING = False
            DIRECTIONS = rrt_star.do_rrt(current_pos, dest)
            rand_V5.renderGui(DIRECTIONS)
            if checkInBoundary(current_pos, dest):

            elif abs(getHeading(current_pose, DIRECTIONS[0])) <= HEADING_TOLERANCE:
                ON_PATH = True
                base_data.angular.z=0
                base_data.linear.x=VELOCITY
            else:
                base_data.angular.z=getHeading(current_pose, dest)


        else:           #ON_PATH
            AVOIDING = False
            if checkInBoundary(current_pos, dest):
                base_data.linear.x = 0
                base_data.angular.z = 0
                ON_PATH = FALSE
            elif checkInBoundary(current_pos, DIRECIONS[0]):
                base_data.linear.x = 0
                DIRECTIONS.pop(0)
            elif abs(getHeading(current_pose, DIRECTIONS[0])) <= HEADING_TOLERANCE:
                base_data.linear.x=0
                ON_PATH=False
            else:
                base_data.angular.z=0
                base_data.linear.x=VELOCITY

    else:
        base_data.linear.x = 0
        base_data.angular.z = 0

    pub.publish(base_data)

def talker():
    rospy.init_node('Mover', anonymous=True)
    rospy.Subscriber('laser_reading', '/amcl_pose', '/destination_pose',Float32MultiArray, moveBot)
    #rospy.Subscriber('odom',Odometry, determineIfComplete)
    # rate = rospy.Rate(10) # 10hz

    rospy.spin()
        # rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
