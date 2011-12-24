import traceback
import stackless

def MakeTasklet(func, *args, **kwargs):
    def _safe_tasklet():
        try:
            func(*args, **kwargs)
        except Exception:
            traceback.print_exc()
    return stackless.tasklet(_safe_tasklet)()
