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
from util import hook, http

@hook.command(autohelp=False)
def streaminfo(url, reply=None, bot=None):
	'streaminfo -- Gets stream info'

	streams = bot.config["plugins"]["streaminfo"].get("streams", {})
	viewers_colors = bot.config["plugins"]["streaminfo"].get("colors", {25: '09',50: '08',75: '07'})

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
		except Exception as e:
			reply(u'\x02Streaminfo\x02 | {}: \x1f\x0311{}\x03\x1f | \x0304Error: {}'.format(stream_name, stream_url, e))
			continue
		try:
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
				for i in sorted(viewers_colors.items()):
					if ((100 * viewers_current) / viewers_max) < i[0]:
						viewers_color = i[1]
						break
			
			viewers = ' | \x03{}{}/{}\x03'.format(viewers_color, viewers_current, viewers_max)
			reply(u'\x02Streaminfo\x02 | {}: \x1f\x0311{}\x03\x1f{}{}'.format(stream_name, stream_url, viewers, extra_info))
		except Exception as e:
			print('\x02Streaminfo\x02 | {}: \x1f\x0311{}\x03\x1f | \x0304NOT LIVE [{}: {}]'.format(stream_name, stream_url, e, e.__doc__))

