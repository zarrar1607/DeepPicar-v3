#!/usr/bin/env python
##########################################################
# camera module selection
#   "camera-webcam" "camera-null"
##########################################################
camera="camera-webcam"

##########################################################
# actuator selection
#   "actuator-drv8835", "actuator-adafruit_hat"
#   "actuator-null"
##########################################################
actuator="actuator-drv8835"

##########################################################
# model selection
#   "model_large"   <-- nvidia dave-2 model
##########################################################
model_name = "model_large"
img_width = 200
img_height = 66
img_channels = 3
model_file = "models/{}-{}x{}x{}".format(model_name[6:], img_width, img_height, img_channels)

##########################################################
# input config 
##########################################################
img_height = 66
img_width = 200
img_channels = 3
