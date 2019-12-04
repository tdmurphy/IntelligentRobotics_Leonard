import rospy
from std_msgs.msg import String,Float32MultiArray
import numpy as np
import sys
#import nbimporter
#if('..' not in sys.path):
#    sys.path.insert(0,'..')

new_task = rospy.Publisher('new_task', String, queue_size=10)
done_task = rospy.Publisher('delivered', String, queue_size=10)

def tester(tasks,published):    
    #rate = rospy.Rate(10) # 10hz
    #while not rospy.is_shutdown():
    if not published:
        for t in tasks:
            taskString = t
            rospy.loginfo(taskString)
            new_task.publish(taskString)
        published=True
	
        #rate.sleep()

def fakeDeliver(data):
    print("Found",data.data.split('#')[0].split('|')[2],". Delivering the tasks to them.") 
    done_msg=String()
    #print("2")
    done_msg.data=data.data.split('#')[0].split('|')[2]
    #print("3")
    done_task.publish(done_msg)
    #print("4")

def listener():
    print("Listening")       
    rospy.Subscriber("deliver", String, fakeDeliver)
    rospy.spin()
 
if __name__ == '__main__':
     try:
        rospy.init_node('tester', anonymous=True)
	#taskType, sender, recipient, payLoad, location, modifier
	t1='message|Tom|Esha|hi||0'
	t2='message|Esha|Alexis|hello, I hate robotics||1' 
	tasks=[t1,t2]
	published=False
        tester(tasks,published)
	listener()
     except rospy.ROSInterruptException:
        pass


