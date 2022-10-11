
import asyncio
from asyncio import Condition
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

async def on_message(wsapp, message):
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


async def on_connect(websocket):
    global output
    print ('Client connected')

    async def receive(websocket):
        print ('receive')
        async for message in websocket:
            print (message)
        # while True:
        #     print ('receiving')
        #     try:
        #         message = await websocket.recv()
        #     except websockets.ConnectionClosedOK:
        #         break
        #     print (message)
    
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

    await send(websocket)
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
    await task_camera
    await task_ws_server
    await task_ws_client

asyncio.run (main())