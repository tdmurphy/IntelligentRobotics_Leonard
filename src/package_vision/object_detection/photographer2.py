import os
import cv2
import datetime
import time
from pynput.keyboard import Key, Listener
import threading

now = datetime.datetime.now()
stamp = now.strftime("%H:%M:%S-")
print(stamp)

camera = cv2.VideoCapture(2)
count = 0


def on_press(key):
    global count
    if str(key) == "'s'":
        print('save')
        path = os.path.join("./images/", image_type, stamp+'frame{:d}.jpg'.format(count))
	ret, frame = camera.read()
        cv2.imwrite(path, frame)
        count+=1

def on_release(key):
    if key == Key.esc:
        # Stop listener
        cv2.destroyAllWindows()
        return False
		
if __name__ == "__main__":
    global image_type
    image_type = sys.argv[1]
    #image_type = 'test'

    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()


	

