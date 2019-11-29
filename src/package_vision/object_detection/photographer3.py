
import os
import cv2
import datetime
import sys


camera = cv2.VideoCapture(2)

now = datetime.datetime.now()
stamp = now.strftime("%H:%M:%S-")
print(stamp)



global image_type
global count 
count = 0 
image_type = sys.argv[1]
while(True):
	print("kill me")
	key = input("press key")
	if key == 1:
		print('save')
		path = os.path.join("./images/", image_type, stamp+'frame{:d}.jpg'.format(count))
		ret, frame = camera.read()
        	cv2.imwrite(path, frame)
        	count+=1
	elif key == 0:
		break
				


    


	

