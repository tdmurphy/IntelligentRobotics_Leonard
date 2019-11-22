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


    def getWeight(self,task):
        weight= self.getDistanceWeight(task) + self.getModifierWeight(task) #+ self.TargetLastSeen(task)
        return weight
                
    def reSchedule(self):
        if (len(self.taskList)==0):
            return
        self.currentTask= max(self.taskWeights, key=self.taskWeights.get)        
        
    def getTask(self):
        return self.currentTask.taskID, self.taskWeights[self.currentTask]

    def getTarget(self):
	return self.currentTask.recipient
    
    def getCurrentPosition(self): #replace with a subscription to odom
        return [0,0]
    
    def getGoalPos(self, goal):
        return self.loc.getLocation(goal)
    
    def getDistance(self, pos,goalPos):  #euclidean atm
        return ((pos[0]-goalPos[0])**2+(pos[1]-goalPos[1])**2)**0.5
    
    def getDistanceWeight(self,task):            
        pos=self.getCurrentPosition()
        goalPos=self.getGoalPos(task.location)
        distance=self.getDistance(pos,goalPos)
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

    def TargetLastSeen(self,task):
	#return self.loc.lastSeen(task.recipient)
        pass
