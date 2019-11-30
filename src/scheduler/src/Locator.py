import sys
from Task import Task
import numpy as np
from PersonFinder import PersonFinder

class Locator():
    def __init__(self):
        self.locationList={}
        f= open("knownLocations.txt","r+")
        fLines=f.readlines()
        for line in fLines:
	    #print(len(line.split(':')),line)
            placeName= line.split(':')[0]    
            placeCord= np.fromstring(line.split(':')[1], sep=' ')
	    #print(placeCord)
            if(placeName not in self.locationList):
                self.locationList[placeName]=placeCord
        f.close()
	self.pf=PersonFinder()

    def setLocation(self,key,value):
        self.locationList[key]=value
        
    def getLocation(self,place,person):
        if place in self.locationList:
	    print("Looking for a room")
            return self.locationList[place]
        else:
	    print("Looking for a person's location")
	    return self.estimatePersonLocation(person)
	return [0,0]


    def estimatePersonLocation(self, person):
	print("Estimating",person,"'s location",self.pf.distributions.keys())
	return self.pf.getMostLikelyCord(person)

