import os
from datetime import datetime
import asyncio
import picamera2
from picamera2.outputs import FileOutput
#import picamera
import time

class Camera():

    camera = None
    # Root of recording files
    recording_root = '../rec/'
    recording = True


    def __init__(self, indicators) -> None:
        self.on_indicator = indicators[0]
        self.error_indicator = indicators[1]


    async def record_to_file(self, camera, splitter_port=2, size=(1280, 720), quality=30, interval = 60):
    
        # async def wait_recording():
        #     camera.wait_recording(interval, splitter_port=splitter_port)

        first_file = True

        while self.recording:
            print ('recording to new file')
            t_present = datetime.now()
            # Create a storage folder
            dir_name = f'{self.recording_root}{t_present.year}/{t_present.month}/{t_present.day}/{t_present.hour}/'
            os.makedirs(dir_name, exist_ok=True)
            # Prepare file name
            file_name = f"{t_present.strftime('%Y_%m_%d_%H_%M_%S')}.h264"
            if first_file:
                camera.start_recording(f'{dir_name}{file_name}', splitter_port=splitter_port, resize=size, quality=quality)
                first_file = False
            else:
                camera.split_recording(f'{dir_name}{file_name}', splitter_port=splitter_port, resize=size, quality=quality)
            
            await asyncio.sleep(interval)
            #await asyncio.to_thread(wait_recording)


    async def start_camera(self, output, frame_size, frame_rate):
        if not self.camera:
            #try:
            print ('starting camera')

            '''Picamera ver 1'''
            #camera = picamera.Picamera(resolution='HD', framerate = 30)
            # self.camera = picamera.PiCamera(resolution = frame_size, framerate = frame_rate)
            # self.camera.rotation = 180
            # self.camera.rotation = 0
            # self.camera.contrast = 0
            # self.camera.sharpness = 50
            # self.recording = True
            # self.camera.start_recording(output, format='mjpeg')
            # self.on_indicator.on()
            # self.error_indicator.off()

            ''' Picamera ver 2'''
            self.camera = picamera2.Picamera2()

            # Setting configuration object
            config = self.camera.create_video_configuration(
                main={'size': (1920,1080)},
                controls={'FrameRate': frame_rate})

            # Align configuration
            self.camera.align_configuration(config)
            # Applying configuration
            self.camera.configure(config)
            full_res = self.camera.camera_properties['PixelArraySize']
            crop_max = self.camera.camera_properties['ScalerCropMaximum']
            print (f'full res: {full_res}')
            print (f'crop max: {crop_max}')
            # Setting the controls
            #self.camera.set_controls({'Sharpness': 8})
            # self.camera.set_controls({'ScalerCrop': [900,772,1280,720]})
            #self.camera.options['quality'] = 95
            #self.camera.options['compress_level'] = 9
            # Starting the camera
            encoder = picamera2.encoders.JpegEncoder()
            self.recording = True
            output_ = FileOutput(output)
            #self.on_indicator.on()
            #self.error_indicator.off()
            self.camera.start_recording(encoder, output_)
            # time.sleep(2)
            # size = self.camera.capture_metadata()['ScalerCrop']
            # print (f'size: {size}')

            print('Camera is started')
                # # await self.record_to_file(self.camera)

            # except Exception as e:
            #     self.on_indicator.off()
            #     self.error_indicator.on()
            #     print (f'Error {e}')

        else:
            print('Camera is already started') 


    async def stop_camera(self):
        if self.camera:
            try:
                self.camera.stop_recording()
                self.camera.stop_recording(splitter_port=2)
                self.recording = False
                self.camera.close()
                self.camera = None
                self.on_indicator.off()
                self.error_indicator.on()
                status = b'stop_ok'
                print('Camera is stopped')
            except Exception as e:
                self.on_indicator.off()
                self.error_indicator.on()
                print (e)
        else:
            print('Camera already stopped')
            status = b'was_stop'
        return status
