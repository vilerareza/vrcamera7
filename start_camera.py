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
serverHost = "192.168.36.23"
t_reconnection = 3
# Camera object
camera = Camera()
# Frame size
#frame_size = (640, 480)
frame_size = (1280, 720)
# Frame rate
frame_rate = 20
# Streaming output object
output = StreamingOutput()

# Servos
servoX = Servo(channel=0)
servoY = Servo(channel=1)

# Light
light = Light(pin = 17)


async def on_message(message):

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

    elif message['op'] == 'st':
        # Stream
        start = message['start']
        if start == True:
            # Start camera
            await camera.start_camera()
        else:
            # Stop camera
            status = await camera.stop_camera()
            print (status)


async def on_connect(websocket):
    global output

    async def receive(websocket):
        while True:
            try:
                message = await websocket.recv()
                await on_message(message)
                print (message)
            except websockets.ConnectionClosedOK:
                print ('closed receive')
                break
    
    def wait (output):
        with output.condition:
            output.condition.wait()
            return output.frame

    async def send(websocket):
        while True:
            try:
                print ('waiting')
                frame = await asyncio.to_thread(wait, output)
                await websocket.send(frame)
            except websockets.ConnectionClosedOK:
                print ('closed send')
                break

    path = websocket.path.split('/')
    socketType = path[1]
    print (f'Client connected, {websocket.path}, {socketType}')

    if socketType == 'frame':
        await send(websocket)
    elif socketType == 'control':
        await receive(websocket)
    elif socketType == 'transfer':
        pass


async def ws_to_client():
    print ('Listening ws from client')
    async with websockets.serve(on_connect, "0.0.0.0", 8000):
        await asyncio.Future()


async def ws_to_server(server_host):
    global output

    def wait (output):
        with output.condition:
            output.condition.wait()
            return output.frame

    while True:
        try:
            print ('Opening ws to server...')
            async with websockets.connect(f"ws://{server_host}:8000/ws/device/device1/") as websocket:
                while True:
                    print ('Waiting for signal form server')
                    data = await websocket.recv()
                    # Sending dummy data
                    if data == (b'1'):
                        #await websocket.send("Hello world!")
                        try:
                            frame = await asyncio.to_thread(wait, output)
                            await websocket.send(frame)
                            print ('frame sent')
                        except websockets.ConnectionClosedOK:
                            break
                        #await asyncio.sleep(1)
        except:
            print (f'Some issue on connection to server. Reconnecting in {t_reconnection} sec...')
            # RV: Please evaluate the implementation of await
            await asyncio.sleep(t_reconnection)
            continue


async def main():
    # Start camera
    task_camera = asyncio.create_task(camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate))
    # Open connection to server
    task_ws_server = asyncio.create_task(ws_to_server(serverHost))
    # Listening connection form client
    task_ws_client = asyncio.create_task(ws_to_client())
    await task_camera
    await task_ws_server
    await task_ws_client

asyncio.run (main())