from configparser import ConfigParser
from application.application_config import load_config
from assistant.intent_detector import IntentDetector

from interface.console import Console
from interface.telegram import Telegram
from interface.whatsapp import WhatsApp
from language.models.en.english_language_model import EnglishLanguageModel
from configs.config_constants import InterfaceTypeKey, LogLevelKey, IsStubMode, W2VModelPathKey, W2VModelFileTypeKey
from gensim.models.keyedvectors import KeyedVectors
from threading import Thread
from distutils.util import strtobool
import logging
import os
from configs.ConfigManager import ConfigManager

STARTED_WORKING_MESSAGE = "Assistant started working"
TELEGRAM = "telegram"
CONSOLE = "console"
WHATSAPP = "whatsapp"


def start():
    print("Started initialization")
    config = ConfigManager(["default_config", "message_bundle"])

    logging.basicConfig(level=config[LogLevelKey],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("Stub mode: {}".format(config[IsStubMode]))

    language_model = EnglishLanguageModel(config)
    logging.info("Selected {} language mode".format(language_model.get_language_name()))

    app_dict = load_config("ApplicationConfig.json", language_model)

    print("Started initialization of Word2Vect")

    is_binary_w2v = strtobool(config[W2VModelFileTypeKey])

    w2v = KeyedVectors.load_word2vec_format(config[W2VModelPathKey], binary=is_binary_w2v)

    print("Making assistant")

    detector: IntentDetector = IntentDetector(config, app_dict, w2v)

    interface_type = config[InterfaceTypeKey]
    interface_class = get_interface(interface_type)
    interface = interface_class(language_model, detector, config)

    if interface_type == CONSOLE:
        print(STARTED_WORKING_MESSAGE)
        interface.start()
    elif interface_type == TELEGRAM or interface_type == WHATSAPP:
        assistant_thread = Thread(target=interface, name="Assistant")
        assistant_thread.start()
        print(STARTED_WORKING_MESSAGE)

        request = input("User: ")
        while request != "exit":
            request = input("User: ")

    interface.stop()
    print("Assistant stopped working")


def get_interface(interface):
    clazz = None

    if interface == CONSOLE:
        clazz = Console
    elif interface == TELEGRAM:
        clazz = Telegram
    else:
        clazz = WhatsApp
    logging.info("Chosen {} mode".format(clazz.__name__))
    return clazz


if __name__ == "__main__":
    start()
