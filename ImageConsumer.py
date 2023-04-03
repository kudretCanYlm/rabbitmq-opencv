import base64
import rabbitpy
import os
import cv2
from imageio import imread
import io

from Utils import get_channel

queue_name='rpc-worker-%s' % os.getpid()
queue=rabbitpy.Queue(get_channel(),queue_name,auto_delete=True,durable=False,exclusive=True)

if queue.declare():
    print('Worker queue declared')

if queue.bind("direct-rpc-requests",'detect-faces'):
    print('Worker queue bound')

#PROCESSING AN IMAGE MESSAGE
def detect_face_from_image(img):
    
    # Load the cascade
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    
    # Convert into grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    #
    ## Draw rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    
    return img;


#CONSUMING THE RPC REQUESTS
for message in queue.consume_messages():
    #duration = (time.time() - int(message.properties['timestamp'].strftime('%s')))
    #print('Received RPC request published %.2f seconds ago' % duration)
    print("processing :"+message.properties['correlation_id'])

    img = imread(io.BytesIO(base64.b64decode(message.body)))
    print(img)

    #SENDING THE RESULT BACK

    body=detect_face_from_image(img);

    properties = {
                'app_id': 'Melih bey anime',
                'content_type': message.properties['content_type'],
                'correlation_id': message.properties['correlation_id'],
                'headers': {
                    'first_publish':message.properties['timestamp'],
                    "img_size":str(body.shape)
                }
            }

    #cv2.imshow("Test",body)
    #cv2.waitKey(10000)

    #body= json.dumps(body)
    response = rabbitpy.Message(get_channel(),base64.b64encode(body), properties)
    #response = rabbitpy.Message(get_channel(), codecs.encode(pickle.dumps(body, protocol=pickle.HIGHEST_PROTOCOL), "base64"), properties)
    response.publish('rpc-replies', message.properties['reply_to'])
    message.ack()


