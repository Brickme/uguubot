from util import hook, database

@hook.command(permissions=["op_lock", "op"], channeladminonly=True, autohelp=False)
def fixdisabled(inp, notice=None, bot=None, chan=None, db=None):
    """enable [#channel] <commands|all> -- Enables commands for a channel.
    (you can enable multiple commands at once)"""

    disabledcommands = database.get(db,'channels','disabled','chan',chan)
    database.set(db,'channels','disabled','','chan',chan)
    notice(u"[{}]: All commands are now enabled.".format(chan))

