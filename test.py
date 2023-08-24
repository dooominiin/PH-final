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

print("Testscript gestartet")

# EC messung Test
try:
    sensor_EC = ADC(Pin(28))
    filter_EC = cv.convolutionfilter()
    filter_EC.setValue(sensor_EC.read_u16())
    for i in range(100):
        value = EC_pH.convert_EC(EC_pH.sensor_EC,EC_pH.filter_EC)
        time.sleep(0.1)
        print("EC : {}".format(value))
    print("EC messung erfolgreich mit {} EC.\n".format(value))
except Exception as e:
    print("EC messung Test fehlgeschlagen")
    print(e)   




# Luftfeuchtigkeit und Temperatur
try:
    i2c = I2C(0,scl=Pin(1), sda=Pin(0), freq =400000)
    sensor = sht31.SHT31(i2c, addr=0x44)
    for i in range(10):
        data = sensor.get_temp_humi()
        print(data)
        time.sleep(0.25)
    print("sht31 Test erfolgreich\n")
except Exception as e:
    print("sht31 Test fehlgeschlagen")
    print(e)
        
# RTC
try:
    i2c_rtc = I2C(0,scl = Pin(1),sda = Pin(0),freq = 100000)
    rtc = DS1307(i2c_rtc)
    # rtc.set_Time(rtc) # nur auskommentieren, um Zeit neu zu setzen!
    print("RTC Test erfolgreich\n!")
except Exception as e:
    print("RTC Test fehlgeschlagen")
    print(e)
    
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
  

    
# Pumpen Treiber Test
try:
    pumpe = []
    pins = [13,14,15,11,12]
    for pin in pins:
        pumpe.append(Pumpe.Pumpe(pin))
    for Pumpe,pin in zip(pumpe,pins):
        print(pin)
        Pumpe.shot(0)
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
    pwm.duty_u16(int(0.5*65535))
    time.sleep(1)
    pwm.duty_u16(int(0))
    
except Exception as e:
    print("AC PWM Test fehlgeschlagen")
    print(e)


# AC Relays Test
try:
    relay = []
    pins = [21,2,20,22,3]
    for pin in pins:
        relay.append(Pin(pin,Pin.OUT))
    for Relay,pin in zip(relay,pins):
        print("Pin Nr: {}".format(pin))
        for i in range(1):
            Relay.on() # Ausgang auf HIGH setzen
            time.sleep(0.3)  # 1 Sekunde warten
            Relay.off()  # Ausgang auf LOW setzen
            time.sleep(0.3)  # 1 Sekunde warten
except Exception as e:
    print("AC Relays Test fehlgeschlagen")
    print(e)
    


# EC kalibrierung
try:
    ist = []
    sensor = []
    relay[4].on()
    time.sleep(1)
    relay[4].off()
    for i in range(20):
        val = sensor_EC.read_u16()   
         
        sensor.append(val)
        ist.append(int(input("val: {}   Drücke Enter, um fortzufahren...".format(val))))
        print(ist[i])
        relay[4].on()
        pumpe[4].shot_ml(5)
        time.sleep(3)
        relay[4].off()
    print(ist)
    print(sensor)
except Exception as e:
    print(e)
       

# PH messung Test
try:
    raise Exception("1IN- und 1IN+ vertauscht im layout footprint")
    sensor_PH = ADC(Pin(26))
    filter_PH = cv.convolutionfilter()
    filter_PH.setValue(sensor_PH.read_u16())
    for i in range(100):
        value = EC_pH.convert_PH(EC_pH.sensor_PH,EC_pH.filter_PH)
        time.sleep(0.1)
        print("PH : {}".format(sensor_PH.read_u16()))
    print("PH messung erfolgreich mit {} PH.\n".format(value))
except Exception as e:
    print("PH messung Test fehlgeschlagen")
    print(e)   







