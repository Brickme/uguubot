#########################################################################################
# Name			Good Boy Points
# Description		Gives the user good boy points for tendies and McRibs
# Version		1.1.1 (2016-12-14)
# Contact		ScottSteiner@irc.rizon.net
# Website		https://github.com/ScottSteiner/uguubot
# Copyright		2016, ScottSteiner <nothingfinerthanscottsteiner@gmail.com>
# License		GPL version 3 or any later version; http://www.gnu.org/copyleft/gpl.html
#########################################################################################

from util import hook, formatting, database
import random

phrases = {
	'great': ['You throw your piss jugs at mummy and scream about not getting you\'re tendies. She gives you {} to shut you up'],
	'good': ['You\'ve been a good boy and earned {} good boy points!'],
	'mediocre': ['You didn\'t do anything to earn good boy points!'],
	'bad': ['You were a bad boy!  You lost {} good boy points!'], 
	'awful': ['REEEEEEEEEEEEEEEEEEEEEEEEE. GET OUT NORMIE AND LEAVE {} GOOD BOY POINTS BEHIND']
}

@hook.command('piss', autohelp=False)
@hook.command(autohelp=False)
def behave(inp, nick=None, db=None, input=None):
	"behave -- be a good boy and earn tendies"

	global phrases
        nick = nick.lower()
	current = database.get(db,'users','gbp','nick',nick) or 0

	command = input.trigger

	if command == 'behave': result = random.randrange(-2,10)
	else:			result = random.randrange(-10,20)

	current = int(current) + result

	if result > 10: phrase = random.choice(phrases['great'])
	elif result > 0: phrase = random.choice(phrases['good'])
	elif result == 0: phrase = random.choice(phrases['mediocre'])
	elif result > -10: phrase = random.choice(phrases['bad'])
	else: phrase = random.choice(phrases['awful'])

	database.set(db,'users','gbp',unicode(current),'nick',nick)
	return formatting.output(db, input.chan, 'Good Boy Points', [phrase.format(abs(result)), 'You now have {} good boy points!'.format(current)])

