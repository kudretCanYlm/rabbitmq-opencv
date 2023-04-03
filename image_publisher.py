import os
from matplotlib import pyplot as plt
import rabbitpy
import glob
import base64
from Utils import get_channel, get_conn
import numpy as np
import struct


queue_name = 'response-queue-%s' % os.getpid()
response_queue = rabbitpy.Queue(get_channel(),
                                queue_name,
                                auto_delete=True,
                                durable=False,
                                exclusive=True)

if response_queue.declare():
    print('Response queue declared')
if response_queue.bind('rpc-replies', queue_name):
    print('Response queue bound')

cv_img = []
for name in glob.glob("images/*.jpg"):

    with open(name, "rb") as fid:
        image = fid.read()
        #print(image)
        cv_img.append((image,name))


for image in enumerate(cv_img):

    #print(name)
    print('Sending request for image #'+image[1][1])
    
    message = rabbitpy.Message(get_channel(),
                                #codecs.encode(pickle.dumps(image[1][0], protocol=pickle.HIGHEST_PROTOCOL), "base64"),
                                base64.b64encode(image[1][0]),
                                {   
                                    'content_type':"jpg",
                                    'correlation_id': str(image[1][1]),
                                    'reply_to': queue_name
                                },
                                opinionated=True
                                )
    
    message.publish('direct-rpc-requests', 'detect-faces')
    print("published")

def convert_string_to_bytes(string):
    bytes = b''
    for i in string:
        bytes += struct.pack("B", ord(i))
    return bytes

for message in response_queue.consume():
    # show image
    #print(message.body)
    #img=imread(io.BytesIO(base64.b64decode(message.body)))
    #print(img)
    #img = imread(io.BytesIO(base64.b64decode(message.body)))
    #print(message.body)
    #imgdata = base64.b64decode(message.body)
    img_byte_arr=base64.b64decode(message.body)
    string_size=str(message.properties["headers"]["img_size"])
    string_size=string_size.split("(")[1].split(")")[0].split(", ")
    print(string_size)
    

    #print(list(img_byte_arr) )
    array_lst=list(img_byte_arr)
    arr=np.array(array_lst)
    a=int(string_size[0])
    b=int(string_size[1])
    c=int(string_size[2])
    
    new_arrr=np.reshape(arr,(a,b,c))
    print(new_arrr)
    
    plt.imshow(new_arrr)
    plt.show()

    #cv2.imshow("Test",im_rgb)
    #cv2.waitKey(10000)
    message.ack()


get_channel().close()
get_conn().close()