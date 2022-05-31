import io
import cv2
camera   = __import__("camera-webcam")
actuator = __import__("actuator-drv8835")
import logging
import socketserver
from threading import Condition
from http import server
import json
import os
import time
import math
import numpy as np


PAGE="""\
<html>
<head>
<title>WebCam MJPEG streaming</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="320" height="240" />
</body>
</html>
"""
def deg2rad(deg):
    return deg * math.pi / 180.0
def rad2deg(rad):
    return 180.0 * rad / math.pi

def preprocess(img):
    img = cv2.resize(img, (200, 66))
    # Convert to grayscale and readd channel dimension
    if params.img_channels == 1:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = np.reshape(img, (66, 200, 3))
    img = img / 255.
    return img

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, POST')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    def do_GET(self):
        global frame
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    frame = camera.read_frame()
                    ret, frame = cv2.imencode('.jpg', frame)
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path == '/out-key.csv':
            f = open(os.curdir + self.path, 'rb')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        elif self.path == '/out-video.avi':
            f = open(os.curdir + self.path, 'rb')
            self.send_response(200)
            self.send_header('Content-Type', 'video/x-msvideo')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        global frame
        global enable_record
        global frame_id
        global angle
        global ts
        global use_dnn
        if self.path == '/actuate':
            self.send_response(301)
            self.end_headers()
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))

            data = json.loads(self.data_string)
            print (data)
            if data['params']['direction'] == 'left':
                angle = deg2rad(-30)
                print("left")
                actuator.left()
            if data['params']['direction'] == 'center':
                angle = deg2rad(0)
                print("center")
                actuator.center()
            if data['params']['direction'] == 'right':
                angle = deg2rad(30)
                print("right")
                actuator.right()
            if data['params']['direction'] == 'forward':
                print ("accel")
                actuator.ffw()
            if data['params']['direction'] == 'stop':
                print ("stop")
                actuator.stop()
            if data['params']['direction'] == 'reverse':
                print ("reverse")
                actuator.rew()
        if self.path == '/record':
            self.send_response(301)
            self.end_headers()
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))

            data = json.loads(self.data_string)
            print (data)

            if data['params']['action'] == 'begin':
                enable_record = True
            if data['params']['action'] == 'finish':
                
                enable_record = False
                frame_id = 0
            
            while enable_record == True:
                if frame_id == 0:
                    # create files for data recording
                    keyfile = open("out-key.csv", 'w+')
                    keyfile.write("ts_micro,frame,wheel\n")
                    try:
                        fourcc = cv2.cv.CV_FOURCC(*'XVID')
                    except AttributeError as e:
                        fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    vidfile = cv2.VideoWriter("out-video.avi", fourcc,
                                            30, (320, 240))
                if frame is not None:
                    # increase frame_id
                    frame_id += 1

                    # write input (angle)
                    str = "{},{},{}\n".format(int(ts*1000), frame_id, angle)
                    keyfile.write(str)

                    # write video stream
                    frame = camera.read_frame()
                    vidfile.write(frame)
                    print ("%.3f %d %.3f %d(ms)" %
                    (ts, frame_id, angle, int((time.time() - ts)*1000)))
        if self.path == '/upload':
            filename = "large-200x66x3.tflite"
            file_length = int(self.headers['Content-Length'])
            read = 0
            with open(filename, 'wb+') as output_file:
                output_file.write(self.rfile.read(file_length))
            self.send_response(201, 'Created')
            self.end_headers()
            reply_body = 'Saved "%s"\n' % filename
            self.wfile.write(reply_body.encode('utf-8'))

        if self.path == '/dnn':
            self.send_response(301)
            self.end_headers()
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))

            data = json.loads(self.data_string)
            print (data)

            if data['params']['action'] == 'start':
                use_dnn = True
            if data['params']['action'] == 'stop':
                use_dnn = False
            try:
                # Import TFLite interpreter from tflite_runtime package if it's available.
                from tflite_runtime.interpreter import Interpreter
                interpreter = Interpreter('large-200x66x3.tflite', num_threads=2)
            except ImportError:
                # If not, fallback to use the TFLite interpreter from the full TF package.
                import tensorflow as tf
                interpreter = tf.lite.Interpreter(model_path='large-200x66x3.tflite', num_threads=2)

            interpreter.allocate_tensors()
            input_index = interpreter.get_input_details()[0]["index"]
            output_index = interpreter.get_output_details()[0]["index"]

            while use_dnn == True:
                # 1. machine input
                img = preprocess(frame)
                img = np.expand_dims(img, axis=0).astype(np.float32)
                interpreter.set_tensor(input_index, img)
                interpreter.invoke()
                angle = interpreter.get_tensor(output_index)[0][0]
                degree = rad2deg(angle)
                if degree <= -15:
                    actuator.left()
                    print ("left (CPU)")
                elif degree < 15 and degree > -15:
                    actuator.center()
                    print ("center (CPU)")
                elif degree >= 15:
                    actuator.right()
                    print ("right (CPU)")




class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    actuator.init(50)
    camera.init()
    enable_record = False
    frame_id = 0
    angle = 0.0
    ts = time.time()
    use_dnn = False

    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop()
