#laser array from start of list to end, corrosponds to 
#right to left (0 to 180 degs) in a semi-circle of 
#readings from the lasers on robot. 
#
#Right = 0 degrees 
#Left = 180 degrees 
#Straight = 90 degrees (note: in rads for LaserScan)
#

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import String,Float32MultiArray
from sensor_msgs.msg import LaserScan
import numpy as np

#laser publisher: rospy.Publisher(topic, datatypePublishToTopic, queuesize)
laserPublisher = rospy.Publisher('laser_reading',Float32MultiArray,queue_size=100)

granularity = 10

#data is a generic inbuilt function that gets the data from ..?
def callback(data):

#There are 500 readings in semi circle laser scan. 
#  0 degs = hard right from forward director of robot.
#  0 degs = 1st element in list array
#  180 degs = hard left from forward director of robot.
#  180 degs = last element in list array

    allLaserReadingValues = np.array(data.ranges)
    print("NumLaserReadings : ", len(allLaserReadingValues))

# allLaserReadingValues array split into 10 sub arrays.
# 500/10 = 50 values(laser readings) per sub array
#(granularity = num of sub arrays)

    granulatedArray = np.array_split(allLaserReadingValues, granularity)
    
    #Average of all values within each sub array of granulated values.
    AV_granulatedArray = []
    for i in range(len(granulatedArray)):

        av = np.average(granulatedArray[i])
        AV_granulatedArray.append(av)

    #flipping as nodes code works on left to right (not the default right to left)
    AV_granulatedArray = np.flip(AV_granulatedArray, 0)

    pub_message = Float32MultiArray()
    pub_message.data =  AV_granulatedArray #rangeMeans

    laserPublisher.publish(pub_message)


def listener():
    rospy.init_node('laser_subscriber', anonymous=True)
    rospy.Subscriber("base_scan", LaserScan, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()

