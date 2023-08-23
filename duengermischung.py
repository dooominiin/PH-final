class duengermischung(object):
    def __init__(self,pumps):
        self.pumps = pumps
    
    def setMischung(self,v):
        self.v = v
         
    def misch(self):
        for pump, v in zip(self.pumps,self.v):
            pump.shot(self.ml2sec(v*1.0000))
        
        
    def ml2sec(self,value):
        self.value = value*1.3434-0.039
        if self.value < 0.001:
            self.value = 0.001
        return self.value
    
    def deinit(self):
        for pump in self.pumps:
            pump.deinit();
    
    def isfinished(self):
        finished = 0
        for p in self.pumps:
            finished = finished + p.isfinished
        if finished == len(self.pumps):
            return 1
        else:
            return 0
