from enum import Enum
from enum import auto


class IntegrationType(Enum):
    Module = auto()
    RemoteApp = auto()


class Application:
    def __init__(self, name_str, description_str, intents, integration_type=IntegrationType.Module, url=None):
        self.__name = name_str
        self.__description = description_str
        self.__integration_type = integration_type
        self.__URL = url
        self.__impl = None
        self.__intents_dict = dict()
        self.__key_phrases_intents_dict = dict()
        self.__intents_list = intents
        for intent in intents:
            for phrase in intent.get_list_of_key_phrases():
                self.__key_phrases_intents_dict[phrase] = intent
            self.__intents_dict[intent.get_name()] = intent

    def get_integration_type(self):
        return self.__integration_type

    def get_endpoint_url(self):
        return self.__URL

    def get_description(self):
        return self.__description

    def get_intent_by_name(self, name):
        return self.__intents_dict.get(name, None)

    def get_intent(self, intent_name_str):
        return self.__key_phrases_intents_dict.get(intent_name_str, None)

    def get_intents(self):
        return self.__key_phrases_intents_dict

    def get_intents_list(self):
        return self.__intents_list

    def get_name(self):
        return self.__name

    def get_impl(self):
        return self.__impl

    def set_impl(self, impl):
        self.__impl = impl