# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 22:55:13 2023

@author: domin
"""
import time

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
            time.sleep(self.Mischzeit)
            try:
                self.Mischpumpe.off()
                time.sleep(1)  
                self.Istwert = self.Inputs.ec
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
        
