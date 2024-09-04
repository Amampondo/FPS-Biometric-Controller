class Magazine:
    
    def __init__(self , min , max):
        
        self._min = min
        self._val = min
        self._max = max
        
    def increase(self):
        
        if self._val == self._max:
            
            self._val = self._min
            
        else:
            self._val += 5
            
    def count(self): return self._val
    
    def zoom(self): self._val = 17*30