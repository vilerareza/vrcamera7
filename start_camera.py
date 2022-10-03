from functools import partial
from camera import Camera
from streamingoutput import StreamingOutput
from servo import Servo
from light import Light
from threading import Thread
import json
import websocket
import subprocess

# Server host
serverHost = "192.168.50.119:8000"
# Camera object
camera = Camera()
# Frame size
frame_size = (640, 480)
# Frame rate
frame_rate = 5
# Streaming output object
output = StreamingOutput()
# Servos
servoX = Servo(channel=0)
servoY = Servo(channel=1)
# Light
light = Light(pin = 17)

def on_message(wsapp, message):
    message = json.loads(message)
    if message['op'] == 'mv':
        # Movement
        dir = message['dir']
        if dir == 'L':
            # Left
            Thread(target = partial(servoX.start_move, distance = +(message['dist']))).start()
        elif dir == 'R':
            # Right
            Thread(target = partial(servoX.start_move, distance = -(message['dist']))).start()
        elif dir == 'D':
            # Down
            Thread(target = partial(servoY.start_move, distance = +(message['dist']))).start()
        elif dir == 'U':
            # Up
            Thread(target = partial(servoY.start_move, distance = -(message['dist']))).start()
        elif dir == 'C':
            # Centering
            Thread(target = servoX.center).start()
            Thread(target = servoY.center).start()
            
    elif message['op'] == 'lt':
        # Light
        on = message['on']
        if on == True:
            Thread(target = light.led_on).start()
        else:
            Thread(target = light.led_off).start()

try:
    # Update the status LED to amber
    #Thread(target = partial(subprocess.run, ['python','rgbled.py','[35,10,0]'])).start()
    # Start camera
    #camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)
    
    # Websocket App: Used for receiving control command from server
    # wsapp = websocket.WebSocketApp(f"ws://{serverHost}/ws/control/device1/", on_message=on_message)
    # try:
    #     # Run the websocket in different thread
    #     wst = Thread(target = wsapp.run_forever)
    #     wst.start()
    # except Exception as e:
    #     print (f'{e}: Failed starting websocketapp connection. closing connection')
    #     wsapp.close()
    #     wst = None
    
    # Websocket: Used for sending frames to server
    ws = websocket.WebSocket()
    ws.connect(f"ws://{serverHost}/ws/frame/device1/")
    # Update the status LED to blue: Connected to server
    #Thread(target = partial(subprocess.run, ['python','rgbled.py','[10,10,35]'])).start()
    # while True:
    #     with output.condition:
    #         output.condition.wait()
    #         frame = output.frame
    #         ws.send(frame, opcode=2)

except Exception as e:
    pass
    # Update the status LED to red: Exception occur
    #Thread(target = partial(subprocess.run, ['python','rgbled.py','[25,0,0]'])).start()
    #print (f'{e}: Camera Starting Error')

finally:
    pass
    # Update the status LED to red: End
    #Thread(target = partial(subprocess.run, ['python','rgbled.py','[25,0,0]'])).start()
