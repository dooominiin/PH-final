import random
import time
from EC_PH_Control import EC_Regler
from HAL import my_inputs, my_outputs
from datalogger import datalogger
from machine import Timer

i = my_inputs(update_freq=1)
o = my_outputs()
log = datalogger(i,o,log_periode=1)

lampe = o.relay__AC_1
lüftung = o.relay__AC_2
heizung = o.relay__AC_3
umwälzpumpe = o.relay__AC_4

lampe.on()
lüftung.on()
heizung.off()
umwälzpumpe.off()



def toggle_random_object(objects):
    object_to_toggle = random.choice(objects)
    if object_to_toggle.value():
        object_to_toggle.off()
        print(f"{object_to_toggle}off()")
    else:
        object_to_toggle.on()
        print(f"{object_to_toggle}on()")

# Hier rufst du den Timer auf und gibst die 'toggle_random_object' Funktion als Callback an, die alle 3 Stunden aufgerufen wird.
#t = Timer()
#t.init(mode=Timer.PERIODIC, period=3 * 60 * 60 * 1000, callback=lambda t: toggle_random_object(s))



def doit():
    print("doit!")
    time.sleep(1)
try:
    i.rtc.set_dayly_timer((23,5,40),doit,tag_des_monats=28)
    
except Exception as e:
    print(e)


ec_regler = EC_Regler(Wasservolumen=50, Düngerkonztentration= 0.1, Mischpumpe=o.relay__AC_4, Düngerpumpe=o.pumpe_5, Inputs=i, Mischzeit=600)
if 0:
    for sp in (1600,1700,1800,1900,1950):
        print(sp)    
        ec_regler.run_regler(sp)
        time.sleep(600)

if 1:    
    # ec regeln
    print(1)
    timer_ec = Timer()
    timer_ec.init(mode=Timer.PERIODIC, period=3 * 60 * 60 * 1000, callback=ec_regler.run_regler(1000))
    print(2)

while True:
    print("ec: {}".format(i.ec))
    print("temp: {}".format(i.temp))
    
    
    time.sleep(1)
    pass

