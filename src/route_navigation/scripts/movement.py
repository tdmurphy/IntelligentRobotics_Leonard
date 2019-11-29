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


def getHeading (pose, dest):


def detectObst():
    #need all forward detection metrics
    #noise filtering?
    return False

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

def moveBot (dest):

    elif detectObst():
        base_data.linear.x=0
        avoidObst()
        ON_PATH = False

    elif not ON_PATH:
        DIRECTIONS = rrt_star.do_rrt(current_pos, dest)
        if checkInBoundary(current_pos, dest):

        elif getHeading(current_pose, dest) <= HEADING_TOLERANCE:
            ON_PATH = True
            base_data.angular.z=0
        else:
            base_data.angular.z=getHeading(current_pose, dest)


    else:           #ON_PATH
        if checkInBoundary(current_pos, dest):
            base_data.linear.x = 0
            base_data.angular.z = 0
            ON_PATH = FALSE

