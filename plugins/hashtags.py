# Written by Scaevolus 2010
from util import hook, http, text, execute, web
import string
import sqlite3
import re
import time
import json
from datetime import datetime

re_lineends = re.compile(r'[\r\n]*')

# some simple "shortcodes" for formatting purposes
shortcodes = {
'[b]': '\x02',
'[/b]': '\x02',
'[u]': '\x1F',
'[/u]': '\x1F',
'[i]': '\x16',
'[/i]': '\x16'}

html_body = u"<html><head><title>{}</title></head><body>{}</body></html>"
html_lines = u"<b>{}</b>: {}<br/>\n"
html_items = u"<span style='border:1px solid {border}; background-color:{bg};' title='Added by {nick} on {date}'>{value}</span>"

def db_init(db):
    db.execute("create table if not exists mem(word, data, nick,"
               " primary key(word))")
    db.commit()


def get_memory(db, word):

    row = db.execute("select data from mem where word=lower(?)",
                     [word]).fetchone()

    if row:
        result = row[0]
        try: result = json.loads(result)
        except: pass
        if isinstance(result, list) == False:
            #Converts old style to dict
            result = [{'value': result, 'nick': None, 'date': None}]
        return result
    else:
        return None

#@hook.regex(r'(.*) is (.*)')
#@hook.regex(r'(.*) are (.*)')
@hook.command("learn", channeladminonly=True)
@hook.command("r", channeladminonly=True)
@hook.command(channeladminonly=True)
def remember(inp, nick='', db=None, say=None, input=None, notice=None):
    "remember <word> <data> -- Remembers <data> with <word>."
    db_init(db)

    try:
        word, data = inp.split(None, 1)
    except ValueError:
        notice(remember.__doc__)
    time_now = time.time()

    old_data = get_memory(db, word)

    if old_data: new_data = old_data
    else: new_data = []
    new_data.append({'value': data, 'nick': input.nick, 'date': time_now})

    db.execute("replace into mem(word, data, nick) values (lower(?),?,?)", (word, json.dumps(new_data), nick))
    db.commit()

    if old_data: notice("Appending \x02{}\x02 to \x02{}\x02".format(data, word))
    else: notice('Remembering \x02{}\x02 for \x02{}\x02. Type ?{} to see it.'.format(data, word, word))

@hook.command("f", adminonly=True)
@hook.command(adminonly=True)
def forget(inp, db=None, input=None, notice=None):
    "forget <word> -- Forgets a remembered <word>."

    db_init(db)
    data = get_memory(db, inp)

    if data:
        db.execute("delete from mem where word=lower(?)",
                   [inp])
        db.commit()
        notice('"%s" has been forgotten.' % inp.replace('`', "'"))
        return
    else:
        notice("I don't know about that.")
        return

@hook.command
def info(inp, notice=None, db=None):
    "info <word> -- Shows the source of a factoid."

    db_init(db)

    # attempt to get the factoid from the database
    data = db.execute("SELECT data FROM mem where word=lower(?)", [inp]).fetchone()[0]

    if data:
        data = json.loads(data)
        for row in data:
            try: date = datetime.fromtimestamp(row['date']).strftime("%F %T%Z")
            except: date = 'N/A'
            nick = row['nick']
            value = row['value']
            print('{}: {} ({} on {})'.format(inp.strip(), value, nick, date))
        notice('{}: {} ({} on {})'.format(inp.strip(), value, nick, date))
    else:
        notice("Unknown Factoid.")

# @hook.regex(r'^(\b\S+\b)\?$')
@hook.regex(r'^\#(\b\S+\b)')
@hook.regex(r'^\? ?(.+)')
def hashtag(inp, say=None, db=None, bot=None, me=None, conn=None, input=None):
    "<word>? -- Shows what data is associated with <word>."
    try:
        prefix_on = bot.config["plugins"]["factoids"].get("prefix", False)
    except KeyError:
        prefix_on = False

    db_init(db)

    output = []

    # split up the input
    split = inp.group(1).strip().split(" ")
    factoid_id = split[0]

    data = get_memory(db, factoid_id)
    if data is None: return

    for key in data:
        result = key['value']

        # factoid postprocessors
        result = text.multiword_replace(result, shortcodes)
        result = result.replace('http://a.pomf.se','https://web.archive.org/web/20150612013823/a.pomf.se')

        if result.startswith("<act>"):
            result = result[5:].strip()
            me(result)
        else:
            if prefix_on:
                output.append("\x02[%s]:\x02 %s" % (factoid_id, result))
            else:
                output.append(result)
    return ', '.join(output)

@hook.command(r'keys', autohelp=False)
@hook.command(r'key', autohelp=False)
@hook.command(autohelp=False)
def hashes(inp, say=None, db=None, bot=None, me=None, conn=None, input=None):
    "hashes -- Shows hash names for all known hashes."

    search = "SELECT word FROM mem"
    if inp: search = "{} WHERE word LIKE '%{}%'".format(search, inp)
    search = "{} ORDER BY word".format(search)

    rows = db.execute(search).fetchall()

    if rows:
	url = web.isgd(web.haste(", ".join(tuple(x[0] for x in rows))))
	return "{}: {}".format(url, ", ".join(tuple(x[0] for x in rows)))
    else: return "No results."

@hook.command(r'allkeys', autohelp=False, adminonly=True)
@hook.command(autohelp=False, adminonly=True)
def allhashes(inp, say=None, db=None):
    "allhashes -- Shows hash names for all known hashes."

    search = "SELECT word, data, nick FROM mem"
    if inp: search = "{} WHERE word LIKE '%{}%'".format(search, inp)
    search = "{} ORDER BY word".format(search)

    rows = db.execute(search).fetchall()

    if rows:
	web_list = []
	irc_list = []
	for row in rows:
		formatted_values = []
		try:
			values = json.loads(row[1])
		except:
			values = [row[1]]
		for value in values:
			if type(value) is not dict:
				value = {'value': value, 'date': 'N/A', 'nick': row[2]}
				background_color = 'palegoldenrod'
				border_color = 'darkgoldenrod'
				#db.execute("replace into mem(word, data, nick) values (lower(?),?,?)", (row, value, nick))
				#db.commit()

			else:
				background_color = 'aqua'
				border_color = 'deepskyblue'
			date = value['date']
			try:
				date = datetime.fromtimestamp(date).strftime("%F %T%Z")
			except:
				date = 'N/A'
			nick = value['nick']
			value = value['value']
			formatted_values.append(html_items.format(border=border_color, bg=background_color, value=value, nick=nick, date=date))
		formatted_values = ' '.join(formatted_values)
		web_list.append(html_lines.format(row[0], formatted_values))
	output_web = html_body.format('rms hashtags', ''.join(web_list))
	url = web.pomf({'hashes.html': output_web})['hashes.html']
	url = web.isgd(url)
	return url
    else: return "No results."
