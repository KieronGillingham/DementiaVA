import oa.legacy
from oa.modules.abilities.interact import say


def say_time():
    """ Speak the current time. """
    time = oa.legacy.sys.time_text()
    say('- The time is %s.' %time)


def say_day():
    """ Speak the current day. """
    day = oa.legacy.sys.day_name()
    say('- Today is %s.' %day)


def say_last_command(string = ''):
    say(string + ' ' + oa.legacy.oa.last_command)