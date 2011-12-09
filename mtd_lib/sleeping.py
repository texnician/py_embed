#!/usr/bin/env stackless2.6
# -*- coding: utf-8 -*-

"""
Author: Alejandro Castillo <pyalec@gmail.com>

Tasklet sleeping technique based on general purpose sleep
on http://www.stackless.com/wiki/Idioms

It uses another thread and a condition variable to not busy wait"""

__all__ = ['sleep', 'wake']

import threading
import stackless
import time
import sys

from weakref import WeakValueDictionary


# weakreferable list
class List(list):
    pass


lock = threading.Lock()
cond = threading.Condition(lock)
sleeping_tasklets = []
sleeping_tasklets_dict = WeakValueDictionary() # tasklet -> above's sleeping_tasklets element
manager_running = False

def sleep(seconds=sys.maxint):
    """current tasklet goes to sleep"""
    if seconds <= 0: return
    
    channel = stackless.channel()
    endTime = time.time() + seconds
    
    with lock:
        sleeping_tasklet = List([endTime, channel])
        sleeping_tasklets.append(sleeping_tasklet)
        sleeping_tasklets.sort()
        sleeping_tasklets_dict[stackless.current] = sleeping_tasklet
        cond.notify()

    while True:
        try:
            channel.receive()
            break
        except StopIteration:
            pass

def wake(t):
    """wakes a sleeping tasklet"""
    with lock:
        sleeping_tasklet = sleeping_tasklets_dict.get(t)
        if sleeping_tasklet is not None:
            # maybe sleeping
            channel = sleeping_tasklet[1]
            try:
                sleeping_tasklets.remove(sleeping_tasklet)
            except ValueError:
                # not really sleeping
                return
        else:
            return
    channel.send(None)


# this function runs in another thread
def manager():
    while True:
        with lock:
            if len(sleeping_tasklets):
                endTime = sleeping_tasklets[0][0]
                if endTime <= time.time():
                    channel = sleeping_tasklets[0][1]
                    del sleeping_tasklets[0]
                    channel.send(None)

            if len(sleeping_tasklets):
                cond.wait(sleeping_tasklets[0][0] - time.time())
            else:
                cond.wait()


if not manager_running:
    manager_t = threading.Thread(target=manager)
    manager_t.daemon = True
    manager_t.start()
    manager_running = True



if __name__ == "__main__":
    import sys
    
    def ticker():
        while True:
            print ".",
            sys.stdout.flush()
            sleep(0.2)
            
    def timer():
        i = 0
        while True:
            i += 1
            print i,
            sys.stdout.flush()
            sleep(1)
    
    t1 = stackless.tasklet(ticker)()
    t2 = stackless.tasklet(timer)()
    
    while t1.scheduled or t2.scheduled:
        stackless.run()
        time.sleep(0.01)
