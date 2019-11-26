import rospy
from std_msgs.msg import Bool, String
from datetime import datetime 


num_objects = 0 

change_publisher = rospy.publisher('change_detected', Bool, queue_size=100)

def detectChange(objects):
    global num_objects 
    #seperate the string into objects using deliminator "|"
    seperated = objects.split("|")
    if not(len(seperated) == num_objects):
        change_publisher.publish(True)
    else:
        change_publisher.publish(False)
    num_objects = len(seperated)



def probabalistic_calculations(objects):
    #a function to give higher weighting to objects that are likely to be in the frame 
    seperated = objects.plit("|")
    

def talker():
	rospy.init_node('DetectorComputer', anonymous=True)
	rospy.Subscriber('objects_detected', String, detectChange)
	rospy.spin()

if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterrupException:
		pass 

