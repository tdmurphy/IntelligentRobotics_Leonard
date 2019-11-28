import sys
from Task import Task
import numpy as np

class Locator():
    def __init__(self):
        self.locationList={}
        f= open("knownLocations.txt","r+")
        fLines=f.readlines()
        for line in fLines:
            placeName= line.split(':')[0]    
            placeCord= np.fromstring(line.split(':')[1], sep=' ')
            if(placeName not in self.locationList):
                self.locationList[placeName]=placeCord
        f.close()
        
    def setLocation(self,key,value):
        self.locationList[key]=value
        
    def getLocation(self,place):
        if place in self.locationList:
            return self.locationList[place]
        return [1,1]

    def TargetLastSeen(self,person):
	#timeDiff=
	#disDiff=
	#return timeDiff,disDiff
	pass
