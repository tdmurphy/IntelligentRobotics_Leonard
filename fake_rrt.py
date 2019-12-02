#!/usr/bin/env python

import rospy
from std_msgs.msg import String, Float32MultiArray
from geometry_msgs.msg import Twist,Point,PoseWithCovariance,Pose

from nav_msgs.msg import Odometry

rospy.init_node('fake_RRT')   
	
destination_publisher = rospy.Publisher('/route_nodes',Float32MultiArray,queue_size=100) # Float32MultiArray

rate = rospy.Rate(1) #3htz
while not rospy.is_shutdown():
	x = Float32MultiArray()
	x.data = [20,45, 20,280, 30,90]
	destination_publisher.publish(x)
	rate.sleep()




	# def fake_scheduler(self):
	# 	pub_message = Float32MultiArray()
	# 	pub_message.data = [50, 120] #rangeMeans
	# 	destination_publisher.publish(pub_message)



	# 	self.fake_scheduler()
	# def scheduler_publisher():
	# 	rospy.init_node()
	# 	destination_publisher = rospy.Publisher('destination_pose',Float32MultiArray,queue_size=100)



