from util import hook, database, http, formatting
import random

fields = {
    'intro':		{ 'title': 'greeting', 'description': 'greeting', 'field': 'greeting' },
    'greeting':		{ 'title': 'greeting', 'description': 'greeting' },
    'waifu':		{ 'title': 'waifu', 'description': 'waifu' },
    'husbando':		{ 'title': 'husbando', 'description': 'husbando' },
    'daughteru':	{ 'title': 'daughteru', 'description': 'daughteru' },
    'imouto':		{ 'title': 'imouto', 'description': 'imouto' },
    'birthday':		{ 'title': 'birthday', 'description': 'birthday' },
    'horoscope':	{ 'title': 'horoscope', 'description': 'horoscope', 'format': 'http://www.astrology-zodiac-signs.com/zodiac-signs/{}/' },
    'snapchat':		{ 'title': 'snapchat', 'description': 'snapchat' },
    'steam':		{ 'title': 'Steam', 'description': 'Steam profile link' },
    'twitch':		{ 'title': 'Twitch', 'description': 'Twitch stream link' },
    'xbl':		{ 'title': 'Xbox Live', 'description': 'Xbox Live ID' },
    'psn':		{ 'title': 'PSN', 'description': 'Playstation Network ID' },
    'nintendo':		{ 'title': 'Nintendo', 'description': 'Nintendo Friend Code' },
    'desktop':		{ 'title': 'desktop', 'description': 'desktop', 'required': 'http' },
    'battlestation':	{ 'title': 'battlestation', 'description': 'battlestation', 'required': 'http' },
    'homescreen':	{ 'title': 'homescreen', 'description': 'homescreen', 'required': 'http' },
    'selfie':		{ 'title': 'selfie', 'description': 'selfie', 'required': 'http' }
}

@hook.command('intro', autohelp=False)
@hook.command('greeting', autohelp=False)
@hook.command('waifu', autohelp=False)
@hook.command('husbando', autohelp=False)
@hook.command('daughteru', autohelp=False)
@hook.command('imouto', autohelp=False)
@hook.command('birthday', autohelp=False)
@hook.command('horoscope', autohelp=False)
@hook.command('snapchat', autohelp=False)
@hook.command('steam', autohelp=False)
@hook.command('twitch', autohelp=False)
@hook.command('xbl', autohelp=False)
@hook.command('psn', autohelp=False)
@hook.command('nintendo', autohelp=False)
@hook.command('desktop', autohelp=False)
@hook.command('homescreen', autohelp=False)
@hook.command('battlestation', autohelp=False)
@hook.command('selfie', autohelp=False)
def user_info(inp, nick=None, db=None, input=None, notice=None):
    global fields
    field_name = input.trigger

    if field_name not in fields:
        print('{} not in {}'.format(field_name, fields))
        return
	
    if 'field' in fields[field_name]:
        field_name = fields[field_name]['field']

    field_title = fields[field_name]['title']
    field_description = fields[field_name]['description']
    if not inp or '@' in inp:
        if '@' in inp: nick = inp.split('@')[1].strip()
        result = database.get(db,'users',field_name,'nick',nick)
        if 'format' in fields[field_name]:
            result = fields[field_name]['format'].format(result)
        if result:
            return formatting.output(db, input.chan, field_title, ['{}: {}'.format(nick,result)])
        else:
            return formatting.output(db, input.chan, field_title, ['No {} saved for {}.'.format(field_description, nick)])
    elif 'del' in inp:
        database.set(db,'users',field_name,'','nick',nick)
        notice("Deleted your {}.".format(field_description))
    else:
        if 'required' in fields[field_name]:
            if fields[field_name]['required'] in inp:
                database.set(db,'users',field_name,'{} '.format(inp.strip().encode('utf8')),'nick',nick)
                notice("Saved your {}.".format(field_description))
            else:
                notice("Invalid input for {}".format(field_description))
        else:
            database.set(db,'users',field_name,'{} '.format(inp.strip().encode('utf8')),'nick',nick)
            notice("Saved your {}.".format(field_description))
    return


@hook.command(autohelp=False)
def vidya(inp, nick=None, conn=None, input=None, chan=None,db=None, notice=None):
    "vidya <vidya | @ person> -- shows a user's video game contacts."
    output = []

    if '@' in inp: nick = inp.split('@')[1].strip()

    fields = {'Twitch': 'twitch', 'Steam': 'steam', 'XBL': 'xbl', 'PSN': 'psn', 'Nintendo Friend Code': 'nintendo'}
    output_fields = ['Twitch', 'Steam', 'XBL', 'PSN', 'Nintendo Friend Code']
    for field in output_fields:
        result = database.get(db,'users',fields[field],'nick',nick)
        if result:
            output.append('{}: {}'.format(field, result).rstrip())
        else:
            output.append('{}: [N/A]'.format(field))

    return formatting.output(db, input.chan, 'vidya', output)

@hook.command(autohelp=False, adminonly=True)
def all(inp, nick=None, conn=None, input=None, chan=None,db=None, notice=None):
	field = 'twitch'
	result = db.execute("SELECT nick,? FROM users WHERE twitch NOT NULL", ('twitch',)).fetchall()
	for r in result:
		nick,stream = r
		print([nick,stream])
