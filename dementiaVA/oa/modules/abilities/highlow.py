import logging
import random
from time import sleep

from oa.modules.abilities.interact import say, user_answer, play

_logger = logging.getLogger(__name__)

class Game:
    current_number = None
    last_number = None
    score = 0
    round = 0
    level = 1
    streak = 0
    # Multiple levels of difficulty
    # Level 1: Numbers 1-10
    # Level 2: Numbers 1-20
    # Level 3: Numbers 1-20, with gaps between numbers
    # Level 4: Numbers 1-50, with gaps between numbers
    # Level 5: Numbers 1-100, with gaps between numbers


    def start(self):
        self.round = 1
        self.current_number = self.get_random_number()
        say(f"The first number I'm thinking of is {self.current_number}.")
        sleep(0.5)
        say("Good luck.")
        self._game_loop()

    def _game_loop(self):
        self.last_number = self.current_number
        self.current_number = self.get_random_number()

        say(f"The next number is {self.current_number}.\nIs that higher, lower, or the same?")
        user_answer(self.get_choices())

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
            play("success.wav")
            sleep(1)
            say("Correct!")
            self.streak += 1
        else:
            play("failure.wav")
            sleep(1)
            say(f"Sorry. That's wrong. The first number was {self.last_number}, and the second was {self.current_number}.")
            if self.streak > 0:
                self.streak = 0
            else:
                self.streak -= 1

        incorrect = self.round - self.score
        accuracy = self.get_accuracy()

        if self.streak <= -2 and self.level > 1:
            self.level -= 1
            self.streak = 0
        elif self.streak >= 5 and self.level < 5:
            self.level += 1
            self.streak = 0

        _logger.debug(f"Game stats: Correct={self.score}, Incorrect={incorrect}, "
                      f"Accuracy={accuracy}, Round={self.round}, Level={self.level}, Streak={self.streak}")

        self.round += 1
        self._game_loop()

    def get_accuracy(self):
        return self.score / self.round

    def end_game(self):
        say("Okay. Let's stop.")

        if self.round > 2:
            if self.score == self.round:
                say(f"You got all questions correct. Well done.")
            elif self.score > 1:
                say(f"You scored {self.score} correct in {self.round - 1} rounds. Thanks for playing.")


    def get_choices(self):
        choices = {}
        for response in ("higher", "hire", "high", "up", "bigger", "larger", "more", "above"):
            choices[response] = self.higher
        for response in ("lower", "low", "down", "smaller", "less", "below"):
            choices[response] = self.lower
        for response in ("same", "equal"):
            choices[response] = self.same
        return choices

    def get_random_number(self):
        if self.level <= 1:
            range = 10
        elif self.level <= 3:
            range = 20
        elif self.level <= 4:
            range = 50
        elif self.level <= 5:
            range = 100
        else:
            _logger.error(f"Unknown game level {self.level}")
            range = 10
        return random.randrange(1, range)


