import oa.legacy
from oa.modules.abilities.interact import say


def say_time():
    """ Speak the current time. """
    time = oa.legacy.sys.time_text()
    say(f'The time is {time}.')


def say_day():
    """ Speak the current day. """
    day = oa.legacy.sys.day_name()
    say(f'Today is {day}.')


def say_last_command(string=''):
    if oa.legacy.oa.last_command:
        say(string + ' ' + oa.legacy.oa.last_command)
    else:
        say('You haven\'t said anything.')
