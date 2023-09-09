# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 22:55:13 2023

@author: domin
"""
import time
from machine import Timer

class Temperatur_Regler:
    
    def __init__(self, setpoint, kp, ki, inputs, outputs, period_integrator, period_heizung):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.integrator = 0  # Initialize the integrator
        self.output = 0  # Initialize the output
        self.t1 = Timer()
        self.t2 = Timer()
        self.t3 = Timer()

        timestep1 = period_integrator # abtastrate für den integrator
        timestep2 = period_heizung # Schaltperiode in Sekunden für die Heizung
        
        self.heizung = outputs.relay__AC_3
        self.inputs = inputs
        
        def update_integrator(timer):
            # Calculate the control signal
            error = (setpoint-inputs.temp)
            self.integrator += error * self.ki * timestep1 / timestep2
            self.integrator = max(-0.8,min(1,self.integrator))
            self.output = max(0,min(0.8,self.kp * error + self.integrator))
            print("update integrator\terror: {}\tint: {}\tout: {}".format(error, self.integrator,self.output))

        def heizung_off(timer):
            self.heizung.off()
            print("\nHeizung off\n")
        def update_heizung(timer):
            self.heizung.on()
            print("\nheizung an für {}s\n".format(self.output* timestep2))
            self.t3.init(mode=Timer.ONE_SHOT, period=int(self.output* timestep2 * 1000), callback=heizung_off)
            
        self.t1.init(mode=Timer.PERIODIC, period=timestep1 * 1000, callback=update_integrator)
        self.t2.init(mode=Timer.PERIODIC, period=timestep2 * 1000, callback=update_heizung)
        

class EC_Regler:
    def __init__(self,Wasservolumen, Düngerkonztentration, Mischpumpe, Düngerpumpe, Inputs, Mischzeit):
        self.Wasservolumen = Wasservolumen
        self.Düngerkonzentration = Düngerkonztentration
        self.Mischpumpe = Mischpumpe
        self.Düngerpumpe = Düngerpumpe
        self.Inputs = Inputs
        self.Mischzeit = Mischzeit
        self.Sollwert = 0
        self.Istwert = 0
        self.error = 0
        self.error_integral = 0
        self.kp = 0.8
        self.ki = 0.05
        self.Sollwert_erreicht = False
    
    def run_regler(self,sollwert):
        zähler = 0

        self.Sollwert = min(1950,max(0,sollwert))
        while not self.Sollwert_erreicht:
            zähler += 1
            print("Zähler :{}".format(zähler))
            self.Mischpumpe.on()
            value = (self.kp * self.error + self.ki * self.error_integral) * self.Wasservolumen/self.Düngerkonzentration/1400
            print("dünger : {}ml, error: {}".format(value,self.error))
            self.Düngerpumpe.shot_ml(value)
            print("Am mischen für {}s".format(self.Mischzeit))
            time.sleep(self.Mischzeit)
            self.Istwert = self.Inputs.ec

            print("Istwert: {} uS".format(self.Istwert))

            self.error_integral += self.error
            self.error = self.Sollwert-self.Istwert
            self.Sollwert_erreicht = self.error<=0 or zähler>=8

            
    
    def set_k(self,kp,ki):
        self.kp = kp
        self.ki = ki


        self.error_integral = 0
        self.error = 0
        self.Sollwert_erreicht = False
        self.Mischpumpe.off()
        
