from util import hook
import sched, time

def check_for_timers(inp):
    split = inp.split(' ')
    timer = 0
    lastparam = split[-1].lower()
    if   'sec'   in lastparam: timer = int(split[-2])
    if   'min'   in lastparam: timer = int(split[-2]) * 60
    elif 'hour'  in lastparam: timer = int(split[-2]) * 60 * 60
    elif 'day'   in lastparam: timer = int(split[-2]) * 60 * 60 * 24
    elif 'week'  in lastparam: timer = int(split[-2]) * 60 * 60 * 24 * 7
    elif 'month' in lastparam: timer = int(split[-2]) * 60 * 60 * 24 * 30
    elif 'year'  in lastparam: timer = int(split[-2]) * 60 * 60 * 24 * 365
    elif  lastparam.isdigit(): timer = int(lastparam) * 60
    return timer

def execute(command, conn):
    conn.send(command)

def schedule(timer, priority, command, conn):
    s = sched.scheduler(time.time, time.sleep)
    s.enter(timer, priority, execute, (command, conn))
    s.run()
