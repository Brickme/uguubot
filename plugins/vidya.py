#########################################################################################
# Name			Video Game Info
# Description		Information about video games
# Version		1.0 (2016-12-30)
# Contact		ScottSteiner@irc.rizon.net
# Website		https://github.com/ScottSteiner/uguubot
# Copyright		2016, ScottSteiner <nothingfinerthanscottsteiner@gmail.com>
# License		GPL version 3 or any later version; http://www.gnu.org/copyleft/gpl.html
#########################################################################################

import decimal
from util import hook, http, formatting
from lxml import html
from HTMLParser import HTMLParser
unescape = HTMLParser().unescape

@hook.command(autohelp=True)
def gameinfo(inp, db=None, input=None):
	'gameinfo -- Gets steam game information'

	appid = app_name_to_id(inp)

	data = game_info(appid)

	name = unescape(data['name'])
	developer = ', '.join(data['developers']) or []
	description = unescape(data['short_description'])
	player_count = '{:,} current players'.format(current_players(appid))

	free = data['is_free']
	if free == True:
		price = 'Free To Play'
	else:
		current_price = data['price_overview']['final'] or 0
		current_price = decimal.Decimal(current_price) / 100
		initial_price = data['price_overview']['initial'] or 0
		initial_price = decimal.Decimal(initial_price) / 100
		discount = data['price_overview']['discount_percent']

		if current_price == initial_price: price = '${}'.format(current_price)
		else:				   price = '${} (reg ${}, {}% off)'.format(current_price, initial_price, discount)

	output = [name,developer,price, player_count, description]
	return formatting.output(db, input.chan, 'Vidya', output)

@hook.command('players', autohelp=True)
@hook.command(autohelp=True)
def compare_players(inp, db=None, input=None):
	output = []

	games = inp.split('|')

	for game in games:
		appid = app_name_to_id(game)
		info = game_info(appid)
		name = info['name'].encode('ascii', 'ignore')
		output.append('{}: {:,} current players'.format(name, current_players(appid)))
	return formatting.output(db, input.chan, 'Vidya', output)

def current_players(appid):
	api_url = 'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1'

	try:
		data = http.get_json(api_url, appid=appid)
		count = data['response']['player_count']
		return count
	except Exception as e:
		return e

def app_name_to_id(appname):
	try: return str(int(appname))
	except: pass
	search_url = 'http://store.steampowered.com/search/'

	body = http.get(search_url, term=appname)
	body = html.fromstring(body)
	id = body.xpath('//a[contains(@class, "search_result_row")]/@data-ds-appid')[0]
	return id

def game_info(appid):
	api_url = 'http://store.steampowered.com/api/appdetails'

	data = http.get_json(api_url, appids=appid)[appid]['data']
	return data
