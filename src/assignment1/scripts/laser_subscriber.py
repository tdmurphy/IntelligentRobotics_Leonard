#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import String,Float32MultiArray
from sensor_msgs.msg import LaserScan
import numpy as np

laserPublisher = rospy.Publisher('laser_reading',Float32MultiArray,queue_size=100)
granularity = 19

def callback(data):
    rangeMeans = np.array([])

    for r in np.array_split(np.array(data.ranges), granularity):
        r[np.isnan(r)]=data.range_max
	for rData in r:
		if rData < data.range_min:
			r[np.where(r == rData)]=data.range_max
        rangeMeans = np.concatenate((rangeMeans, np.array([np.average(r)])), axis=None)

    rangeMeans = np.flip(rangeMeans, 0)

    rospy.loginfo("------------------------------------------------------------")
    rospy.loginfo(rangeMeans)
    rospy.loginfo("------------------------------------------------------------")

    pub_message = Float32MultiArray()
    pub_message.data = rangeMeans

    laserPublisher.publish(pub_message)

    
    

def listener():
    rospy.init_node('laser_subscriber', anonymous=True)
    rospy.Subscriber("base_scan", LaserScan, callback)

    rospy.spin()

if __name__ == '__main__':
    listener()

