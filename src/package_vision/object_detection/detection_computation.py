import rospy
from std_msgs.msg import Bool, String
from datetime import datetime 


num_objects = 0 

most_likely_objects = ['bottle','cup','wine glass','laptop','mouse']
weight_increase = 1.2
object_dict = {}

change_publisher = rospy.publisher('change_detected', Bool, queue_size=100)

def detectChange(detecting_object):
    #global num_objects 
    global detecting 
    change_publisher.publish(detecting == detecting_object)
    #seperate the string into objects using deliminator "|"
    """seperated = objects.split("|")
    if not(len(seperated) == num_objects):
        change_publisher.publish(True)
    else:
        change_publisher.publish(False)
    num_objects = len(seperated)
    """


def probabalistic_calculations(objects):
    #a function to give higher weighting to objects that are likely to be in the frame 
    seperated = objects.split("|")
    for ob in seperated:
        splt = ob.split("-")
        name = splt[0]
        prob = splt[1]
        if(name in most_likely_objects):
            prob * weight_increase
        object_dict[name] = prob
    print(object_dict)

    

def talker():
	rospy.init_node('DetectorComputer', anonymous=True)
	rospy.Subscriber('decting_object', Bool, detectChange)
    rospy.Subscriber('objects_detected', String, probabalistic_calculations)
	rospy.spin()

if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterrupException:
		pass 

