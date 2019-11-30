import rospy
from geometry_msgs.msg import Twist,Point,PoseWithCovariance,Pose
from std_msgs.msg import Float64MultiArray, Float32MultiArray
from nav_msgs.msg import Odometry
import numpy as np
import math
#from scipy import stats
from util import getHeading
from tf.transformations import euler_from_quaternion, quaternion_from_euler
'''

roll = pitch = yaw = 0.0
 
def get_rotation (msg):
    global roll, pitch, yaw
    orientation_q = msg.pose.pose.orientation
    orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
    (roll, pitch, yaw) = euler_from_quaternion (orientation_list)
    print yaw
 
rospy.init_node('my_quaternion_to_euler')
 
sub = rospy.Subscriber ('/odom', Odometry, get_rotation)
 
r = rospy.Rate(1)
while not rospy.is_shutdown():
    quat = quaternion_from_euler (roll, pitch,yaw)
    print quat
    r.sleep()
'''
pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
base_data = Twist()

radians_psec = 0.8
full_spin_rads =  6.28319
#global RAD_COUNT
#RAD_COUNT = 0


def full_circle(data):
    RAD_COUNT = 0
    count = 0
    #rads per second
    while RAD_COUNT < full_spin_rads:
        base_data.angular.z = radians_psec
        RAD_COUNT +=RAD_COUNT + radians_psec
        count = count + 1

        print(count, "inwhile ", RAD_COUNT)

    print(count, "inwhile ", RAD_COUNT)

    pub.publish(base_data)




def talker():





    rospy.init_node('Mover', anonymous=True)
    rospy.Subscriber('laser_reading',Float32MultiArray, full_circle)
    #full_circle()
    rospy.spin()
    # rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass



'''

pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
base_data = Twist()

#constants 
VELOCITY = 0.2
GRANULARITY = 15
DETECTING_RANGE = 1.0
FIND_WALL_TURN = 0.4
HARD_RIGHT = -0.6
CORRECT_COURSE = -0.3
CORRECT_COURSE_RANGE = 0.75
base_data = Twist()
BEGUN_EXPLORATION = False
START_POSITION = None
STOP_MOVING = False
COUNTER = 0


ROTATION_DONE=False
BEARING=0
INCREMENT_ANGLE=0.1
saved_dist=0
BEARING_REACHED=False

def findWall(data):    
    base_data.linear.x = VELOCITY
    print("Attempting to find wall with vel ",base_data.linear.x)
    if base_data.angular.z <= 0:
        base_data.angular.z = FIND_WALL_TURN

def hardRight(data):
    print("hard right")
    base_data.angular.z = HARD_RIGHT
    for(x,y) in data:
        if(x <= 0.5):
            base_data.angular.z = -1
    print(base_data.angular.z)

def detect_object(grain_data):
	avoid=False
	direction=-1
	return avoid, direction

def return_readings(data):
    print("return_readings     ")
    thresholds = np.full(len(data.data), DETECTING_RANGE)
    print("return_readings     ")
    zipped = zip(data.data, thresholds)
    print("return_readings     ")
    increment = int(len(zipped)/(GRANULARITY/3))
    print("return_readings     ")

    L_laser = zipped[0:increment]
    print("return_readings     ")
    FL_laser = zipped[increment:increment*2]
    print("return_readings     ")
    F_laser = zipped[increment*2:increment*3]
    print("return_readings     ")
    FR_laser = zipped[increment*3:increment*4]
    print("return_readings     ")
    R_laser = zipped[increment*4:]
    print("return_readings     ")
    return L_laser,FL_laser,F_laser,FR_laser,R_laser



def turn_right(q,bearing):
    base_data.angular.z=0.05
    if np.abs(bearing- getHeading(q))<0.2:	 
         BEARING_REACHED=True
         base_data.angular.z=0

def goForward():
    base_data.linear.x = VELOCITY


def findClosestWall(data):   
    print("clos wall       ") 
    base_data.angular.z=0.2

    print("clos wall   1    ") 
    print("poseinfo ",data.pose.pose.orientation.x)
    print("clos wall     2  ") 
    BEARING=getHeading(data.pose.pose.orientation) 
    print("clos wall    3   ") 
    print("Spinning, currently at bearing ", BEARING)
    print("clos wall    4   ") 



    if (bearing>=2*np.pi):
        print("clos wall   5    ") 
        ROTATION_DONE=True
        print("ROTATION_DONE")
        print("clos wall  6     ") 

    L_laser,FL_laser,F_laser,FR_laser,R_laser=return_readings(data)
    if(saved_dist==0):
        print("clos wall  7     ") 
        saved_dist=(np.mean(F_laser),bearing)
        print("clos wall  8     ") 

    if (saved_dist[0]>np.mean(F_laser)):
        print("clos wall    9   ") 
        saved_dist=(np.mean(F_laser),bearing)
        print("clos wall  10     ") 
    return saved_dist




def run(data):

    # boolean, float detect object(granulated data)
    # move_right	
        print("run  1")
        L_laser,FL_laser,F_laser,FR_laser,R_laser=return_readings(data)
        print("run  2")
        smallest_dist=findClosestWall(data) 
        print("run  3")
        print("smallest dist ",smallest_dist)
        print("run  4")
        return


def talker():
    print("talker   1 ")
    rospy.init_node('Mover', anonymous=True)
#Odometry
    #rospy.Subscriber('odom',Odometry, run)
    print("talker  2  ")


    
   #rospy.Subscriber('laser_reading',Float32MultiArray, run)
   rospy.Subscriber('odom',Odometry, findClosestWall)
   #rospy.Subscriber('laser_reading',Float64MultiArray, run)
    
    # rate = rospy.Rate(10) # 10hz
    print("talker  3  ")
    rospy.spin()
    print("talker  4  ")
        # rate.sleep()

if __name__ == '__main__':
    try:
        print("main")
        talker()
        print("main")
    except rospy.ROSInterruptException:
        pass



 #   if(not ROTATION_DONE):
  #      smallest_dist=findClosestWall(data)	
	#return
    #if(ROTATION_DONE):
     #   base_data.angular.z=0
	#if not BEARING_REACHED:
	#	turn_right(data.pose.pose.orientation,smallest_dist[1])
     #   if BEARING_REACHED:
      #  	goForward()
		#if():
         #           FollowWall()

    #global STOP_MOVING


    farLeftDetecting = False
    frontLeftDetecting = False
    midDetecting = False
    frontRightDetecting = False
    farRightDetecting = False

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
        if(x<=y):
            rightDetecting = True

    for (x,y) in farRightReadings:
        if(x<=y):
            farRightDetecting = True

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
    global COUNTER
    global STOP_MOVING
    global START_POSITION
    odomPose = data.pose.pose.position
    if(odomPose.x != 0 and odomPose.y != 0 and BEGUN_EXPLORATION == False and (odomPose.x**2+odomPose.y**2)**0.5>2 ):
        print("I have begun my exploration")
        BEGUN_EXPLORATION = True
        START_POSITION = odomPose
    elif(BEGUN_EXPLORATION ==  True and COUNTER >= 50):
        xBoundary = np.absolute(odomPose.x - START_POSITION.x)
        yBoundary = np.absolute(odomPose.y - START_POSITION.y)

        if(xBoundary <= 0.5 and yBoundary <= 0.5):
            print("I've reached my start position")
            STOP_MOVING = True

    COUNTER+=1



def talker():
    rospy.init_node('Mover', anonymous=True)
#Odometry
    #rospy.Subscriber('odom',Odometry, run)
    rospy.Subscriber('laser_reading',Float32MultiArray, run)
  #  rospy.Subscriber('odom',Odometry, determineIfComplete)
    # rate = rospy.Rate(10) # 10hz

    rospy.spin()
        # rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
'''