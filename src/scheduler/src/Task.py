class Task():
    taskID=0
    def __init__(self,sender='',recipient='',taskType='',payLoad='',location='',modifier='',current=False):
        self.taskID=Task.taskID
        Task.taskID +=1     
        self.sender=sender
        self.recipient=recipient
        self.taskType= taskType
        self.payLoad=payLoad
        self.location=location
        self.urgent=modifier
        self.current=current

    def printTask(self):
        print("ID: "+str(self.taskID)+ " "+str(self.sender)+" -> " +str(self.recipient)+" : "+str(self.payLoad)+" : "+str(self.location)+": now? : "+str(self.current))
        
        
        
#taskType, payload, recipient, location, sender, urgent
