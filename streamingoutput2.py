from io import BytesIO 
from threading import Condition


class StreamingOutput2(BytesIO):
    '''
    Streaming output object
    '''
    def __init__(self):
        super().__init__()
        self.frame = None
        self.condition = Condition()
        print ('init')

    def write(self, buf):
        print ('write buff')
        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.truncate()
            with self.condition:
                self.frame = self.getvalue()
                self.condition.notify_all()
            self.seek(0)
            print ('new frame')
        return self.write(buf)