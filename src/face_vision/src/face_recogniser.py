import os
import face_recognition
import cv2
import easygui
import numpy as np

class FacialRecogniser():
    
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names =[]
        self.unknownCount=0
        self.currentTargetUnknownOrNoTarget=True
        self.target=None
        self.peoplePresent=[]
        self.backgroundPeople=[]
        self.init_people()
	self.video_capture=None
        #self.resetFile("knownFaces.txt")
        #self.new_Screen()
        
        
    def resetFile(self,file):
        if(os.path.exists(file)):
            os.remove(file)
            print("File Removed!")
        f= open("knownFaces.txt","w+")
        f.close()
    
    
    def addPerson(self, face_encoding, name): 
        f= open("knownFaces.txt","a+")       
        name = easygui.enterbox("Name of "+name+" :")
        print("Oh, you're",name, ", okay.")
        line=str(name)+":"
        for i in range(0,len(face_encoding)):
            line+= str(face_encoding[i])
            if(i!=(len(face_encoding)-1)):
                line+= str(" ")
        f.write(line+"\n")
        f.close() 
        self.init_people()
        return
    
    def isPersonPresent(self,name):
        present=False
        if name in self.peoplePresent:
            present=True
        return present
        
         
    def init_people(self):
        f= open("knownFaces.txt","r+")
        fLines=f.readlines()
        for line in fLines:
            face_identity= line.split(':')[0]    
            face_encoding= np.fromstring(line.split(':')[1], sep=' ')
            if(face_identity not in self.known_face_names):
                self.known_face_encodings.append(face_encoding) 
                self.known_face_names.append(face_identity) 
        f.close()
        
    def displayNames(self,face_locations, face_names,cv2,frame):
        self.peoplePresent=face_names
	#print("Looking for",self.target, "Background searching",self.backgroundPeople)
        if ((self.target != None) and (self.target in self.peoplePresent)):
            # found person! Send message back!
	    self.close_Screen()
	    return True, self.target
	for person in self.backgroundPeople:
		if person in self.peoplePresent:
		    # found background person! Send message back!
		    print("Found",person," in fg")
	            self.close_Screen()
	    	    return True, person
        for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 3)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        cv2.imshow('Video', frame)
        return None, ''

          
    def setCurrentTarget(self,person):
        if(self.target==None):
            print("Finding new person")
            self.target=person
        elif((self.target!=None) and(self.target!=person)):
	    if (self.target not in self.backgroundPeople):
                self.backgroundPeople.append(self.target)
                print("Inserting",self.target," into background finding")
            self.target=person    
        self.currentTargetUnknownOrNoTarget=False
	if person in self.backgroundPeople:
	    self.backgroundPeople.remove(person)
        print("Looking for",self.target, "And I know",self.known_face_names)
        
    def setBackgroundTarget(self,person_to_back,new_target):
	if(new_target==self.target):
		return
	if (person_to_back not in self.backgroundPeople):
		self.backgroundPeople.append(person_to_back)
	self.setCurrentTarget(new_target)	

	"""if person_to_back==new_target: #if person to background is the new target, don't add
	    self.target=new_target
	if self.target!=person_to_back:
	    if():
	    self.backgroundPeople.append(self.target)

	if ((person_to_back not in self.backgroundPeople) and(person_to_back!=new_target)):
            self.backgroundPeople.append(person_to_back) #person to back isn't current
	    print("Inserting",person_to_back,"into queue")
	if self.target==person_to_back:
	    if (self.target not in self.backgroundPeople and (person_to_back!=new_target)) :
		self.backgroundPeople.append(self.target)
		print("Inserting",self.target,"into queue")
	    self.target=new_target"""

            
    def removeTarget(self,person):
        if self.target==person:
            self.target=None
            self.currentTargetUnknownOrNoTarget=True
        elif person in self.backgroundPeople:
            self.backgroundPeople.remove(person)
        else:
            return

    def close_Screen(self):
        print("Closing screen",self.target)
        self.video_capture.release()
        cv2.destroyAllWindows()
        
    def new_Screen(self):
	print("Opening Screen",self.target)
        self.init_people()
        self.video_capture = cv2.VideoCapture(0)    
        unknownNames={}

        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True
        
        while True:
            ret, frame = self.video_capture.read()    
            #print("1",frame)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            #print("2")
            rgb_small_frame = small_frame[:, :, ::-1]
            cv2.imshow('Video', frame)
            if process_this_frame:
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                #print("Only know:",self.known_face_names)
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"+str(self.unknownCount)                    
                    if(self.known_face_encodings!=[]):
                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)                    
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            #print("Think this is",name)
                    if(name=="Unknown"+str(self.unknownCount)):
                        if(self.currentTargetUnknownOrNoTarget):
                            self.unknownCount+=1
                        unknownNames[name]=(face_encoding)
                        #print("Don't know them")
                    face_names.append(name)
                Found, foundPerson=self.displayNames(face_locations, face_names,cv2, frame) 
            
            if(self.currentTargetUnknownOrNoTarget):
                for name in list(unknownNames.keys()):
                    self.addPerson(unknownNames[name],name)                    
                    del unknownNames[name]
                    print(len(unknownNames))
            process_this_frame = not process_this_frame
            
            Found, foundPerson=self.displayNames(face_locations, face_names,cv2, frame)  
	    if (Found!=None):
		self.close_Screen()
		return foundPerson          
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break   

        self.close_Screen()
        return 
