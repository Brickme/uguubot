from util import hook, http, web, text, scheduler

feeds = {
		"xkcd":		  ["http://xkcd.com/rss.xml"],
		"ars":		  ["http://feeds.arstechnica.com/arstechnica/index"],
		"redlettermedia": ["http://redlettermedia.com/feed/"]
}

@hook.command("feed")
@hook.command
def rss(inp, limit=None, say=None, conn=None):
    "rss <feed> -- Gets the first three items from the RSS feed <feed>."

    output = []
    input = inp.split()
    strip = input[0].lower().strip()

    if strip in feeds: feed = feeds[strip][0]
    else: feed = input[0]

    if limit == None:
	    try: limit = feeds[strip][1]
	    except:
		try: limit = int(input[1])
		except: limit = 3


    query = "SELECT title, link FROM rss WHERE url=@feed LIMIT @limit"
    result = web.query(query, {"feed": feed, "limit": limit})

    if not result.rows: return "Could not find/read RSS feed."

    for row in result.rows:
        title = text.truncate_str(row["title"], 100)
        try:
            link = web.isgd(row["link"])
	except AttributeError:
	    link = web.isgd(row["link"]["href"])
        except (web.ShortenError, http.HTTPError, http.URLError):
            link = row["link"]
        output.append(u"{} - {}".format(title, link))

    return(" | ".join(output))

@hook.command(channeladminonly=True, autohelp=False)
def rsstopic(inp, chan=None, say=None, conn=None):
    conn.send(u"TOPIC {} :{}".format(chan, rss(inp, 1)))

#timer = scheduler.check_for_timers("rssscottsteiner")
#if timer == 0:
#	scheduler.schedule(300, 5, rsstopic("xkcd", "#scottsteiner"), conn)
