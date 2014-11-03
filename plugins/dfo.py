# Written by ScottSteiner

# Dice roll portion written by Scaevolus, updated by Lukeroge

import re
import random

from util import hook

def dforoll (count, n):
    "roll an n-sided die count times"
    if count < 100:
      rolls = []
      x = 0
      while x < count:
        result = random.randint(1, 10)
        rolls.append(result)
        if result < 10: x += 1
      return rolls

@hook.command('dfo')
def dfo(inp, nick=None):
    "roll2 <dice> <action> -- Simulates dicerolls." \

    try:
      count = int(inp.split(' ', 1)[0])
    except ValueError:
      return "Invalid diceroll"

    if count >= 100:
      return "Too many dice!"
 
    rolls = dforoll(count, 10)
    total = sum(rolls)
    numreroll = rolls.count(10)
    numsuccess = rolls.count(9)+numreroll
    numfail = rolls.count(1)

    if len(inp.split(' ', 1)) > 1:
      desc = "to {} ".format(inp.split(' ', 1)[1].strip())
    else: desc = ""

    end = ""
    if numreroll > 0:
      end = "{} (\x0313\x02+{}\x02 reroll{}\x03)".format(end,str(numreroll),"s"[numreroll==1:])
    if numsuccess > 0:
      end = "{} (\x0309\x02{}\x02 success{}\x03)".format(end,str(numsuccess),"es"[numsuccess==1:])
    if numfail > 0:
      end = "{} (\x0304\x02{}\x02 critical failure{}\x03)".format(end,str(numfail),"s"[numfail==1:])

    return "\x02{}\x02 rolls {} times {}{}{}".format(nick, count, desc, rolls, end)
