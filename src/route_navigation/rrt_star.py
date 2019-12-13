#!/usr/bin/env python
import webcolors
from PIL import Image
import numpy as np
import random

picture = Image.open("clean_map_updated.png")

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


def color_pixals(points_x_y, rgb):  
	#for all points
	for i in range(len(points_x_y)):
		picture.putpixel((points_x_y[i][0], points_x_y[i][1]), (100))
		picture.save("clean_map_updated_lines.png")

#goal1 80, 300
#goal2 500, 200

point1 = [80, 300]
point2 = [90, 200]

g = draw_line_between_points(point1, point2)

print(g)

rgb = [30, 245, 3]
color_pixals(g,rgb)



def simplify_image():


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


	# now we rewrite the image to new black and white comprising of only two rgb values
	picture.save("clean_map_updated.png")


	#now we create an occupancy grid from therefore image data teh same dimentions as the image size
	#	. if the area is black it is occupied and is therefore true. If unoccupued = false
	Matrix = [[0 for x in range(height)] for y in range(width)] 

	for x in range (width):
   		for y in range (height):
   			current_color = picture.getpixel( (x,y) )
   			print("current color upd ", current_color)
   			if current_color == 254:
   				print("x,y ", x, "  ", y)
   				Matrix[x][y] = 0

   			print("unoc ", Matrix[x][y])
   			print("width,", width," ")
   			print("height",height, " ")
   		else:
   			print("x,y ", x, "  ", y)
   			Matrix[x][y] = 1
   			print("oc ", Matrix[x][y])
   			print("width,", width," ")
   			print("height",height, " ")

	print(Matrix)



# def RRT(start, destination):
# 	#first point
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


#draw line on picture between two points
#line_between_points(point1, point2)
	
	#find y = mx +c
	#find all points between point 1 x and point 2 x with set size of 1
	#color all points 





       	
