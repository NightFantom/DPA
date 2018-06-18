import traceback
import logging

from assistant.intent_detector import IntentDetector
from configs.config_constants import StartMessageKey
from assistant.assistant import Assistant
from interface.base_interface import BaseInterface


class Console(BaseInterface):

    def __init__(self, language_model, intent_detector: IntentDetector, config):
        super().__init__( config)
        self.__assistant = Assistant(language_model,  config, intent_detector)
        self.__START_MESSAGE_KEY = self.config[StartMessageKey]

    def start(self):
        print(self.config[self.__START_MESSAGE_KEY])
        request = input("User: ")
        while request != "exit":
            try:
                answer = self.__assistant.process_request(request)
                print("OpenMind: " + answer.message)
            except Exception:
                logging.error(traceback.print_exc())
            request = input("User: ")

    def stop(self):
        self.__assistant.stop()


