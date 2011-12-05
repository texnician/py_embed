print('aaaaaaaaaa')
#import rpdb2; rpdb2.start_embedded_debugger('123')
from mtd_lib import *
import stackless
import Queue

class TestObj(object):
    pass

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
            return stackless.channel.receive(self)

cli_channel = QueuedChannel()

cli = StacklessClient(10, cli_channel)
cli.SetupTasklet()
def MakeEvent():
    ev = CliEvent()
    ev.msg_ = "hello"
    ev.type_ = 1
    return ev
    
stackless.tasklet(cli_channel.send)(MakeEvent())
stackless.run()



