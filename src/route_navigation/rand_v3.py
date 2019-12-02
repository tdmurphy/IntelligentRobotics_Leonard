# !/usr/bin/env python
import sys 
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
import webcolors
from PIL import Image
import numpy as np
import random





#GUI
class ranfdom(QDialog):

	START_POINT = [0,0]
	DEST_POINT = [0,0]
	

	def __init__(self):
		super(ranfdom,self).__init__()
		loadUi('ranfdom.ui', self)
		self.setWindowTitle('ranfdom PyQt5 Gui')
		self.label.setPixmap(QPixmap('clean_map_updated.png'))
		self.label.mousePressEvent = self.getPos
		
	@pyqtSlot()

	def append_points(self,point_set, points_to_add):

		
		for i in range(len(points_to_add)):
			point_set.append(points_to_add[i])
			print("point_set", points_to_add[i])

	def generate_point(self,point, point_size):
		
		#define x and y for grid of points creation
		x = point[0]
		y = point[1]
		point_g = []

		#creates a grid box with point at centre of box
		for i in range(x-point_size, x +point_size):
			for j in range(y-point_size, y+point_size):
				point_g.append([i,j])

		return point_g

	def draw_points(self,point_set, color, input_image, output_image):
		picture = Image.open(input_image)
		for i in range(len(point_set)):
			print("point :", i ,"  ", point_set[i])
			if(point_set[i] != 0):
				picture.putpixel((point_set[i]), (color))
		picture.save(output_image)
	


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
			self.START_POINT = self.generate_point(clicked_point, 5)
			self.append_points(goal_posts, self.START_POINT)
			self.append_points(goal_posts, self.DEST_POINT)	
			print("START_POINT ", self.START_POINT)
			print("goal_posts", len(goal_posts))
			print("starting")

		#draw point at destination position
		if(self.radioButton_2.isChecked()):
			self.DEST_POINT = self.generate_point(clicked_point, 10)
			self.append_points(goal_posts, self.START_POINT)
			self.append_points(goal_posts, self.DEST_POINT)
			print("destination")

		self.draw_points(goal_posts,100,"clean_map_simple.png", "clean_map_updated.png")
		self.label.setPixmap(QPixmap('clean_map_updated.png'))
		


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

	print(Matrix)


point1 = [4, 5]
point2 = [200, 100]
draw_line_between_points(point1, point2)



# def draw_multiple_point():
# 	picture = Image.open(input_image_path)
# 	generate_point(point,color, point_size, input_image_path)

# 	x = point[0]
# 	y = point[1]
# 	point_g = []


simplify_image("clean_map.png")

count = 0
if count == 0:
	count = 1
	occupancy_grid("clean_map_simple.png")

app=QApplication(sys.argv)
widget=ranfdom()
widget.show()
sys.exit(app.exec_())


