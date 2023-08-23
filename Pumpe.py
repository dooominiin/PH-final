from machine import Pin, ADC, Timer, PWM, I2C

class Pumpe(object):
 
    def __init__(self,pinNumber):
        self.pumpe = PWM(Pin(pinNumber))
        self.pwm_frequenz = 50;
        self.pumpe.freq(self.pwm_frequenz)
        self.pumpe.duty_u16(0)
        self.isfinished = 1

    
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


    def deinit(self):
        self.pumpe.duty_u16(0)
        self.isfinished = 1
        