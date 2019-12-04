import speech_recognition as sr
import pyttsx3 as tts
import dialogflow_v2 as dialogflow
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToDict
import os
from dotenv import load_dotenv
import rospy
from std_msgs.msg import String, Int32


#Publishers
taskPublisher = rospy.Publisher('new_task', String, queue_size=100)
speakPublisher = rospy.Publisher('speak_msg', String, queue_size=1)
listenPublisher = rospy.Publisher('start_listening', String, queue_size=1)
stopPublisher = rospy.Publisher('stop_moving', String, queue_size=100)
deliverPublisher = rospy.Publisher('delivered', String, queue_size=100)


#Global for listen control - wont background listen if delivering task(s)
delivering = False
justDelivered = False
ignoreResult = False

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
        client = dialogflow.SessionsClient(credentials=credentials)
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
    rospy.loginfo("Done speaking message: {0}".format(message))


def waitForMessage():
    global processedSpeech

    listenPublisher.publish("listen")
    gotMessage = False
    while not gotMessage:
    	if ignoreResult:
    		gotMessage = True
        elif not processedSpeech == "":
            gotMessage = True
    rospy.loginfo("Received message: {0}".format(processedSpeech))
    return processedSpeech

    
def createMsgTask(response):
    global processedSpeech

    taskCreated = False

    while not taskCreated:
        parameters = MessageToDict(response.query_result.parameters)
        rospy.loginfo("Current task parameters: {0}".format(parameters))
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

            request = " "
            while request != " ":
            	request = waitForMessage()
            	processedSpeech = ""

            response = sendToDialogflow(request)

        else:
            taskCreated = True

    waitUntilDone(response.query_result.fulfillment_text)
    waitUntilDone("Is this correct?")

    confirmation = " "
    while confirmation != " ":
    	confirmation = waitForMessage()
    	processedSpeech = ""

    if ("yes" in confirmation.lower() or "correct" in confirmation.lower()) and (not "not" in confirmation.lower() or not "no" in confirmation.lower()):
        waitUntilDone("Great! I'll get round to it. Thank you")
        sendTask("message",sender, recipient, msgToSend, "", urgency)
    else:
        beginConversation("I must have misunderstood something, lets start again. What can I do for you?")


def createPkgTask(response):
    global processedSpeech
    taskCreated = False

    while not taskCreated:
        parameters = MessageToDict(response.query_result.parameters)
        rospy.loginfo("Current task parameters: {0}".format(parameters))
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

            request = " "
            while request != " ":
            	request = waitForMessage()
            	processedSpeech = ""

        else:
            taskCreated = True

    waitUntilDone(response.query_result.fulfillment_text)
    waitUntilDone("Is this correct?")

    confirmation = " "
    while confirmation != " ":
    	confirmation = waitForMessage()
    	processedSpeech = ""

    if ("yes" in confirmation.lower() or "correct" in confirmation.lower()) and (not "not" in confirmation.lower() or not "no" in confirmation.lower()):
        objectsBeforePlacement = numObjects
        obNotAdded = True
        waitUntilDone("Great! Please give me the item you want to deliver")
        while obNotAdded:
            if objectsBeforePlacement < numObjects:
                obNotAdded = False

        print("object added")
        waitUntilDone("Thank you, I will get round to it!")

        sendTask("package", sender, recipient, "", deliveryLoc, urgency)
    else:
        beginConversation("I must have misunderstood something, lets start again. What can I do for you?")


def listenForCommand():
    global processedSpeech, justDelivered, ignoreResult

    if not delivering and not justDelivered:

    	text = waitForMessage()
    	processedSpeech = ""

    	if "leonard" in text.lower():
        	beginConversation("Hello")
    elif justDelivered:
    	justDelivered = False
    	ignoreResult = False
    	beginConversation("Thats's everything I have for you, is there anything else I can do?")


def beginConversation(opener):
    global processedSpeech

    stopPublisher.publish("stop")
    
    if opener == "Hello":
    	response = sendToDialogflow(opener)
    	waitUntilDone(response.query_result.fulfillment_text)
    else:
    	waitUntilDone(opener)

    processedSpeech = ""

    request = " "
    while request != " ":
    	request = waitForMessage()
    	processedSpeech = ""

    result = sendToDialogflow(request)

    if result.query_result.intent.display_name == "create-msg-task":
        createMsgTask(result)
    elif result.query_result.intent.display_name == "create-pkg-task":
        createPkgTask(result)
    else:
        waitUntilDone(result.query_result.fulfillment_text)
        stopPublisher.publish("move")


def deliverTask(data):
	global delivering, justDelivered, ignoreResult
	delivering = True
	ignoreResult = True
	rospy.loginfo("Received tasks to deliver: {0}".format(data.data))

	tasks = data.data.split("#")
	tasksToDeliver = []
	for task in tasks:
		if task != "":
			tasksToDeliver.append(task)

	recipient = tasksToDeliver[0].split("|")[2]

	if len(tasksToDeliver) == 1:
		waitUntilDone("Hello {0}, I have {1} task to deliver to you".format(recipient,len(tasksToDeliver)))
	else:
		waitUntilDone("Hello {0}, I have {1} tasks to deliver to you".format(recipient,len(tasksToDeliver)))

	for task in tasksToDeliver:
		taskInfo = task.split("|")

		if taskInfo[0] == "message":
			waitUntilDone("I have a message from {0} for you, the message is as follows: {1}".format(taskInfo[1],taskInfo[3]))
		else:
			objectsBeforeCollect = numObjects
			obTaken = False
			waitUntilDone("I have a package from {0} for you, please take it".format(taskInfo[1]))
			while not obTaken:
				if objectsBeforeCollect > numObjects:
					obTaken = True
					print("object taken")
	delivering = False
	justDelivered = True
	deliverPublisher.publish(recipient)


def objectsDetected(data):
    global numObjects
    print(data.data)
    numObjects = data.data


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
    rospy.Subscriber('unique_objects',Int32, objectsDetected)
    rospy.Subscriber('done_speaking', String, doneSpeaking)
    rospy.Subscriber('user_speech', String, processedRequest)
    rospy.Subscriber('deliver', String, deliverTask)
    initialise()

    while True:
        listenForCommand()


if __name__ == '__main__':
    try:
        setUpNode()
    except rospy.ROSInterruptException:
        pass
