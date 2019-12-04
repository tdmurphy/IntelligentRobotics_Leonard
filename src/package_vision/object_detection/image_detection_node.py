
from imageai.Detection.Custom import CustomObjectDetection
from imageai.Detection import ObjectDetection
import os
import cv2
from matplotlib import pyplot as plt
import rospy
from std_msgs.msg import Bool, String

execution_path = os.getcwd()
camera = cv2.VideoCapture(0)

minimum_percentage_probability = 80

def show_frame(camera):
	if(not camera.isOpened()):
    		print("camera not opened")
	else:
                print("camera opened")
                _, frame = camera.read()
                cv2.waitKey(20)
                cv2.imwrite('camera_view.png', frame)
                #cv2.destroyAllWindows()
''' 
TRAINED YOLO 
model_path = "models/detection_model-ex-038--loss-0002.471.h5"
detector = CustomObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath(model_path)
detector.setJsonPath("./models/detection_config.json")
detector.loadModel() '''

'''YOLO TINY
model_path="models/yolo-tiny.h5"
detector = ObjectDetection()
detector.setModelTypeAsTinyYOLOv3()
detector.setModelPath(model_path)
detector.loadModel() 
'''

'''RESNET'''
model_path="models/resnet50_coco.h5"
detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath(model_path)
detector.loadModel(detection_speed="faster") 



pub_str = rospy.Publisher('objects_detected', String, queue_size=100)


custom = detector.CustomObjects(handbag=True, tie=True, suitcase=True, bottle=True, wine_glass=True, 
cup=True, fork=True, knife=True, spoon=True, bowl=True, banana=True, apple=True, sandwich=True, orange=True, pizza=True, 
donut=True, cake=True, mouse=True, remote=True, keyboard=True, cell_phone=True, book=True,  
clock=True, scissors=True)


def detect_image():
	print("detecting...")
	_, frame = camera.read()
	detections = detector.detectCustomObjectsFromImage(input_type='array', input_image=frame, output_image_path='./output/output.png', minimum_percentage_probability=90, thread_safe=True, custom_objects=custom)
	objects_string = filter_detections(detections)
	print(objects_string)
	pub_str.publish(objects_string)


def filter_detections(detections):
	objects_string = ""
	for d in detections:
		if(d['percentage_probability'] > minimum_percentage_probability):
			objects_string += str(d['name'])
	return objects_string 

def talker():
        rospy.init_node('Detector', anonymous=True)
        detect_image()

if __name__ == '__main__':
	show_frame(camera)
	while(True):
		try:
			talker()
		except rospy.ROSInterruptException:
			pass 

