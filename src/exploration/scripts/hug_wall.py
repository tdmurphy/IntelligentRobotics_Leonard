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
GRANULARITY = 5
MAX_RANGE = 3
DETECTING_RANGE = 1.75
TURN_INCREMENT = 0.3

def initPdf():
    samples = np.random.normal(size=1000)
    # Compute a histogram of the sample
    bins = np.linspace(-0.5, 0.5, GRANULARITY+1)
    histogram, bins = np.histogram(samples, bins=bins, normed=True)
    bin_centers = 2*(bins[1:] + bins[:-1])
    # Compute the PDF on the bin centers from scipy distribution object
    pdf = stats.norm.pdf(bin_centers)
    shift=1-max(pdf)
    pdf = [x+shift for x in pdf]
    return pdf

pdf = initPdf()
weights = pdf[:int(len(pdf)/2)] + [0] + [x*-1 for x in pdf[(int(len(pdf)/2))+1:]]
base_data = Twist()
wasFollowing = False
timesTurned = 0

def findWall(data):
  ##  global timesTurned
  ##  global wasFollowing
  ##  if(wasFollowing and timesTurned < 10):
  ##      print("continue following to right")
  ##      base_data.linear.x = VELOCITY
  ##      base_data.angular.z = -5
  ##      timesTurned+=1
  ##  else:
  ##  timesTurned = 0
    wasFollowing = False
    print("Attempting to find wall")
    base_data.linear.x = VELOCITY
    base_data.angular.z = -3 #np.dot(weights,data)

def hardLeft(data):
    print("hard left")
    base_data.angular.z = 5
    print(base_data.angular.z)

def hardRight(data):
    print("hard right")
    base_data.angular.z = -5
    print(base_data.angular.z)

def defineMovement(data):
    #hug the wall (tranvels to the right)
    thresholds = np.full(len(data.data), 1.5)
    zipped = zip(data.data, thresholds)
    increment = int(len(zipped)/5)
    leftReadings = zipped[0:increment]
    midReadings = zipped[increment*2:increment*3]
    rightReadings = zipped[increment*4:]
    frontLeftReadings = zipped[increment:increment*2]
    frontRightReadings = zipped[increment*3:increment*4]
    
    leftDetecting = False
    midDetecting = False
    rightDetecting = False
    farRightDetecting = False

    for (x,y) in frontLeftReadings:
        if(x<=y):
            leftDetecting = True

    for (x,y) in midReadings:
        if(x<=y):
            midDetecting = True

    for (x,y) in frontRightReadings:
        if(x<=y):
            rightDetecting = True
    for (x,y) in rightReadings:
        if(x<=y):
            farRightDetecting = True

    #front and right out of range = travelling away from wall (move back to wall)
    if(not(midDetecting) and not(rightDetecting) and (not farRightDetecting)):
        findWall(data.data)
    #front detecting, right at max range = about to hit the wall (turn left to get parallel to the wall)
    ##elif(midDetecting and not(rightDetecting)):
    ##    base_data.linear.x=0
    ##    if(base_data.angular.z == 0):
    ##        hardLeft(data.data)
    #right and front detecting = corner (turn left)
    elif(midDetecting):
        base_data.linear.x=0
        if(base_data.angular.z == 0):
            hardLeft(data.data)

    #right detecting, front at max range = following the wall (good)
    else:
        print("Im following a wall")
        global wasFollowing
        global timesTurned
        wasFollowing  = True
        timesTurned = 0
        print(rightReadings[0][0])
        base_data.linear.x = VELOCITY/2
        if (rightReadings[0][0] <= 1 and base_data.angular.z==0):
            base_data.angular.z = 0.5
            print("correcting course left")
        ##elif (rightReadings[0][0] >= 0.75 and rightReadings[0][0] <=0.8 and base_data.angular.z==0):
         ###   base_data.angular.z = -0.5
         ##   print("correcting course right")
        else:
            base_data.linear.x = VELOCITY
            base_data.angular.z = 0
    pub.publish(base_data)
    

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
