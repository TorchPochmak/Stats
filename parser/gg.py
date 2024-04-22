
import threading
i = 0

def target():
    g = 0
    while(True):
        g += 1

try:   
    while(True):
        i += 1
        s = threading.Thread(target=target)
        s.start()
except:
    print(i)
