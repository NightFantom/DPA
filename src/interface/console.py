import traceback
import logging
from configs.config_constants import StartMessageKey
from assistant import Assistant
from interface.base_interface import BaseInterface


class Console(BaseInterface):

    def __init__(self, language_model, app_dict, w2v, message_bundle, config):
        super().__init__(message_bundle, config)
        self.__assistant = Assistant(language_model, message_bundle, app_dict, config, w2v=w2v)
        self.__START_MESSAGE_KEY = self.config[StartMessageKey]

    def start(self):
        print(self.message_bundle[self.__START_MESSAGE_KEY])
        request = input("User: ")
        while request != "exit":
            try:
                answer = self.__assistant.process_request(request)
                message = self.format_answer(answer)
                print("Masha: " + message)
            except Exception:
                logging.error(traceback.print_exc())
            request = input("User: ")

    def stop(self):
        self.__assistant.stop()


