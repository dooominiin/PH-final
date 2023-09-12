import random
import time
from EC_PH_Control import EC_Regler, Temperatur_Regler
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

T = Temperatur_Regler(setpoint=26,kp=0.01,ki=0.01,inputs=i,outputs=o, period_integrator=1,period_heizung=300)
#ec_regler = EC_Regler(Wasservolumen=100, Düngerkonztentration= 0.1, Mischpumpe=o.relay__AC_4, Düngerpumpe=o.pumpe_5, Inputs=i, Mischzeit=5)
#ec_regler.ec_regeln(700)

while True:
    print("temp: {}".format(i.temp))
    
    time.sleep(1)
    pass

