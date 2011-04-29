import time
import threading

import socketconsole

socketconsole.launch()

def waiter():
    time.sleep(500)


ts = [threading.Thread(target=waiter) for i in range(3)]
for i, t in enumerate(ts):
    t.name = "thread-%d" % i
    t.daemon = True
    t.start()
    print "Started", t.name

waiter()
