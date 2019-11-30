import rospy
from std_msgs.msg import String,Float32MultiArray
from nav_msgs.msg import Odometry
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
current_pos=[0,0]
weight_seenbackgroundTarget=150

def setCurrentPosition(data):
    odomPose = data.data.pose.pose.position
    current_pos=[odomPose.x,odomPose.y]

def createTask(data):
    parts=data.data.split("|")
    #print(parts)
    #taskType, sender, recipient, payLoad, location, modifier
    task=Task(parts[0],parts[1],parts[2],parts[3],parts[4],int(parts[5]),False,data.data)
    task.printTask()
    return task

#publish from tom's work when task is done to remove it


def schedule(data):
    print("Scheduling")
    new_task=createTask(data)
    scheduler.updatePos(current_pos)
    scheduler.newTask(new_task)
    pub_message_backgroundTarget=String()    
      
    #if recipient same as target, don't set to background?
    print("Background Target:",new_task.recipient)
    CurrentTask, weight= scheduler.getTask()
    destination=CurrentTask.destinationPos
    print("Current Task:",CurrentTask.taskID,CurrentTask.recipient,destination)
    print(" ")

    #rospy.loginfo("------------------------------------------------------------")
    #rospy.loginfo(destination)
    #rospy.loginfo("------------------------------------------------------------")

    pub_message = Float32MultiArray()
    pub_message.data = destination
    destination_pose.publish(pub_message) 
    print("Current Target:",scheduler.getTarget())
    pub_message_target=String()
    pub_message_target.data=scheduler.getTarget()     
    pub_message_backgroundTarget.data=new_task.recipient+"|"+scheduler.getTarget()
    target_background.publish(pub_message_backgroundTarget)
    target_current.publish(pub_message_target) 

def recalculate(data):
    if (len(scheduler.taskList)==0):
	    print("No more tasks")
            return
    print("Recalculating schedule")
    scheduler.updatePos(current_pos)
    person=data.data
    message=''
    for task in list(scheduler.taskWeights.keys()):
	if (person==task.recipient):
    	     scheduler.adjustWeight(task, weight_seenbackgroundTarget)
	else:
	     scheduler.adjustWeight(task, 0)
    print("Target is now",scheduler.getTarget(), scheduler.getTask())
    activateLeonard(scheduler.getTarget())

def activateLeonard(person):
    print("Creating return message")
    message=''
    for task in list(scheduler.taskWeights.keys()):
	if (person==task.recipient):
		print(task.taskID," is for",task.recipient)
		message=message+task.original+"#"
		scheduler.removeTask(task)
		print("No of tasks left",len(scheduler.taskList))
    pub_message_target=String()
    print("Message:",message)
    pub_message_target.data=message
    talker.publish(pub_message_target)	
    

def listener():
    print("Listening")
    rospy.init_node('scheduler', anonymous=True)
    rospy.Subscriber("new_task", String, schedule)
    rospy.Subscriber("found_person", String, recalculate)
    rospy.Subscriber("odom", Odometry, setCurrentPosition)

    rospy.spin()

if __name__ == '__main__':
    listener()

