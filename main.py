import time
from EC_PH_Control import EC_Regler
from HAL import my_inputs, my_outputs
from datalogger import datalogger


i = my_inputs(update_freq=1)
o = my_outputs()
log = datalogger(i,o,log_periode=1)




if 1:
    
    ec_regler = EC_Regler(Wasservolumen=120, Düngerkonztentration= 0.1, Mischpumpe=o.relay_AC_PWM, Düngerpumpe=o.pumpe_5, Inputs=i, Mischzeit=300)
    for sp in range(1200,1900,200):
        print(sp)    
        ec_regler.run_regler(sp)
        time.sleep(600)

