import re
from util import hook, http, formatting
from HTMLParser import HTMLParser

twitch_re = (r'(.*:)//(twitch.tv|www.twitch.tv)(:[0-9]+)?(.*)', re.I)
multitwitch_re = (r'(.*:)//(www.multitwitch.tv|multitwitch.tv)/(.*)', re.I)


def test(s):
    valid = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/')
    return set(s) <= valid


def truncate(msg):
    nmsg = msg.split(" ")
    out = None
    x = 0
    for i in nmsg:
        if x <= 7:
            if out:
                out = out + " " + nmsg[x]
            else:
                out = nmsg[x]
        x += 1
    if x <= 7:
        return out
    else:
        return out + "..."


@hook.regex(*multitwitch_re)
def multitwitch_url(match):
    usernames = match.group(3).split("/")
    out = ""
    for i in usernames:
        if not test(i):
            print "Not a valid username"
            return None
        if out == "":
            out = twitch_lookup(i)
        else:
            out = out + " \x02|\x02 " + twitch_lookup(i)
    return out


@hook.regex(*twitch_re)
def twitch_url(match):
    bit = match.group(4).split("#")[0]
    location = "/".join(bit.split("/")[1:])
    if not test(location):
        print "Not a valid username"
        return None
    return formatting.output('Twitch', twitch_lookup(location))


# @hook.command('twitchviewers')
@hook.command
def twitch(inp):
    inp = inp.split("/")[-1]
    if test(inp):
        location = inp
    else:
        return "Not a valid channel name."
    return formatting.output('Twitch', twitch_lookup(location))


def twitch_lookup(location):
    locsplit = location.split("/")
    if len(locsplit) > 1 and len(locsplit) == 3:
        channel = locsplit[0]
        type = locsplit[1]  # should be b or c
        id = locsplit[2]
    else:
        channel = locsplit[0]
        type = None
        id = None
    h = HTMLParser()
    fmt = "{}: {} playing {} ({})"  # Title: nickname playing Game (x views)
    if type and id:
        if type == "b":  # I haven't found an API to retrieve broadcast info
            soup = http.get_soup("http://twitch.tv/" + location)
            title = soup.find('span', {'class': 'real_title js-title'}).text
            game = soup.find('a', {'class': 'game js-game'}).text
            views = soup.find('span', {'id': 'views-count'}).text + " view"
            views = views + "s" if not views[0:2] == "1 " else views
            return [channel, title, game, views]
        elif type == "c":
            data = http.get_json("https://api.twitch.tv/kraken/videos/" + type + id)
            title = data['title']
            game = data['game']
            views = str(data['views']) + " view"
            views = views + "s" if not views[0:2] == "1 " else views
            return [channel, title, game, views]
    else:
        try:
            data = http.get_json("https://api.twitch.tv/kraken/streams/" + channel)['stream']
        except:
            return
	if data is not None:
		channel = data['channel']['display_name']
	        title = data['channel']['status']
	        game = data['channel']['game']
	        status = '\x0309\x02Online\x02\x0f'
		viewers = '{} viewers'.format(data['viewers'])
	        return [channel, title, game, viewers, status]
	else:
	        try:
	            data = http.get_json("https://api.twitch.tv/kraken/channels/" + channel)
	        except:
	            return
		channel = data['channel']['display_name']
	        title = data['status']
	        game = data['game']
	        status = "\x034\x02Offline\x02\x0f"
	        return [channel, title, game, status]

