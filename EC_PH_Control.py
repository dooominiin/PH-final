# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 22:55:13 2023

@author: domin
"""
import time
from machine import Timer

class Temperatur_Regler:
    
    def __init__(self, setpoint, kp, ki, inputs, outputs):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.integrator = 0  # Initialize the integrator
        self.output = 0  # Initialize the output
        self.t1 = Timer()
        self.t2 = Timer()
        self.t3 = Timer()

        timestep1 = 1
        timestep2 = 3600
        
        self.heizung = outputs.relay__AC_3
        self.inputs = inputs
        
        self.t1.init(mode=Timer.PERIODIC, period=timestep1 * 1000, callback=update_integrator)
        self.t2.init(mode=Timer.PERIODIC, period=timestep2 * 1000, callback=update_heizung)
        
        def update_integrator():
            # Calculate the control signal
            error = (setpoint-inputs.temp)
            self.integrator += error * self.ki * timestep1 / timestep2
            self.output = max(0,min(1,self.kp * error + self.integrator))

        def update_heizung(self):
            self.heizung.on()
            self.t3.init(mode=Timer.ONE_SHOT, period=self.output* timestep2 * 1000, callback=self.heizung.off())


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
            print("Am mischen für {}s".format(self.Mischzeit))
            time.sleep(self.Mischzeit)
            self.Istwert = self.Inputs.ec

            print("Istwert: {} uS".format(self.Istwert))

            self.error_integral += self.error
            self.error = self.Sollwert-self.Istwert
            self.Sollwert_erreicht = self.error<=0 or zähler>=8

        self.error_integral = 0
        self.error = 0
        self.Sollwert_erreicht = False
        self.Mischpumpe.off()
        
