import time
from functools import partial
from threading import Thread, Condition
from adafruit_servokit import ServoKit


class Servo():
    # Servo parameter
    moveThread = None
    posMin = 5
    posMax = 175
    stepDegree = 2
    delayS = float(0.002)

    def __init__(self, channel = 0) -> None:
        self.kit = ServoKit(channels = 16)
        self.channel = channel
        self.condition = Condition()
        self.initialMove = True
        self.center()
        time.sleep(0.3)
        print ('servo init ok')

    def center(self, center_position = 90):
        if self.initialMove:
            self.kit.servo[self.channel].angle = center_position
            self.initialMove = False
        else:
            self.start_move(pos = center_position)

    def start_move(self, distance = 0, pos=None):
        #def move(distance, pos):
        if pos:
            distance = pos - self.kit.servo[self.channel].angle
        if distance > 0:
            # Positive direction
            if self.kit.servo[self.channel].angle < self.posMax:
                # Still within x movement range
                # Calculate target position
                if (self.kit.servo[self.channel].angle + distance) >= self.posMax:
                    # Limit the movement to max limit.
                    targetPos = self.posMax
                else:
                    targetPos = self.kit.servo[self.channel].angle + distance
                # Move
                while self.kit.servo[self.channel].angle <= targetPos:
                    self.kit.servo[self.channel].angle += self.stepDegree
                    #print (f'targetPos: {targetPos}')
                    #print (f'pos: {self.kit.servo[self.channel].angle}')
                    time.sleep(self.delayS)
            else:
                # Dont move, already at max position
                pass

        elif distance < 0:
            # Negative direction
            if self.kit.servo[self.channel].angle > self.posMin:
                # Still within x movement range
                # Calculate target position
                if (self.kit.servo[self.channel].angle + distance) <= self.posMin:
                    # Limit the movement to min limit.
                    targetPos = self.posMin
                else:
                    targetPos = self.kit.servo[self.channel].angle + distance
                # Move
                while self.kit.servo[self.channel].angle >= targetPos:
                    self.kit.servo[self.channel].angle -= self.stepDegree
                    #print (f'targetPos: {targetPos}')
                    #print (f'pos: {self.kit.servo[self.channel].angle}')
                    time.sleep(self.delayS)
            else:
                # Dont move, already at min position
                pass

def excercise():
    # Excercise the camera movement to position posX1, posX2, posY1, posY2
    servoX = Servo(channel=0)
    servoY = Servo(channel=1)
    posX1 = 170
    posX2 = 10
    posY1 = 120
    posY2 = 70
    centerX = 90
    centerY = 90
    nLoop = 5

    def runX():
        i = 0
        while i < nLoop:
            try:
                servoX.start_move(pos = posX1)
                servoX.start_move(pos = posX2)
            except Exception as e:
                print (e)
                break
            i+=1
        # Centering
        servoX.start_move(pos = centerX)

    def runY():
        j = 0
        while j < nLoop:
            try:
                servoY.start_move(pos = posY1)
                servoY.start_move(pos = posY2)
            except Exception as e:
                print (e)
                break
            j+=1
        # Centering
        servoY.start_move(pos = centerY)

    Thread(target = runX).start()
    Thread(target = runY).start()

