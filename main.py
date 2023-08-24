
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
from EC_PH_Control import EC_pH, EC_Regler


if 1:
    
    ec_regler = EC_Regler(Wasservolumen=8, Düngerkonztentration= 0.1, Mischpumpe=3, Düngerpumpe=12, EC_Sensor_pin=28, Mischzeit=45)
    ec_regler.run_regler(1950)

if 0:
    # Pumpen Treiber Test
    try:
        pumpe = []
        pins = [13,14,15,11,12]
        for pin in pins:
            pumpe.append(Pumpe.Pumpe(pin))
        for Pumpe,pin in zip(pumpe,pins):
            print(pin)
            Pumpe.shot_ml(10)
            time.sleep(0.2)
        print("Pumpen Treiber Test erfolgreich\n")
    except Exception as e:
        print("Pumpen Treiber Test fehlgeschlagen")
        print(e)

