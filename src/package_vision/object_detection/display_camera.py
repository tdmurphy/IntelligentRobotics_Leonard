	
import cv2

camera = cv2.VideoCapture(2)
cv2.namedWindow("Camera View")

while(True):
	ret, frame = camera.read()
	cv2.imshow("Camera View", frame)
	cv2.waitKey(20)
