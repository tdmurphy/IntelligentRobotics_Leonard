import rospy
from std_msgs.msg import String,Float32MultiArray
import numpy as np
import sys
from face_recogniser import FacialRecogniser

found_person = rospy.Publisher('found_person',String,queue_size=100)
fg= FacialRecogniser()

def backgroundRecognise(data):
    person=data.data
    target=None
    print("Setting finding",person," to background job")
    fg.setBackgroundTarget(person)
 


def recognise(data):
    person=data.data
    target=None
    print("Trying to find",person)
    if person in fg.backgroundPeople:
	print("Finding",person," was a background task. Promoting to current.")
	fg.backgroundPeople.remove(person)

    fg.setCurrentTarget(person)   
    print("1")    	
    while(target==None): 
	print("2")
    	target=fg.new_Screen()
	print("3")
    	if(target==person):
    		print("Found Current Target:",target,"!!")		
    	else:
		print("Found Background Target:",target,"!!")
		pub_message = String()
    		pub_message.data = target
    		found_person.publish(pub_message)
		target=None
	fg.removeTarget(person)
   

    pub_message = String()
    pub_message.data = target
    found_person.publish(pub_message)  

def stopSearch(data):    
    face_recogniser.removeTarget(data.data)    

def listener():
    print("Listening")    
    rospy.init_node('face_recognition', anonymous=True)
    rospy.Subscriber("person_to_find", String, recognise)
    rospy.Subscriber("background_person",String,backgroundRecognise)
    rospy.Subscriber("person_to_remove", String, stopSearch)

    rospy.spin()

if __name__ == '__main__':
    listener()

