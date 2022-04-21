#!/usr/bin/python
import os
import time
import atexit
import cv2
import math
import numpy as np
import sys
import params
import argparse

from PIL import Image
from PIL import ImageDraw
import input_kbd

##########################################################
# import deeppicar's sensor/actuator modules
##########################################################
camera   = __import__(params.camera)
actuator = __import__(params.actuator)

##########################################################
# global variable initialization
##########################################################
use_dnn = False
use_thread = True
view_video = False
fpv_video = False
enable_record = False

cfg_cam_res = (320, 240)
cfg_cam_fps = 30
cfg_throttle = 50 # 50% power.

frame_id = 0
angle = 0.0
period = 0.05 # sec (=50ms)

##########################################################
# local functions
##########################################################
def deg2rad(deg):
    return deg * math.pi / 180.0
def rad2deg(rad):
    return 180.0 * rad / math.pi

def g_tick():
    t = time.time()
    count = 0
    while True:
        count += 1
        yield max(t + count*period - time.time(),0)

def turn_off():
    actuator.stop()
    camera.stop()
    if frame_id > 0:
        keyfile.close()
        vidfile.release()

def preprocess(img):
    img = cv2.resize(img, (params.img_width, params.img_height))
    # Convert to grayscale and readd channel dimension
    if params.img_channels == 1:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = np.reshape(img, (params.img_height, params.img_width, params.img_channels))
    img = img / 255.
    return img

def overlay_image(l_img, s_img, x_offset, y_offset):
    assert y_offset + s_img.shape[0] <= l_img.shape[0]
    assert x_offset + s_img.shape[1] <= l_img.shape[1]

    l_img = l_img.copy()
    for c in range(0, 3):
        l_img[y_offset:y_offset+s_img.shape[0],
              x_offset:x_offset+s_img.shape[1], c] = (
                  s_img[:,:,c] * (s_img[:,:,3]/255.0) +
                  l_img[y_offset:y_offset+s_img.shape[0],
                        x_offset:x_offset+s_img.shape[1], c] *
                  (1.0 - s_img[:,:,3]/255.0))
    return l_img

##########################################################
# program begins
##########################################################

parser = argparse.ArgumentParser(description='DeepPicar main')
parser.add_argument("-d", "--dnn", help="Enable DNN", action="store_true")
parser.add_argument("-t", "--throttle", help="throttle percent. [0-100]%", type=int)
parser.add_argument("-n", "--ncpu", help="number of cores to use.", type=int, default=1)
parser.add_argument("-f", "--fpvvideo", help="Take FPV video of DNN driving", action="store_true")
args = parser.parse_args()

if args.dnn:
    print ("DNN is on")
    use_dnn = True
if args.throttle:
    cfg_throttle = args.throttle
    print ("throttle = %d pct" % (args.throttle))
if args.fpvvideo:
    fpv_video = True


##########################################################
# import deeppicar's DNN model
##########################################################
print ("Loading model: " + params.model_file)
try:
    # Import TFLite interpreter from tflite_runtime package if it's available.
    from tflite_runtime.interpreter import Interpreter
    interpreter = Interpreter(params.model_file+'.tflite', num_threads=args.ncpu)
except ImportError:
    # If not, fallback to use the TFLite interpreter from the full TF package.
    import tensorflow as tf
    interpreter = tf.lite.Interpreter(model_path=params.model_file+'.tflite', num_threads=args.ncpu)

interpreter.allocate_tensors()
input_index = interpreter.get_input_details()[0]["index"]
output_index = interpreter.get_output_details()[0]["index"]

# initlaize deeppicar modules
actuator.init(cfg_throttle)
camera.init(res=cfg_cam_res, fps=cfg_cam_fps, threading=use_thread)
atexit.register(turn_off)

g = g_tick()
start_ts = time.time()

frame_arr = []
angle_arr = []
# enter main loop
while True:
    if use_thread:
        time.sleep(next(g))
    frame = camera.read_frame()
    ts = time.time()

    if view_video == True:
        cv2.imshow('frame', frame)
        ch = cv2.waitKey(1) & 0xFF
    else:
        ch = ord(input_kbd.read_single_keypress())

    if ch == ord('j'): # left 
        angle = deg2rad(-30)
        actuator.left()
        print ("left")
    elif ch == ord('k'): # center 
        angle = deg2rad(0)
        actuator.center()
        print ("center")
    elif ch == ord('l'): # right
        angle = deg2rad(30)
        actuator.right()
        print ("right")
    elif ch == ord('a'):
        actuator.ffw()
        print ("accel")
    elif ch == ord('s'):
        actuator.stop()
        print ("stop")
    elif ch == ord('z'):
        actuator.rew()
        print ("reverse")
    elif ch == ord('r'):
        print ("toggle record mode")
        enable_record = not enable_record
    elif ch == ord('t'):
        print ("toggle video mode")
        view_video = not view_video
    elif ch == ord('d'):
        print ("toggle DNN mode")
        use_dnn = not use_dnn
    elif ch == ord('q'):
        break
    elif use_dnn == True:
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

    dur = time.time() - ts
    if dur > period:
        print("%.3f: took %d ms - deadline miss."
              % (ts - start_ts, int(dur * 1000)))
    else:
        print("%.3f: took %d ms" % (ts - start_ts, int(dur * 1000)))

    if enable_record == True and frame_id == 0:
        # create files for data recording
        keyfile = open(params.rec_csv_file, 'w+')
        keyfile.write("ts_micro,frame,wheel\n")
        try:
            fourcc = cv2.cv.CV_FOURCC(*'XVID')
        except AttributeError as e:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        vidfile = cv2.VideoWriter(params.rec_vid_file, fourcc,
                                cfg_cam_fps, cfg_cam_res)
    if enable_record == True and frame is not None:
        # increase frame_id
        frame_id += 1

        # write input (angle)
        str = "{},{},{}\n".format(int(ts*1000), frame_id, angle)
        keyfile.write(str)

        if use_dnn and fpv_video:
            textColor = (255,255,255)
            bgColor = (0,0,0)
            newImage = Image.new('RGBA', (100, 20), bgColor)
            drawer = ImageDraw.Draw(newImage)
            drawer.text((0, 0), "Frame #{}".format(frame_id), fill=textColor)
            drawer.text((0, 10), "Angle:{}".format(angle), fill=textColor)
            newImage = cv2.cvtColor(np.array(newImage), cv2.COLOR_BGR2RGBA)
            frame = overlay_image(frame,
                                     newImage,
                                     x_offset = 0, y_offset = 0)
        # write video stream
        vidfile.write(frame)
        #img_name = "cal_images/opencv_frame_{}.png".format(frame_id)
        #cv2.imwrite(img_name, frame)
        if frame_id >= 1000:
            print ("recorded 1000 frames")
            break
        print ("%.3f %d %.3f %d(ms)" %
           (ts, frame_id, angle, int((time.time() - ts)*1000)))

print ("Finish..")
turn_off()
