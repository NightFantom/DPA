from configparser import ConfigParser
from application.application_config import load_config
from assistant.intent_detector import IntentDetector
from configs.ConfigManager import ConfigManager
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

STARTED_WORKING_MESSAGE = "Assistant started working"
TELEGRAM = "telegram"
CONSOLE = "console"
WHATSAPP = "whatsapp"


def start():
    print("Started initialization")
    paths = []
    if os.path.isfile("configs/config.ini"):
        paths.append("configs/config.ini")
    paths.append("configs/default_config.ini")
    default_config = ConfigManager(paths)

    logging.basicConfig(level=default_config[LogLevelKey],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logging.info("Stub mode: {}".format(default_config[IsStubMode]))

    language_model = EnglishLanguageModel(default_config)
    logging.info("Selected {} language mode".format(language_model.get_language_name()))

    config_parser = ConfigParser()
    config_parser.read("language/models/en/message.ini", encoding="utf-8")
    message_bundle = config_parser["DEFAULT"]

    app_dict = load_config("ApplicationConfig.json", language_model)

    print("Started initialization of Word2Vect")
    is_binary_w2v = strtobool(default_config[W2VModelFileTypeKey])
    w2v = KeyedVectors.load_word2vec_format(default_config[W2VModelPathKey], binary=is_binary_w2v)
    print("Making assistant")

    detector: IntentDetector = IntentDetector(default_config, app_dict, w2v)

    interface_type = default_config[InterfaceTypeKey]
    interface_type = WHATSAPP
    interface_class = get_interface(interface_type)
    interface = interface_class(language_model, detector, message_bundle, default_config)

    if interface_type == CONSOLE:
        print(STARTED_WORKING_MESSAGE)
        interface.start()
    elif interface_type == TELEGRAM or interface_type==WHATSAPP:
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
