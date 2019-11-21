import rospy
from std_msgs.msg import String,Float32MultiArray
import numpy as np
import sys
#import nbimporter
#if('..' not in sys.path):
#    sys.path.insert(0,'..')


def tester(tasks,published):
    pub = rospy.Publisher('task', String, queue_size=10)
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
	t1= 'message|yo :3|Esha|Benet|Felix|0'
	t2='message|<3|Xinpeng|London|Esha|0' 
	t3='message|hey :)|Alexis|London|Esha|0'
	t4='message|:D|Alexis|Benet|Tom|0'
	tasks=[t1,t2,t3,t4]
	published=False
        tester(tasks,published)
     except rospy.ROSInterruptException:
        pass


