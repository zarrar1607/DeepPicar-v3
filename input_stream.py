#!/usr/bin/python3
import os
import time
import atexit
import termios, fcntl, sys, os
import select

from multiprocessing import Process, Lock, Array, Value

# WEB INPUT
from http.server import BaseHTTPRequestHandler, HTTPServer
from functools import partial
import json

class input_stream:
    def __init__(self):
        self.buffer = ' '
        self.direction = 0.

    def read_inp():
        return self.buffer, self.direction

    def stop(self):
        return

    def __del__(self):
        self.stop()

class input_kbd(input_stream):
    def init(self):
        super().__init__()
        fd = sys.stdin.fileno()
        # save old state
        flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
        attrs_save = termios.tcgetattr(fd)
        # make raw - the way to do this comes from the termios(3) man page.
        attrs = list(attrs_save) # copy the stored version to update
        # iflag
        attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK 
                      | termios.ISTRIP | termios.INLCR | termios. IGNCR 
                      | termios.ICRNL | termios.IXON )
        # oflag
        attrs[1] &= ~termios.OPOST
        # cflag
        attrs[2] &= ~(termios.CSIZE | termios. PARENB)
        attrs[2] |= termios.CS8
        # lflag
        attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                      | termios.ISIG | termios.IEXTEN)
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        # turn off non-blocking
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
        # read a single keystroke
        return (flags_save, attrs_save)
    
    def deinit(self,state):
        fd = sys.stdin.fileno()
        # restore old state
        termios.tcsetattr(fd, termios.TCSAFLUSH, state[1])
        fcntl.fcntl(fd, fcntl.F_SETFL, state[0])
     
    def read_inp(self):
        state = self.init()    
        r, w, e = select.select([sys.stdin], [], [], 0.000)
        self.buffer = ' '
        for s in r:
            if s == sys.stdin:
                self.buffer = sys.stdin.read(1)
                break
        self.deinit(state)

        if self.buffer == 'j': # left
            self.direction = -1.0
        elif self.buffer == 'l': # right
            self.direction = 1.0
        elif self.buffer == 'k': # center
            self.direction = .0

        return self.buffer, self.direction


class input_gamepad(input_stream):
    def __init__(self):
        super().__init__()
        self.shared_arr = Array('d', [0.]*8) # joystick pos and other buttons and finish state
        #self.finish = Value('i', 1)
        self.lock=Lock()
        self.gamepad_process = Process(target=self.inputs_process, \
                args=(), daemon=True )#args=(self.shared_arr, self.finish, lock,))
        self.gamepad_process.start()

    def inputs_process(self): #shr_gamepad_state, finish, lock):
        import inputs
        pads = inputs.devices.gamepads
        if len(pads) == 0:
            raise Exception("Couldn't find any Gamepads!")

        #shr_gamepad_state, finish, lock = self.shared_arr, self.finish, self.lock
        shr_gamepad_state, lock = self.shared_arr, self.lock
        # Empty buffer
        gamepad_events = inputs.get_gamepad()
        print('Joystick is ready')

        disable_joystick=False
        while True: #finish.value != 0:
            gamepad_events = inputs.get_gamepad()
            if disable_joystick and time.time() - gamepad_disable_time > 0.3: # 300 ms
                disable_joystick = False
            lock.acquire()
            for event in gamepad_events:
                if not disable_joystick and event.ev_type == 'Absolute' and event.code == 'ABS_X':
                    val = int(event.state)
                    if val <= -256 or val >= 256: # calib, dead area
                        shr_gamepad_state[0] = val / 32768 #/ -32768 to 32767
                elif event.ev_type == 'Absolute' and event.code == 'ABS_HAT0Y':
                    if int(event.state) == -1:
                        shr_gamepad_state[1]=1.
                    elif int(event.state) == 1:
                        shr_gamepad_state[2]=1.
                elif event.ev_type == 'Absolute' and event.code == 'ABS_HAT0X':
                    if int(event.state) == -1:
                        shr_gamepad_state[0]= -1.
                    elif int(event.state) == 1:
                        shr_gamepad_state[0]= 1.
                    elif int(event.state) == 0:
                        shr_gamepad_state[0]= 0.
                elif event.ev_type == 'Key' and event.code == 'BTN_NORTH' and int(event.state) == 1:
                    shr_gamepad_state[3]=1. # stop
                elif event.ev_type == 'Key' and event.code == 'BTN_EAST' and int(event.state) == 1:
                    shr_gamepad_state[4]=1. # record
                elif event.ev_type == 'Key' and event.code == 'BTN_START' and int(event.state) == 1:
                    shr_gamepad_state[5]=1.
                elif event.ev_type == 'Key' and event.code == 'BTN_SELECT':
                    shr_gamepad_state[6]=1.
                    #finish.value=1
                elif event.ev_type == 'Key' and event.code == 'BTN_WEST' and int(event.state) == 1:
                    shr_gamepad_state[7]=1.
                elif event.ev_type == 'Key' and event.code == 'BTN_SOUTH' and int(event.state) == 1:
                    shr_gamepad_state[0]=0.
                    disable_joystick=True
                    gamepad_disable_time = time.time()
            #if shr_gamepad_state[0] < 32768//2 and shr_gamepad_state[0] > -32768//2:
            #    shr_gamepad_state[0] = 0. # dead area
            lock.release()

    def read_inp(self):
        self.buffer = ' '
        self.lock.acquire()
        if self.shared_arr[1] == 1.:
            self.shared_arr[1] = 0.
            self.buffer='a'
            #print ("accel")
        elif self.shared_arr[2] == 1.:
            self.shared_arr[2] = 0.
            self.buffer='z'
            #print ("reverse")
        elif self.shared_arr[3] == 1.:
            self.shared_arr[3] = 0.
            self.buffer='s'
            #print ("stop")
        elif self.shared_arr[4] == 1.:
            self.shared_arr[4] = 0.
            self.buffer='r'
            #print ("toggle record mode")
        elif self.shared_arr[5] == 1.:
            self.shared_arr[5] = 0.
            self.buffer='d'
            #print ("toggle DNN mode")
        elif self.shared_arr[6] == 1.:
            self.shared_arr[6] = 0.
            self.buffer='q'
            #self.finish.value = 0
        elif self.shared_arr[7] == 1.:
            self.shared_arr[7] = 0.
            self.buffer='t'
            #print ("toggle video mode")

        self.direction = self.shared_arr[0] 
        self.lock.release()

        return self.buffer, self.direction

    def stop(self):
        #self.finish.value = 0
        self.gamepad_process.terminate()


class input_web_handler(BaseHTTPRequestHandler):
    def __init__(self, shared_arr, lock, *args, **kwargs):
        self.shared_arr = shared_arr
        self.lock = lock
        super().__init__(*args, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, POST')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            #fps=30
            #period = 1./fps
            #end_time = time.time() + period
            try:
                #while True:
                frame = camera.read_frame()
                ret, frame = cv2.imencode('.jpg', frame)
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')

                    #tdiff = end_time - time.time()
                    #if tdiff > 0:
                    #    time.sleep(tdiff)
                    #end_time += period
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
        if self.path == '/actuate':
            self.send_response(301)
            self.end_headers()
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))

            data = json.loads(self.data_string)
            print (data)
            if data['params']['direction'] == 'left':
                self.shared_arr[0] = -1.
            elif data['params']['direction'] == 'center':
                self.shared_arr[0] = 0.
            elif data['params']['direction'] == 'right':
                self.shared_arr[0] = 1.
            elif data['params']['direction'] == 'forward':
                self.shared_arr[1] = 1.
            elif data['params']['direction'] == 'stop':
                self.shared_arr[3] = 1. 
            elif data['params']['direction'] == 'reverse':
                self.shared_arr[2] = 1.
            #TODO throttle
            #actuator.set_speed(data['params']['speed'])
        elif self.path == '/record':
            self.send_response(301)
            self.end_headers()
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))

            data = json.loads(self.data_string)
            print (data)

            self.shared_arr[4] = 1. 

            #if data['params']['action'] == 'begin':
            #    enable_record = True
            #if data['params']['action'] == 'finish':
            #    enable_record = False
            #    frame_id = 0

        elif self.path == '/upload':
            filename = "large-200x66x3.tflite"
            file_length = int(self.headers['Content-Length'])
            read = 0
            with open(filename, 'wb+') as output_file:
                output_file.write(self.rfile.read(file_length))
            self.send_response(201, 'Created')
            self.end_headers()
            reply_body = 'Saved "%s"\n' % filename
            self.wfile.write(reply_body.encode('utf-8'))

        elif self.path == '/dnn':
            self.send_response(301)
            self.end_headers()
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))

            data = json.loads(self.data_string)
            print (data)

            self.shared_arr[5] = 1. 
            #if data['params']['action'] == 'start':
            #    use_dnn = True
            #if data['params']['action'] == 'stop':
            #    use_dnn = False


# this takes the p
class input_web(input_stream):
    def __init__(self):
        self.shared_arr = Array('d', [0.]*8) # joystick pos and other buttons and finish state
        self.lock = Lock()

        self.ws_process = Process(target=self.web_server_process, \
                args=(), daemon=True )
        self.ws_process.start()

    def web_server_process(self):
        address = ('', 8000)
        handler = partial(input_web_handler, self.shared_arr, self.lock)
        server = HTTPServer(address, handler)
        server.serve_forever() # until terminated

    def read_inp(self):
        self.buffer = ' '
        self.lock.acquire()
        if self.shared_arr[1] == 1.:
            self.shared_arr[1] = 0.
            self.buffer='a'
            #print ("accel")
        elif self.shared_arr[2] == 1.:
            self.shared_arr[2] = 0.
            self.buffer='z'
            #print ("reverse")
        elif self.shared_arr[3] == 1.:
            self.shared_arr[3] = 0.
            self.buffer='s'
            #print ("stop")
        elif self.shared_arr[4] == 1.:
            self.shared_arr[4] = 0.
            self.buffer='r'
            #print ("toggle record mode")
        elif self.shared_arr[5] == 1.:
            self.shared_arr[5] = 0.
            self.buffer='d'
            #print ("toggle DNN mode")
        elif self.shared_arr[6] == 1.:
            self.shared_arr[6] = 0.
            self.buffer='q'
            #self.finish.value = 0
        elif self.shared_arr[7] == 1.:
            self.shared_arr[7] = 0.
            self.buffer='t'
            #print ("toggle video mode")

        self.direction = self.shared_arr[0] 
        self.lock.release()

        return self.buffer, self.direction

    def stop(self):
        self.ws_process.terminate()
