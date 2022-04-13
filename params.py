#!/usr/bin/env python
from __future__ import division

import os

##########################################################
# camera module selection
#   "camera-webcam" "camera-null"
##########################################################
camera="camera-null"

##########################################################
# actuator selection
#   "actuator-drv8835", "actuator-adafruit_hat"
#   "actuator-null"
##########################################################
actuator="actuator-null"

##########################################################
# model selection
#   "model-5conv_3fc"   <-- nvidia dave-2 model
##########################################################
model="model-5conv_3fc"

##########################################################
# input config 
##########################################################
img_height = 66
img_width = 200
img_channels = 3

##########################################################
# directories
##########################################################
save_dir = os.path.abspath('models')
data_dir = os.path.abspath('epochs')
out_dir = os.path.abspath('output')

if not os.path.isdir(data_dir):
    os.makedirs(data_dir)
if not os.path.isdir(out_dir):
    os.makedirs(out_dir)
