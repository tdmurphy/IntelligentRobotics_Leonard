import rospy
from std_msgs.msg import String,Float32MultiArray
import numpy as np
import sys
from face_recogniser import FacialRecogniser

found_person = rospy.Publisher('found_person',String,queue_size=100)
fg= FacialRecogniser()
backgroundPeopletoAdd=[]
currentTarget=None
okayToContinue=False

def destroyScreen():
	global fg
	if(fg.video_capture!=None):
		print("Closing previous screen")		
	    	fg.close_Screen()

def handleScreen(current_target,backgroundPeople):
	global fg
	global backgroundPeopletoAdd
	global currentTarget
	print("Facial Recogniser given new instructions to find",current_target,"and",backgroundPeople)
	destroyScreen()
	for bp in backgroundPeopletoAdd:
		fg.backgroundPeople.append(bp)
	backgroundPeopletoAdd=[]
	fg.setCurrentTarget(current_target)
	target=fg.new_Screen()
	print("Found", target, "from people to find. Was looking for", fg.target, "and", fg.backgroundPeople)
	return target

def backgroundRecognise(data):
    global fg
    global backgroundPeopletoAdd
    global currentTarget
    destroyScreen()
    person=data.data.split("|")[0]
    new_target=data.data.split("|")[1]
    if ((currentTarget!=None) and (currentTarget!=person)):
	if (currentTarget not in backgroundPeopletoAdd):
		backgroundPeopletoAdd.append(currentTarget)
    #currentTarget=person
    print("BACKGROUNDRECOGNISE: Been told that recognising",data.data,"is a backgroundtask, Current target is",currentTarget)
    if (person not in backgroundPeopletoAdd):
    	backgroundPeopletoAdd.append(person)
    #handleScreen(currentTarget,backgroundPeopletoAdd)  
    #target=None
    #if(fg.video_capture!=None):
	#print("closing from node")
    	#fg.close_Screen()
	#fg.setBackgroundTarget(person,new_target)
	#print("opening from node, background")
	#fg.new_Screen()
    #fg.setBackgroundTarget(person,new_target)       
    #print("Setting finding",person," to background job ",fg.target)
    


def recognise(data):    
    global fg
    global backgroundPeopletoAdd
    global currentTarget

    destroyScreen()
    person=data.data
    #target=None
    print("RECOGNISE: Scheduler told me to find",person)    

    if ((currentTarget!=None) and (currentTarget!=person)):
	if (currentTarget not in backgroundPeopletoAdd):
		backgroundPeopletoAdd.append(currentTarget)
    currentTarget=person

    if person in backgroundPeopletoAdd:	
	backgroundPeopletoAdd.remove(person)
	print("Finding",person," was a background task. Promoting to current. BG Tasks are atm",backgroundPeopletoAdd)

    #for bp in backgroundPeopletoAdd:
	#fg.backgroundPeople.append(bp)

    #fg.setCurrentTarget(person)   
    #print("1")     
 	
    while((currentTarget != None)or(len(backgroundPeopletoAdd)>0)): 
	found= handleScreen(currentTarget,backgroundPeopletoAdd) 
	#print("2, opening from node, current")
    	#target=fg.new_Screen()
	#print("new screen returns",target)
	#print("3")
    	if(found==person):
    		print("Oh nice, I found the current Target.",found)
		#fg.removeTarget(target)			
		#print("Removed",target,"from people to find",fg.target,fg.backgroundPeople)
		#pub_message = String()
    		#pub_message.data = target
    		#found_person.publish(pub_message) 	
    	else:   #not always sees a background target so don't publish
		print("Oh, so I found a background target?",found)
	pub_message = String()
    	pub_message.data = found
    	found_person.publish(pub_message)
        while(not okayToContinue):
		pass
	print("Been given permission to continue looking")
		#fg.removeTarget(target)	
		#print("Removed",target,"from people to find",fg.target,fg.backgroundPeople)			
		#target=None  

def CarryOn(data):
	global okayToContinue
	print("Okay, a task has been completed. Can carry on searching.")
	okayToContinue=True 

def stopSearch(data):  
    global backgroundPeopletoAdd 
    global currentTarget   
    global fg
    if data.data in backgroundPeopletoAdd:
	backgroundPeopletoAdd.remove(data.data)
        fg.removeTarget(data.data)
    if(currentTarget==data.data):	
        currentTarget=None
    handleScreen(currentTarget,backgroundPeopletoAdd)

def listener():
    print("Listening")    
    rospy.init_node('face_recognition', anonymous=True)
    rospy.Subscriber("person_to_find", String, recognise)
    rospy.Subscriber("background_person",String,backgroundRecognise)
    rospy.Subscriber("person_to_remove", String, stopSearch)
    rospy.Subscriber("delivered", String, CarryOn)

    rospy.spin()

if __name__ == '__main__':
    listener()

