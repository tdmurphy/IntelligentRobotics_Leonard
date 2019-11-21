import rospy
from std_msgs.msg import String,Float32MultiArray
import numpy as np
import sys
#import nbimporter
#if('..' not in sys.path):
#    sys.path.insert(0,'..')
from Task import Task
from Scheduler import scheduler

destination_pose = rospy.Publisher('destination_pose',Float32MultiArray,queue_size=100)
target_current=rospy.Publisher('person_to_find',String,queue_size=100)
target_background=rospy.Publisher('background_person',String,queue_size=100)
talker=rospy.Publisher('deliver',String,queue_size=100)
scheduler= scheduler()

def createTask(data):
    parts=data.data.split("|")
    #print(parts)
    #taskType, payload, recipient, location, sender, urgent
    task=Task(parts[4],parts[2],parts[0],parts[1],parts[3],int(parts[5]),False,data.data)
    task.printTask()
    return task

def schedule(data):
    print("Scheduling")
    new_task=createTask(data)
    scheduler.newTask(new_task)
    pub_message_backgroundTarget=String()
    pub_message_backgroundTarget.data=new_task.recipient
    target_background.publish(pub_message_backgroundTarget)  
    print("Background Target:",new_task.recipient)
    destination, weight= scheduler.getTask()
    print("Current Task:",scheduler.getTask())

    #rospy.loginfo("------------------------------------------------------------")
    #rospy.loginfo(destination)
    #rospy.loginfo("------------------------------------------------------------")

    pub_message = Float32MultiArray()
    pub_message.data = destination
    destination_pose.publish(pub_message) 
    print("Current Target:",scheduler.getTarget())
    pub_message_target=String()
    pub_message_target.data=scheduler.getTarget()
    target_current.publish(pub_message_target)  

def activateLeonard(data):
    print("Creating return message")
    person=data.data
    message=''
    for task in list(scheduler.taskWeights.keys()):
	if (person==task.recipient):
		print(task.taskID," is for",task.recipient)
		message=message+task.original+"#"
		scheduler.removeTask(task)
    pub_message_target=String()
    print("Message:",message)
    pub_message_target.data=message
    talker.publish(pub_message_target)	
    

def listener():
    print("Listening")
    rospy.init_node('scheduler', anonymous=True)
    rospy.Subscriber("task", String, schedule)
    rospy.Subscriber("found_person", String, activateLeonard)

    rospy.spin()

if __name__ == '__main__':
    listener()

