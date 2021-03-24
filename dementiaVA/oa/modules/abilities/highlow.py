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
        self._game_loop()

    def _game_loop(self):
        self.round = 1
        while True:
            if self.round == 1:
                self.current_number = get_random_number()
                say(f"Let's begin. The first number I'm thinking of is {current_number}.")
                sleep(0.5)
                say("Good luck.")
                sleep(1)

            self.last_number = self.current_number
            self.current_number = get_random_number()

            say(f"The next number is {self.current_number}.\nIs that higher, lower, or the same?")

            response = None
            while True:
                response = get_response()
                if response in {"higher", "lower", "equal"}:
                    break
                else:
                    say("Sorry, I didn't catch that.")

            if response == "X":
                break
            elif response == "+":
                if self.current_number > self.last_number:
                    self.score += 1
                    say("Correct!")
                else:
                    say(f"Sorry. That's wrong. The first number was {self.last_number}, and the second was {self.current_number}.")
            elif response == "-":
                if self.current_number < self.last_number:
                    self.score += 1
                    say("Correct!")
                else:
                    say(f"Sorry. That's wrong. The first number was {self.last_number}, and the second was {self.current_number}.")
            elif response == "=":
                if self.current_number == self.last_number:
                    self.score += 1
                    say("Correct!")
                else:
                    say(f"Sorry. That's wrong. The first number was {self.last_number}, and the second was {self.current_number}.")

            self.round += 1

        say(f"You scored {self.score} correct in {self.round - 1} round(s). Thanks for playing.")


def get_random_number():
    return random.randrange(1, 100)

def get_response():
    response = None
    if response in ("higher", "high", "up", "bigger", "larger", "more"):
        response = "higher"
    elif response in ("lower", "low", "down", "smaller", "less"):
        response = "lower"
    elif response in ("same", "equal"):
        response = "equal"
    return response
