import os
import cv2
import datetime
import sys


now = datetime.datetime.now()
stamp = now.strftime("%H:%M:%S-")
print(stamp)

camera = cv2.VideoCapture(2)
count = 0

global image_type

base_path = "./images/"

image_type = sys.argv[1]

full_path = base_path + image_type
if not os.path.exists(full_path):
        os.mkdir(full_path)

cv2.namedWindow("Camera View")
while(True):
	global count
	print(count)
	ret, frame = camera.read()
	key = cv2.waitKey(50)
	if key == 32:
		cv2.imshow("Camera View", frame)
		path = os.path.join(full_path, stamp+ "image{:d}.jpg".format(count))
		print(path)
		cv2.imwrite(path, frame)
		print(count)
		count += 1
	elif key == 27:
		cv2.destroyAllWindows()	
		break
	else:
		cv2.imshow("Camera View", frame)
		


	

