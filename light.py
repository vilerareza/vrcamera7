import RPi.GPIO as GPIO

class Light():

    def __init__(self, pin) -> None:
        self.ledPin = pin
        self.led_init()

    def led_init(self):
        # GPIO is in BCM mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ledPin, GPIO.OUT)

    def led_on(self):
        GPIO.output(self.ledPin,1)

    def led_off(self):
        GPIO.output(self.ledPin,0)

    def led_cleanup(self):
        GPIO.cleanup()
