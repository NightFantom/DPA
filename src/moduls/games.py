from answer import AssistantAnswer
import random

class MatchesBot:
    def move(self, left):
        for i in range(1, min(left, 3) + 1):
            if (left - i - 1) % 4 == 0:
                return i
        return 1


class MatchesGameModule:

    def __init__(self, config):
        self.amount_of_matches = 0
        self.is_started = False
        self.bot = MatchesBot()

    def run(self, assistant, parameters_dict):
        intent = parameters_dict["Intent"]
        answer = None
        if intent == "Start Matches Game":
            answer = self.start(assistant, parameters_dict)
        elif intent == "Turn":
            answer = self.turn(assistant, parameters_dict)
        return answer

    def start(self, assistant, parameters_dict):
        self.amount_of_matches = int(parameters_dict.get("AmountOfMatches", 30))
        self.is_started = True
        is_bot_first = random.randint(0, 1)
        if is_bot_first:
            bot_choice = self.bot.move(self.amount_of_matches)
            was_matches = self.amount_of_matches
            self.amount_of_matches -= bot_choice
            param = {"matches": was_matches, "amount": bot_choice}
            answer = AssistantAnswer("matches_game.start_game.bot_first", param)
        else:
            answer = AssistantAnswer("matches_game.start_game.user_first", {"matches": self.amount_of_matches})
        return answer

    @property
    def is_active(self):
        return self.is_started

    def turn(self, assistant, parameters_dict):
        answer = None
        if self.is_started:
            amount_to_remove = int(parameters_dict["Amount"])
            if 1 <= amount_to_remove <= 3:
                self.amount_of_matches -= amount_to_remove
                bot_choice = self.bot.move(self.amount_of_matches)
                if self.amount_of_matches < 2:
                    answer = AssistantAnswer("matches_game.win")
                    self.is_started = False
                else:
                    self.amount_of_matches -= bot_choice
                    if self.amount_of_matches < 2:
                        answer = AssistantAnswer("matches_game.lose")
                        self.is_started = False
                    else:
                        params = {"matches": self.amount_of_matches,
                                  "amount": bot_choice}
                        answer = AssistantAnswer("matches_game.amount_of_matches", params)
            else:
                answer = AssistantAnswer("matches_game.wrong_input_amount")

        return answer
