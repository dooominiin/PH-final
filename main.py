
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
from EC_PH_Control import EC_Regler
from HAL import my_inputs, my_outputs
from datalogger import datalogger


i = my_inputs(update_freq=1)
o = my_outputs()
log = datalogger(i,o,log_periode=3)




if 1:
    
    ec_regler = EC_Regler(Wasservolumen=120, Düngerkonztentration= 0.1, Mischpumpe=o.relay_AC_PWM, Düngerpumpe=o.pumpe_5, Inputs=i, Mischzeit=300)
    for sp in range(1200,1900,200):
        print(sp)    
        ec_regler.run_regler(sp)
        time.sleep(600)


if 0:
    #sdcard karten test    
    try:
        sd = sdcard.SDCard(SPI(0, 40_000_000, sck=Pin(18), mosi=Pin(19), miso=Pin(16)), Pin(17))
        os.mount(sd, '/sd')
        print(os.listdir('/sd'))
        file = open("/sd/sample.txt","w")
        for i in range(20):
            file.write("Sample text = %s\r\n" % i)
        file.close() 
        print("sd karte Test erfolgreich\n")
    except Exception as e:
        print("sd karte Test fehlgeschlagen")
        print(e)
  
if 0:
    
    try:
        #os.mount(sd, '/sd')
        print(os.listdir('/sd'))
    except Exception as e:
        print(e)

    sensor = EC_Sensor(28)
    file_path = 'sd/ec_sensor.txt'
    while True:
        print(sensor.sensor.read_u16())
        try:
            val = sensor.get_value_u16()
            file = open(file_path, "a") 
            file.write(str(val) + "\n")
            file.close()
            p = Pumpe.Pumpe(15)
            p.shot(0.1)
            time.sleep(0.5)
        except Exception as e:
            print(e)
            try:
                sd = sdcard.SDCard(SPI(0, 40_000_000, sck=Pin(18), mosi=Pin(19), miso=Pin(16)), Pin(17))
                os.umount(sd)
                os.mount(sd, '/sd')
            except Exception as e:
                print(e)

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

while True:
    pass