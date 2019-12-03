import rospy
from geometry_msgs.msg import Twist, Point, PoseWithCovariance,Pose
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped
import numpy as np
import math
import scipy as scp
import rrt_star
import sys

#constants
VELOCITY = 0.4
ANGULAR_VEL = 0.2
DETECTING_RANGE = 0.6
GRANULARITY = 19
base_data = Twist()
MOVE = True
pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
DIRECTIONS = []
WAYPOINT_BOUNDARY = 0.5
ON_PATH = True
HEADING_TOLERANCE = 0.11
AVOIDING = False
AMCL = None
DEST = None
TURNED_LEFT = False
HEADING = None
LAST_ODOM = None
LAST_AMCL = None
TRUEPOSE = None
LAST_HEADING = None

routePublisher = rospy.Publisher('/route_nodes', Float32MultiArray, queue_size=100)

def getHeading2(q):
    """
    Get the robot heading in radians from a Quaternion representation.

    :Args:
        | q (geometry_msgs.msg.Quaternion): a orientation about the z-axis
    :Return:
        | (double): Equivalent orientation about the z-axis in radians
    """
    yaw = math.atan2(2 * (q.x * q.y + q.w * q.z),
                     q.w * q.w + q.x * q.x - q.y * q.y - q.z * q.z)
    return yaw

def odomSubscriber (data):
    global LAST_ODOM, HEADING, AMCL, LAST_AMCL
    if LAST_ODOM == None:
        LAST_ODOM = data
        return 69
    if LAST_HEADING == None or LAST_AMCL == None:
        print "heading none"
        return 69
    
    AMCL[0] = int(LAST_AMCL[0] + data.pose.pose.position.x - LAST_ODOM.pose.pose.position.x)
    AMCL[1] = int(LAST_AMCL[1] + data.pose.pose.position.y - LAST_ODOM.pose.pose.position.y)
    HEADING = LAST_HEADING + (getHeading2(data.pose.pose.orientation) - getHeading2(LAST_ODOM.pose.pose.orientation))
    print(getHeading2(data.pose.pose.orientation), getHeading2(LAST_ODOM.pose.pose.orientation))
    print("LAST HEADING: ", LAST_HEADING, "HEADING: ", HEADING)
    return 420

def poseSubscriber (localisation_pos):
    global AMCL, HEADING, LAST_ODOM, TRUEPOSE, LAST_AMCL, LAST_HEADING
    LAST_ODOM = None
    print(localisation_pos)
    actual_resolution_x = localisation_pos.pose.pose.position.x*(605./33.1)
    actual_resolution_y = localisation_pos.pose.pose.position.y*(528./31.95)

    print("actual x ",actual_resolution_x)
    print("actual y",actual_resolution_y)

    origin_translation = [int(actual_resolution_x), 529 - int(actual_resolution_y)]

    TRUEPOSE = [localisation_pos.pose.pose.position.x, localisation_pos.pose.pose.position.y]
    AMCL = origin_translation
    LAST_AMCL = origin_translation
    HEADING = getHeading2(localisation_pos.pose.pose.orientation)
    LAST_HEADING = getHeading2(localisation_pos.pose.pose.orientation)
    print ('original amcl: ', [localisation_pos.pose.pose.position.x, localisation_pos.pose.pose.position.y],'AMCL: ', AMCL)
    print ('heading: ', HEADING, LAST_HEADING)

def destSubscriber (dest):
    global DEST, HEADING
    print(dest)
    DEST = [int(dest.data[0]), int(dest.data[1])]
    print ('dest: ', DEST)

def getHeading (pose, dest, heading):
    yDist = dest[1] - pose[1]
    xDist = dest[0] - pose[0]
    if yDist == 0:
        if xDist == 0:
            print("return 0")
            return 0
        else:
            print("return: ", math.pi - 0.1)
            return math.pi - 0.1
    #mapAngle = math.atan(xDist/yDist)
    mapAngle = math.atan2(yDist,xDist)
    if xDist < 0 and yDist < 0:
        mapAngle += math.pi
    elif xDist < 0 and yDist > 0:
        mapAngle -= math.pi

    print abs(mapAngle)

    if abs(mapAngle) > math.pi:
        print("unmod mapAngle", mapAngle)
        mapAngle = mapAngle % (math.pi)

    print("getheading: ", pose, dest, heading)
    print("original coords: ", TRUEPOSE)
    print("mapAngle: ", mapAngle)
    total = mapAngle - HEADING

    if abs(total) > math.pi:
        print("unmod total", total)
        total = (total % 2*(math.pi))-math.pi
    print('total: ', total)
    return total #(????)

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
    dist = math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)
    
    print("dist: ", dist)
    return dist<=WAYPOINT_BOUNDARY

def moveBot (data):
    global AVOIDING, ON_PATH, DIRECTIONS, TURNED_LEFT, MOVE

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
        if(x<=0.4):
            farLeftDetecting = True

    for (x,y) in frontLeftReadings:
        if(x<=y):
            frontLeftDetecting = True

    for (x,y) in midReadings:
        if(x<=y):
            midDetecting = True

    for (x,y) in frontRightReadings:
        if(x<=y):
            frontRightDetecting = True

    for (x,y) in farRightReadings:
        if(x<=0.4):
            farRightDetecting = True

    crash = frontLeftDetecting or midDetecting or frontRightDetecting


    if len(DIRECTIONS) == 0 and (not (DEST == None)):
        DIRECTIONS = rrt_star.rrt(AMCL, DEST)
        onedDirection = []
        for d in DIRECTIONS:
            onedDirection.append(d[0])
            onedDirection.append(d[1])
        print onedDirection
        message = Float32MultiArray()
        message.data = onedDirection
        routePublisher.publish(message)

    crash = False
    ON_PATH = True


    if MOVE and (not (AMCL == None)) and (not (DEST == None)):
        print ("i'm moving yo")

        print('Distance: ', math.sqrt((AMCL[0]-DIRECTIONS[0][0])**2+(AMCL[1]-DIRECTIONS[0][1])**2))

        print('DIRECTIONS: ', DIRECTIONS)
        if crash or AVOIDING:
            print("2fast2furious")
            if (not AVOIDING) or crash:
                base_data.linear.x=0
                if abs(base_data.angular.z) == 0:
                    if not frontLeftDetecting or not farLeftDetecting:
                        base_data.angular.z = 0.6
                        TURNED_LEFT = True
                        print('turning left')
                    else:
                        base_data.angular.z = -0.6
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
            onedDirection = []
            for d in DIRECTIONS:
                onedDirection.append(d[0])
                onedDirection.append(d[1])
            print onedDirection
            message = Float32MultiArray()
            message.data = onedDirection
            routePublisher.publish(message)
            #message = Float32MultiArray()
            #message.data = DIRECTIONS
            #routePublisher.publish(message)
            #rand_V5.renderGui(DIRECTIONS)
            if checkInBoundary(AMCL, DEST):
                #reached end goal
                base_data.angular.z = 0
                base_data.linear.x = 0
                #notify someone i guess
            elif abs(getHeading(AMCL, [DIRECTIONS[0][0], 528-DIRECTIONS[0][1]], HEADING)) <= HEADING_TOLERANCE:
                ON_PATH = True
                base_data.angular.z=0
                base_data.linear.x=VELOCITY
            else:
                base_data.angular.z=getHeading(AMCL, DEST, HEADING)
                ON_PATH = True


        else:           #ON_PATH
            print ("keep goin")
            AVOIDING = False
            if checkInBoundary(AMCL, DEST):
                base_data.linear.x = 0
                base_data.angular.z = 0
                ON_PATH = FALSE
            elif checkInBoundary(AMCL, DIRECTIONS[0]):
                print("got to checkpoint: ", DIRECTIONS[0])
                base_data.linear.x = 0
                DIRECTIONS.pop(0)
            elif checkInBoundary(AMCL, DEST):
                MOVE = False
            elif not abs(getHeading(AMCL, DIRECTIONS[0], HEADING)) <= HEADING_TOLERANCE:
                print('reorientating')
                base_data.linear.x=0
                base_data.angular.z=np.sign(getHeading(AMCL, DIRECTIONS[0], HEADING))/3
                #ON_PATH=False
            else:
                print ('press on')
                #if farLeftDetecting:
                #    base_data.angular.z=-0.7
                #elif farRightDetecting:
                #    base_data.angular.z=0.7
                #else:
                base_data.angular.z=0
                base_data.linear.x=VELOCITY

    else:
        print("stop", AMCL, DEST)
        base_data.linear.x = 0
        base_data.angular.z = 0

    pub.publish(base_data)

def talker():
    rospy.init_node('Mover', anonymous=True)
    rospy.Subscriber('odom',Odometry, odomSubscriber)
    rospy.Subscriber('amcl_pose', PoseWithCovarianceStamped, poseSubscriber)
    print('amcl: ', AMCL)
    rospy.Subscriber('destination_pose', Float32MultiArray, destSubscriber)
    print('dest: ',  DEST)
    rospy.Subscriber('laser_reading', Float32MultiArray, moveBot)
    # rate = rospy.Rate(10) # 10hz

    rospy.spin()
        # rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
