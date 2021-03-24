from itertools import groupby

import oa.legacy

import random
from time import sleep

from oa.modules.abilities.core import info
from oa.modules.abilities.interact import say, user_answer

class Game:
    current_number = None
    last_number = None
    score = 0
    round = 0

    def start(self):
        self.round = 1
        self.current_number = get_random_number()
        say(f"The first number I'm thinking of is {self.current_number}.")
        sleep(0.5)
        say("Good luck.")
        self._game_loop()

    def _game_loop(self):
        self.last_number = self.current_number
        self.current_number = get_random_number()

        say(f"The next number is {self.current_number}.\nIs that higher, lower, or the same?")
        user_answer({'higher': self.higher, 'lower': self.lower, 'same': self.same})

    def higher(self):
        # Call end of round method with True if number is higher
        self.end_of_round(self.current_number > self.last_number)

    def lower(self):
        # Call end of round method with True if number is lower
        self.end_of_round(self.current_number < self.last_number)

    def same(self):
        # Call end of round method with True if number is equal
        self.end_of_round(self.current_number == self.last_number)

    def end_of_round(self, correct):
        if correct:
            self.score += 1
            say("Correct!")
        else:
            say(f"Sorry. That's wrong. The first number was {self.last_number}, and the second was {self.current_number}.")

        say(f'You have got {self.score} correct answers so far.')

        self.round += 1
        self._game_loop()

    def end_game(self):
        say(f"Okay. Let's stop. You scored {self.score} correct in {self.round - 1} rounds. Thanks for playing.")

def get_random_number():
    return random.randrange(1, 100)

def get_response(response):
    response = None
    if response in ("higher", "high", "up", "bigger", "larger", "more"):
        response = "higher"
    elif response in ("lower", "low", "down", "smaller", "less"):
        response = "lower"
    elif response in ("same", "equal"):
        response = "equal"
    return response
