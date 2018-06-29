from typing import Dict, Any
from configs.ConfigManager import ConfigManager
from application.application import Application
from language.models.language_model import RequestInformation
from configs.config_constants import WMDThresholdKey
from gensim.models.keyedvectors import KeyedVectors


class IntentDetector:

    def __init__(self, config: ConfigManager, application_dict: Dict[str, Application], w2v: KeyedVectors): 
        self.__config = config
        self.__application_dict = application_dict
        self.__w2v = w2v

    def detect_intent(self, request_information: RequestInformation) -> tuple:
        app_name = request_information.get_app_name()
        app = self.__application_dict.get(app_name, None)
        if app is None:
            app, intent_description = self.__find_intent_by_samples(request_information)
            if intent_description is None:
                app, intent_description = self.__find_intent_by_intersection_words(request_information)
        else:
            lemma = request_information.get_intent().get_lemma()
            intent_description = app.get_intent(lemma)

        return app, intent_description

    def __find_intent_by_samples(self, request_information):
        temp_list = request_information.get_tokens_list()
        new_request_list = []
        for token in temp_list:
            new_request_list.append(token.get_lemma())

        app = None
        intent_description = None
        min_dist = float(self.__config[WMDThresholdKey])
        for app_name, app_description in self.__application_dict.items():
            for intent in app_description.get_intents_list():
                samples = intent.get_samples()
                for sample in samples:
                    dist = self.__w2v.wmdistance(new_request_list, sample)
                    if dist < min_dist:
                        min_dist = dist
                        app = app_description
                        intent_description = intent
        return app, intent_description

    def __find_intent_by_intersection_words(self, request_information):
        app = None
        intent_description = None
        for app_name, app_imp in self.__application_dict.items():
            intents_dict = app_imp.get_intents()
            for intent_key, intent in intents_dict.items():
                for token in request_information.get_tokens_list():
                    if token.get_lemma() == intent_key:
                        app = app_imp
                        intent_description = intent
                        return app, intent_description
        return app, intent_description
