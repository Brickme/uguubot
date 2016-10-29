import re
import channel

def filesize(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return '{0:.2f}{1}{2}'.format(num, unit, suffix)
        num /= 1024.0
    return '{0:.1f}{}{}'.format(num, 'Yi', suffix)

def output(db, chan, scriptname, fields=[], color=11):
    split_output = set(re.sub('[#~&@+%,\.]', '', ' '.join(fields).lower()).split(' '))
    users = set(channel.users(db, chan))
    match = split_output & users
    if scriptname is False:
        scriptname = ''
    else:
        scriptname = '[{}] '.format(scriptname)

    if len(match) >= 3:
        print(u'Nick spam detected. Output ignored: [{}] {}'.format(scriptname, ' - '.join(fields)))
    else:
        return u'{}{}'.format(scriptname, ' - '.join(fields))
