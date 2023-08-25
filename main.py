
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
from EC_PH_Control import EC_Regler, EC_Sensor

if 1:
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
  

if 1:
    
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
    
    ec_regler = EC_Regler(Wasservolumen=8, Düngerkonztentration= 0.1, Mischpumpe=3, Düngerpumpe=12, EC_Sensor_pin=28, Mischzeit=1)
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

