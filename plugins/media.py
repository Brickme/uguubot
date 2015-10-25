# IMDb lookup plugin by Ghetto Wizard (2011).

from util import hook, http, formatting
import re

import datetime
from urllib2 import URLError
from zipfile import ZipFile
from cStringIO import StringIO

from lxml import etree
from util import hook, http, web


base_url = "http://thetvdb.com/api/"

# http://thetvdb.com/api/GetSeries.php?seriesname=clannad

def get_zipped_xml(*args, **kwargs):
    try:
        path = kwargs.pop("path")
    except KeyError:
        raise KeyError("must specify a path for the zipped file to be read")
    zip_buffer = StringIO(http.get(*args, **kwargs))
    return etree.parse(ZipFile(zip_buffer, "r").open(path))

def get_episodes_for_series(seriesname, bot):
    res = {"error": None, "ended": False, "episodes": None, "name": None}
    # http://thetvdb.com/wiki/index.php/API:GetSeries

    api_key = bot.config.get("api_keys", {}).get("tvdb", None)
    if not api_key:
        return "error: no api key set"

    try:
        query = http.get_xml(base_url + 'GetSeries.php', seriesname=seriesname)
    except URLError:
        res["error"] = "error contacting thetvdb.com"
        return res

    series_id = query.xpath('//seriesid/text()')

    if not series_id:
        res["error"] = "unknown tv series (using www.thetvdb.com)"
        return res

    series_id = series_id[0]

    try:
        series = get_zipped_xml('{}{}/series/{}/all/en.zip'.format(base_url, api_key, series_id), path="en.xml")
    except URLError:
        res["error"] = "error contacting thetvdb.com"
        return res

    series_name = series.xpath('//SeriesName/text()')[0]

    if series.xpath('//Status/text()')[0] == 'Ended':
        res["ended"] = True

    res["episodes"] = series.xpath('//Episode')
    try:
        res["airtime"] = series.xpath('//Airs_Time/text()')[0]
    except:
        res["airtime"] = 'N/A'
    res["name"] = series_name
    return res


def get_episode_info(episode):
    first_aired = episode.findtext("FirstAired")

    try:
        airdate = datetime.date(*map(int, first_aired.split('-')))
    except (ValueError, TypeError):
        return None

    episode_num = "S%02dE%02d" % (int(episode.findtext("SeasonNumber")),
                                  int(episode.findtext("EpisodeNumber")))

    episode_name = episode.findtext("EpisodeName")
    # in the event of an unannounced episode title, users either leave the
    # field out (None) or fill it with TBA
    if episode_name == "TBA":
        episode_name = None

    episode_summary = episode.findtext("Overview")

    episode_desc = episode_num
    if episode_name:
        episode_desc += u' - {}'.format(episode_name)
    return (first_aired, airdate, episode_desc, episode_summary)




@hook.command
@hook.command('show')
@hook.command('series')
def tv(inp, bot=None):
    ".tv <series> -- get info for the <series>"
    res = {"error": None, "ended": False, "episodes": None, "name": None}
    # http://thetvdb.com/wiki/index.php/API:GetSeries
    try:
        query = http.get_xml(base_url + 'GetSeries.php', seriesname=inp)
    except URLError as e:
        return e
    series_id = ""
    try: series_id = query.xpath('//id/text()')
    except: print "Failed"

    if not series_id:
        return "\x02Could not find show:\x02 {}".format(inp)
    else:
        series_name = query.xpath('//SeriesName/text()')[0]
        overview = query.xpath('//Overview/text()')[0]
        firstaired = query.xpath('//FirstAired/text()')[0]
        tvdb_url = web.isgd("http://thetvdb.com/?tab=series&id={}".format(series_id[0]))
        status = get_status(inp, bot)
	if len(status) > 1:
		(airdate, airtime, episode_number, episode_name, summary) = status
		status = u"Next Episode: {} {} ({})".format(airdate, airtime, episode_name)

    if len(status) == 1:
	status = status[0]
	if status == "ended":
		status = "Ended"
	elif status == "noeps":
		status = "No new episodes"

    return formatting.output('TV', [u'\x02{}\x02 ({}) \x02-\x02 \x02{}\x02 - {} - {}'.format(series_name, firstaired, status, tvdb_url, overview)])

@hook.command('next')
@hook.command
def tv_next(inp, bot=None):
    ".tv_next <series> -- get the next episode of <series>"
    status = get_status(inp, bot)
    
    if len(status) == 1:
	if status[0] == "ended":
		return "{} has ended.".format(inp)
	elif status[0] == "noeps":
		return "No new episodes for {}.".format(inp)
	else:
		return status[0]
    else:
	(airdate, airtime, episode_number, episode_name, summary) = status

	return formatting.output("TV", [u"\x02Next Episode Name\x02: {} ({})".format(episode_name, episode_number), "\x02Airdate\x02: {} {}".format(airdate, airtime), u"\x02Summary\x02: {}".format(summary)])

def get_status(seriesname, bot):

    episodes = get_episodes_for_series(seriesname, bot)

    if episodes["error"]:
        return episodes["error"]

    series_name = episodes["name"]
    ended = episodes["ended"]
    airtime = episodes["airtime"]
    episodes = episodes["episodes"]

    if ended:
        return ["ended"]

    next_eps = []
    today = datetime.date.today()

    for episode in reversed(episodes):
        ep_info = get_episode_info(episode)

        if ep_info is None:
            continue

        (first_aired, airdate, episode_desc, episode_summary) = ep_info
        try:
            (episode_number, episode_name) = episode_desc.split(' - ', 1)
        except:
            (episode_number, episode_name) = [episode_desc, 'N/A']
        if airdate > today:
            next_eps.insert(0,[first_aired, airtime, episode_number, episode_name, episode_summary])
        elif airdate == today:
            next_eps.insert(0,["Today", airtime, episode_number, episode_name, episode_summary])
        else:
            #we're iterating in reverse order with newest episodes last
            #so, as soon as we're past today, break out of loop
            break

    if not next_eps:
        return ["noeps"]

    return next_eps[0]

@hook.command
@hook.command('tv_prev')
@hook.command('prev')
@hook.command('last')
def tv_last(inp, bot=None):
    ".tv_last <series> -- gets the most recently aired episode of <series>"

    episodes = get_episodes_for_series(inp, bot)

    if episodes["error"]:
        return episodes["error"]

    series_name = episodes["name"]
    ended = episodes["ended"]
    episodes = episodes["episodes"]

    prev_ep = None
    today = datetime.date.today()

    for episode in reversed(episodes):
        ep_info = get_episode_info(episode)

        if ep_info is None:
            continue

        (first_aired, airdate, episode_desc) = ep_info

        if airdate < today:
            #iterating in reverse order, so the first episode encountered
            #before today was the most recently aired
            prev_ep = '{} ({})'.format(first_aired, episode_desc)
            break

    if not prev_ep:
        return "There are no previously aired episodes for {}".format(series_name)
    if ended:
        return '{} ended. The last episode aired {}'.format(series_name, prev_ep)
    return "The last episode of {} aired {}".format(series_name, prev_ep)

@hook.command('tonight', autohelp=False)
@hook.command(autohelp=False)
def tv_tonight(inp,bot=None):
    '.tonight -- gets upcoming TV shows from Sickbeard'

    api_key = bot.config.get("api_keys", {}).get("sickbeard_key", None)
    api_ip = bot.config.get("api_keys", {}).get("sickbeard_ip", None)
    if not api_key:
        return formatting.output("TV Tonight", ["Error: No API Key set"])

    sickbeard_url = "http://{}/api/{}/?cmd=future&sort=date&type=today".format(api_ip, api_key)
    sickbeard_data = http.get_json(sickbeard_url)['data']['today']

    results = {}
    output = []

    for show in sickbeard_data:
        showinfo = '{} ({})'.format(show['show_name'], show['network'])

        airtime = show['airs'].split(' ', 1)[1]
        try:
            airtime = datetime.datetime.strptime(airtime, '%H:%M').strftime('%I:%M %p')
        except:
            pass
        if airtime in results:
            results[airtime].append(showinfo)
        else:
            results[airtime] = [showinfo]

    for t in sorted(results.keys()):
	output.append('\x02{}\x02: {}'.format(t, ', '.join(results[t])))
    if results == {}:
        return formatting.output("TV Tonight", ["No shows airing tonight"])

    return formatting.output("TV Tonight", output)


id_re = re.compile("tt\d+")

@hook.command('movie')
@hook.command
def imdb(inp):
    "imdb <movie> -- Gets information about <movie> from IMDb."

    strip = inp.strip()

    if id_re.match(strip):
        content = http.get_json("http://www.omdbapi.com/", i=strip)
    else:
        content = http.get_json("http://www.omdbapi.com/", t=strip)

    if content.get('Error', None) == 'Movie not found!':
        return 'Movie not found!'
    elif content['Response'] == 'True':
        content['URL'] = 'http://www.imdb.com/title/%(imdbID)s' % content

        out = '\x02%(Title)s\x02 (%(Year)s) (%(Genre)s): %(Plot)s'
        if content['Runtime'] != 'N/A':
            out += ' \x02%(Runtime)s\x02.'
        if content['imdbRating'] != 'N/A' and content['imdbVotes'] != 'N/A':
            out += ' \x02%(imdbRating)s/10\x02 with \x02%(imdbVotes)s\x02' \
                   ' votes.'
        out += ' %(URL)s'
        return out % content
    else:
        return 'Unknown error.'



api_root = 'http://api.rottentomatoes.com/api/public/v1.0/'
movie_search_url = '{}movies.json'.format(api_root)
movie_reviews_url = '{}movies/{}/reviews.json'.format(api_root, '{}')

@hook.command('rt')
@hook.command
def rottentomatoes(inp,bot=None):
    '.rt <title> -- gets ratings for <title> from Rotten Tomatoes'

    api_key = bot.config.get("api_keys", {}).get("rottentomatoes", None)
    if not api_key:
        return "error: no api key set"

    results = http.get_json(movie_search_url, q=inp, apikey=api_key)
    if results['total'] == 0:
        return 'no results'

    movie = results['movies'][0]
    title = movie['title']
    id = movie['id']
    critics_score = movie['ratings']['critics_score']
    audience_score = movie['ratings']['audience_score']
    url = movie['links']['alternate']

    if critics_score == -1:
        return

    reviews = http.get_json(movie_reviews_url.format(id), apikey=api_key, review_type='all')
    review_count = reviews['total']

    fresh = critics_score * review_count / 100
    rotten = review_count - fresh

    return u"{} - critics: \x02{}%\x02 ({}\u2191/{}\u2193) audience: \x02{}%\x02 - {}".format(title, critics_score, fresh, rotten, audience_score, url)
