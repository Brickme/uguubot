#########################################################################################
# Name			streaminfo
# Description		Fetches stream information
# Version		1.0 (2015-04-12)
# Contact		ScottSteiner@irc.rizon.net
# Website		https://github.com/ScottSteiner/uguubot
# Copyright		2015, ScottSteiner <nothingfinerthanscottsteiner@gmail.com>
# License		GPL version 3 or any later version; http://www.gnu.org/copyleft/gpl.html
#########################################################################################

import urllib2
from util import hook, http, formatting

@hook.command(autohelp=False)
def streaminfo(url, chan=None, reply=None, bot=None, input=None, db=None):
	'streaminfo -- Gets stream info'

	streams = bot.config["plugins"]["streaminfo"].get("streams", {})
	viewers_colors = bot.config["plugins"]["streaminfo"].get("colors", {"0": '09',"33": '08',"66": '07'})

	stream_info = getinfo(streams, viewers_colors)
	for s in sorted(stream_info.keys()):
	    reply(formatting.output(db, input.chan, 'streaminfo', stream_info[s]))

def getinfo(streams, viewers_colors):
	output = {}
	for stream_name in streams:
		stream_url = '{}/{}'.format(streams[stream_name]['root'], streams[stream_name]['stream'])
		viewers_max = streams[stream_name]['viewers_max']

		status = '{}/{}?mount=/{}'.format(streams[stream_name]['root'], streams[stream_name]['status'], streams[stream_name]['stream'])
		try:
			if streams[stream_name]['status'] == 'status-json.xsl':
				info = http.get_json(status)['icestats']
				viewers_current = int(info['source']['listeners'])
			elif streams[stream_name]['status'] == '':
				raise Exception('\x0307May Be Live \x0304Status Page Not Found')
			else:
				info = http.get_xml(status).text
				viewers_current = int(info.split(',')[9])

			extra_info = ''
			if 'extra_info' in streams[stream_name]:
				extra_info = ' | {}'.format(streams[stream_name]['extra_info'])
			if viewers_current == 0:
				status_code = urllib2.urlopen(stream_url, timeout=2).getcode()
				if status_code != 200: raise Exception('Stream not found')

			if viewers_max == '???':
				viewers_color = '03'
			else:
				viewers_color = '04'
				viewers_percent = (100 * viewers_current) / viewers_max
				for i in sorted(viewers_colors.items(), reverse=True):
					if (viewers_percent >= int(i[0])):
						viewers_color = i[1]
						break
			
			viewers = '\x03{}{}/{}\x03{}'.format(viewers_color, viewers_current, viewers_max, extra_info)
			stream_url = '\x1f\x0311{}\x03\x1f'.format(stream_url)

			output[stream_name] = [stream_name, stream_url, viewers]
		except Exception as e:
			error_info = '\x0304NOT LIVE [{}: {}]'.format(e, e.__doc__)
			print(formatting.output('', [], 'streaminfo', [stream_name, stream_url, error_info]))
	return(output)
