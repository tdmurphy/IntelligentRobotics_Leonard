from imageai.Detection import ObjectDetection, VideoObjectDetection
import os
import cv2
from matplotlib import pyplot as plt
import rospy
from std_msgs.msg import Bool, String

execution_path = os.getcwd()
camera = cv2.VideoCapture(3)

def show_frame(camera):
	if(not camera.isOpened()):
    		print("camera not opened")
	else:
    		print("camera opened")
    		_, frame = camera.read()
    		cv2.waitKey(20)
		cv2.imwrite('camera_view.png', frame)
    		#cv2.destroyAllWindows()

video_detector = VideoObjectDetection()

model_path = "./models/yolo.h5"

video_detector.setModelTypeAsYOLOv3()

video_detector.setModelPath(model_path)

video_detector.loadModel()

pub_str = rospy.Publisher('objects_detected', String, queue_size=100)

custom = video_detector.CustomObjects(person=True, handbag=True, tie=True, suitcase=True, bottle=True, wine_glass=True, 
cup=True, fork=True, knife=True, spoon=True, bowl=True, banana=True, apple=True, sandwich=True, orange=True, pizza=True, 
donut=True, cake=True, chair=True, potted_plant=True, laptop=True, mouse=True, remote=True, keyboard=True, cell_phone=True, book=True,  
clock=True, scissors=True)

def objectsInFrame(frame_number, output_array, output_count, returned_frame):
    print("output_array length %i" % len(output_array))
    items = len(output_count)
    print("objects in frame %i" % items)
    string = ""
    objects_string = ""
    for eachItem in output_array:
        ob = str(eachItem['name']) + "-" + str(eachItem['percentage_probability']) + "|"
        string += ob
	objects_string += str(eachItem['name']) + "|"
    print(string)
    pub_str.publish(objects_string)
    return string 

def detectVideo(detector):
	print("detecting video...") 
    	video_detector.detectCustomObjectsFromVideo(output_file_path=os.path.join(execution_path, "./output/camera_video_detected"), 
    camera_input=camera, frames_per_second=5, log_progress=True, minimum_percentage_probability=80, 
    per_frame_function=objectsInFrame, save_detected_video=False, custom_objects=custom, return_detected_frame=True)

def talker():
	print("talker...")
        rospy.init_node('Detector', anonymous=True)
	detectVideo(video_detector)

if __name__ == '__main__':
	show_frame(camera)
	
	try:
		talker()
	except rospy.ROSInterruptException:
		pass 

