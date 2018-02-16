from configparser import ConfigParser
from application.application_config import load_config

from interface.console import Console
from interface.telegram import Telegram
from language.models.en.english_language_model import EnglishLanguageModel
from configs.config_constants import InterfaceTypeKey, LogLevelKey, IsStubMode, W2VModelPathKey, W2VModelFileTypeKey
from moduls.facts_module import FactGenerator
from gensim.models.keyedvectors import KeyedVectors
from threading import Thread
from distutils.util import strtobool
import logging

STARTED_WORKING_MESSAGE = "Assistant started working"
TELEGRAM = "telegram"
CONSOLE = "console"


def start():
    print("Started initialization")
    config_parser = ConfigParser()
    config_parser.read("configs/config.ini", encoding="utf-8")
    default_config = config_parser["DEFAULT"]

    logging.basicConfig(level=default_config[LogLevelKey],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logging.info("Stub mode: {}".format(default_config[IsStubMode]))

    language_model = EnglishLanguageModel(default_config)
    logging.info("Selected {} language mode".format(language_model.get_language_name()))

    config_parser = ConfigParser()
    config_parser.read("language/models/en/message.ini", encoding="utf-8")
    message_bundle = config_parser["DEFAULT"]

    app_dict = load_config("ApplicationConfig.json", language_model)

    print("Fitting facts generator")
    FactGenerator(default_config)

    print("Started initialization of Word2Vect")
    is_binary_w2v = strtobool(default_config[W2VModelFileTypeKey])
    w2v = KeyedVectors.load_word2vec_format(default_config[W2VModelPathKey], binary=is_binary_w2v)
    print("Making assistant")

    interface_type = default_config[InterfaceTypeKey]
    interface_class = get_interface(interface_type)
    interface = interface_class(language_model, app_dict, w2v, message_bundle, default_config)

    if interface_type == CONSOLE:
        print(STARTED_WORKING_MESSAGE)
        interface.start()
    elif interface_type == TELEGRAM:
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

    logging.info("Chosen {} mode".format(clazz.__name__))
    return clazz


if __name__ == "__main__":
    start()
