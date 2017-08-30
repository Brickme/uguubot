" seen.py: written by sklnd in about two beers July 2009"

import time
import re
import datafiles

from util import hook, timesince, formatting

db_ready = False

with open("plugins/data/insults.txt") as f:
    insults = [line.strip() for line in f.readlines() if not line.startswith("//")]


def db_init(db):
    "check to see that our db has the the seen table and return a connection."
    db.execute("create table if not exists seen(name, time, quote, chan, host, primary key(name, chan))")
    db.commit()
    db_ready = True


def findnth(source, target, n):
    num = 0
    start = -1
    while num < n:
        start = source.find(target, start+1)
        if start == -1: return -1
        num += 1
    return start

def replacenth(source, old, new, n):
    p = findnth(source, old, n)
    if n == -1: return source
    return source[:p] + new + source[p+len(old):]


def correction(input,db,notice,say):
    splitinput = input.msg.split("/")
    nick = input.nick
    num=1
    if len(splitinput) > 3:
        if splitinput[1] == '': return
        if ' ' in splitinput[3]:
            nick = splitinput[3].split(' ')[1].strip()
            splitinput[3] = splitinput[3].split(' ')[0].strip()

        if len(splitinput[3]) > 2: 
            nick = splitinput[3].strip()
        else:
            if 'g' in splitinput[3]:
                num = 0
            else: 
                try: num = int(splitinput[3].strip())
                except: num = 1

    last_message = db.execute("select name, quote from seen where name like ? and chan = ?", (nick.lower(), input.chan.lower())).fetchone()

    if last_message:
        splitinput = input.msg.split("/")
        find = splitinput[1]
        replace = splitinput[2]
        if find in last_message[1]:
            if "\x01ACTION" in last_message[1]:
                msg = last_message[1].replace("\x01ACTION ", "/me ").replace("\x01", "")
            else:
                msg = last_message[1]

            if num == 0:
                say(u"<{}> {}".format(nick, msg.replace(find, "\x02" + replace + "\x02")))
            else:
                say(u"<{}> {}".format(nick, replacenth(msg,find,"\x02" + replace + "\x02",num)))
        #else:
            #notice(u"{} can't be found in your last message".format(find))
    else:
        if nick == input.nick:
            notice(u"I haven't seen you say anything here yet")
        else:
            notice(u"I haven't seen {} say anything here yet".format(nick))


@hook.singlethread
@hook.event('PRIVMSG', ignorebots=False)
def seen_sieve(paraml, input=None, db=None, bot=None, notice=None, say=None):
    if not db_ready: db_init(db)

    if re.match(r'^(s|S)/.*/.*\S*$', input.msg): 
        correction(input,db,notice,say)
        return

    # keep private messages private
    if input.chan[:1] == "#":
        db.execute("insert or replace into seen(name, time, quote, chan, host) values(?,?,?,?,?)", (input.nick.lower(), time.time(), input.msg.replace('\"', "").replace("'", ""), input.chan, input.mask))
        db.commit()
        # database.set(db,'users','mask',input.mask.lower().replace('~',''),'nick',input.nick.lower())
        # db.execute("UPDATE {} SET {} = '{}' WHERE {} = '{}';".format(table,field,value,matchfield,matchvalue))

@hook.command
def seen(inp, nick='', chan='', db=None, input=None, conn=None, notice=None, bot=None):
    "seen <nick> -- Tell when a nickname was last in active in one of this bot's channels."

    if inp.lower() == input.conn.nick.lower() or inp.lower() == nick.lower():
        phrase = datafiles.get_phrase(nick,insults,nick,conn,notice,chan)
        return phrase

    #if not re.match("^[A-Za-z0-9_|.\-\]\[]*$", inp.lower()):
    #    return "I can't look up that name, its impossible to use!"

    if not db_ready: db_init(db)

    last_seen = None
    db_results = db.execute("select name, time, quote, chan from seen where name like ?", (inp,))
    for row in db_results:
        last_seen = row

    if last_seen:
        reltime = timesince.timesince(last_seen[1])
        if last_seen[0] != inp.lower():  # for glob matching
            inp = last_seen[0]
        if last_seen[2][0:1] == "\x01":
            output = '{} was last seen {} ago: * {} {}'.format(inp, reltime, inp,
                                                             last_seen[2][8:-1])
        else:
            output = '{} was last seen {} ago in {} saying: {}'.format(inp, reltime, last_seen[3], last_seen[2])
    else:
        output = "I've never seen {} talking in this channel.".format(inp)
    return(formatting.output(db, input.chan, 'seen', [output]))

@hook.command(adminonly=True)
def resetseen(inp, chan='', db=None, notice=None, input=None):
    "resetseen <nick> -- Resets a user's last spoken line"
    inp = inp.split(' ')
    nick = inp[0]
    if len(inp) > 1: text = ' '.join(inp[1:])
    else: text = 'Theres Nothing Finer Than Scott Steiner'

    resetseendb(nick,chan,db, text)
    notice('Last spoken text for {} reset to {}.'.format(nick, text))

def resetseendb(inp, chan='', db=None, txt=''):
    print('Last spoken text reset for {}.'.format(inp))
    if not db_ready: db_init(db)

    seen_host = db.execute("select host from seen where name like ?", (inp,)).fetchone()[0]
    db.execute("insert or replace into seen(name, time, quote, chan, host) values(?,?,?,?,?)", (inp, time.time(), txt, chan, seen_host))
    db.commit()
