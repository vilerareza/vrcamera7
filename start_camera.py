import os
import asyncio
import websockets
from functools import partial
from camera import Camera
from streamingoutput import StreamingOutput
from servo import Servo
from light import Light
from threading import Thread, Condition
import json
from get_rec_file import get_rec_file


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
is_recording = True

# Websockets
ws_download = None

# Servos
servoX = Servo(channel=0)
servoY = Servo(channel=1)

# Light
light = Light(pin = 17)

# Recording files directory
rec_path = '../rec/'
# Recording files directory
transfer_buffer_path = '../mp4buf/'

# Rec file reading sync condition
condition_send = Condition()
# Rec file bytes
rec_file_bytes = None


async def on_message(message):

    global is_recording
    global rec_path
    global transfer_buffer_path
    global condition_send
    global rec_file_bytes
    
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
            is_recording = False
            # Notify socket to not waiting the streaming output buffer
            with output.condition:
                output.condition.notify_all()
            with condition_send:
                condition_send.notify_all()

    elif message['op'] == 'download':
        # Client app request rec file download

        files = []
        for root,_,files_ in os.walk(rec_path):
            for file in files_:
                files.append(os.path.join(root, file))
        the_file = files[0]

        # Convert to MP4        
        result, mp4file = get_rec_file(the_file, transfer_buffer_path)
        
        if result:
            
            # Read the file
            print (os.path.getsize(mp4file))
            with open (mp4file, 'rb') as file_obj:
                rec_file_bytes = file_obj.read()

        else:
            print ('Conversion to mp4 failed. Nothing is transferred...')

        with condition_send:
            condition_send.notify_all()


async def on_connect(websocket):
    
    # Camera streaming output object
    global output
    # Websocket for downloading recording file
    global ws_download
    
    # Async function for control websocket
    async def receive(websocket):
        
        while True:
            try:
                message = await websocket.recv()
                await on_message(message)
                print (message)
            except websockets.ConnectionClosedOK:
                print ('closed receive')
                break
    
    # Async function for streaming websocket
    async def send(websocket):
        
        global output
        global is_recording
        global frame_size
        global frame_rate

        def __wait (output):
            with output.condition:
                output.condition.wait()
                return output.frame

        if not is_recording:
            # If camera is stopped then start it
            try:
                # Start camera (no need to await for this task)
                task_camera = asyncio.create_task(camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate))
                is_recording = True
                
            except Exception as e:
                print (e)

        while is_recording:
            # Continue streaming while recording flag is set
            try:
                frame = await asyncio.to_thread(__wait, output)
                await websocket.send(frame)
            except websockets.ConnectionClosedOK:
                print ('closed send')
                break

    # Async function for download websocket to send rec file to the client app
    async def send_rec_file(websocket):
    
        def __wait_file_bytes():

            # Rec file sync condition
            global condition_send
            # Rec file bytes
            global rec_file_bytes

            with condition_send:
                condition_send.wait()
            return rec_file_bytes

        try:
            # Wait until the rec file bytes is read and ready to be sent
            file_bytes = await asyncio.to_thread(__wait_file_bytes)
            # Send the rec file bytes via download websocket
            await websocket.send(file_bytes)
            print ('rec file sent')
        except websockets.ConnectionClosedOK:
            print ('closed send')


    # Determine the type of incoming websocket request
    path = websocket.path.split('/')
    socketType = path[1]
    print (f'Client connected, {websocket.path}, {socketType}')

    if socketType == 'frame':
        await send(websocket)
    elif socketType == 'control':
        await receive(websocket)
    elif socketType == 'download':
        await send_rec_file(websocket)


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
    print ('end')

asyncio.run (main())