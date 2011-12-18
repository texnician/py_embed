print('aaaaaaaaaa')

    # while 1:
    #     ev = cli.Receive()
    #     print('ev', ev)
    #     if ev.type_ == 0:
    #         break
    #     else:
    #         print('++++++++msg_id: {0}, msg: {1}'.format(ev.type_, ev.msg_))
    
#import rpdb2; rpdb2.start_embedded_debugger('123')
from mtd_lib import *
import stackless
import Queue
import pickle

pickle_ch = stackless.channel()

def PyLoop(cli):
    while not cli.IsQuit():
        try:
            ev = cli.Receive()
            if ev.type_ == 0:
                print(cli.RoleId(), 'Quit')
                cli.Quit()
            else:
                #print('{0} type: {1}, msg: {2}'.format(cli.RoleId(), ev.type_, ev.msg_))
                pass
        except Exception as e:
            print e
            break

class TestObj(object):
    def Foo(self):
        print('Foo callllllllllllllllllllllllllllllllllllllllllllllllllll')
        return 3

def MakeTestObj():
    return TestObj()

class PyCallback(ScriptSkillCallback):
    def __init__(self):
        ScriptSkillCallback.__init__(self)

    def DoSkill(self, data):
        t.start()
        print('Python callback DoSkill')
        print(dir(data))
        print(TestObj())
        print(data)
        print(data.id)
        print(data.name)
        l = [i*2 for i in data.data]
        print(l)
        result = SkillResult()
        result.id = 1
        result.result = "python result"
        return result
    

    def DoVoid(self):
        print('DoVoid')
        print('join', t.join())
        
def TestCallback():
    print('TestCallback')
    g_caller = GetCaller()
    s = StrFoo()
    g_caller.TestString(s);
    cb = PyCallback()
    print(dir(cb))
    try:
        if g_caller.SetPyCallback(cb):
            cb.__disown__()
            pass
    except Exception as e:
        print(e)
        print("Unexpected error:")
    print('callback setted')

import threading

class TestThread(threading.Thread):
    def __init__(self, n):
        threading.Thread.__init__(self)
        self.n = n

    def run(self):
        while self.n > 0:
            self.n -= 1
        print('Do something useless')
        return 'done'

t = TestThread(100000)

# def ping():
#     print('ping')
#     pong()

# def pong():
#     print('pong')
#     ping()


ping_channel = stackless.channel()
pong_channel = stackless.channel()

def ping():
    while ping_channel.receive(): #blocks here
        print('longlonglonglonglonglonglonglonglonglonglonglonglonglonglonglongping')
        pong_channel.send("from ping")

def pong():
    while pong_channel.receive():
        print('longlonglonglonglonglonglonglonglonglonglonglonglonglonglonglongpong')
        ping_channel.send("from pong")



#stackless.tasklet(ping)()
#stackless.tasklet(pong)()

# # we need to 'prime' the game by sending a start message
# # if not, both tasklets will block
#stackless.tasklet(ping_channel.send)('startup')

class QueuedChannel(stackless.channel):
    def __init__(self, size=1024):
        stackless.channel.__init__(self)
        self.msgq = Queue.Queue(size)
        
    def send(self, d):
        if self.balance < 0:
            stackless.channel.send(self, d)
        else:
            self.msgq.put(d)

    def receive(self):
        if self.msgq.qsize() > 0:
            return self.msgq.get()
        else:
            ev = stackless.channel.receive(self)
            return ev

ch1 = QueuedChannel()

cli = StacklessClient(10, ch1)
#cli.SetupTasklet()

ch2 = QueuedChannel()
cli2 = StacklessClient(11, ch2)
#cli2.SetupTasklet()

ch3 = QueuedChannel()

#cli3 = stackless.tasklet(PyLoop)(None)

class PyClient(object):
    def __init__(self, roleid, ch):
        self.roleid = roleid
        self.ch = ch
        self.is_quit = False
        self.task = None
        
    def SetupTasklet(self):
        self.task = stackless.tasklet(PyLoop)
        self.task(self)

    def IsQuit(self):
        return self.is_quit

    def Receive(self):
        return self.ch.receive()

    def Send(self, ev):
        self.ch.send(ev)
    
    def Quit(self):
        self.is_quit = True

    def RoleId(self):
        return self.roleid

class PyEvent(object):
    def __init__(self):
        self.type_ = 0
        self.msg_ = None
        
def MakeEvent(tp, msg):
    ev = CliEvent()
    ev.msg_ = msg
    ev.type_ = tp
    return ev

ch_list = []
ts_list = []
def InitClient(n):
    for i in xrange(n):
        ch = QueuedChannel()
        ch_list.append(ch)
        ts = StacklessClient(i, ch)
        ts.SetupTasklet()
        ts_list.append(ts)
num = 5000
#InitClient(num)

def PickleClient():
    roleid = pickle_ch.receive()
    pickle.dump(ts_list[roleid].task, file('role{0}.pickle'.format(roleid), 'wb'))
    
# stackless.tasklet(PickleClient)()

def RunIt():
    stackless.run()
    from random import randint
    ev_num = 1000000
    EV = MakeEvent(1, 'hello')
    for i in xrange(ev_num):
        idx = i % 1
        #idx = randint(0, num-1)
        ch_list[idx].send(EV)

if __name__ == '__main__':
    from timeit import Timer
    t = Timer("RunIt()", "from __main__ import RunIt")
    print t.timeit(1)
