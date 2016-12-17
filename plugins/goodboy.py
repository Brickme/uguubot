#########################################################################################
# Name			Good Boy Points
# Description		Gives the user good boy points for tendies and McRibs
# Version		1.1.2 (2016-12-14)
# Contact		ScottSteiner@irc.rizon.net
# Website		https://github.com/ScottSteiner/uguubot
# Copyright		2016, ScottSteiner <nothingfinerthanscottsteiner@gmail.com>
# License		GPL version 3 or any later version; http://www.gnu.org/copyleft/gpl.html
#########################################################################################

from util import hook, formatting, database, timeformat
import random, json, time

phrases = {
	'great': ['You throw your piss jugs at mummy and scream about not getting you\'re tendies. She gives you {} to shut you up'],
	'good': ['You\'ve been a good boy and earned {} good boy points!'],
	'mediocre': ['You didn\'t do anything to earn good boy points!'],
	'bad': ['You were a bad boy!  You lost {} good boy points!'], 
	'awful': ['REEEEEEEEEEEEEEEEEEEEEEEEE. GET OUT NORMIE AND LEAVE {} GOOD BOY POINTS BEHIND']
}

items = {
	'tendies': {'price': 10, 'bonus': 0.05, 'description': 'Mommy\'s homemade tendies'},
	'piss bottle': {'price': 50, 'bonus': 0.25, 'description': 'A 2 liter mountain dew bottle so you never have to leave the room while shitposting on pedochan.'}
}

@hook.command('piss', autohelp=False)
@hook.command(autohelp=False)
def behave(inp, nick=None, db=None, input=None, notice=None):
	"behave -- be a good boy and earn tendies"

	global phrases
        nick = nick.lower()

	last_run = database.get(db,'goodboy','last','nick',nick) or 0
	last_run = int(float(last_run))
	next_run = last_run + 3600
	next_run = int(next_run)
	if time.time() <= next_run:
		delay = next_run - time.time()
		delay = timeformat.format_time(int(delay))
		notice(formatting.output(db, input.chan, 'Good Boy Points', ['You\'re going too fast!  Try again in {}.'.format(delay)]))
		return


	current = database.get(db,'goodboy','gbp','nick',nick) or 0

	command = input.trigger

	if command == 'behave': result = random.randrange(-2,10)
	else:			result = random.randrange(-10,20)

	current = int(current) + result

	if result > 10: phrase = random.choice(phrases['great'])
	elif result > 0: phrase = random.choice(phrases['good'])
	elif result == 0: phrase = random.choice(phrases['mediocre'])
	elif result > -10: phrase = random.choice(phrases['bad'])
	else: phrase = random.choice(phrases['awful'])

	database.set(db,'goodboy','gbp',unicode(current),'nick',nick)
	database.set(db,'goodboy','last',unicode(time.time()),'nick',nick)
	return formatting.output(db, input.chan, 'Good Boy Points', [phrase.format(abs(result)), 'You now have {} good boy points!'.format(current)])

@hook.command()
def buy(inp, nick=None, db=None, input=None, notice=None):
	"buy -- buy special presents with your good boy points"

	global items
	nick = nick.lower()
	current = database.get(db,'goodboy','gbp','nick',nick) or 0
	current = int(current)

	try:
		item = ' '.join(input.inp_unstripped.split()[1:])
		quantity = int(input.inp_unstripped.split()[0])
	except:
		item = inp
		quantity = 1

	if item not in items:
		notice(formatting.output(db, input.chan, 'Good Boy Points', ['Item not available in store.']))
	else:
		price = items[item]['price'] * quantity
		if current >= price:
			balance = current - price
			database.set(db,'goodboy','gbp',unicode(balance),'nick',nick)

			inventory = database.get(db,'goodboy','items','nick',nick) or "{}"
			inventory = json.loads(inventory)
			if item in inventory:	inventory[item] += quantity
			else: 			inventory[item]  = quantity

			inventory = json.dumps(inventory)
			database.set(db,'goodboy','items',inventory,'nick',nick)

			return formatting.output(db, input.chan, 'Good Boy Points', ['You purchased {} {} for {} good boy points.'.format(quantity, item, price), 'You now have {} good boy points!'.format(balance)])
		else:
			return formatting.output(db, input.chan, 'Good Boy Points', ['You can\'t afford that!  You have {} good boy points but need {} to buy {} {}!!'.format(current, price, quantity, item)])

@hook.command(autohelp=False)
def balance(inp, nick=None, db=None, input=None, notice=None):
	"balance -- check your good boy points balance"

	current = database.get(db,'goodboy','gbp','nick',inp)
	if current is False:
		nick = nick.lower()
		current = database.get(db,'goodboy','gbp','nick',nick) or 0
		return formatting.output(db, input.chan, 'Good Boy Points', ['You currently have {} good boy points.'.format(current)])
	return formatting.output(db, input.chan, 'Good Boy Points', ['{} currently has {} good boy points.'.format(inp, current)])

@hook.command(autohelp=False)
def inventory(inp, nick=None, db=None, input=None, notice=None):
	"inventory -- check your good boy points balance"

	inventory = database.get(db,'goodboy','items','nick',inp)
	if inventory is False:
		nick = nick.lower()
		inventory = database.get(db,'goodboy','items','nick',nick)
		if inventory is False: inventory = None
		else: inventory = json.loads(inventory)
		return formatting.output(db, input.chan, 'Good Boy Points', ['You currently have the following items: {}.'.format(dict2str(inventory))])
	inventory = json.loads(inventory)
	return formatting.output(db, input.chan, 'Good Boy Points', ['{} currently has the following items: {}.'.format(inp, dict2str(inventory))])

@hook.command('items', autohelp=False)
@hook.command(autohelp=False)
def store(inp, nick=None, db=None, input=None, notice=None):
	"store -- lists items you can purchase with good boy points"

	global items

	if inp in items:
		output = [inp, '{} gbp'.format(items[inp]['price']), items[inp]['description']]
	else:
		output = []
		for item in items:
			output.append('{}: {} gbp'.format(item, items[item]['price']))
		
	return formatting.output(db, input.chan, 'Good Boy Points Store', output)

@hook.command(autohelp=False, adminonly=True)
def gbpdebug(inp, db=None, input=None):
	if inp == '': nick = input.nick.lower()
	else: nick = inp.lower()
	info = db.execute("SELECT nick, gbp, items, last from goodboy where nick = '{}'".format(nick))
	for i in info:
		print(i)

@hook.command(autohelp=False, adminonly=True)
def gbpdelete(inp, db=None, input=None):
	if inp == '': nick = input.nick.lower()
	else: nick = inp.lower()
	db.execute("DELETE from goodboy WHERE nick = '{}';".format(nick))
	db.commit()
	gbpdebug(nick, db, input)

def dict2str(dict):
	return ', '.join('{} {}'.format(c,i) for i,c in sorted(dict.items()))
