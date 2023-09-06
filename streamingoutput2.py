from io import BufferedIOBase
from threading import Condition

class StreamingOutput2(BufferedIOBase):
    '''
    Streaming output object
    '''
    def __init__(self):
        super().__init__()
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()