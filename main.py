
import convolutionfilter as cv
from machine import Pin, ADC, Timer, PWM, I2C, SPI
import sdcard
import utime
import time
import array
import sht31
import os
import convolutionfilter as filt
import Pumpe
import duengermischung as dm
from ds1307 import DS1307
from EC_PH_Control import EC_pH






# Pumpen Treiber Test
try:
    pumpe = []
    pins = [12]#,14,15,11,12]
    for pin in pins:
        pumpe.append(Pumpe.Pumpe(pin))
    for Pumpe,pin in zip(pumpe,pins):
        print(pin)
        Pumpe.shot_ml(0)
        time.sleep(0.2)
    print("Pumpen Treiber Test erfolgreich\n")
except Exception as e:
    print("Pumpen Treiber Test fehlgeschlagen")
    print(e)

# AC PWM Test
try:
    print("PWM gestartet!")
    pwm = PWM(Pin(3))
    pwm.freq(8)
    print(pwm)
    pwm.duty_u16(int(0.8*65535))
    time.sleep(1)
except Exception as e:
    print("AC PWM Test fehlgeschlagen")
    print(e)
