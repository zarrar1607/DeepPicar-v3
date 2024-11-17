# DeepPicar

DeepPicar is a low-cost autonomous RC car platform using a deep
convolutional neural network (CNN). DeepPicar is a small scale replication
of [NVIDIA's real self-driving car called DAVE-2](https://developer.nvidia.com/blog/deep-learning-self-driving-cars/), which drove on public
roads using a CNN. DeepPicar uses the same CNN architecture of NVIDIA's
DAVE-2 and can drive itself in real-time locally on a Raspberry Pi.

## Build instructions video

https://www.youtube.com/watch?v=X1DDN9jcwjk

## Setup

Install DeepPicar.

    $ sudo apt install libatlas-base-dev
    $ git clone --depth=1 https://github.com/CSL-KU/DeepPicar-v3 -b devel
    $ cd DeepPicar-v3 
    $ sudo pip3 install -r requirements.txt

Edit `params.py` to select correct camera and actuator drivers. 
The setting below represents the standard webcam and drv8835 configuration, for example. 

    camera="camera-webcam"
    actuator="actuator-drv8835"
    
In addition, you need to install necessary python drivers. For polulu drv8835, do following.

    $ git clone https://github.com/pololu/drv8835-motor-driver-rpi.git
    $ cd drv8835-motor-driver-rpi
    $ sudo python3 setup.py install

Also install the python package "inputs" if you would like to to use Logitech F710 gamepad for data collection.

    $ git clone https://github.com/zeth/inputs.git
    $ cd inputs
    $ sudo python setup.py install
    
Lastly install node.js and serve package to enable web interface

    $ sudo apt install nodejs npm
    $ npm i serve
    
## Manual control and Data collection

To start the backend server

    $ sudo nice --20 python3 deeppicar.py -w -n 4 -f 30

To start the web client

    $ npx serve web/dist/ 

Using the web client, you can control the car, record and download data, upload the model, and run the DNN

Keyboard controls
* **'UpArrow'**: move forward 
* **'DownArrow'**: move backward
* **'Space'**: stop
* **'LeftArrow'**: turn left
* **'RightArrow'**: turn right 

Use the keys to manually control the car. Once you become confident in controlling the car, collect the data to be used for training the DNN model. 

The data collection can be enabled and stopped by pressing `Finish` button. Once recording is enabled, the video feed and the corresponding control inputs are stored in `out-video.avi` and `out-key.csv` files, respectively. Later, we will use these files for training. It can be downloaded with the download button.

Each recording attempt with overwrite the previous

Rename recorded avi and csv files to out-video-XX.avi and out-video-XX.csv where XX with appropriate numbers. 

Compress all the recorded files into a single zip file, say Dataset.zip for Colab.

    $ zip Dataset.zip out-*
    updating: out-key.csv (deflated 81%)
    updating: out-video.avi (deflated 3%)

## Train the model
    
Open the colab notebook. Following the notebook, you will upload the dataset to the colab, train the model, and download the model back to your PC. 

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CSL-KU/DeepPicar-v3/blob/devel/RunAll.ipynb)

After you are done trainig, you need to copy the trained tflite model file (`large-200x66x3.tflite` by default) to the Pi using the web uploader

## Autonomous control

Copy the trained model to the DeepPicar. 

Enable autonomous driving through the `Start DNN` button.

## Driving Videos

[![DeepPicar Driving](http://img.youtube.com/vi/SrS5iQV2Pfo/0.jpg)](http://www.youtube.com/watch?v=SrS5iQV2Pfo "DeepPicar_Video")

Some other examples of the DeepPicar driving can be found at: https://photos.app.goo.gl/q40QFieD5iI9yXU42

## Fining Tuning
To fine-tune the model, use the Jupyter Notebook "[Retrain and Transfer Learn.ipynb](https://github.com/zarrar1607/DeepPicar-v3/blob/main/Retrain_and_Transfer_Learn.ipynb)". provided in the DeepPiCar repository. This notebook includes step-by-step instructions for the fine-tuning process.

### Data Collection
You will need to record three additional laps of data in varying environmental conditions. These conditions can include:
<ul>
<li>Different lighting (e.g., dim or bright light settings).</li>
<li>A new track layout.</li>
<li>Reversing the car's direction on the same track.</li>
<li>This additional data is essential to help the model adapt and generalize to new settings.</li>
</ul>

### Fine-Tuning Process
The key idea behind fine-tuning is to freeze two layers of the existing model while training the remaining layers on the new dataset. By doing so, the model retains its performance in the original environment while adapting to the new conditions, thus improving its generalizability.

### Installation

1. Install TensorFlow: Use the command ```pip install –no-cache-dir tensorflow``` to in-
stall TensorFlow2.

2. Upgrade Packages: Use the command below to upgrade outdated packages. For more de-
tails, see 3.
```pip3 list -- outdated -- format = freeze | grep -v ’^\ -e ’ | cut -d = -f 1 | xargs - n1 pip3 install -U```

3. Install Compatible Flatbuffers: The following version is necessary to ensure compatibility
with TensorFlow Lite.
```pip install flatbuffers ==2.0```

4. Increase Swap File Size:
The default swap size and available RAM may not be sufficient for training. Follow the
instructions on [website](https://nebl.io/neblio-university/enabling-increasing-raspberry-pi-swap/increasing Rasp-
berry Pi swap size) to enable on-device training effectively

### Demonstration
For a quick demonstration of the fine-tuning process and results, watch this [video](https://youtube.com/shorts/gDC6Y_qBBx4?si=O_FPp69FHaZu_Moy).
