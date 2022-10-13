
import asyncio
import websockets

from functools import partial
from camera import Camera
from streamingoutput import StreamingOutput
from servo import Servo
from light import Light
from threading import Thread
import json


# Server host
serverHost = "192.168.19.102"
# Camera object
camera = Camera()
# Frame size
frame_size = (640, 480)
# Frame rate
frame_rate = 20
# Streaming output object
output = StreamingOutput()
# Servos
servoX = Servo(channel=0)
servoY = Servo(channel=1)
# Light
light = Light(pin = 17)

# async def on_message(message):
#     message = json.loads(message)
#     if message['op'] == 'mv':
#         # Movement
#         dir = message['dir']
#         if dir == 'L':
#             # Left
#             Thread(target = partial(servoX.start_move, distance = +(message['dist']))).start()
#         elif dir == 'R':
#             # Right
#             Thread(target = partial(servoX.start_move, distance = -(message['dist']))).start()
#         elif dir == 'D':
#             # Down
#             Thread(target = partial(servoY.start_move, distance = +(message['dist']))).start()
#         elif dir == 'U':
#             # Up
#             Thread(target = partial(servoY.start_move, distance = -(message['dist']))).start()
#         elif dir == 'C':
#             # Centering
#             Thread(target = servoX.center).start()
#             Thread(target = servoY.center).start()
            
#     elif message['op'] == 'lt':
#         # Light
#         on = message['on']
#         if on == True:
#             Thread(target = light.led_on).start()
#         else:
#             Thread(target = light.led_off).start()

def on_message(message):
    message = json.loads(message)
    if message['op'] == 'mv':
        # Movement
        dir = message['dir']
        if dir == 'L':
            # Left
            servoX.start_move(distance = +(message['dist']))
        elif dir == 'R':
            # Right
            servoX.start_move(distance = -(message['dist']))
        elif dir == 'D':
            # Down
            servoY.start_move(distance = +(message['dist']))
        elif dir == 'U':
            # Up
            servoY.start_move(distance = -(message['dist']))
        elif dir == 'C':
            # Centering
            servoX.center()
            servoY.center()
            
    elif message['op'] == 'lt':
        # Light
        on = message['on']
        if on == True:
            light.led_on()
        else:
            light.led_off()

async def on_connect(websocket):
    global output

    async def receive(websocket):
        while True:
            try:
                message = await websocket.recv()
                on_message(message)
                print (message)
            except websockets.ConnectionClosedOK:
                print ('closed')
                break
    
    def wait (output):
        with output.condition:
            output.condition.wait()
            return output.frame

    async def send(websocket):
        while True:
            try:
                frame = await asyncio.to_thread(wait, output)
                await websocket.send(frame)
            except websockets.ConnectionClosedOK:
                break

    path = websocket.path.split('/')
    socketType = path[1]
    print (f'Client connected, {websocket.path}, {socketType}')

    if socketType == 'frame':
        await send(websocket)
    elif socketType == 'control':
        await receive(websocket)

async def ws_to_client():
    print ('Listening ws from client')
    async with websockets.serve(on_connect, "0.0.0.0", 8000):
        await asyncio.Future()

async def ws_to_server(server_host):
    print ('Opening ws to server...')
    async with websockets.connect(f"ws://{server_host}:8000/ws/device/device1/") as websocket:
        while True:
            # Sending dummy data
            await websocket.send("Hello world!")
            await asyncio.sleep(1)

async def main():
    # Start camera
    task_camera = asyncio.create_task(camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate))
    # Open connection to server
    task_ws_server = asyncio.create_task(ws_to_server(serverHost))
    # Listening connection form client
    task_ws_client = asyncio.create_task(ws_to_client())
    #task_ws_client_control = asyncio.create_task(ws_to_client_control())
    await task_camera
    await task_ws_server
    await task_ws_client
    #await task_ws_client_control

asyncio.run (main())