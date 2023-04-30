import os
from datetime import datetime
import asyncio
import picamera


class Camera():

    camera = None
    # Root of recording files
    recording_root = '../rec/'

    def record_to_file(self, camera, splitter_port=2, size=(1280, 720), quality=30):
        t_present = datetime.now()
        # Create a storage folder
        dir_name = f'{self.recording_root}{t_present.year}/{t_present.month}/{t_present.day}/{t_present.hour}/'
        os.makedirs(dir_name, exist_ok=True)
        # Prepare file name
        file_name = f"{t_present.strftime('%Y_%m_%d_%H_%M_%S')}.h264"
        camera.start_recording(f'{dir_name}{file_name}', splitter_port=splitter_port, resize=size, quality=quality)

    async def start_camera(self, output, frame_size, frame_rate):
        if not self.camera:
            #camera = picamera.PiCamera(resolution='HD', framerate = 30)
            self.camera = picamera.PiCamera(resolution = frame_size, framerate = frame_rate)
            #self.camera.rotation = 180
            self.camera.rotation = 0
            self.camera.contrast = 0
            self.camera.sharpness = 50
            self.camera.start_recording(output, format='mjpeg')
            self.record_to_file(self.camera)
            print('Camera is started')
        else:
            print('Camera is already started') 

    async def stop_camera(self):
        if self.camera:
            try:
                self.camera.stop_recording()
                self.camera.stop_recording(splitter_port=2)
                self.camera.close()
                self.camera = None
                status = b'stop_ok'
                print('Camera is stopped')
            except Exception as e:
                print (e)
        else:
            print('Camera already stopped')
            status = b'was_stop'
        return status
