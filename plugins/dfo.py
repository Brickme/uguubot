# Written by ScottSteiner

# Dice roll portion written by Scaevolus, updated by Lukeroge

import re
import random

from util import hook

def dforoll (count, n):
    "roll an n-sided die count times"
    rolls = []
    rollstrings = []
    x = 0
    while x < count:
      numresult = random.randint(1, 10)
      if numresult >= 9:
        result = "\x0309{}\x03".format(numresult)
        if numresult == 10:
          result = "\x02{}\x02".format(result)
      elif numresult == 1:
        result = "\x02\x0304{}\x03\x02".format(numresult)
      else:
        result = str(numresult)      

      rolls.append(numresult)
      rollstrings.append(result)
      if numresult < 10: x += 1
    return [rolls, rollstrings]

@hook.command('roll')
def dfo(inp, nick=None):
    "roll <dice> <action> -- Simulates dicerolls." \

    try:
      count = int(inp.split(' ', 1)[0])
      action = " ".join(inp.split(' ', 1)[1:])
    except ValueError:
      count = 2
      action = inp

    if count > 50:
      return "Too many dice!"

    result = dforoll(count, 10)
    rolls = result[0]
    rollstrings = result[1]
    total = sum(rolls)
    numreroll = len(rolls) - count
    numsuccess = rolls.count(9)+numreroll
    numfail = rolls.count(1)

    if len(action) > 1:
      desc = "to {} ".format(action.strip())
    else: desc = ""

    end = ""
    if numreroll > 0:
      end = "{} (\x0313\x02+{}\x02 reroll{}\x03)".format(end,str(numreroll),"s"[numreroll==1:])
    if numsuccess > 0:
      end = "{} (\x0309\x02{}\x02 success{}\x03)".format(end,str(numsuccess),"es"[numsuccess==1:])
    if numfail > 0:
      end = "{} (\x0304\x02{}\x02 critical failure{}\x03)".format(end,str(numfail),"s"[numfail==1:])

    rolls="[{}]".format(", ".join(rollstrings))

    return u"\x02{}\x02 rolls {} times {}{}{}".format(nick, count, desc, rolls, end)
