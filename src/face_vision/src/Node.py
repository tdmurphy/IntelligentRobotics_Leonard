import rospy
from std_msgs.msg import String,Float32MultiArray
import numpy as np
import sys
from face_recogniser import FacialRecogniser

found_person = rospy.Publisher('found_person',String,queue_size=100)
fg= FacialRecogniser()

def recognise(data):
    print("Trying to find",data.data)
    fg.setCurrentTarget(data.data)       
    target=fg.new_Screen()
    print("Found:",target,"!!")

    #rospy.loginfo("------------------------------------------------------------")
    #rospy.loginfo(destination)
    #rospy.loginfo("------------------------------------------------------------")

    pub_message = String()
    pub_message.data = target
    found_person.publish(pub_message)  

def stopSearch(data):    
    face_recogniser.removeTarget(data.data)    

def listener():
    print("Listening")    
    rospy.init_node('face_recognition', anonymous=True)
    rospy.Subscriber("person_to_find", String, recognise)
    rospy.Subscriber("person_to_remove", String, stopSearch)

    rospy.spin()

if __name__ == '__main__':
    listener()

