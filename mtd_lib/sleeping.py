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
import heapq
import itertools
from weakref import WeakValueDictionary

# weakreferable list
class List(list):
    pass

_lock = threading.Lock()
_cond = threading.Condition(_lock)
sleeping_tasklets = []
sleeping_tasklets_dict = WeakValueDictionary() # tasklet -> above's sleeping_tasklets element
manager_running = False
_counter = itertools.count()
_REMOVED = '<removed-task>'

def sleep(seconds=sys.maxint):
    """current tasklet goes to sleep"""
    if seconds <= 0: return
    
    channel = stackless.channel()
    endTime = time.time() + seconds
    
    with _lock:
        sleeping_tasklet = List([endTime, next(_counter), channel])
        heapq.heappush(sleeping_tasklets, sleeping_tasklet)
        sleeping_tasklets_dict[stackless.current] = sleeping_tasklet
        _cond.notify()

    while True:
        try:
            channel.receive()
            break
        except StopIteration:
            pass

def wake(t):
    """wakes a sleeping tasklet"""
    with _lock:
        try:
            sleeping_tasklet = sleeping_tasklets_dict.pop(t)
            if sleeping_tasklet is not None:
                # maybe sleeping
                channel = sleeping_tasklet[-1]
                sleeping_tasklet[-1] = _REMOVED
                if channel is not _REMOVED and channel.balance < 0:
                    channel.send(None)
            else:
                return
        except KeyError:
            return
    
# this function runs in another thread
def _manager():
    while True:
        with _lock:
            while len(sleeping_tasklets) and sleeping_tasklets[0][0] <= time.time():
                endTime, _, channel = sleeping_tasklets[0]
                if channel is not _REMOVED:
                    channel.send(None)
                heapq.heappop(sleeping_tasklets)

            if len(sleeping_tasklets):
                _cond.wait(sleeping_tasklets[0][0] - time.time())
            else:
                _cond.wait()

def ManagerMain():
    t = stackless.tasklet(_manager)()
    while t.alive:
        stackless.run()
    
if not manager_running:
    manager_t = threading.Thread(target=_manager)
    manager_t.daemon = True
    manager_t.start()
    manager_running = True

def Foo():
    print('ok')
    
def ticker():
    while True:
        sleep(0.2)
        print ".",
        sys.stdout.flush()
            
def timer(n=1):
    i = 0
    while True:
        sleep(n)
        i += 1
        print i,
        sys.stdout.flush()

class StTimer(object):
    def __init__(self, interval, times, func, *args, **kwargs):
        def _fn():
            n = 0
            while n < times:
                sleep(interval)
                n += 1
                func(*args, **kwargs)
        self.tasklet = stackless.tasklet(_fn)()
        self.tasklet.run()

    def Alive(self):
        return self.tasklet.alive

    def Waiting(self):
        return self.tasklet.blocked

    def Cancel(self):
        with _lock:
            try:
                sleeping_tasklets_dict[self.tasklet][-1] = _REMOVED
            except KeyError:
                pass
            self.tasklet.kill()

_test_cont = 0

def _cb():
    global _test_cont
    _test_cont += 1

def Run1(n):
    tt = []
    for i in xrange(n):
        t = threading.Timer(1.0, _cb)
        tt.append(t)
        t.start()
    for t in tt:
        t.join()
        
def Run2(n):
    for i in xrange(n):
        t = StTimer(1.0, 1, _cb)
    while len(sleeping_tasklets_dict):
        stackless.run()
        time.sleep(0.01)
        
if __name__ == "__main__":
    from timeit import Timer
    t = Timer("Run2(100000)", "from __main__ import Run2")
    print t.timeit(1)
    print(_test_cont)
    # import sys
    
    # t1 = stackless.tasklet(ticker)()
    # t2 = stackless.tasklet(timer)()
    
    # while t1.scheduled or t2.scheduled:
    #     stackless.run()
    #     time.sleep(0.01)
