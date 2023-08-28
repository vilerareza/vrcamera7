from io import BytesIO, BufferedIOBase
from threading import Condition


# class StreamingOutput2(BytesIO):
#     '''
#     Streaming output object
#     '''
#     def __init__(self):
#         super().__init__()
#         self.frame = None
#         self.condition = Condition()

#     def write(self, buf):
#         super().write(buf)
#         if buf.startswith(b'\xff\xd8'):
#             # New frame
#             self.truncate()
#             with self.condition:
#                 self.frame = self.getvalue()
#                 self.condition.notify_all()
#             self.seek(0)


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