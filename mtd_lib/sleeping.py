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
def manager():
    while True:
        with _lock:
            while len(sleeping_tasklets) and sleeping_tasklets[0][0] <= time.time():
                endTime, _, channel = sleeping_tasklets[0]
                heapq.heappop(sleeping_tasklets)
                if channel is not _REMOVED:
                    channel.send(None)

            if len(sleeping_tasklets):
                _cond.wait(sleeping_tasklets[0][0] - time.time())
            else:
                _cond.wait()

if not manager_running:
    manager_t = threading.Thread(target=manager)
    manager_t.daemon = True
    manager_t.start()
    manager_running = True

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

# Do FOO N secs later
# Do FOO every N secs
# Do FOO every N secs atmost K times

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
    global _test_cont
    for i in xrange(n):
        t = StTimer(1.0, 1, _cb)
    while _test_cont < n or stackless.getruncount() > 1:
        stackless.run()
        
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
