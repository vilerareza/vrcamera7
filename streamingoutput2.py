import io
from threading import Condition

class StreamingOutput2(io.BytesIO):
    '''
    Streaming output object
    '''
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.truncate()
            with self.condition:
                self.frame = self.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.write(buf)