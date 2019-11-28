from imageai.Detection import ObjectDetection, VideoObjectDetection
import os
import cv2
import rospy
from std_msgs.msg import Bool, String

video_detector = VideoObjectDetection()
camera = cv2.VideoCapture(3)
execution_path = os.getcwd()

model_path = "./models/yolo-tiny.h5"

video_detector.setModelTypeAsTinyYOLOv3()

video_detector.setModelPath(model_path)

video_detector.loadModel()

#publishers 
pub_bool = rospy.Publisher('detecting_object', Bool, queue_size=100)
pub_str = rospy.Publisher('objects_detected', String, queue_size=100)

custom = video_detector.CustomObjects(person=True, handbag=True, tie=True, suitcase=True, bottle=True, wine_glass=True, 
cup=True, fork=True, knife=True, spoon=True, bowl=True, banana=True, apple=True, sandwich=True, orange=True, pizza=True, 
donut=True, cake=True, chair=True, potted_plant=True, laptop=True, mouse=True, remote=True, keyboard=True, cell_phone=True, book=True,  
clock=True, scissors=True)

def objectsInFrame(frame_number, output_array, output_count):
	#print("length of output array %i" % len(output_array))
	#print("length of output count %i" % len(output_count))
	for eachItem in output_count:
		print(eachItem)
	return

def detectVideo(detector):
    	detector.detectCustomObjectsFromVideo(output_file_path=os.path.join(execution_path, "./output/camera_video_detected.mp4"),camera_input=camera, frames_per_second=1, log_progress=True, minimum_percentage_probability=85, return_detected_frame=False, per_frame_function=objectsInFrame, save_detected_video=False, custom_objects=custom)
	return


def talker():
        rospy.init_node('Detector', anonymous=True)
        detectVideo(video_detector)
        rospy.spin()

if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		pass 
