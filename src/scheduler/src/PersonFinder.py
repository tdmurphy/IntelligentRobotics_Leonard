import sys 
import rospy
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
import webcolors
from PIL import Image
import numpy as np
import random
from numpy import random,argsort,sqrt
from pylab import plot,show
import array as arr
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
from matplotlib._png import read_png
from matplotlib.cbook import get_sample_data
from scipy.stats import multivariate_normal
from std_msgs.msg import String,Float32MultiArray
from geometry_msgs.msg import PoseStamped
from random import randint, seed

pf = None

class PersonFinder:
	distributions={}
	current_pos=[0,0]
	def __init__(self):
		self.picture = Image.open("/data/private/robot/catkin_ws/src/route_navigation/clean_map_updated.png")
		
		self.width, self.height = self.picture.size
		self.X = np.arange(0, self.width, 1)
		self.Y = np.arange(0, self.height, 1)
		self.X, self.Y = np.meshgrid(self.X, self.Y)		
		f= open("KnownPeopleLocations.txt","r+")
		fLines=f.readlines()
		for line in fLines:
			personName= line.split(':')[0]    
			list_of_cords=line.split(':')[1].split("|")
			for personCord in list_of_cords:
				personCord= np.fromstring(personCord, sep=' ')
				print("Updating for",personName,personCord)
				self.updateDist(personName, personCord,False)
		f.close()
		for key in PersonFinder.distributions:
			print(key,PersonFinder.distributions[key])

	def getGaussian(self,cord):	
		mu=[cord[0],cord[1]]
		covariance=[10000,10000]
		XY=np.column_stack([self.Y.flat,self.X.flat])
		G = pow(10,5)*multivariate_normal.pdf(XY,mean=mu,cov=covariance)
		G=G.reshape(self.X.shape)
		for x in range (self.X.shape[0]):
			for y in range (self.X.shape[1]):
				current_color = self.picture.getpixel( (y,x) )
				if current_color == 0 :
					G[x][y] = 0 
				else:
					if (G[x][y] != 0):
						#print("Kept value",G[x][y])
						pass
		return G

	def getDist(self,cordList):
		G = np.zeros((len(self.X),len(self.X[0])))
		i=len(cordList)-1
		for cord in cordList:
			print("Factor of",pow(0.9,i),"for",cord)
			G+=self.getGaussian(cord)*pow(0.9,i)
			i-=1
		return G

	def updateDist(self,person, cord,new='True'):
		f= open("KnownPeopleLocations.txt","a+")
		fLines=f.readlines()
		if(new):
			for index in range (0,len(fLines)):
				personName= fLines[index].split(':')[0]    
				if personName==person:
					cords=fLines[index].split(':')[1]+"|"+str(cord[0])+" "+str(cord[1])
					fLines[index]=personName+":"+cords+"\n"

		if person in PersonFinder.distributions:
			PersonFinder.distributions[person]=np.append(PersonFinder.distributions[person],[cord],axis=0)
		else:		
			PersonFinder.distributions[person]=[cord]
			if new:
				print("Writing to KnownPeopleLocations",person+":"+str(cord[0])+" "+str(cord[1])+"\n")
				f.write(person+":"+str(cord[0])+" "+str(cord[1])+"\n")
		f.close()
		#print("In update dist",PersonFinder.distributions[person])

	def getDistribution(self,person):	
		print("Looking for",person, "and I know",PersonFinder.distributions.keys())
		if person in PersonFinder.distributions:
			print(len(PersonFinder.distributions[person]))
			return self.getDist(PersonFinder.distributions[person])
		else:
			print("Have not seen this person before")
			return np.zeros((len(self.X),len(self.X[0])))

	def getZValues(self,person):
		Z = np.zeros((len(self.X),len(self.X[0])))
		for x in range (self.X.shape[0]):
			for y in range (self.X.shape[1]):
				current_color = self.picture.getpixel( (y,x) )
				#print(current_color)
				if current_color == 254 :
					Z[x][y] = 1
		Z= Z+self.getDistribution(person)
		return Z

	def plotGraph(self,person):
		fig = plt.figure()
		ax = fig.gca(projection='3d')
		Z = self.getZValues(person)
		surf = ax.plot_surface(self.X, self.Y, Z, rstride=1, cstride=1, cmap=cm.Greys,
				       linewidth=0, antialiased=True)
		#ax.set_zlim(0, 10)
		ax.set_xlabel('x')
		ax.set_ylabel('y')

		plt.show()

	def getRandomPopularLoc(self):
		seed(1)
		locationList=[]
		f= open("knownLocations.txt","r+")
		fLines=f.readlines()
		for line in fLines:
		    placeName= line.split(':')[0]    
		    placeCord= np.fromstring(line.split(':')[1], sep=' ')
		    if(placeName not in locationList):
		        locationList.append(placeCord)
		f.close()
		randNum=randint(0,len(locationList)-1)
		return locationList[randNum][0],locationList[randNum][1]

	def getMostLikelyCord(self,person):
		Z = self.getZValues(person)
		maxVal,maxValX,maxValY=0,-1,-1
		for x in range (self.X.shape[0]):
			for y in range (self.X.shape[1]):
				if Z[x][y]>maxVal:
					maxVal=Z[x][y]
					maxValX=x
					maxValY=y
		if(person not in PersonFinder.distributions):
			print("Trying somewhere popular")
			maxValX,maxValY=self.getRandomPopularLoc()
		print(person,"is most likely to be at [",maxValX,",",maxValY,"]")
		print(maxValX,maxValY)
		#self.plotGraph(person)
		return[maxValX,maxValY]

def setCurrentPosition(data):
	estimatedpose = data.data.pose.position
	PersonFinder.current_pos=[estimatedpose.x,estimatedpose.y]

def seenSomeone(data):
	person=data.data.split('|')[2]
	print("Saw",person,"at",PersonFinder.current_pos)
	pf.updateDist(person,PersonFinder.current_pos)
   
def listener():
    global pf
    print("Listening")
    pf=PersonFinder()
    rospy.init_node('personFinder', anonymous=True)
    rospy.Subscriber("deliver", String, seenSomeone)
    rospy.Subscriber("estimatedpose", PoseStamped, setCurrentPosition)
    rospy.spin()

if __name__ == '__main__':    
    listener()


