import psutil
import random
import socket
import string

import oa.legacy

from oa.modules.abilities.core import info
from oa.modules.abilities.interact import say
from oa.modules.abilities.system import read_file

def diagnostics():
    """ Run system diagnostics. """
    response = '- Running diagnostics... '

    # Processor Temperature.
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
        if not temps:
            response += "Unable to read temperature.\n"
        else:
            for name, entries in temps.items():
                for entry in entries:
                    response += 'Proccessor temperature is currently %.0f degrees Centegrade...\n' %entry.current
                    break
                break

    # Memory Free.
    response += 'System memory has %.0f Gigabytes free...\n' % oa.legacy.bytes2gb(oa.legacy.sys.free_memory())

    # Drive Space Free.
    response += 'Internal hard drive has %.0f Gigabytes free...\n' % oa.legacy.bytes2gb(psutil.disk_usage('/').free)

    # Network Status.
    response += oa.legacy.switch(is_online(), True, 'Internet access is currently available.', 'We are offline.')

    say(response)


def is_online(host = '8.8.8.8', port = 53, timeout = 1):
    """ If online Return True, if not return False.
     Host: 8.8.8.8 (google-public-dns-a.google.com)
     OpenPort: 53/tcp
     Service: domain (DNS/TCP) """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        info(ex)
        return False


def random_from_file(fname):
    l = read_file(fname, result_as_list = 1)
    return random.choice(l)


def read_forecast():
    return None

def read_news_feed(news_feed, category):
    return None

def lines_to_dict(sLines, func = lambda s : s, params = {}):
    """ Tranlate dictionary string.
      where
         end of line - separator between keys
         : - separator between key and value
         params and oa.sys dicts - is using to fill parameters:
            %(param)s, %(user)s etc
      Example string:
       key1 : value1
       key2 : value2
       ...
       You there?: yes... i am here...
       You think: i think sometimes...
    """
    params.update(oa.legacy.sys.__dict__)
    sLines = sLines %params
    ret = dict([[k, func(v)] for k, v in [[x.strip() for x in ph.split(':')] for ph in sLines.split('\n') if ph.strip() != '']])
    return ret

def say_random(slist):
    return random.choice([x.strip() for x in slist.split(',')])

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

def get_sys(s):
    """ Return system information from `oa.sys`. """
    return getattr(oa.legacy.sys, s)
