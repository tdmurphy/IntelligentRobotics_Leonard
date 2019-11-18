import speech_recognition as sr
import pyttsx3 as tts
import dialogflow_v2 as dialogflow
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
import rospy


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

		return response.query_result.fulfillment_text


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
		speak(response)
		audio = listener.listen(source)
		rospy.loginfo("Captured audio. Processing...")

	try:
		speak(listener.recognize_google(audio))
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