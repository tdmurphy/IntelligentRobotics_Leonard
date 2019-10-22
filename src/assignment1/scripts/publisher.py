#!usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
import numpy as np
import math
from scipy import stats

pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
base_data = Twist()
granularity=9

def initPdf():
    samples = np.random.normal(size=1000)

    # Compute a histogram of the sample
    bins = np.linspace(-0.5, 0.5, granularity+1)
    histogram, bins = np.histogram(samples, bins=bins, normed=True)
    bin_centers = 2*(bins[1:] + bins[:-1])

    # Compute the PDF on the bin centers from scipy distribution object
    pdf = stats.norm.pdf(bin_centers)

    shift=1-max(pdf)
    pdf = [x+shift for x in pdf]
    return pdf

pdf = initPdf()

def defineMovement(data):

    #if((data.data[2] <= 1.0) or (((data.data[3] or data.data[1]) <= 0.7) or ( (data.data[0] or data.data[4]) <= 0.5))):
    obstacle = False
    for (x, y) in zip(data.data, pdf):
        if (x<=y):
            obstacle=True

    if(obstacle):
        print("Going to crash")
        VELOCITY = 0
        if(base_data.angular.z == 0):
            findDirection(data.data, pdf)
    else:
        base_data.angular.z = 0
        VELOCITY = 0.2
    base_data.linear.x = VELOCITY
    pub.publish( base_data)
    print(VELOCITY)

def findDirection(data, pdf):
    
    length = int(len(pdf)/2)
    weights = pdf[:length] + [0] + [x*-1 for x in pdf[length+1:]]

    direction = np.dot(weights, data)
    print("direction = " , direction)
    base_data.angular.z = direction


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
