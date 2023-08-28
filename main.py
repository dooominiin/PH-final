import time
from EC_PH_Control import EC_Regler
from HAL import my_inputs, my_outputs
from datalogger import datalogger


i = my_inputs(update_freq=1)
o = my_outputs()
log = datalogger(i,o,log_periode=1)

def doit():
    print("doit!")
    time.sleep(0.3)
try:
    i.rtc.set_dayly_timer((23,5,40),doit,tag_des_monats=28)
    print("regler")
    
except Exception as e:
    print(e)


if 1:
    ec_regler = EC_Regler(Wasservolumen=120, Düngerkonztentration= 0.1, Mischpumpe=o.relay_AC_PWM, Düngerpumpe=o.pumpe_5, Inputs=i, Mischzeit=600)
    for sp in (1600,1700,1800,1900,1950):
        print(sp)    
        ec_regler.run_regler(sp)
        time.sleep(600)

while True:
    pass

