from machine import Pin, ADC, Timer, PWM, I2C
import sht31
import Pumpe
from ds1307 import DS1307

# Hardware Abstraction Layer
class my_inputs:
    def __init__(self,update_freq):
        self.sensor_EC = sensor_EC(10)
        self.sensor_TEMP_HUMI = sensor_TEMP_HUMI()
        self.rtc = my_RTC()
    
        self.time = (1,1,1,1,1)
        self.temp = 0
        self.humi = 0
        self.ec = 0

        def update_sensors(t):
            self.ec = self.sensor_EC.get_value()
            data = self.sensor_TEMP_HUMI.get_temp_humi()
            self.temp = data[0]
            self.humi = data[1]

        update_sensors(0)

        self.timer = Timer()
        self.timer.init(mode=Timer.PERIODIC, freq = update_freq,callback= update_sensors)
    
    def get_inputs(self):
        # Definition des benannten Tupels
        my_dict = {
            "Temperatur" : self.temp, # type: ignore
            "Humidity" : self.humi, # type: ignore
            "EC" : self.ec, # type: ignore
            "datetime" : self.rtc.get_time() # type: ignore
        }
        return my_dict
        
class my_outputs:
    def __init__(self):
 
        self.relay__AC_1 = (Pin(21,Pin.OUT))        
        self.relay__AC_2 = (Pin(2,Pin.OUT))        
        self.relay__AC_3 = (Pin(20,Pin.OUT))        
        self.relay__AC_4 = (Pin(22,Pin.OUT))
        self.relay_AC_PWM = my_pwm(3,freq=8,duty_u16=0)

        self.pumpe_1 = Pumpe.Pumpe(13)
        self.pumpe_2 = Pumpe.Pumpe(14)
        self.pumpe_3 = Pumpe.Pumpe(15)
        self.pumpe_4 = Pumpe.Pumpe(11)
        self.pumpe_5 = Pumpe.Pumpe(12)

        self.all_output = (
            self.relay__AC_1,
            self.relay__AC_2,
            self.relay__AC_3,
            self.relay__AC_4,
            self.relay_AC_PWM,
            self.pumpe_1,
            self.pumpe_2,
            self.pumpe_3,
            self.pumpe_4,
            self.pumpe_5
            )

    def get_outputs(self):
        # Definition des benannten Tupels
        my_dict = {
            "relay_AC_1" : self.relay__AC_1, # type: ignore
            "relay_AC_2" : self.relay__AC_2, # type: ignore
            "relay_AC_3" : self.relay__AC_3, # type: ignore
            "relay_AC_4" : self.relay__AC_4, # type: ignore
            "relay_AC_PWM" : self.relay_AC_PWM, # type: ignore
            "Pumpe_1" : self.pumpe_1, # type: ignore
            "Pumpe_2" : self.pumpe_2, # type: ignore
            "Pumpe_3" : self.pumpe_3, # type: ignore
            "Pumpe_4" : self.pumpe_4, # type: ignore
            "Pumpe_5" : self.pumpe_5 # type: ignore
        }
        return my_dict
    
class my_queue:
    def __init__(self, length,init_value):
        self.queue = [init_value] * length
        self.index = 0
        self.length = length

    def append(self, value):
        self.queue[self.index] = value
        self.index = (self.index + 1) % self.length
   
    def check_for_freeze(self):
        if all(x == self.queue[0] for x in self.queue):
            class SensorFreezeException(Exception): pass
            #raise SensorFreezeException("Sensor regiert nicht mehr!\n{}".format(self.queue))
            #machine.reset()
            print("Sensor regiert nicht mehr!\n{}".format(self.queue))

    def filter(self,value):
        self.append(value)
        return sum(self.queue) / self.length

class sensor_EC:
    def __init__(self, q_length):
        try:
            self.sensor_EC = ADC(Pin(28))
            value = self.sensor_EC.read_u16()
            print("EC sensor erfolgreich verbunden mit {} EC u16.\n".format(value))
            self.q = my_queue(q_length,value)
        except Exception as e:
            print("EC sensor verbinden fehlgeschlagen")
            print(e)   

    def lookup(self, value):
        lookup_table = [
            (0.00000000000000000,0),
            (4874.44498922495495,200),
            (10135.6120464669602,400),
            (15454.7941955584974,600),
            (20858.1918005606531,800),
            (26331.5818066974098,1000),
            (31790.3744671429922,1200),
            (37049.6700698092027,1400),
            (41794.315664132766,1600),
            (45548.9617878626232,1800),
            (47648.1191938473567,2000)
            ]
        value = min(lookup_table[len(lookup_table)-1][0],max(value,lookup_table[0][0]))
        # Finde den Index des nächsten kleineren Werts in der Lookup-Tabelle
        index = 0
        while index < len(lookup_table) - 2 and value > lookup_table[index][0]:
            index += 1
        # Extrahiere die Werte der nächsten beiden Punkte
        x0, y0 = lookup_table[index]
        if index > len(lookup_table)-1:
            index = len(lookup_table)-2
        x1, y1 = lookup_table[index + 1]
        # Lineare Interpolation zwischen den beiden Punkten
        interpolated_value = y0 + (y1 - y0) * (value - x0) / (x1 - x0)
        return interpolated_value      
    
    def get_value_u16(self):
        try:
            value = self.sensor_EC.read_u16()
            value = self.q.filter(value)
            self.q.check_for_freeze()
            return value
        except Exception as e:
            print(e)
            self.__init__(self.q.length)
            return 0

    def get_value(self):
        return self.lookup(self.get_value_u16())

class sensor_TEMP_HUMI:
    def __init__(self):
        # Luftfeuchtigkeit und Temperatur
        try:
            i2c = I2C(0,scl=Pin(1), sda=Pin(0), freq =400000)
            self.sensor_temp_humi = sht31.SHT31(i2c, addr=0x44)
            data = self.sensor_temp_humi.get_temp_humi()
            temperatur = data[0]
            luftfeuchtigkeit = data[1]
            print("Temp/Humi sensor erfolgreich verbunden mit T: {} Humi: {} EC.\n".format(temperatur,luftfeuchtigkeit))
        except Exception as e:
            print("Temp/Humi sensor verbinden fehlgeschlagen")
            print(e)

    def get_temp_humi(self):
        try:
            return self.sensor_temp_humi.get_temp_humi()
        except Exception as e:
            print(e)
            self.__init__()
            return (0,0)

class my_pwm:
    def __init__(self,pin,freq,duty_u16):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.pwm.duty_u16(duty_u16)
    def freq(self,freq):
        self.pwm.freq(freq)
    def duty_u16(self,duty_u16):
        self.pwm.duty_u16(duty_u16)
    def value(self):
        return self.pwm.duty_u16()
    def deinit(self):
        self.pwm.deinit()
    def on(self):
        self.pwm.duty_u16(65535)
    def off(self):
        self.pwm.duty_u16(0)
        
class my_RTC:
    def __init__(self):
        try:
            i2c_rtc = I2C(0,scl = Pin(1),sda = Pin(0),freq = 100000)
            self.rtc = DS1307(i2c_rtc)
            # rtc.set_Time(rtc) # nur auskommentieren, um Zeit neu zu setzen!
            print("RTC erfolgreich verbunden mit {}.".format(self.rtc.datetime()))
        except Exception as e:
            print("RTC verbinden fehlgeschlagen")
            print(e)

    def get_time(self):
        try:
            datetime = self.rtc.datetime()
            datetime = datetime[0:3] + datetime[4:7]
            return datetime
        except Exception as e:
            print(e)
            self.__init__()
            return (0,0,0,0,0,0)

