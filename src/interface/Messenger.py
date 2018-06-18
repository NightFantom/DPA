from typing import Dict
from assistant.answer import AssistantAnswer
from assistant.intent_detector import IntentDetector
from configs.config_constants import StartMessageKey, TokenKey, PrintMessages
from assistant.assistant import Assistant
from interface.base_interface import BaseInterface

USER_ASKS_PATTERN = "User {} {} asks: '{}'"
ASSISTANT_ANSWERS_PATTERN = "Answer for user {} {}: '{}'"
STOP_MESSAGE_KEY = "stop_message_key"


class Messenger(BaseInterface):

    def __init__(self, language_model, intent_detector: IntentDetector, config):
        super().__init__( config)

        self.__language_model = language_model
        self.__intent_detector = intent_detector
        self.user_assistant_dict: Dict[int, Assistant] = {}

    def proccess_request(self, user_id: int, user_name: str, request: str):
        does_print = bool(self.config[PrintMessages])
        if does_print:
            print((USER_ASKS_PATTERN.format(user_id, user_name, request)))
        assistant: Assistant = self.user_assistant_dict.get(user_id, None)
        if assistant is None:
            assistant: Assistant = Assistant(self.__language_model,
                                             self.config, self.__intent_detector, user_id=user_id)
            self.user_assistant_dict[user_id] = assistant
        answer = assistant.process_request(request)
        message = answer.message
        if does_print:
            print(ASSISTANT_ANSWERS_PATTERN.format(user_id, user_name, message))
        return answer

    def evaluate_request(self,user_id, mark,step=None, last=False):
        assistant: Assistant = self.user_assistant_dict.get(user_id)
        if assistant:
            if (not last):
                answer: AssistantAnswer = assistant.mark(step, mark)
            else:
                answer: AssistantAnswer = assistant.mark_last(mark)

            if answer:
                return answer.message
        return None
