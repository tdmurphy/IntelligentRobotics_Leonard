#!usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
import numpy as np
import math

pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
base_data = Twist()

def defineMovement(data):
    if((data.data[2] <= 1.0) or (((data.data[3] or data.data[1]) <= 0.7) or ( (data.data[0] or data.data[4]) <= 0.5))):
        print("Going to crash")
        VELOCITY = 0
        if(base_data.angular.z == 0):
            findDirection(data.data)
    else:
        base_data.angular.z = 0
        VELOCITY = 0.2
    base_data.linear.x = VELOCITY
    pub.publish( base_data)
    print(VELOCITY)

def findDirection(data):
   direction = (((data[0]*0.5+data[1])-(data[3] + data[4]*0.5))/6)#(np.abs(data[0]-data[4] + 0.1 ))) 
   print("direction = " , direction)
   base_data.angular.z = 1/direction


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
