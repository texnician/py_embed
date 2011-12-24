import threading
import stackless

commandChannel = stackless.channel()

def master_func():
    print('MAIN SEND 1')
    commandChannel.send("ECHO 1")
    print('MAIN SEND 2')
    commandChannel.send("ECHO 2")
    print('MAIN SEND 3')
    commandChannel.send("ECHO 3")
    print('MAIN SEND 4')
    commandChannel.send("QUIT")

def slave_func():
    print "SLAVE STARTING"
    while 1:
        command = commandChannel.receive()
        print "SLAVE:", command
        if command == "QUIT":
            break
    print "SLAVE ENDING"

def scheduler_run(tasklet_func):
    t = stackless.tasklet(tasklet_func)()
    while t.alive:
        stackless.run()

thread = threading.Thread(target=scheduler_run, args=(master_func,))
thread.start()

scheduler_run(slave_func)
