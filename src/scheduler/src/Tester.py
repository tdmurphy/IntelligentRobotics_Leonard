import rospy
from std_msgs.msg import String,Float32MultiArray
import numpy as np
import sys
#import nbimporter
#if('..' not in sys.path):
#    sys.path.insert(0,'..')


def tester(tasks,published):
    pub = rospy.Publisher('new_task', String, queue_size=10)
    rospy.init_node('tester', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        if not published:
            for t in tasks:
                taskString = t
                rospy.loginfo(taskString)
                pub.publish(taskString)
            published=True
	
        rate.sleep()
 
if __name__ == '__main__':
     try:
	#taskType, sender, recipient, payLoad, location, modifier
	t1='message|Tom|Esha|:D||0' 
	tasks=[t1]
	published=False
        tester(tasks,published)
     except rospy.ROSInterruptException:
        pass


