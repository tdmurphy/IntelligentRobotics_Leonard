import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
import numpy as np
import math
from scipy import stats

pub = rospy.Publisher('cmd_vel', Twist, queue_size=100)
base_data = Twist()

#constants 
IDEAL_DISTANCE = 0.5
VELOCITY = 0.2
GRANULARITY = 9
MAX_RANGE = 2.5
DETECTING_RANGE = 1
TURN_INCREMENT = 0.3

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
weights = pdf[:length] + [0] + [x*-1 for x in pdf[length+1:]]

def findWall():
    base_data = Twist()
    base_data.linear.x = VELOCITY
    base_data.angular.z = (TURN_INCREMENT * -1)
    return base_data

def hardLeft():
    base_data = Twist()
    base_data.angular.z = TURN_INCREMENT * 1.2
    return base_data

def defineMovement(data):
    #hug the wall (tranvels to the right)
    left_reading = data.data[0]
    right_reading = data.data[GRANULARITY]
    mid_reading = data.data[int(GRANULARITY/2)]

    #front and right out of range = travelling away from wall (move back to wall)
    if(mid_reading >= MAX_RANGE and right_reading >= MAX_RANGE):
        base_data = findWall()
    #front detecting, right at max range = about to hit the wall (turn left to get parallel to the wall)
    elif(mid_reading <= DETECTING_RANGE and right_reading >= MAX_RANGE):
        base_data= hardLeft()
    #right and front detecting = corner (turn left)
    elif(mid_reading <= DETECTING_RANGE and right_reading <= DETECTING_RANGE):
        base_data = hardLeft()

    #right detecting, front at max range = following the wall (good)
    else:
        base_data.linear.x = VELOCITY
    pub.publish( base_data)
    

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
