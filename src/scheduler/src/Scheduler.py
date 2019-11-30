import sys
#import nbimporter
#if('..' not in sys.path):
#    sys.path.insert(0,'..')
from Task import Task
from Locator import Locator
import operator
import numpy as np
import datetime

#Task Scheduler
class scheduler():
    def __init__(self):
        self.taskList=[]
        self.taskWeights={}
        self.currentTask=None
	self.current_pos=[0,0]
        self.loc=Locator()
    
    def newTask(self,task):
        self.taskList.append(task)
        weight=self.getWeight(task)
        self.taskWeights[task]=weight
        self.reSchedule()

    def removeTask(self,task):
	self.taskList.remove(task)
	del self.taskWeights[task]
	if self.currentTask==task:
		self.currentTask=None
	self.reSchedule()

    def adjustWeight(self,task,weight):
	self.taskWeights[task]=self.getWeight(task)+weight
	self.reSchedule()

    def getWeight(self,task):
        weight= self.getDistanceWeight(task) + self.getModifierWeight(task) #+ self.TargetLastSeen(task)
        return weight
                
    def reSchedule(self):
        if (len(self.taskList)==0):
            return
        self.currentTask= max(self.taskWeights, key=self.taskWeights.get) 
        
    def getTask(self):
	if (len(self.taskList)==0):
            return
        return self.currentTask, self.taskWeights[self.currentTask]

    def getTarget(self):
	if (len(self.taskList)==0):
            return
	return self.currentTask.recipient

    def updatePos(self, current_pos):	
	self.current_pos=current_pos
    
    def getCurrentPosition(self): #replace with a subscription to odom
        return self.current_pos
    
    def getGoalPos(self, goal,person):
        return self.loc.getLocation(goal,person)
    
    def getDistance(self, pos,goalPos):  #euclidean atm
        return ((pos[0]-goalPos[0])**2+(pos[1]-goalPos[1])**2)**0.5
    
    def getDistanceWeight(self,task):            
        pos=self.getCurrentPosition()
        goalPos=self.getGoalPos(task.location,task.recipient)
	task.destinationPos=goalPos
        distance=self.getDistance(pos,goalPos)
	print("Going from",pos,"to",goalPos,"for task",task.taskID)
        distanceWeight=1/distance
        return distanceWeight
    
    def getTimeWeight(self,task):            
        currentTime=datetime.datetime.now()
        if(task.time==''):
            return 0
        #goalTime=self.getGoalPos(task.location)
        #difference=self.getDistance(pos,goalPos)
        #timeWeight=1/difference
        #return timeWeight
        pass
    
    def getModifierWeight(self,task):         
        modifierWeight=0
        if task.urgent==1:
            modifierWeight=100
        return modifierWeight

