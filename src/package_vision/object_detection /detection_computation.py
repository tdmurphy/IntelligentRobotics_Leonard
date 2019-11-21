import rospy

num_objects = 0 

change_publisher = rospy.publisher('change_detected', Boolean, queue_size=100)

def detectChange(objects):
    #seperate the string into objects using deliminator "|"
    seperated = objects.split("|")
    if not(len(seperated) == num_objects):
        change_publisher.publish(True)
    else:
        change_publisher.publish(False)
    num_objects = len(seperated)

 

def talker():
	rospy.init_node('DetectorComputer', anonymous=True)
	rospy.Subscriber('objects_detected', String, detectChange)
	rospy.spin()

if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterrupException:
		pass 

#heyy