from mtd_lib import *

class PyCallback(ScriptSkillCallback):
    def __init__(self):
        ScriptSkillCallback.__init__(self)

    def DoSkill(self, data):
        print('Python callback DoSkill')
        print(dir(data))
        print(data)
        print(data.id)
        print(data.name)
        l = [i*2 for i in data.data]
        print(l)
        print(data.data)
        result = SkillResult()
        result.id = 10
        result.result = "python result"
        return result
        
def TestCallback():
    print('TestCallback')
    g_caller = GetCaller()
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

