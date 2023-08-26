from machine import Pin, ADC, Timer, PWM, I2C
import time 
class Pumpe(object):
 
    def __init__(self,pinNumber):
        self.pumpe = PWM(Pin(pinNumber))
        self.pwm_frequenz = 50;
        self.pumpe.freq(self.pwm_frequenz)
        self.pumpe.duty_u16(0)
        self.isfinished = 1

    def value(self):
        return 1 - self.isfinished

    def shot(self,value):
        def off(timer):
            self.pumpe.duty_u16(0)
            self.isfinished = 1
        self.tim = Timer()
        self.pumpe.duty_u16(65535)
        self.isfinished = 0
        self.tim.init(mode = Timer.ONE_SHOT, period=int(value*1000),callback=off)

    def shot_ml(self,value):
        self.shot(value/7.35*10)
        while not self.isfinished:
            time.sleep(0.1)

    def deinit(self):
        self.pumpe.duty_u16(0)
        self.isfinished = 1
        