from imageai.Detection.Custom import DetectionModelTrainer

trainer = DetectionModelTrainer()
trainer.setModelTypeAsYOLOv3()

def create_model():
    trainer.setDataDirectory(data_directory="./model_trainer/training_data")
    trainer.setTrainConfig(object_names_array=['apple','cup','knife','mouse','mug','pen','pencil','phone','scissors','w'], batch_size=4, num_experiments=100, train_from_pretrained_model="./model_trainer/pretrained-yolov3.h5")
    trainer.trainModel()

def evaluateModel():
    metrics = trainer.evaluateModel(model_path="./model_trainer/models", json_path="./model_trainer/json/detection_config.json", iou_threshold=0.5, object_threshold=0.3, nms_threshold=0.5)
    print(metrics)
