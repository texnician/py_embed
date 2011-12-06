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

def PyLoop(cli):
    MainLoop(cli)
    while not cli.IsQuit():
        try:
            ev = cli.Receive()
            if ev.type_ == 0:
                print(cli.RoleId(), 'Quit')
                cli.Quit()
            else:
                print('++++++++msg_id: {0}, msg: {1}'.format(ev.type_, ev.msg_))
        except Exception as e:
            print e
            break
    
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

#t = TestThread(100000)

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
cli.SetupTasklet()

ch2 = QueuedChannel()
cli2 = StacklessClient(11, ch2)
cli2.SetupTasklet()

ch3 = QueuedChannel()

#cli3 = stackless.tasklet(PyLoop)(None)

def MakeEvent(tp, msg):
    ev = CliEvent()
    ev.msg_ = msg
    ev.type_ = tp
    return ev

if __name__ == '__main__':
    ch1.send(MakeEvent(1, 'hello'))
    ch2.send(MakeEvent(1, 'world'))
    ch1.send(MakeEvent(0, 'py'))
    stackless.run()
