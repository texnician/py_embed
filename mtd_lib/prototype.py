import stackless
import Queue

def RunRound():
    ai_cmd = ai_server.Think()
    pass



def PlayerMove():
    EmitEvent(MoveEvent())

def CombatWin():
    win_event = WinEvent()
    EmitEvent(WinEvent())

EVENT_MANAGER_MAP = {}

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

g_ch = stackless.channel()

def BeNice():
    g_ch.receive()
    
class EventManager(object):
    def __init__(self):
        self.listener_map = {}
        self.ch = QueuedChannel()

    def ManageEventInRegion(self, *regions):
        for r in regions:
            EVENT_MANAGER_MAP[r] = self.ch
        
    def AddListener(self, ev_type, listenr):
        try:
            self.listener_map[ev_type].append(listenr)
        except KeyError:
            self.listener_map[ev_type] = [listenr]

    def Run(self):
        ev_count = 0
        while 1:
            ev = self.ch.receive()
            for l in self.listener_map[ev.tp]:
                l.OnEvent(ev)
            ev_count += 1
            if ev_count >= 1000:
                print(ev_count)
                ev_count = 0
                BeNice()

# Sync system listen for MOVE EVENT in SCENE
# Sync system listen for PUSH TREE EVENT in SCENE
# Sync system listen for COLLECT ITEM EVENT in SCENE
# Sync system listen for EQUIPMENT CHANGE EVENT in SCENE
# Chat system listen for CHAT EVENT in SCENE
# Item system listen for USE ITEM EVENT in WORLD
# Item system listen for COLLECT_ITEM EVENT in WORLD
# Card system listen for SEAL EVENT in WORLD
# Quest system listen for COMBAT WIN event in WORLD
# Experience system listen for COMBAT WIN event in WORLD
# Experience system listen for QUEST COMPLETE event in WORLD
# Quest system listen for COLLECT ITEM EVENT in WORLD

EVENT_MANAGER = EventManager()

class GameEvent(object):
    def __init__(self, tp):
        self.tp = tp
        
    def Emit(self):
        EVENT_MANAGER.ch.send(self)

def AddEventListener(type, listenr):
    EVENT_MANAGER.AddListener(type, listenr)

class System(object):
    def __init__(self):
        AddEventListener('move', self)
        pass

    def OnMessage(self):
        pass

    def OnEvent(self, ev):
        # do sth
        GameEvent('move').Emit()

stackless.tasklet(EVENT_MANAGER.Run)()
sys = System()

if __name__ == '__main__':
    e = GameEvent('move')
    e.Emit()
    
