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
            #print("update integrator\terror: {}\tint: {}\tout: {}".format(error, self.integrator,self.output))

        def heizung_off(timer):
            self.heizung.off()
            #print("\nHeizung off\n")
        def update_heizung(timer):
            self.heizung.on()
            #print("\nheizung an für {}s\n".format(self.output* timestep2))
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
        self.state = "warten"
        self.timer_running = False
        self.zähler = 0
        self.my_timer = Timer(mode=Timer.PERIODIC,period=1000, callback=lambda x: self.run())

    def run(self):
        
        if self.state == "mischen":
            # Hier kannst du den Code für den Zustand "mischen" einfügen
            if not self.timer_running: 
                self.mischtimer = 0
                print("Timer start")
                self.timer_running = True        
            print("timer_running: {}    Am mischen für {}s".format(self.timer_running,self.Mischzeit-self.mischtimer),end='\r')
            self.Mischpumpe.on()
            self.mischtimer += 1
            if self.mischtimer>=self.Mischzeit:
                self.state = "messen"

        elif self.state == "messen":
            print("Messen...")
            # Hier kannst du den Code für den Zustand "messen" einfügen
            self.error_integral += self.error
            self.error = self.Sollwert-self.Inputs.ec
            
            
            if self.error<=0 or self.zähler>=8:
                self.state = "warten"
                print("EC Sollwert erreicht")
            else:
                self.state = "düngen"
        
        elif self.state == "düngen":
            print("Düngen...")
            # Hier kannst du den Code für den Zustand "düngen" einfügen
            self.zähler += 1
            print("Zähler :{}".format(self.zähler))
            value = (self.kp * self.error + self.ki * self.error_integral) * self.Wasservolumen/self.Düngerkonzentration/1400
            self.Düngerpumpe.shot_ml(value)
            print("dünger : {}ml, error: {}".format(value,self.error))
            self.state = "mischen"
        
        elif self.state == "warten":
            #print("Warten...")
            # Hier kannst du den Code für den Zustand "warten" einfügen
            self.zähler = 0

    def transition(self, state):
        self.state = state
        self.timer_running = False
        print("Transition zu {}".format(state))
    
    def ec_regeln(self, sollwert):
        self.Sollwert = sollwert
        if self.state == "warten":
            self.transition("mischen")
        else:
            pass
            #print("Regler nicht bereit! ist am {}".format(self.state))







    def run_regler(self,sollwert):
        zähler = 0
        print("sfdasdsf")
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

        self.error_integral = 0
        self.error = 0
        self.Sollwert_erreicht = False
        self.Mischpumpe.off()


class michi:
    def __init__(self):
        self.test = 1
        self.t = Timer()
        self.t.init(mode=Timer.ONE_SHOT,period=1000,callback=lambda x: self.testfunktion())
            
    def testfunktion(self):
        print(23)
        print(554)

if __name__ == "__main__":
    
    r = EC_Regler(1,1,1,1,1,4)

    while True:
        time.sleep(0.1)
        r.run()