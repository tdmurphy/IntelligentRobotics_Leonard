from imageai.Detection import ObjectDetection, VideoObjectDetection
import os
import cv2
import rospy

detector = ObjectDetection()
video_detector = VideoObjectDetection()
camera = cv2.VideoCapture(0) #throws error on VScode but works

model_path = "./models/yolo-tiny.h5"

detector.setModelTypeAsTinyYOLOv3()
video_detector.setModelTypeAsTinyYOLOv3()

detector.setModelPath(model_path)
video_detector.setModelPath(model_path)

detector.loadModel()
video_detector.loadModel()

#publisher 
pub_bool = rospy.publisher('detecting_object', Boolean, queue_size=100)
pub_str = rospy.publisher('objects_detected', String, queue_size=100)

def detectImage(input_path, output_path):
    #returns a dictionary containing names and percentage probabilities of detected objects
    detection = detector.detectObjectsFromImage(input_image=input_path, output_image_path=output_path)

    for eachItem in detection:
        print(eachItem["name"], " : ", eachItem["percentage_probability"])

    return detection

def objectsInFrame(frame_number, output_array, output_count):
    items = len(output_count)
    print("objects in frame %i" % items)
    for eachItem in output_count:
        print(eachItem)
    
    #if there are some items being detected, return true 
    detecting = (items > 0)
    pub_bool.publish(detecting)
    typesOfObjectInFrame(output_count)

    return output_count

def typesOfObjectInFrame(output_count):
    items = ""
    delim = "|"
    for eachItem in output_count:
        items = items + delim + eachItem["name"]
    pub_str.publish(items)

def detectVideo(output_path):
    execution_path = os.getcwd()

    video_path = video_detector.detectObjectsFromVideo(camera_input=camera,
                                output_file_path=os.path.join(execution_path, output_path)
                                , frames_per_second=5, log_progress=True, minimum_percentage_probability=30,
                                per_frame_function=objectsInFrame)
    print(video_path)

def talker():
	rospy.init_node('Detector', anonymous=True)
    detectVideo("./output/camera_video_detected")
	#rospy.Subscriber('objects', Float32MultiArray, detectVideo)
	rospy.spin()

if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterrupException:
		pass 

#detectImage("./input/test_image.jpg", "./output/newimage.jpg")
detectVideo("./output/camera_video_detected")
