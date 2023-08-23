# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 22:55:13 2023

@author: domin
"""


import time
import Pumpe
import duengermischung
import convolutionfilter as cv
from machine import Pin, Timer, ADC

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
        self.ki = 0.1
        self.Sollwert_erreicht = False


    def run_regler(self,Sollwert):
        zähler = 0
        self.Sollwert = Sollwert
        while not self.Sollwert_erreicht:
            zähler += 1
            print(zähler)
            self.Mischpumpe.on()
            value = (self.kp * self.error + self.ki * self.error_integral) * self.Wasservolumen/self.Düngerkonzentration
            print("dünger : {}ml, error: {}".format(value,self.error))
            self.Düngerpumpe.shot_ml(value)
            time.sleep(self.Mischzeit)
            try:
                self.Istwert = self.EC_Sensor.get_value()
            except Exception as e:
                print(e)
            self.error_integral += self.error
            self.error = self.Sollwert-self.Istwert
            self.Sollwert_erreicht = self.error<0
        self.error_integral = 0
        self.error = 0
        self.Sollwert_erreicht = False
        self.Mischpumpe.off()
        

class Tank_neu_fuellen:
    ''' Diese Klasse soll genutzt werden, um den Tank einmal komplett neu zu füllen. Starten mit Tank_neu_fuellen.start(). Ist fertig, wenn Tank_neu_fuellen.is_finished() auf true geht.''' 
    
    leerzeit = 1000#1000*60*10  # ms
    fuellzeit = 1000#24*60*60*1000/180 * 100 # ms
    timer_leeren = Timer()
    timer_fuellen = Timer()
    timer_check = Timer()
    fuellstand = Pin(6, Pin.IN)
    RO_ventil = Pin(7,Pin.OUT,value=0)
    Entleerpumpe = Pin(21,Pin.OUT,value=0)#AC1
    finished = 0

        
    def is_finished(self):
        return Tank_neu_fuellen.finished
    
    def start(self):
        Tank_neu_fuellen.finished = 0
        Tank_neu_fuellen.Entleerpumpe.on()
        Tank_neu_fuellen.timer_leeren.init(mode=Timer.ONE_SHOT, period=Tank_neu_fuellen.leerzeit, callback=Tank_neu_fuellen.fuellen)
        
    def fuellen(timer):
        Tank_neu_fuellen.Entleerpumpe.off()
        Tank_neu_fuellen.RO_ventil.on()
        Tank_neu_fuellen.timer_fuellen.init(mode=Timer.ONE_SHOT, period=Tank_neu_fuellen.fuellzeit, callback=Tank_neu_fuellen.finish)
        Tank_neu_fuellen.timer_check.init(period=1000, callback=Tank_neu_fuellen.check_if_full)

        
    def finish(timer):
        Tank_neu_fuellen.RO_ventil.off()
        Tank_neu_fuellen.finished = 1
    
    
    def check_if_full(timer):
        if Tank_neu_fuellen.fuellstand.value():
            Tank_neu_fuellen.timer_fuellen.deinit()
            Tank_neu_fuellen.RO_ventil.off()
            Tank_neu_fuellen.finished = 1

    def mystates(self):
        return ['fuellstand: ',Tank_neu_fuellen.fuellstand.value(),'RO_ventil: ',Tank_neu_fuellen.RO_ventil.value(),'Entleerpumpe: ',Tank_neu_fuellen.Entleerpumpe.value(),'finished: ',Tank_neu_fuellen.finished]

#test
# T = Tank_neu_fuellen()
# t = Timer()
# T.start()
# t.init(mode=Timer.PERIODIC, period=200,callback= lambda x:print(T.mystates()))
# 


class EC_Sensor():
    def __init__(self,pin):
        self.sensor = ADC(Pin(pin))
        self.filter = cv.convolutionfilter()

    def get_value(self):
        def lookup(value, lookup_table):
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
    
        value = self.filter.filterSignal(self.sensor.read_u16())
        lookup_table = [
            (0,4.21197388614424462),
            (5400000,202.058449644594873),
            (10800000,398.271812926794325),
            (16200000,591.12460920663932),
            (21600000,778.940186344151243),
            (27000000,960.380591160864469),
            (32400000,1134.24639678983294),
            (37800000,1299.33859080336583),
            (43200000,1496.94847074355403),
            (48600000,1994.91364226592555)
            ]
        value = lookup(value*1000,lookup_table)
        return value
        
class EC_pH:
    '''regelung zur anpassung des EC WErtes und des pH Wertes. simple State Machine'''
    
    target_EC = 1000
    target_PH = 5.8
    genauigkeit_PH = 1.2
    genauigkeit_EC = 1000
    mischzeit = 3000
    timeout = 1000*60*30
    
    pumpe_grow      = Pumpe.Pumpe(11)
    pumpe_micro     = Pumpe.Pumpe(12)
    pumpe_flower    = Pumpe.Pumpe(13)
    pumpe_PH_minus  = Pumpe.Pumpe(14)
    pumpe_PH_plus   = Pumpe.Pumpe(15)
    
    sensor_EC = ADC(Pin(28))
    filter_EC = cv.convolutionfilter()
    filter_EC.setValue(sensor_EC.read_u16())

    sensor_PH = ADC(Pin(26))
    filter_PH = cv.convolutionfilter()
    filter_PH.setValue(sensor_PH.read_u16())
    
    
    duengen = 0
    
    Mischpumpe = Pin(1,Pin.OUT,value=0)

    flower = duengermischung.duengermischung([pumpe_grow,pumpe_micro,pumpe_flower])
    flower.setMischung([8,16,24])
    vegetativ = duengermischung.duengermischung([pumpe_grow,pumpe_micro,pumpe_flower])
    vegetativ.setMischung([18,12,6])
    current_mischung = vegetativ
    ph_plus = duengermischung.duengermischung([pumpe_PH_plus])
    ph_plus.setMischung([4])
    ph_minus = duengermischung.duengermischung([pumpe_PH_minus])
    ph_minus.setMischung([4])
    
    loop_timer = Timer()
    misch_timer = Timer()
    timeout_timer = Timer()
    
    finished = 0
    def test(self):
        print('pH u16: ' ,EC_pH.convert_PH(EC_pH.sensor_PH,EC_pH.filter_PH),'\tEC u16: ' ,EC_pH.convert_EC(EC_pH.sensor_EC,EC_pH.filter_EC))
 
    def start(self):
        EC_pH.loop_timer.init(period=1000, mode=Timer.PERIODIC, callback=EC_pH.duengen_loop)
        EC_pH.finished = 0
        EC_pH.timeout_timer.init(mode=Timer.ONE_SHOT, period=EC_pH.timeout, callback=EC_pH.stop)
        
    def is_finished(self):
        return EC_pH.finished
        
    def duengen_loop(timer):   
        def callback_null(timer):
            EC_pH.duengen = 0
        
        #EC plus
        if EC_pH.duengen == 0:
            if EC_pH.convert_EC(pin=EC_pH.sensor_EC, filter=EC_pH.filter_EC) < EC_pH.target_EC - EC_pH.genauigkeit_EC:
                EC_pH.duengen = 1
        if EC_pH.duengen == 1:
            EC_pH.current_mischung.misch()
            EC_pH.duengen = 2
        if EC_pH.duengen == 2:
            if EC_pH.current_mischung.isfinished():
                EC_pH.duengen = 3
                EC_pH.misch_timer.init(mode=Timer.ONE_SHOT, period=EC_pH.mischzeit, callback=callback_null)
        
        #ph plus
        if EC_pH.duengen == 0:
            if EC_pH.convert_EC(EC_pH.sensor_EC,EC_pH.filter_EC) >= EC_pH.target_EC:
                if EC_pH.convert_PH(pin=EC_pH.sensor_PH, filter=EC_pH.filter_PH) < EC_pH.target_PH - EC_pH.genauigkeit_PH:
                    EC_pH.duengen = 4
                    EC_pH.ph_plus.misch()

        if EC_pH.duengen == 4:
            if EC_pH.ph_plus.isfinished():
                EC_pH.duengen = 3
                EC_pH.misch_timer.init(period=EC_pH.mischzeit, mode=Timer.ONE_SHOT, callback=callback_null)
    
        #ph minus
        if EC_pH.duengen == 0:
            if EC_pH.convert_EC(pin=EC_pH.sensor_EC, filter=EC_pH.filter_EC) >= EC_pH.target_EC:
                if EC_pH.convert_PH(pin=EC_pH.sensor_PH,filter=EC_pH.filter_PH) > EC_pH.target_PH + EC_pH.genauigkeit_PH:
                    EC_pH.duengen = 5
                    EC_pH.ph_minus.misch()
        if EC_pH.duengen == 5:
            if EC_pH.ph_minus.isfinished():
                EC_pH.duengen = 3
                EC_pH.misch_timer.init(period=EC_pH.mischzeit, mode=Timer.ONE_SHOT, callback=callback_null)

        #isfinished
        if EC_pH.duengen == 0:
            if EC_pH.convert_EC(EC_pH.sensor_EC,EC_pH.filter_EC) >= EC_pH.target_EC:
                if EC_pH.convert_PH(EC_pH.sensor_PH,EC_pH.filter_PH) > EC_pH.target_PH - EC_pH.genauigkeit_PH:
                    EC_pH.stop(0)
  
    # faktor anpassen !!!!!!!!!!!!!!!!                    
    def convert_PH(pin,filter):
        value = filter.filterSignal(pin.read_u16())
        return value/1024/64*3.3
    
    def convert_EC(pin,filter):
                              
        def lookup(value, lookup_table):
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
    
        value = filter.filterSignal(pin.read_u16())
        lookup_table = [
            (0,4.21197388614424462),
            (5400000,202.058449644594873),
            (10800000,398.271812926794325),
            (16200000,591.12460920663932),
            (21600000,778.940186344151243),
            (27000000,960.380591160864469),
            (32400000,1134.24639678983294),
            (37800000,1299.33859080336583),
            (43200000,1496.94847074355403),
            (48600000,1994.91364226592555)
            ]
        value = lookup(value*1000,lookup_table)
        return value
    
    def stop(timer):
        EC_pH.loop_timer.deinit()
        EC_pH.misch_timer.deinit()
        EC_pH.Mischpumpe.off()
        EC_pH.finished = 1
        print('stop')
        
    def mystates(self):
        return ['duengen :', EC_pH.duengen]
    



#test
# a = EC_pH()
# a.start()
# from machine import Timer
# tt = Timer()
# tt.init(mode=Timer.PERIODIC, period=200,callback= lambda x:print(a.mystates()))
