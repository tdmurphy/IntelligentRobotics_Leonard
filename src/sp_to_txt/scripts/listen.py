import speech_recognition as sr
import rospy
from std_msgs.msg import String


#Global for speech recognition
listener = sr.Recognizer()
shouldListen = False

#Publish to the processed message
processedAudio = rospy.Publisher('user_speech', String, queue_size=100)


def processAudio():
	global shouldListen

	while shouldListen:
		rospy.loginfo("Begun listening")
		with sr.Microphone() as source:
			listener.adjust_for_ambient_noise(source, duration=1)
			rospy.loginfo("Node is listening")
			audio = listener.listen(source)
			rospy.loginfo("Captured audio. Processing...")
		try:
			text = listener.recognize_google(audio)
			rospy.loginfo("Audio processed as : " + text)
			processedAudio.publish(text)
			shouldListen = False
		except sr.UnknownValueError:
			rospy.loginfo("Empty text - Could not recognise utterance")
		except sr.RequestError as e:
			rospy.loginfo("Could not request results from Google Speech Recognition Service; {0}".format(e))


def start_listening(data):
	global shouldListen
	if data.data == "listen":
		shouldListen = True


def setUpNode():
	rospy.init_node('speech_recogition', anonymous=True)
	rospy.Subscriber('start_listening', String, start_listening)
	rospy.loginfo("Speech recognition node initialised")

	while True:
		processAudio()


if __name__ == '__main__':
	setUpNode()

