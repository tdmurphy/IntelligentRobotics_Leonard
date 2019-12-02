#!/usr/bin/env python
import sys 
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
import webcolors
from PIL import Image
import numpy as np
import scipy as scp
import random
from sklearn.neighbors import KDTree
#import sklearn.neighbors
#import KDTree
from numpy import random,argsort,sqrt
from pylab import plot,show
import array as arr
import rospy
from geometry_msgs.msg import Twist,Point,PoseWithCovariance,Pose
from std_msgs.msg import Float32MultiArray, String
from nav_msgs.msg import Odometry

from geometry_msgs.msg import PoseWithCovarianceStamped as Pose

# def knn_search(x, D, K):
#  """ find K nearest neighbours of data among D """
#  ndata = D.shape[1]
#  K = K if K < ndata else ndata
#  # euclidean distances from the other points
#  sqd = sqrt(((D - x[:,:ndata])**2).sum(axis=0))
#  idx = argsort(sqd) # sorting
#  # return the indexes of K nearest neighbours
#  return idx[:K]

#def translate_to():
#f = [34,78, 986, 678, 567576, 567]




	

		
		






class Node:
    prevNode = None
    nextNodes = []
    coords = None

    def __init__(self, prevNode, coords):
        self.prevNode = prevNode
        self.coords = coords

 
def generate_point_g(self, point, point_size):
	#define x and y for grid of points creation (round to nearest int)
		x = point[0]#[0]
		y = point[1]
		print(len(point))
		print("x", x, "y", y)
		x =int(x)
		y =int(y)
		print("x1", x, "y1", y)
		
		point_g = []

		#creates a grid box with point at centre of box
		for i in range(x-point_size, x +point_size):
			for j in range(y-point_size, y+point_size):
				point_g.append([i,j])

		return point_g

def draw_points_g(self,point_set, color, input_image, output_image):
	picture = Image.open(input_image)
	for i in range(len(point_set)):
			
		if(point_set[i] != 0):
			#print("pointif :", i ,"  ", point_set[i])
			picture.putpixel((point_set[i]), (color))
			picture.save(output_image)



def draw_line_between_points(point1, point2):
#To draw a line between two points we need to color in all pixal that ly on the line between the points. 
# you can do this by finding all points that lie on that line for all integer x values. 

#(edge case1: when x values are same)
	#ensure x2 has the largest x value

	if(point1[0] < point2[0]):
		y_1 = point1[1] 
		y_2 = point2[1]
		x_1 = point1[0]
		x_2 = point2[0]

	else:
		y_1 = point1[0] 
		y_2 = point2[0]
		x_1 = point1[1]
		x_2 = point2[1]

	print("x1y1: ",x_1,y_1, " x2y2 ", x_2, y_2 )

	#find y = mx +c
	#solve for m 
	#if((x_2 - x_1) ** add div zero edge case
	m = (y_2 - y_1)/(x_2 - x_1)
	print("m", m)

	# solve for c
	c = y_1 - (m*x_1)
	print("c", c)

	all_pixals_on_line = []

##finds all pixaLS on line between two points and puts to list
##if statemenets handle the edge cases of x2/y2 or x1/y1 being switched around

	if (x_2 < x_1):
		for x in range(x_2, (x_1 + 1)): # +1 because we want last x2 value to be included
			y = (m * x) + c
			y = int(y)
			x = int(x)
			all_pixals_on_line.append([x, y])
	else:
		for x in range(x_1, (x_2 + 1)): # +1 because we want last x2 value to be included
			y = (m * x) + c
			y = int(y)
			x = int(x)
			all_pixals_on_line.append([x, y])

	if (y_2 < y_1):

		for y in range(y_2, (y_1+1)):
			x = (y - c)/m
			print("y",y)
			y = int(y)
			x = int(x)
			print("x ", x)
			all_pixals_on_line.append([x, y])
	else:
		for y in range(y_1, (y_2+1)):
			x = (y - c)/m
			print("y",y)
			y = int(y)
			x = int(x)
			print("x ", x)
			all_pixals_on_line.append([x, y])

	#add yrange
	return all_pixals_on_line



def simplify_image(image_path):
	picture = Image.open(image_path);

	# Get the size of the image
	width, height = picture.size

	#the image from slam is made up of several greyscale rgb values. A more simple
	#black and white image will be more simple when creating an occupancy grid. 
	##RGB with 255 or 254 are white areas in map that are UNoccupied. So we ensure all areas are 254

	new_color = 254
	count = 0
	# Process every pixel
	for x in range (width):
		for y in range (height):
			current_color = picture.getpixel( (x,y) )
			if current_color == 255 :
				picture.putpixel((x,y), (new_color))

	#all areas that are grey are unexplored. We will change this to black, and assume area is occupied
	new_color = 0
	for x in range (width):
   		for y in range (height):
   			current_color = picture.getpixel((x,y))
   			if current_color != 254 : 
   				picture.putpixel((x,y), (new_color))


	#now we rewrite the image to new black and white comprising of only two rgb values
	picture.save("clean_map_simple.png")


def occupancy_grid(image_path):
	# now we create an occupancy grid from therefore image data teh same dimentions as the image size
	# If the area is black it is occupied, where white is unoccupied.
	
	picture = Image.open(image_path)
	
	# Get the size of the image
	width, height = picture.size

	Matrix = [[0 for x in range(height)] for y in range(width)]

	for x in range (width):
   		for y in range (height):
   			current_color = picture.getpixel( (x,y) )
   			print("current color upd ", current_color)
   			if current_color == 254:
   				#print("x,y ", x, "  ", y)
   				Matrix[x][y] = 0
   				#print("unoc ", Matrix[x][y])
   				#print("width,", width," ")
   				#print("height",height, " ")

   			else:
   				#print("x,y ", x, "  ", y)
   				Matrix[x][y] = 1
   				#print("oc ", Matrix[x][y])
   				#print("width,", width," ")
   				#print("height",height, " ")

	return (Matrix)


def generate_rand_node(init_point):

	print("init_point", init_point)
	#generate point on cirumference from origin
	radius = 14
	rand_angle =random.uniform(0, (2*np.pi))
	x = radius* np.cos(rand_angle)
	y = radius* np.sin(rand_angle)

	#translate random coord to initial point as origin
	new_node_point = [init_point[0] + x, init_point[1] + y]
	
	return new_node_point
	#x coordinate = radius x cos(rand(betwee0-360))
	#y coordinate = radius x sin(rand(betwee0-360))


#GUI
class ranfdom(QDialog):
	global Node
	START_POINT = [0,0]
	DEST_POINT = [0,0]
	OCCUPANCY = occupancy_grid('clean_map_updated.png')
	NODES = []
	TREE = {}
	

	def __init__(self):
		super(ranfdom,self).__init__()
		loadUi('ranfdom.ui', self)
		self.setWindowTitle('ranfdom PyQt5 Gui')
		self.label.setPixmap(QPixmap('clean_map_updated.png'))
		self.label.mousePressEvent = self.getPos
		self.pushButton.clicked.connect(self.call_RRT)#self.print_ham)#RRT)
		
	@pyqtSlot()

	def translate_from(self,rrt_points_2d_list):
	#new_list = []
		count = 0
		x = 0
		y = 0
		multilist = []
		for i in range(len(rrt_points_2d_list)):
			if count == 0:
	
				print("1if ",rrt_points_2d_list[i])
				x = rrt_points_2d_list[i]
	
			if count == 1:
			
				print("0if ",rrt_points_2d_list[i])
				y = rrt_points_2d_list[i]
				print("x", x, "y", y)
				x = int(x)
				y=int(y)
				multilist.append([x,y])
				

			if count == 0:
				count = 2

			if count == 1:
				count = 0
			if count == 2:
				count = 1
				
	
		return multilist


	def render(self,data):
		self.label.setPixmap(QPixmap('clean_map_updated.png'))
		print("in")
		print(data.data)
		x = []
		x = self.translate_from(data.data)

		self.label.setPixmap(QPixmap('clean_map_updated.png'))

		print(x)
		#self.draw_points(self.translate_from(data)
		pointset =[]
		for i in range(len(x)):
			points2add = self.generate_point(x[i], 5)
			self.append_points(pointset,points2add)


		self.draw_points(pointset, 50, 'clean_map_simple.png', 'clean_map_updated.png')
		 
		self.label.setPixmap(QPixmap('clean_map_updated.png'))
		self.show()
		
		
	
	def destination_subscriber(self):
		
		
    		rospy.init_node('destination_reciever', anonymous=True)
    		rospy.Subscriber('/destination_pose',Float32MultiArray,destination_recieved) #Float32MultiArray
    		rospy.Subscriber("/amcl_pose", Pose, current_position_recieved)
		rospy.Subscriber("route_nodes", Float32MultiArray, self.render)
    		# rate = rospy.Rate(10) # 10hz
    		rospy.spin()
		self.label.setPixmap(QPixmap('clean_map_updated.png'))

	def append_points(self,point_set, points_to_add):

		
		for i in range(len(points_to_add)):
			point_set.append(points_to_add[i])
			#print("point_set", points_to_add[i])

	def generate_point(self, point, point_size):
		
		#define x and y for grid of points creation (round to nearest int)
		x = point[0]#[0]
		y = point[1]
		#print(len(point))
		#print("x", x, "y", y)
		x =int(x)
		y =int(y)
		#print("x1", x, "y1", y)
		
		point_g = []

		#creates a grid box with point at centre of box
		for i in range(x-point_size, x +point_size):
			for j in range(y-point_size, y+point_size):
				point_g.append([i,j])

		return point_g

	def draw_points(self,point_set, color, input_image, output_image):
		#print("point set ", point_set)
		picture = Image.open(input_image)
		for i in range(len(point_set)):
			
			if(point_set[i] != 0):
				#print("pointif :", i ,"  ", point_set[i])
				picture.putpixel((point_set[i]), (color))
		picture.save(output_image)

	def check_line(self, start, end, draw):
		y_step = float(end[1] - start[1])/float(end[0] - start[0])
		y_counter = float (0)

		inc = 1
		if start[0] > end[0]:
			inc = -1
			print("ystep: ", y_step, start, end)

		for x in range(start[0], end[0], inc):
			y_counter += y_step*inc
			if(draw):
				self.draw_points([[x, int(start[1] + y_counter)]], 10, 'clean_map_updated.png', 'clean_map_updated.png')
				print("checking: ", x, start[1] + int(y_counter))
			if (self.OCCUPANCY[x][int(start[1] + y_counter)] == 1):
				return False
			return True



	def call_RRT(self , event):
		init_node = []
		self.label.setPixmap(QPixmap('clean_map_updated.png'))
		self.destination_subscriber()
		# if len(self.NODES)==0:
		# 	self.NODES.append(self.start_clicked_point)
		# 	self.TREE[tuple(self.start_clicked_point)] = Node(None, self.start_clicked_point)
		# print("START POINT clicked  ___",self.start_clicked_point)
		# self.RRT(self.start_clicked_point, 'clean_map_updated.png')#init_node)


	all_nodes = []
	def RRT(self,initial_point, image_path):

		print("init_point------", initial_point)
		#print("rand poitn", rand_point)

		if self.all_nodes == 0:
			print("inif")
			self.all_nodes.append(initial_point)


		picture = Image.open(image_path)
	
		# Get the size of the image
		width, height = picture.size

		enivronment_rand_point = [0,0]

		while (True):
			enviro_x = np.random.randint(width)
			enviro_y = np.random.randint(height)

			environment_rand_point = [enviro_x, enviro_y]

			if (self.OCCUPANCY[enviro_x][enviro_y] == 0):
				break

			print("environment_rand_point ",environment_rand_point)
			selected = False
			print("nodes: ", self.NODES)
			ktree = scp.spatial.KDTree(self.NODES)
			nearest_nodes = ktree.query(environment_rand_point, 20)[1]

			print ("nearest: ", nearest_nodes)
			for n in nearest_nodes:
				if n >= len(ktree.data):
					break
				if self.check_line(ktree.data[n], environment_rand_point, False):
					print("selected: ", ktree.data[n])
					self.NODES.append(environment_rand_point)
					self.TREE[tuple(environment_rand_point)] = Node(self.TREE[tuple(ktree.data[n])], environment_rand_point)
					(self.TREE[tuple(environment_rand_point)]).nextNodes.append(self.TREE[tuple(environment_rand_point)])
					self.check_line(ktree.data[n], environment_rand_point, True)
					break
				print("nearest to end: ", nearest_nodes)
		        #self.draw_points(draw_line_between_points(environment_rand_point, ktree.data[n]), 10, 'clean_map_updated.png', 'clean_map_updated.png')
		  

		    #check if goal is acheiva

			nearest_nodes = ktree.query(self.dest_clicked_point, 20)[1]
			for n in nearest_nodes:
				if n >= len(ktree.data):
					break
				if self.check_line(ktree.data[n], self.dest_clicked_point, False):
					print ("Got goal")
					self.TREE[tuple(self.dest_clicked_point)]= Node(self.TREE[tuple(ktree.data[n])], self.dest_clicked_point)
					(self.TREE[tuple(self.dest_clicked_point)]).nextNodes.append(self.TREE[tuple(self.dest_clicked_point)])
					self.check_line(ktree.data[n], self.dest_clicked_point, True)
					break
				print(self.NODES)

		#neig_idx = knn_search(enviroment_rand_point,self.all_nodes,1)

		#print("k nearest   ", neig_idx)
		# tree = KDTree(all_nodes)

		# tree.query(enviro_rand_point, )
 	# 	nearest_dist, nearest_ind = tree.query(X, k=2)

		# total_nodes = len(self.all_nodes)
		# print("total nodes", total_nodes)

		# random = np.random.randint(total_nodes);

		# rand_select_node = self.all_nodes[random]

		# #generate rand point at radius 
		# rand_point = generate_rand_node(rand_select_node)
		# self.all_nodes.append(rand_point)

		# # select point randomly from current nodes in set
		# print("rand select node", rand_select_node)
		# print("all nodes",self.all_nodes)


		# take selected point create new rand point



		# find closest point from data set kd 2


		# select point randomly from current points


		# take point create another point



		node_color = 50 #rgb
		point_size = 3

		
		# #rand_point = generate_rand_node(initial_point)
		
		rand_point_visible = self.generate_point(environment_rand_point, point_size)
		# print(len(rand_point_visible))
		self.draw_points(rand_point_visible, node_color, 'clean_map_updated.png', 'clean_map_updated.png')

		# #render
		self.label.setPixmap(QPixmap('clean_map_updated.png'))

	def getPos(self , event):
		#create a point set, which gets added to image.
		#includes both start and destination points
		goal_posts = []

		#call back click event gives coordinates of clicked point
		x = event.pos().x()
		y = event.pos().y()

		clicked_point = [x,y]
		print("x: ",x, "y: ", y)

		#draw point at start position
		if(self.radioButton.isChecked()):
			self.start_clicked_point = clicked_point
			self.START_POINT = self.generate_point(clicked_point, 5)
			self.append_points(goal_posts, self.START_POINT)
			self.append_points(goal_posts, self.DEST_POINT)	
			print("START_POINT ", self.START_POINT)
			print("goal_posts", len(goal_posts))
			print("starting")

		#draw point at destination position
		if(self.radioButton_2.isChecked()):
			self.dest_clicked_point = clicked_point
			self.DEST_POINT = self.generate_point(clicked_point, 10)
			self.append_points(goal_posts, self.START_POINT)
			self.append_points(goal_posts, self.DEST_POINT)
			print("destination")

		self.draw_points(goal_posts,100,"clean_map_simple.png", "clean_map_updated.png")
		self.label.setPixmap(QPixmap('clean_map_updated.png'))



	def getPosFromDestPublisher(data):
		#create a point set, which gets added to image.
		#includes both start and destination points
		goal_posts = []

		#call back click event gives coordinates of clicked point
		# x = event.pos().x()
		# y = event.pos().y()

		# clicked_point = [x,y]

		print("x: ",data.data[0], "y: ", data.data[1])

		# #draw point at start position
		# if(self.radioButton.isChecked()):
		# 	self.start_clicked_point = #clicked_point
		# 	self.START_POINT = self.generate_point(clicked_point, 5)
		# 	self.append_points(goal_posts, self.START_POINT)
		# 	self.append_points(goal_posts, self.DEST_POINT)	
		# 	print("START_POINT ", self.START_POINT)
		# 	print("goal_posts", len(goal_posts))
		# 	print("starting")

		# #draw point at destination position
		# if(self.radioButton_2.isChecked()):
		# 	self.dest_clicked_point = clicked_point
		# 	self.DEST_POINT = self.generate_point(clicked_point, 10)
		# 	self.append_points(goal_posts, self.START_POINT)
		# 	self.append_points(goal_posts, self.DEST_POINT)
		# 	print("destination")

		# self.draw_points(goal_posts,100,"clean_map_simple.png", "clean_map_updated.png")
		# self.label.setPixmap(QPixmap('clean_map_updated.png'))

		



# select point randomly from current points in set
# take selected point create rand point
# find closest point from data set kd 2
# select point randomly from current points
# take point create another point


# point1 = [4, 5]
# point2 = [200, 100]

# draw_line_between_points(point1, point2)



# def draw_multiple_point():
# 	picture = Image.open(input_image_path)
# 	generate_point(point,color, point_size, input_image_path)

# 	x = point[0]
# 	y = point[1]
# 	point_g = []


# simplify_image("clean_map.png")

# count = 0
# if count == 0:
# 	count = 1
# 	occupancy_grid("clean_map_simple.png")








# def receiving_from_schueduler(data):
# 	print(data)

def destination_recieved(data):
	# print("data in")
	# gui_object = ranfdom()
	print("coord from scheduler ", data.data)

def current_position_recieved(data):
	print("in")
	print("amcl data",data.pose.pose.position)
	print()
	print("x ", data.pose.pose.position.x, "y ", data.pose.pose.position.y )

	# draw_points_g(goal_posts,100,"clean_map_simple.png", "clean_map_updated.png")
	# 	self.label.setPixmap(QPixmap('clean_map_updated.png'))






        # rate.sleep()


#f = [34,78, 986, 678, 567576, 567]

#ranslate_from(f)
		




if __name__ == '__main__':
    try:
    

    	

    	app=QApplication(sys.argv)
    	widget=ranfdom()
    	widget.show()
    	sys.exit(app.exec_())
    	



    except rospy.ROSInterruptException:
        pass








# def RRT(start, destination):
# # first point

# #create random point from set radius from initial point
# generate_rand_node(start point)

# connect_nearest_node

# 	#create random point in radius of 8 of first point. if point is occupied try again

# 	new_rand_point =random.uniform(0, 1) *2*(np.pi)

# 	#find nearest point to itself

# 	count_smallest
# 	for (all points)
# 	distance_between_2_points()

# 	#create connection between two points and draw line
# 	#draw line between the two points
# 	#draw node at point


# 	#randomly choose point from existing points
# 	append new rand point to nodes array


# 	random sample from current point selection

# 	#restart algorithim to however many nodes needed
# 	restart algorithm

# 	#if node reached point area, route found

# 	return 0

#picture.putpixel((x,y), (new_color))
#
#find all points between point 1 x and point 2 x with set size of 1
#color all points
