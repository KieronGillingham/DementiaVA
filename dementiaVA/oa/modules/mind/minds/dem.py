from oa.core.util import command_registry

from oa.modules.abilities.interact import say, play, mind, yes_no, user_answer
from oa.modules.abilities.other import read_news_feed, diagnostics, read_forecast
from oa.modules.abilities.other import say_day, say_last_command, say_time

kws = {}

command = command_registry(kws)

def start():
    say('- Hello, I am GLAD. How can I help?')


@command(["what can you do"])
def what_do():
    say('At the moment, I can\'t do very much I\'m afraid.')


@command(["demo", "intro", "hello", "start"])
def run_demo():
    say('- Hello! How can I help?')


@command(["close", "stop", "end"])
def close_assistant():
    oa.legacy.hub.finished.set()

def numbergame_yes():
    say('Okay let\'s play.')
    mind('numbergame')

def numbergame_no():
    say('Okay, we won\'t play.')

@command(["number game"])
def number_game():
    #yes_no("Do you want to play the number game?", 'dem', {yes})
    #if confirm("Do you want to play the number game?", "Okay, let's play.", "Okay, we will not play the number game."):
    #    mind("numbergame")
    say('Do you want to play?')
    user_answer({'yes': numbergame_yes, 'no': numbergame_no})


"""
@command(["list commands", "what can i say"])
def list_commands():
    say('- The currently available voice commands are:\n{}'.format(',\n'.join(kws.keys())))

@command("read world news")
def read_world_news():
    read_news_feed('https://www.reddit.com/r/worldnews/.rss', 'world')

@command("run diagnostics")
def run_diagnostics():
    diagnostics()

@command("sing a song")
def sing_a_song():
    play('daisy.wav')

@command("what day is it")
def what_day():
    say_day()

@command("what did I say")
def what_command():
    say_last_command('You just said:')

@command("what is the weather")
def what_weather():
    read_forecast()

@command("what time is it")
def what_time():
    say_time()
"""
