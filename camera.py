import picamera

class Camera():
    camera = None

    def start_camera(self, output, frame_size, frame_rate):
        if not self.camera:
            #camera = picamera.PiCamera(resolution='HD', framerate = 30)
            self.camera = picamera.PiCamera(resolution = frame_size, framerate = frame_rate)
            #self.camera.rotation = 180
            self.camera.rotation = 0
            self.camera.contrast = 0
            self.camera.sharpness = 50
            self.camera.start_recording(output, format='mjpeg')
            print('Camera is started')
        else:
            print('Camera is already started') 

    def wait_recording(self, time):
        self.camera.wait_recording(time)

    def stop_camera(self):
        if self.camera:
            try:
                self.camera.stop_recording()
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
