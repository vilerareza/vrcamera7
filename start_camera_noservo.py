import os
import asyncio
import websockets
from camera import Camera
from streamingoutput2 import StreamingOutput2
from light import Light
from indicator import Indicator
import json
from get_rec_file import get_rec_file
import base64

import time


async def on_control(message):
    # Callback function for control message receved by control websocket

    global is_recording
    global light
    global rec_path
    global mp4_buffer_path
    global rec_file_dict
    
    message = json.loads(message)
    
    if message['op'] == 'lt':
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

    elif message['op'] == 'rec_info':
        # Client app request list of recording files

        files = []
        for root,_,files_ in os.walk(rec_path):
            for file in files_:
                files.append(os.path.join(root, file))

        return {'resp_type':'rec_files', 'files':files}


async def on_download_request(message):
    # Callback function for download request from download websocket
    # Get list of path for requested files
    # Convert requested h264 files to mp4
    # Return list of mp4 file paths

    global mp4_buffer_path
    
    message = json.loads(message)
    
    if message['op'] == 'download':
        # Client app request recording file download
        # Get list of files to be sent
        files = message['files']
        # Placeholder for mp4 file paths
        mp4_files = []

        for file in files:
            # Convert to MP4        
            result, mp4file = get_rec_file(file, mp4_buffer_path)            
            mp4_files.append(mp4file)
            
        return mp4_files


async def on_connect(websocket):
    
    # Camera streaming output object
    global output
    
    # Async function for control websocket
    async def receive(websocket):
        
        while True:
            try:
                message = await websocket.recv()
                print (message)
                resp = await on_control(message)
                if resp:
                    resp_json = json.dumps(resp)
                    await websocket.send(resp_json)
                
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
    async def send_rec_file(websocket, n_files):
    
        # MP4 buffer location
        global mp4_buffer_path
        # Rec file bytes
        global rec_file_dict

        # Ensure the previous mp4 files are cleaned
        try: 
            prev_mp4_files = os.listdir(mp4_buffer_path)
            if len(prev_mp4_files) > 0:
                for file in prev_mp4_files:
                    os.remove(os.path.join(prev_mp4_files, file))
        except Exception as e:
            print (e)
        finally:
            print('Files on mp4 buffer are cleared...')

        while True:

            try:
                # Wait to receive download start command
                message = await websocket.recv()
                print (message)
                # Convert requested files to mp4 and return list of mp4 paths.
                mp4_files = await on_download_request(message)

                # Send each mp4 files
                for mp4file in mp4_files:
                    print (f'sending {mp4file}')

                    with open (mp4file, 'rb') as file_obj:
                        content = file_obj.read()
                        # Creating dictionary for file to be sent
                        rec_file_dict['filename'] = os.path.split(mp4file)[-1]
                        rec_file_dict['filebytes'] = base64.b64encode(content).decode('ascii')
                        msg = json.dumps(rec_file_dict)
                        # Send the file
                        await websocket.send(msg)
                        print (f'{mp4file} sent')
                        rec_file_dict.clear()
                
                # Clean all mp4 files
                for mp4file in mp4_files:
                    os.remove(mp4file)

            except websockets.ConnectionClosedOK:
                print ('websocket download closed')
                break


    # Determine the type of incoming websocket request
    path = websocket.path.split('/')
    socketType = path[1]
    print (f'Client connected, {websocket.path}, {socketType}')

    if socketType == 'frame':
        await send(websocket)
    elif socketType == 'control':
        await receive(websocket)
    elif socketType == 'download':
        n_files = path[2]
        await send_rec_file(websocket, n_files)


async def ws_to_client():
    print ('Listening ws from client')
    async with websockets.serve(on_connect, "0.0.0.0", 8000):
        # Keep on listening for new connection request
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
                    # Waiting for ready signal from server
                    if data == (b'1'):
                        try:
                            # Send the frame from buffer when it is complete
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


async def main(camera, output, frame_size, frame_rate, serverHost):
    # Start camera
    task_camera = asyncio.create_task(camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate))
    # Open connection to server
    task_ws_server = asyncio.create_task(ws_to_server(serverHost))
    # Listening connection from client
    task_ws_client = asyncio.create_task(ws_to_client())
    await task_camera
    await task_ws_server
    await task_ws_client
    # Resetting indicators state before exit.
    indicator_1.off()
    indicator_0.on()
    print ('end')


if __name__ == '__main__':

    # Indicators
    indicator_0 = Indicator(pin = 22)
    indicator_1 = Indicator(pin = 27)
    # Resetting indicators state before exit.
    indicator_1.off()
    indicator_0.on()

    # Camera object
    camera = Camera([indicator_1, indicator_0])
    # Frame size
    #frame_size = (640, 480)
    frame_size = (1280, 720)
    # Frame rate
    frame_rate = 15   
    
    # Streaming output object
    output = StreamingOutput2()
    is_recording = True

    # Server host
    serverHost = "vrserver99.local"
    t_reconnection = 3

    # Light
    light = Light(pin = 17)

    # Recording files directory
    rec_path = '../rec/'
    # Recording files directory
    mp4_buffer_path = '../mp4buf/'
    # Rec file bytes
    rec_file_dict = {}
    
    try:
        asyncio.run (main(camera=camera, 
                          output=output, 
                          frame_size=frame_size, 
                          frame_rate=frame_rate, 
                          serverHost=serverHost ))
    except:
        # Resetting indicators state before exit.
        indicator_1.off()
        indicator_0.on()
        print ('end')
