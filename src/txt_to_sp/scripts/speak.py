import pyttsx3 as tts
import rospy
from std_msgs.msg import String


#Global for tts Engine
engine = None

#Publish to inform done speaking the utterance
finishSpeaking = rospy.Publisher('done_speaking', String, queue_size=100)


def initialise():
	global engine
	rospy.loginfo("Initialising the text-to-speech engine")

	engine = tts.init()
	engine.setProperty('rate', 140) #Set rate of speech
	engine.setProperty('volume',1.0)

	rospy.loginfo("Text-to-Speech successfully configured")


def speak(utterance):
	rospy.loginfo("Text to be spoken: {0}".format(utterance.data))
	engine.say(utterance.data)
	engine.runAndWait()
	finishSpeaking.publish("done")


def setUpNode():
	rospy.init_node('tts', anonymous=True)
	rospy.Subscriber('speak_msg', String, speak)
	initialise()

	rospy.spin()


if __name__ == '__main__':
	setUpNode()

