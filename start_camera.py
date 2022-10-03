
import asyncio
from threading import Condition, Lock
import websockets

from functools import partial
from camera import Camera
from streamingoutput import StreamingOutput
from servo import Servo
from light import Light
from threading import Thread
import json


# Server host
serverHost = "192.168.50.102:8000"
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
    global frames
    
    async def receive(websocket):
        while True:
            try:
                with frames[websocket.path].condition:
                    frames[websocket.path].content = await websocket.recv()
                    frames[websocket.path].condition.notify_all()
                    #print ('receive')
            except websockets.ConnectionClosedOK:
                break
    
    async def send(websocket):
        while True:
            try:
                with frames[websocket.path].condition:
                    frames[websocket.path].condition.wait()
                    await websocket.send(frames[websocket.path].content)
                    print ('send')
            except websockets.ConnectionClosedOK:
                break

    source, device = websocket.path.split('/')[0], websocket.path.split('/')[0]
    print (f'Connection request, {websocket.path}')
    frames [device] = Frame()
    if source == 'device':
        await receive(websocket)
    else:
        await send(websocket)

async def ws_to_client():
    async with websockets.serve(on_connect, "0.0.0.0", 8000):
        print ('starting server')
        await asyncio.Future()

async def ws_to_server(server_host):
    print ('Opening ws to server')
    async with websockets.connect(f"ws://{server_host}") as websocket:
        while True:
            print ('sending data to server')
            await websocket.send("Hello world!")
            await asyncio.sleep(1)

async def main():
    task1 = asyncio.create_task(ws_to_server(serverHost))
    #task2=asyncio.create_task(another_job())
    # task3=asyncio.create_task(start_client())
    # await task1
    # await task2
    # await task3
    # async with websockets.serve(on_connect, "0.0.0.0", 8000):
    #     await asyncio.Future()

asyncio.run (main())

