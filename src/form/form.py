from assistant.answer import AssistantAnswer
from application.data_type import DataType
from language.models.named_entity_recognition import NERType
from language.models.request_type import RequestType
from constants import FORM_ACTION_NAME


class Form:
    def __init__(self, app, intent_description):
        self.__app = app
        self.__int_desc = intent_description
        self.__parameters_value = dict()
        self.__parameters_value[FORM_ACTION_NAME] = intent_description.get_name()
        self.__is_finish = False
        self.__expected_field = None

    def get_parameters_value(self):
        return self.__parameters_value

    def     process(self, request_information):
        token_list = request_information.get_tokens_list()
        parameters_list = self.__int_desc.get_parameters_list()
        for token in token_list:
            for param in parameters_list:
                if self.__expected_field is not None and param.get_name() != self.__expected_field:
                    continue
                value = self.__parameters_value.get(param.get_name(), None)
                if value is None:
                    dt = param.get_data_type()
                    ner_type = token.get_NER_type()
                    if dt == DataType.DATE and ner_type == NERType.DATE:
                        self.__parameters_value[param.get_name()] = token.get_word()
                        break
                    elif dt == DataType.NUMBER and ner_type == NERType.NUMBER:
                        self.__parameters_value[param.get_name()] = token.get_word()
                        break
                    elif dt == DataType.STR:
                        req_exp = param.get_regexp()
                        if req_exp is not None:
                            result = req_exp.match(request_information.get_raw_request())
                            if result is not None:
                                id_list = param.group_ids
                                groups = result.groups()
                                for g_id in id_list:
                                    element = groups[g_id]
                                    if element is not None:
                                        self.__parameters_value[param.get_name()] = element
                                        break
                        temp_value = self.__parameters_value.get(param.get_name(), None)
                        if temp_value is None and request_information.get_type() == RequestType.ANSWER:
                            self.__parameters_value[param.get_name()] = request_information.get_raw_request()

        answer = None
        for param in parameters_list:
            value = self.__parameters_value.get(param.get_name(), None)
            if value is None and param.is_obligatory():
                answer = AssistantAnswer(None, message_str=param.get_clarifying_question())
                self.__expected_field = param.get_name()
                break

        if answer is None:
            self.__is_finish = True
            self.__expected_field = None
        return answer

    def is_finish(self):
        return self.__is_finish

    def get_app(self):
        return self.__app
