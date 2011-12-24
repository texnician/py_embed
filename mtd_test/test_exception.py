import stackless
import traceback

yieldChannel = stackless.channel()
yieldChannel.preference = 1

def BeNice():
    yieldChannel.receive()

def ScheduleTasklets():
    # Only schedule as many tasklets as there are waiting when
    # we start.  This is because some of the tasklets we awaken
    # may BeNice their way back onto the channel.
    n = -yieldChannel.balance
    while n > 0:
        yieldChannel.send(None)
        n -= 1

    # Run any scheduled tasklets.  We should never find ourselves
    # having interrupted one, as that would be more likely to indicate
    # an infinite loop, as tasklets should use BeNice and never end
    # up in the scheduler.
    interruptedTasklet = stackless.run(1000000)
    if interruptedTasklet:
        # Print a stacktrace for the tasklet.
        raise RuntimeError("Better handling needed")

class TestErr(Exception):
    pass

def TestException():
    while 1:
        print fx
        BeNice()

t1 = stackless.tasklet(TestException)()

