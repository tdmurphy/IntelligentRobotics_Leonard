import speech_recognition as sr
import pyttsx3 as tts
import dialogflow_v2 as dialogflow
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToDict
import os
from dotenv import load_dotenv
import rospy


taskPublisher = rospy.Publisher('new_task',String,queue_size=100)
engine = tts.init()
listener = sr.Recognizer()
client = None
session = None


def initialise():
	global engine, client, session
	load_dotenv()
	rospy.loginfo("Environment variables loaded from .env")

	try:
		credentials = service_account.Credentials.from_service_account_file(os.getenv("GCP_SERVICE_ACC_CRED"))
		client = dialogflow.SessionsClient(credentials = credentials)
		session = client.session_path(os.getenv("DIALOGFLOW_PROJECT_ID"), "unique")
		rospy.loginfo("GCP credentials verified and session created with DialogFlow API")
	except IOError as e:
		rospy.loginfo("ERROR - could not establish connection to DialogFlow API - {0}".format(e))

	engine.setProperty('rate', 140) #Set rate of speech
	engine.setProperty('volume',1.0)
	rospy.loginfo("Text-to-Speech successfully configured")


def sendToDialogflow(text):

	if text:
		textInput = dialogflow.types.TextInput(text = text, language_code = "en")
		queryInput = dialogflow.types.QueryInput(text = textInput)

		response = client.detect_intent(session = session, query_input = queryInput)

		return response


def sendTask(taskType, sender, recipient, msgToSend, deliveryLoc, urgency):
	taskString = taskType + "|" + sender + "|" + recipient + "|" + msgToSend "|" + deliveryLoc + "|" + urgency
	task = String()
	task.data = taskString
	taskPublisher.publish(task)


def createMsgTask(response):
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
                speak(response.query_result.fulfillment_text)
                listener.adjust_for_ambient_noise(source, duration=1)
                print("I'm listening")
                audio = listener.listen(source)
                print("got it")
                try:
                    request = listener.recognize_google(audio)
                    print(request)
                    response = sendToDialogflow(request)
                except sr.UnknownValueError:
                    speak("Sorry, I didn't get that")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
            else:
                print("Im done")
                taskCreated = True

        speak(response.query_result.fulfillment_text)
        speak("Is this correct?")

        listener.adjust_for_ambient_noise(source, duration=1)
        print("I'm listening")
        audio = listener.listen(source)
        print("got it")
        try:
            confirmation = listener.recognize_google(audio)
            print(confirmation)
            if "yes" in confirmation.lower():
                speak("Great! I'll get round to it. Thank you")
                sendTask("message",sender, recipient, msgToSend, "", urgency)
            else:
                speak("I must have misunderstood something, lets start again.")
                listen()
        except sr.UnknownValueError:
            speak("Sorry, I didn't get that")
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
                speak(response.query_result.fulfillment_text)
                listener.adjust_for_ambient_noise(source, duration=1)
                print("I'm listening")
                audio = listener.listen(source)
                print("got it")
                try:
                    request = listener.recognize_google(audio)
                    print(request)
                    response = sendToDialogflow(request)
                except sr.UnknownValueError:
                    speak("Sorry, I didn't get that")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
            else:
                print("Im done")
                taskCreated = True

        speak(response.query_result.fulfillment_text)
        speak("Is this correct?")

        listener.adjust_for_ambient_noise(source, duration=1)
        print("I'm listening")
        audio = listener.listen(source)
        print("got it")
        try:
            confirmation = listener.recognize_google(audio)
            print(confirmation)
            if "yes" in confirmation.lower():
                speak("Great! I'll get round to it. Thank you")
                sendTask("package", sender, recipient, "", deliveryLoc, urgency)
            else:
                speak("I must have misunderstood something, lets start again.")
                listen()
        except sr.UnknownValueError:
            speak("Sorry, I didn't get that")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


def listenForCommand():

	with sr.Microphone() as source:
		listener.adjust_for_ambient_noise(source, duration = 0.3)
		rospy.loginfo("Node is listening")
		audio = listener.listen(source)
		rospy.loginfo("Captured audio. Processing...")

	try:
		text = listener.recognize_google(audio)
		rospy.loginfo("Audio processed as : " + text)
		if "leonard" in text.lower() or "hey leonard" in text.lower():
			beginConversation()
	except sr.UnknownValueError:
		rospy.loginfo("Empty text - Could not recognise utterance")
	except sr.RequestError as e:
		rospy.loginfo("Could not request results from Google Speech Recognition Service; {0}".format(e))


def beginConversation():
	response = sendToDialogflow("Hello")

	with sr.Microphone() as source:
		listener.adjust_for_ambient_noise(source, duration = 0.3)
		speak(response.query_result.fulfillment_text)
		print("I'm listening")
		audio = listener.listen(source)
		rospy.loginfo("Captured audio. Processing...")

	try:
		speak(listener.recognize_google(audio))
		result = sendToDialogflow(request)
        if result.query_result.intent.display_name == "create-msg-task":
            createMsgTask(result)
        elif result.query_result.intent.display_name == "create-pkg-task":
            createPkgTask(result)
        else:
            speak(result.query_result.fulfillment_text)
	except sr.UnknownValueError:
		rospy.loginfo("Empty text - Could not recognise utterance")
		speak("Sorry, I didn't get that")
	except sr.RequestError as e:
		rospy.loginfo("Could not request results from Google Speech Recognition Service; {0}".format(e))


def speak(utterance):
	rospy.loginfo("Text to be spoken: {0}".format(utterance))
	engine.say(utterance)
	engine.runAndWait()


def setUpNode():
	rospy.init_node('Interaction', anonymous=True)
	initialise()

	while True:
		listenForCommand()



if __name__ == '__main__':
    try:
        setUpNode()
    except rospy.ROSInterruptException:
        pass