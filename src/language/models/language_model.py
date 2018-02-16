from language.models.part_of_speech import POS
from language.models.request_type import RequestType
EMPTY_STRING = ""

class RequestInformation:
    def __init__(self, tokens_list, intent, rtype, raw_request):
        self.__type = rtype
        self.__tokens_list = tokens_list
        self.__intent = intent
        self.__app_name_str = EMPTY_STRING
        self.__raw_request = raw_request

    def get_type(self):
        return self.__type

    def set_type(self, rtype):
        self.__type = rtype

    def get_tokens_list(self):
        return self.__tokens_list

    def get_intent(self):
        return self.__intent

    def get_app_name(self):
        return self.__app_name_str

    def set_app_name(self, name):
        self.__app_name_str = name

    def get_raw_request(self):
        return self.__raw_request


class LanguageModel:
    def parse(self, string):
        string = self.__preprocess_text(string)
        tokens_list = self.tokenize(string)
        verb = self.__find_first_verb(tokens_list)
        obj = RequestInformation(tokens_list, verb, rtype=RequestType.ACTION, raw_request=string)
        app_name = self.__get_app_name(tokens_list)
        obj.set_app_name(app_name)
        return obj

    def tokenize(self, string):
        raise NotImplementedError()

    def get_language_name(self):
        pass

    @property
    def language_code(self):
        pass

    def __preprocess_text(self, string):
        return string

    def __find_first_verb(self, tokens_list):
        for token in tokens_list:
            if token.get_pos() == POS.VERB:
                return token
        return None

    def __get_app_name(self, tokens_list):
        return tokens_list[0].get_word()

    def convert_ner(self, ner):
        raise NotImplementedError()

    def convert_pos(self, pos_str):
        raise NotImplementedError()

    def is_question(self, tokens_list):
        raise NotImplementedError()
