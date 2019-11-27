import speech_recognition as sr
import pyttsx3 as tts
import dialogflow_v2 as dialogflow
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToDict
import os
from dotenv import load_dotenv
import rospy
from std_msgs.msg import String


#Publishes new task
taskPublisher = rospy.Publisher('new_task', String, queue_size=100)
speakPublisher = rospy.Publisher('speak_msg', String, queue_size=100)
listenPublisher = rospy.Publisher('start_listening', String, queue_size=100)

#Globals for speech recognition
listener = sr.Recognizer()
client = None
session = None

#Global for object detection
numObjects = 0

#Global for tts - will continue conversation when it knows its done speaking
canContinue = False

#Global for speech recognition - stores the received speech transcription
processedSpeech = ""

def initialise():
    global client, session
    load_dotenv()
    rospy.loginfo("Environment variables loaded from .env")

    try:
        credentials = service_account.Credentials.from_service_account_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        client = dialogflow.SessionsClient(transport=os.getenv("https_proxy"))
        session = client.session_path(os.getenv("DIALOGFLOW_PROJECT_ID"), "unique")
        rospy.loginfo("GCP credentials verified and session created with DialogFlow API")
    except IOError as e:
        rospy.loginfo("ERROR - could not establish connection to DialogFlow API - {0}".format(e))


def sendToDialogflow(text):

    if text:
        textInput = dialogflow.types.TextInput(text=text, language_code="en")
        queryInput = dialogflow.types.QueryInput(text=textInput)

        response = client.detect_intent(session=session, query_input=queryInput)

        return response


def sendTask(taskType, sender, recipient, msgToSend, deliveryLoc, urgency):
    isUrgent = None
    if urgency == "urgent":
        isUrgent = 1
    else:
        isUrgent = 0
    taskString = taskType + "|" + sender + "|" + recipient + "|" + msgToSend  + "|" + deliveryLoc + "|" + str(isUrgent)
    task = String()
    task.data = taskString
    taskPublisher.publish(task)


def waitUntilDone(message):
	global canContinue
	done = False
	canContinue = False
	speakPublisher.publish(message)

	while not done:
		if canContinue:
			done = True
	print("done")


def waitForMessage():
	global processedSpeech

	listenPublisher.publish("listen")
	gotMessage = False
	while not gotMessage:
		if not processedSpeech == "":
			gotMessage = True
	print("Got message")
	return processedSpeech

	
def createMsgTask(response):
    global canContinue

    taskCreated = False

    with sr.Microphone() as source:
        while not taskCreated:
            parameters = MessageToDict(response.query_result.parameters)
            print(parameters)
            if parameters['msg-payload'] == "":
                msgToSend = None
            else:
                msgToSend = parameters['msg-payload']

            if parameters['sender'] == "":
                sender = None
            else:
                sender = parameters['sender']['name']

            if parameters['recipient'] == "":
                recipient = None
            else:
                recipient = parameters['recipient']['person']['name']

            if parameters['urgency'] == "":
                urgency = None
            else:
                urgency = parameters['urgency']

            if (msgToSend is None or sender is None) or (recipient is None or urgency is None):
            	waitUntilDone(response.query_result.fulfillment_text)

                listener.adjust_for_ambient_noise(source, duration=0.3)
                print("I'm listening")
                audio = listener.listen(source)
                print("got it")
                try:
                    request = listener.recognize_google(audio)
                    print(request)
                    response = sendToDialogflow(request)
                except sr.UnknownValueError:
                	waitUntilDone("Sorry, I didn't get that")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
            else:
                taskCreated = True

        waitUntilDone(response.query_result.fulfillment_text)

        waitUntilDone("Is this correct?")

        listener.adjust_for_ambient_noise(source, duration=0.3)
        print("I'm listening")
        audio = listener.listen(source)
        print("got it")
        try:
            confirmation = listener.recognize_google(audio)
            print(confirmation)
            if "yes" in confirmation.lower():
                waitUntilDone("Great! I'll get round to it. Thank you")
                sendTask("message",sender, recipient, msgToSend, "", urgency)
            else:
                waitUntilDone("I must have misunderstood something, lets start again.")
                listen()
        except sr.UnknownValueError:
            waitUntilDone("Sorry, I didn't get that")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


def createPkgTask(response):
    taskCreated = False

    with sr.Microphone() as source:
        while not taskCreated:
            parameters = MessageToDict(response.query_result.parameters)
            print(parameters)
            if parameters['delivery-location'] == "":
                deliveryLoc = None
            else:
                deliveryLoc = parameters['delivery-location']

            if parameters['sender'] == "":
                sender = None
            else:
                sender = parameters['sender']['name']

            if parameters['recipient'] == "":
                recipient = None
            else:
                recipient = parameters['recipient']['person']['name']

            if parameters['urgency'] == "":
                urgency = None
            else:
                urgency = parameters['urgency']

            if (deliveryLoc is None or sender is None) or (recipient is None or urgency is None):
                waitUntilDone(response.query_result.fulfillment_text)
                listener.adjust_for_ambient_noise(source, duration=0.3)
                print("I'm listening")
                audio = listener.listen(source)
                print("got it")
                try:
                    request = listener.recognize_google(audio)
                    print(request)
                    response = sendToDialogflow(request)
                except sr.UnknownValueError:
                    waitUntilDone("Sorry, I didn't get that")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
            else:
                taskCreated = True

        waitUntilDone(response.query_result.fulfillment_text)

        waitUntilDone("Is this correct?")

        listener.adjust_for_ambient_noise(source, duration=0.3)
        print("I'm listening")
        audio = listener.listen(source)
        print("got it")
        try:
            confirmation = listener.recognize_google(audio)
            print(confirmation)
            if "yes" in confirmation.lower():
                objectsBeforePlacement = numObjects
                obNotAdded = True
                waitUntilDone("Great! Please give me the item you want to deliver")
                while obNotAdded:
                    if objectsBeforePlacement == numObjects:
                        print("Object not added")
                    else:
                        print("object added")
                        obNotAdded = False
                waitUntilDone("Thank you, I will get round to it!")

                sendTask("package", sender, recipient, "", deliveryLoc, urgency)
            else:
                waitUntilDone("I must have misunderstood something, lets start again.")
                listen()
        except sr.UnknownValueError:
            waitUntilDone("Sorry, I didn't get that")
        except sr.RequestError as e:
            rospy.loginfo("Could not request results from Google Speech Recognition service; {0}".format(e))


def listenForCommand():
	global processedSpeech

	text = waitForMessage()
	processedSpeech = ""

	if "leonard" in text.lower() or "hey leonard" in text.lower():
		beginConversation()


def beginConversation():
    response = sendToDialogflow("Hello")

    with sr.Microphone() as source:
        listener.adjust_for_ambient_noise(source, duration=0.3)
        waitUntilDone(response.query_result.fulfillment_text)
        print("I'm listening")
        audio = listener.listen(source)
        rospy.loginfo("Captured audio. Processing...")

    try:
        request = listener.recognize_google(audio)
        result = sendToDialogflow(request)
        if result.query_result.intent.display_name == "create-msg-task":
            createMsgTask(result)
        elif result.query_result.intent.display_name == "create-pkg-task":
            createPkgTask(result)
        else:
            waitUntilDone(result.query_result.fulfillment_text)

    except sr.UnknownValueError:
        rospy.loginfo("Empty text - Could not recognise utterance")
        waitUntilDone("Sorry, I didn't get that")
    except sr.RequestError as e:
        rospy.loginfo("Could not request results from Google Speech Recognition Service; {0}".format(e))


def objectsDetected(data):
    global numObjects
    objects = data.data.split("|")
    print(objects.size)
    numObjects = objects.size


def doneSpeaking(data):
    global canContinue
    if data.data == "done":
        canContinue = True


def processedRequest(data):
	global processedSpeech
	rospy.loginfo("Received request: {0}".format(data.data))
	processedSpeech = data.data


def setUpNode():
    rospy.init_node('interaction', anonymous=True)
    rospy.Subscriber('objects_detected',String, objectsDetected)
    rospy.Subscriber('done_speaking', String, doneSpeaking)
    rospy.Subscriber('user_speech', String, processedRequest)
    initialise()

    while True:
        listenForCommand()


if __name__ == '__main__':
    try:
        setUpNode()
    except rospy.ROSInterruptException:
        pass
