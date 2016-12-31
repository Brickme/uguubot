#########################################################################################
# Name			steiner
# Description		Miscellanous triggers and functions which don't need their own home
# Version		1.0 (2016-12-28)
# Contact		ScottSteiner@irc.rizon.net
# Website		https://github.com/ScottSteiner/uguubot
# Copyright		2016, ScottSteiner <nothingfinerthanscottsteiner@gmail.com>
# License		GPL version 3 or any later version; http://www.gnu.org/copyleft/gpl.html
#########################################################################################

from util import hook, http, formatting
import re

hello_re = (r'^hello (.*?)(?: |)reddit', re.I)

@hook.regex(*hello_re)
@hook.command(autohelp=False)
def helloreddit(sub, db=None, input=None):
	'hello reddit -- First reddit thread (subreddit optional)'

	if type(sub) is not unicode: sub = sub.group(1)
	if sub == '': sub = 'all'
	output = reddit_top(sub)
	
	return formatting.output(db, input.chan, False, output)

def reddit_top(sub):
	api_url = 'http://www.reddit.com/r/{}.json'.format(sub)

	try:
		data = http.get_json(api_url)['data']['children'][0]['data']

		url = 'https://redd.it/{}'.format(data['id'])
		title = data['title']
		return ['{} {}'.format(title, url)]
	except Exception as e:
		return ['hello reddit', e]
