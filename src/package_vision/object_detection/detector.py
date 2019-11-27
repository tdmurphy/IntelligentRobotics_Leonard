from imageai.Detection import ObjectDetection, VideoObjectDetection
import os
import cv2

camera = cv2.VideoCapture(0)
if(not camera.isOpened()):
    print("camera not opened")
else:
    print("camera opened")
    #_, frame = camera.read()
    #cv2.imshow('Video', frame)

detector = ObjectDetection()
#video_detector = VideoObjectDetection()
video_detector_resnet = VideoObjectDetection()

#model_path = "./models/yolo-tiny.h5"
model_path_resnet = "./models/resnet50_coco_best_v2.0.1.h5"

#detector.setModelTypeAsTinyYOLOv3()
#video_detector.setModelTypeAsTinyYOLOv3()
video_detector_resnet.setModelTypeAsRetinaNet()

#detector.setModelPath(model_path)
#video_detector.setModelPath(model_path)
video_detector_resnet.setModelPath(model_path_resnet)

#detector.loadModel()
#video_detector.loadModel()
video_detector_resnet.loadModel()

custom = video_detector_resnet.CustomObjects(person=True, handbag=True, tie=True, suitcase=True, bottle=True, wine_glass=True, 
cup=True, fork=True, knife=True, spoon=True, bowl=True, banana=True, apple=True, sandwich=True, orange=True, pizza=True, 
donut=True, cake=True, chair=True, potted_plant=True, laptop=True, mouse=True, remote=True, keyboard=True, cell_phone=True, book=True,  
clock=True, scissors=True)

"""
def detectImage(input_path, output_path):
    #returns a dictionary containing names and percentage probabilities of detected objects
    detection = detector.detectObjectsFromImage(input_image=input_path, output_image_path=output_path)

    for eachItem in detection:
        print(eachItem["name"], " : ", eachItem["percentage_probability"])

    return detection
"""
def objectsInFrame(frame_number, output_array, output_count):
    items = len(output_count)
    print("objects in frame %i" % items)
    string = ""
    for eachItem in output_array:
        ob = str(eachItem['name']) + "-" + str(eachItem['percentage_probability']) + "|"
        string += ob
    print(string)
    return string 

def detectVideo(detector):
    
    execution_path = os.getcwd()

    detector.detectCustomObjectsFromVideo(output_file_path=os.path.join(execution_path, "./output/camera_video_detected"), 
    camera_input=camera, frames_per_second=5, log_progress=True, minimum_percentage_probability=70, 
    per_frame_function=objectsInFrame, save_detected_video=False, custom_objects=custom)

#detectImage("./input/test_image.jpg", "./output/newimage.jpg")
#detectVideo("./output/camera_video_detected", video_detector)
detectVideo(video_detector_resnet)

