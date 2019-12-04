
from imageai.Detection.Custom import CustomObjectDetection
from imageai.Detection import ObjectDetection, VideoObjectDetection
import os
import cv2
from matplotlib import pyplot as plt
import rospy
from std_msgs.msg import Bool, String

execution_path = os.getcwd()
camera = cv2.VideoCapture(5)

minimum_percentage_probability = 60
min_low_probability = 8
count_weight = 0.1

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
detector.loadModel(detection_speed='fast') 

video_detector = VideoObjectDetection()
video_detector.setModelTypeAsRetinaNet()
video_detector.setModelPath(model_path)
video_detector.loadModel()

objects_dict = {}

pub_str = rospy.Publisher('objects_detected', String, queue_size=100)


custom = detector.CustomObjects(bottle=True, wine_glass=True, 
cup=True, fork=True, knife=True, spoon=True, banana=True, apple=True, sandwich=True, orange=True,
 mouse=True, remote=True, cell_phone=True, book=True,  scissors=True)


def detect_image():
	print("detecting...")
	_, frame = camera.read()
	frame = increase_brightness(frame)
	detections = detector.detectCustomObjectsFromImage(input_type='array', input_image=frame, output_image_path='./output/output.png', minimum_percentage_probability=60, thread_safe=True, custom_objects=custom)
	#objects_string = filter_detections(detections)
	objects_string=edit_dict(detections)
	print(objects_string)
	pub_str.publish(objects_string)

def detectVideo(detector):
	print("detecting video...") 
	video_detector.detectCustomObjectsFromVideo(output_file_path="./output/camera_video_detected", 
    camera_input=camera, frames_per_second=10, log_progress=True, minimum_percentage_probability=40, 
    per_frame_function=objectsInFrame, save_detected_video=False, custom_objects=custom, return_detected_frame=False)

def edit_dict(frame_number, output_array, output_count):
	global objects_dict
	print(objects_dict)
	objects_string = ""
	objects = []
	for d in output_array: 
		percentage_prob = d['percentage_probability'] 
		object_name = d['name']
		#print('percentage prob before: %f' % percentage_prob)
		if(percentage_prob >= min_low_probability and not(object_name in objects)):
			objects += [object_name]

			#increase the count 
			if(object_name in objects_dict.keys()):
				objects_dict[object_name] = objects_dict[object_name] + 1
			else:
				objects_dict[object_name] = 1
			
			#times the percentage probability by a count so that those that are seen consistently are favoured 
			percentage_prob = (percentage_prob +  (percentage_prob * objects_dict[object_name] * count_weight))

			if(percentage_prob >= minimum_percentage_probability):
				objects_string += object_name + '|'
	
	#print('percentage prob after: %f' % percentage_prob)
	#reset the count of objects that are not recorded 
	objects = set(objects)
	print(objects)
	for ob, _ in objects_dict.items():
		if not(ob in objects):
			objects_dict[ob] = 0 		
		
	return objects_string		

def filter_detections(detections):
	objects_string = ""
	for d in detections:
		if(d['percentage_probability'] > minimum_percentage_probability):
			objects_string += str(d['name']) + '|'
	return objects_string 

def convert_hsv(frame):
	return cv2.cvtColor(frame, cv2.COLOR_HSV2RGB)

def increase_brightness(frame):
	alpha = 1.1 
	beta = 0
	return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

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

