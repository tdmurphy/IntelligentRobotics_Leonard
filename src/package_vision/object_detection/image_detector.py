from imageai.Detection import ObjectDetection, VideoObjectDetection
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from imageai.Prediction import ImagePrediction


execution_path = os.getcwd()
camera = cv2.VideoCapture(0)

prediction = ImagePrediction()
prediction.setModelTypeAsResNet()
prediction.setModelPath( os.path.join('models/resnet50_weights_tf_dim_ordering_tf_kernels.h5'))
prediction.loadModel()

detector = ObjectDetection()
detector.setModelTypeAsTinyYOLOv3()
detector.setModelPath('models/yolo-tiny.h5')
detector.loadModel()


count = 0
def take_pictures(camera):
    global count
    ret, frame = camera.read()

    if ret:
        path = os.path.join("./output/", 'frame{:d}.jpg'.format(count))
        #cv2.imwrite(path, frame) 

        #predictions, probabilities = prediction.predictImage(path, result_count=5)

        '''for eachPrediction, eachProbability in zip(predictions, probabilities):
            print(eachPrediction, " : " , eachProbability)
        '''
        detected_image_array, detections = detector.detectObjectsFromImage(output_type="array", input_type="array", input_image=np.asarray(frame) ) # For numpy array output type

        #detections = detector.detectObjectsFromImage(input_image=path, output_image_path=os.path.join(execution_path , "image3new.jpg"), minimum_percentage_probability=30,  extract_detected_objects=True)

        for eachObject in detections:
            print(eachObject)
            #print(eachObject["name"] , " : " , eachObject["percentage_probability"])
            print("--------------------------------")


        count += 30 # i.e. at 30 fps, this advances one second
        camera.set(1, count)

    else:
        camera.release()
        

for i in range(0,20):
    take_pictures(camera)