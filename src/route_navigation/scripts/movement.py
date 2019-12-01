import rospy
from geometry_msgs.msg import Twist, Point, PoseWithCovariance,Pose
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped
import numpy as np
import math
import scipy as scp
import rrt_star

#constants
VELOCITY = 0.4
ANGULAR_VEL = 0.2
DETECTING_RANGE = 0.5
GRANULARITY = 19
base_data = Twist()
MOVE = True
pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
DIRECTIONS = []
WAYPOINT_BOUNDARY = 0.5
ON_PATH = True
HEADING_TOLERANCE = 0.01
AVOIDING = False
AMCL = None
DEST = None
HEADING = 0


def poseSubscriber (localisation_pos):
    global AMCL, HEADING
    print(localisation_pos)
    actual_resolution_x = localisation_pos.pose.pose.position.x/0.05
    actual_resolution_y = localisation_pos.pose.pose.position.y/0.05

    print("actual x ",actual_resolution_x)
    print("actual y",actual_resolution_y)

    origin_translation = [int(actual_resolution_x), int(522 - actual_resolution_y)]

    AMCL = origin_translation
    HEADING = localisation_pos.pose.position.z
    print (AMCL)

def destSubscriber (dest):
    global DEST, HEADING
    print(dest)
    DEST = [int(dest.data[0]), int(dest.data[1])]
    print (DEST)

def getHeading (pose, dest, heading):
    yDist = dest[1] - pose[1]
    xDist = dest[0] - pose[0]
    mapAngle = math.atan(yDist/xDist)
    return mapAngle - HEADING #(????)

#def detectObst():
    #need all forward detection metrics
    #noise filtering?

#def avoidObst():
    #insert hug wall?

    #if ahead and or frontright: turn left
    #if frontleft: turn right

    #step forward
    #check if clear
    #veer back towards original trajectory

def checkInBoundary(p1, p2):
    xDist = math.sqrt(p1[0]**2 + p2[0]**2)
    yDist = math.sqrt(p1[1]**2 + p2[0]**2)
    
    return all(i<=WAYPOINT_BOUNDARY for i in [xDist, yDist])

def moveBot (data):
    global AVOIDING, ON_PATH, DIRECTIONS, TURNED_LEFT 
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

    if len(DIRECTIONS) == 0 and (not (DEST == None)):
        DIRECTIONS = rrt_star.rrt(AMCL, DEST)

    if MOVE and (not (AMCL == None)) and (not (DEST == None)):
        print ("i'm moving yo")
        if crash or AVOIDING:
            print("2fast2furious")
            if (not AVOIDING) or crash:
                base_data.linear.x=0
                if not frontLeftDetecting or not farLeftDetecting:
                    base_data.angular.z = 0.7
                    TURNED_LEFT = True
                    print('turning left')
                else:
                    base_data.angular.z = -0.7
                    TURNED_LEFT = False
                    print('turning right')
                AVOIDING = True
            else:
                if (TURNED_LEFT and not farRightDetecting) or ((not TURNED_LEFT) and not farLeftDetecting):
                    AVOIDING = False
                    base_data.linear.x=0
                else:
                    base_data.angular.z=0
                    base_data.linear.x=VELOCITY/1.5
            
            
            #avoidObst()
            ON_PATH = False

        elif not ON_PATH:
            print("off course")
            AVOIDING = False
            DIRECTIONS = rrt_star.rrt(AMCL, DEST)
            #rand_V5.renderGui(DIRECTIONS)
            if checkInBoundary(AMCL, DEST):
                #reached end goal
                base_data.angular.z = 0
                base_data.linear.x = 0
                #notify someone i guess
            elif abs(getHeading(AMCL, DIRECTIONS[0], HEADING)) <= HEADING_TOLERANCE:
                ON_PATH = True
                base_data.angular.z=0
                base_data.linear.x=VELOCITY
            else:
                base_data.angular.z=getHeading(AMCL, DEST, HEADING)


        else:           #ON_PATH
            print ("keep goin")
            AVOIDING = False
            if checkInBoundary(AMCL, DEST):
                base_data.linear.x = 0
                base_data.angular.z = 0
                ON_PATH = FALSE
            elif checkInBoundary(AMCL, DIRECTIONS[0]):
                base_data.linear.x = 0
                DIRECTIONS.pop(0)
            elif abs(getHeading(AMCL, DIRECTIONS[0], HEADING)) <= HEADING_TOLERANCE:
                base_data.linear.x=0
                ON_PATH=False
            else:
                base_data.angular.z=0
                base_data.linear.x=VELOCITY

    else:
        print("stop", AMCL, DEST)
        base_data.linear.x = 0
        base_data.angular.z = 0

    pub.publish(base_data)

def talker():
    rospy.init_node('Mover', anonymous=True)
    rospy.Subscriber('amcl_pose', PoseWithCovarianceStamped, poseSubscriber)
    print('amcl: ', AMCL)
    rospy.Subscriber('destination_pose', Float32MultiArray, destSubscriber)
    print('dest: ',  DEST)
    rospy.Subscriber('laser_reading', Float32MultiArray, moveBot)
    #rospy.Subscriber('odom',Odometry, determineIfComplete)
    # rate = rospy.Rate(10) # 10hz

    rospy.spin()
        # rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
