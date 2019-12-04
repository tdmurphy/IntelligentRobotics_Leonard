#!/usr/bin/env python

import rospy
from std_msgs.msg import String, Float32MultiArray
from geometry_msgs.msg import Twist,Point,PoseWithCovariance,Pose

from nav_msgs.msg import Odometry

rospy.init_node('fake_scheduler')  

destination_publisher = rospy.Publisher('/destination_pose',Float32MultiArray,queue_size=100) # Float32MultiArray

rate = rospy.Rate(1) #3htz
while not rospy.is_shutdown():
	x = Float32MultiArray()
	x.data = [480, 212]
	destination_publisher.publish(x)
	rate.sleep()
