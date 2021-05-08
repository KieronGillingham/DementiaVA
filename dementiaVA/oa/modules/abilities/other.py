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


def string_to_number(string=''):
    if not string:
        return None
    elif isinstance(string, str):
        string = string.replace("-", " ")
        string = string.split(" ")

    numbers = {}
    numbers["zero"] = 0
    numbers["one"] = 1
    numbers["two"] = 2
    numbers["three"] = 3
    numbers["four"] = 4
    numbers["five"] = 5
    numbers["six"] = 6
    numbers["seven"] = 7
    numbers["eight"] = 8
    numbers["nine"] = 9
    numbers["ten"] = 10
    numbers["eleven"] = 11
    numbers["twelve"] = 12
    numbers["thirteen"] = 13
    numbers["fourteen"] = 14
    numbers["fifteen"] = 15
    numbers["sixteen"] = 16
    numbers["seventeen"] = 17
    numbers["eighteen"] = 18
    numbers["nineteen"] = 19
    numbers["twenty"] = 20
    numbers["thirty"] = 30
    numbers["forty"] = 40
    numbers["fifty"] = 50
    numbers["sixty"] = 60
    numbers["seventy"] = 70
    numbers["eighty"] = 80
    numbers["ninety"] = 90
    numbers["hundred"] = 100

    foundnumbers = []
    sum = 0

    for substring in string:
        num = numbers.get(substring)
        print(substring, num)
        if num is not None:
            sum += num
            foundnumbers.append(num)

    return foundnumbers

