import RPi.GPIO as GPIO


class Indicator:

    def __init__(self, pin) -> None:
        self.pin = pin
        self.indicator_init()

    def indicator_init(self):
        # GPIO is in BCM mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin,1)

    def off(self):
        GPIO.output(self.pin,0)

    def cleanup(self):
        GPIO.cleanup()