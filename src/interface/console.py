import traceback
import logging
from configs.config_constants import StartMessageKey
from assistant import Assistant


class Console:

    def __init__(self, language_model, app_dict, w2v, message_bundle, config):
        self.__assistant = Assistant(language_model, message_bundle, app_dict, config, w2v=w2v)
        self.__message_bundle = message_bundle
        self.__config = config
        self.__START_MESSAGE_KEY = self.__config[StartMessageKey]

    def start(self):
        print(self.__message_bundle[self.__START_MESSAGE_KEY])
        request = input("User: ")
        while request != "exit":
            try:
                answer = self.__assistant.process_request(request)
                print("Masha: " + answer)
            except Exception:
                logging.error(traceback.print_exc())
            request = input("User: ")

    def stop(self):
        self.__assistant.stop()

    def __call__(self, *args, **kwargs):
        self.start()

