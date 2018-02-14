import json
import importlib
from application.application import Application
from application.application import IntegrationType
from application.intent import Intent
from application.parameter import Parameter
from application.data_type import DataType

APPLICATIONS_TAG = "applications"
APPLICATION_NAME_TAG = "name"
APPLICATION_DESCRIPTION_TAG = "description"
APPLICATION_TYPE_TAG = "type"
APPLICATION_ENDPOINT_URL_TAG = "url"
APPLICATION_INTENTS_TAG = "intents"
APPLICATION_IMPLEMENTATION = "impl"

INTENT_NAME_TAG = "name"
INTENT_KEY_PHRASES_TAG = "key_phrases"
INTENT_SAMPLES_TAG = "samples"
INTENT_PARAMETERS_TAG = "parameters"
INTENT_DESCRIPTION_TAG = "description"

PARAMETER_NAME_TAG = "name"
PARAMETER_TYPE_TAG = "data_type"
PARAMETER_OBLIGATORY_TAG = "obligatory"
PARAMETER_QUESTION_TAG = "question"
PARAMETER_REGEXP_TAG = "regexp"
PARAMETER_REGEXP_GROUP_TAG = "reqexp_group_id"
EMPTY_LIST = []


def load_config(path_str, language_model):
    with open(path_str) as data_file:
        data = json.load(data_file)

    app_dict = {}
    for app in data[APPLICATIONS_TAG]:
        app_name = app[APPLICATION_NAME_TAG]
        description = app[APPLICATION_DESCRIPTION_TAG]
        type = app[APPLICATION_TYPE_TAG]
        URL = app.get(APPLICATION_ENDPOINT_URL_TAG, None)
        intents = []
        for intent in app[APPLICATION_INTENTS_TAG]:
            intent_name = intent[INTENT_NAME_TAG]
            samples_list = intent.get(INTENT_SAMPLES_TAG, None)
            if samples_list is not None:
                samples_list = [get_lemmas(el, language_model) for el in samples_list]

            key_phrases_list = intent.get(INTENT_KEY_PHRASES_TAG, EMPTY_LIST)
            key_phrases_list = [x.lower() for x in key_phrases_list]
            parameters_list = []
            param_description_list = intent.get(INTENT_PARAMETERS_TAG, EMPTY_LIST)
            for parameter in param_description_list:
                param_name = parameter[PARAMETER_NAME_TAG]
                param_data_type = parameter[PARAMETER_TYPE_TAG]
                param_data_type = DataType[param_data_type.upper()]
                param_obligatory = parameter[PARAMETER_OBLIGATORY_TAG]
                param_regexp = parameter.get(PARAMETER_REGEXP_TAG, None)
                param_regexp_group = parameter.get(PARAMETER_REGEXP_GROUP_TAG, None)
                param_question = parameter.get(PARAMETER_QUESTION_TAG, None)
                param_inst = Parameter(param_name, param_data_type, obligatory_bool=param_obligatory,
                                       question_str=param_question, regexp=param_regexp,
                                       regexp_group=param_regexp_group)
                parameters_list.append(param_inst)

            intent_desc = intent.get(INTENT_DESCRIPTION_TAG, None)
            intent_ints = Intent(intent_name, key_phrases_list, parameters_list, samples=samples_list, description=intent_desc)
            intents.append(intent_ints)

        app_inst = Application(app_name, description, intents, integration_type=IntegrationType[type], url=URL)

        clazz = app.get(APPLICATION_IMPLEMENTATION, None)
        if clazz is not None:
            app_inst.set_impl(clazz)

        app_dict[app_name.lower()] = app_inst

    return app_dict


def get_lemmas(text, language_model):
    tokens = language_model.tokenize(text)
    new_request_list = []
    for token in tokens:
        new_request_list.append(token.get_lemma().lower())
    return new_request_list