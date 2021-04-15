from time import sleep, time

from oa.core.util import command_registry

from oa.modules.abilities.interact import say, play, mind, yes_no, user_answer
from oa.modules.abilities.other import say_day, say_last_command, say_time
from oa.modules.abilities.core import set_config, adjust_config

import oa


kws = {}

command = command_registry(kws)

mute_message = False

def start():
    if not oa.legacy.mind.mute_message:
        play("startup.wav", "Start-up Jingle")
        sleep(2)
        say('Hello, I am GLAD. How can I help?')
        oa.legacy.mind.mute_message = True


@command(["can you", "you can+do", "what+can+you", "help"])
def what_do():
    say('At the moment, I can play a simple number game with you, or put some music on.')


@command(["hello"])
def run_demo():
    say('Hello! How can I help?')


@command(["close", "stop", "end", "off", "sleep", "go+sleep", "turn of", "switch of", "shut+down"])
def close_assistant():
    oa.legacy.hub.finished.set()
    say('Shutting down.')
    play('sleep.wav', "Shut-down Jingle")


def numbergame_yes():
    say('Okay let\'s play.')
    mind('numbergame')


def numbergame_no():
    say('Okay, we won\'t play.')


@command(["number", "game", "high+low", "low+high"])
def number_game():
    yes_no('Do you want to play the number game?', numbergame_yes, numbergame_no)


@command(["radio", "music", "sound", "too quiet"])
def radio():
    yes_no('Do you want to listen to the radio?', radio_yes, radio_no)


def radio_yes():
    say('I\'ll play the radio for you then.')
    mind('radio')


def radio_no():
    say('Okay, I won\'t put any music on.')


@command(["day", "date"])
def what_day():
    say_day()


@command(["what did I say", "repeat"])
def what_command():
    say_last_command('You just said:')


@command("time")
def what_time():
    say_time()


@command(["your name", "who+you"])
def your_name():
    say("My name is GLAD.")


@command(["thank"])
def thanks():
    time_since_last_reply = time() - oa.legacy.sys.last_say_time
    if time_since_last_reply < 10:
        say("You're welcome.")

@command(["configure", "settings", "options"])
def settings():
    say("You can change my talking speed, or set me to monitoring mode.")


@command(["how+change+talk"])
def how_change_talk():
    say("Just tell me to talk faster or slower.")


@command(["talk+faster", "talk+too slow"])
def talk_faster():
    say("I'll talk faster from now on.")
    adjust_config("talkspeed", 25)


@command(["talk+slower", "talk+too fast", "slow down", "talk+lower"])
def talk_slower():
    say("I'll talk slower from now on.")
    adjust_config("talkspeed", -25)