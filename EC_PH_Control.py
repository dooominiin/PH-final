# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 22:55:13 2023

@author: domin
"""

import uarray
import time
import Pumpe
from machine import Pin, Timer, ADC
import machine

class EC_Regler():
    def __init__(self,Wasservolumen, Düngerkonztentration, Mischpumpe, Düngerpumpe, EC_Sensor_pin,Mischzeit):
        self.Wasservolumen = Wasservolumen
        self.Düngerkonzentration = Düngerkonztentration
        self.Mischpumpe = Pin(Mischpumpe,Pin.OUT)
        self.Düngerpumpe = Pumpe.Pumpe(Düngerpumpe)
        self.EC_Sensor = EC_Sensor(EC_Sensor_pin)
        self.Mischzeit = Mischzeit
        self.Sollwert = 0
        self.Istwert = 0
        self.error = 0
        self.error_integral = 0
        self.kp = 0.8
        self.ki = 0.05
        self.Sollwert_erreicht = False

    def set_k(self,kp,ki):
        self.kp = kp
        self.ki = ki

    def run_regler(self,Sollwert):
        zähler = 0

        self.Sollwert = min(2000,max(0,Sollwert))
        while not self.Sollwert_erreicht:
            zähler += 1
            print("Zähler :{}".format(zähler))
            self.Mischpumpe.on()
            value = (self.kp * self.error + self.ki * self.error_integral) * self.Wasservolumen/self.Düngerkonzentration/1400
            print("dünger : {}ml, error: {}".format(value,self.error))
            self.Düngerpumpe.shot_ml(value)
            time.sleep(self.Mischzeit)
            try:
                self.Mischpumpe.off()
                time.sleep(1)            
                self.Istwert = self.EC_Sensor.get_value()
                self.Mischpumpe.on()

            except Exception as e:
                print(e)
            print("Istwert: {} uS".format(self.Istwert))

            self.error_integral += self.error
            self.error = self.Sollwert-self.Istwert
            self.Sollwert_erreicht = self.error<=0 or zähler>=8

        self.error_integral = 0
        self.error = 0
        self.Sollwert_erreicht = False
        self.Mischpumpe.off()
        

#test

# t = Timer()
# t.init(mode=Timer.PERIODIC, period=200,callback= lambda x:print(T.mystates()))



class EC_Sensor():
    def __init__(self,pin):
        self.sensor = ADC(Pin(pin))
        self.k1 = 1
        self.k2 = 2
        self.k3 = 3
        self.lookup_table = [
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

    def get_value(self):
        values = []
        for i in range(10):
            values.append(self.sensor.read_u16())
            print(values[i])
            time.sleep(0.1)
        if all(x == values[0] for x in values):
            raise FreezeException()
        value = sum(values) / len(values)

        value = self.lookup(value)
        return value

    def lookup(self, value):
        lookup_table = self.lookup_table
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
  
class FreezeException(Exception):
    def __init__(self):
        print("Sensor Freeze Exception. Pico wird neu gestartet in 5 Sekunden!")
        time.sleep(5)
        machine.reset()
        super().__init__("Sensor Freeze Exception")


#test

# from machine import Timer
# tt = Timer()
# tt.init(mode=Timer.PERIODIC, period=200,callback= lambda x:print(a.mystates()))
