from imageai.Detection import ObjectDetection, VideoObjectDetection
from imageai.Detection.Custom import CustomVideoObjectDetection
import os
import cv2
from matplotlib import pyplot as plt


execution_path = os.getcwd()
camera = cv2.VideoCapture(0)

def show_frame(camera):
	if(not camera.isOpened()):
    		print("camera not opened")
	else:
                print("camera opened")
                _, frame = camera.read()
                cv2.waitKey(20)
                cv2.imwrite('camera_view.png', frame)
                #cv2.destroyAllWindows()

model_path = "models/detection_model-ex-030--loss-0002.725.h5"
video_detector = CustomVideoObjectDetection()
video_detector.setModelTypeAsYOLOv3()
video_detector.setModelPath(model_path)
video_detector.setJsonPath("./models/detection_config.json")
video_detector.loadModel()


'''
custom = video_detector.CustomObjects(person=True, handbag=True, tie=True, suitcase=True, bottle=True, wine_glass=True, 
cup=True, fork=True, knife=True, spoon=True, bowl=True, banana=True, apple=True, sandwich=True, orange=True, pizza=True, 
donut=True, cake=True, chair=True, potted_plant=True, laptop=True, mouse=True, remote=True, keyboard=True, cell_phone=True, book=True,  
clock=True, scissors=True)
'''

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
    return string 

'''
def detectVideo(detector):
	print("detecting video...") 
    	video_detector.detectCustomObjectsFromVideo(output_file_path=os.path.join(execution_path, "./output/camera_video_detected"), 
    camera_input=camera, frames_per_second=10, log_progress=True, minimum_percentage_probability=80, 
    per_frame_function=objectsInFrame, save_detected_video=False, custom_objects=custom, return_detected_frame=True)
'''

def detectVideo(detector):
    print("detecting video...")
    video_detector.detectObjectsFromVideo(output_file_path=os.path.join(execution_path, "./output/camera_video_detected"), camera_input=camera, frames_per_second=10, log_progress=True, minimum_percentage_probability=80, per_frame_function=objectsInFrame, save_detected_video=False, return_detected_frame=True)

def talker():
        print("talker...")
        detectVideo(video_detector)

if __name__ == '__main__':
	show_frame(camera)
	talker() 

