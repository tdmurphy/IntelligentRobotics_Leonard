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
target=rospy.Publisher('person_to_find',String,queue_size=100)
scheduler= scheduler()

def createTask(data):
    parts=data.data.split("|")
    #print(parts)
    #taskType, payload, recipient, location, sender, urgent
    task=Task(parts[4],parts[2],parts[0],parts[1],parts[3],int(parts[5]),False)
    task.printTask()
    return task

def schedule(data):
    print("Scheduling")
    new_task=createTask(data)
    scheduler.newTask(new_task)
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
    target.publish(pub_message_target)  
    

def listener():
    print("Listening")
    rospy.init_node('scheduler', anonymous=True)
    rospy.Subscriber("task", String, schedule)

    rospy.spin()

if __name__ == '__main__':
    listener()

