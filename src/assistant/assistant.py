from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict
import pandas as pd
import requests
import language.models.message_constant as mc
from assistant.answer import AssistantAnswer
from application.application import IntegrationType
from assistant.intent_detector import IntentDetector
from configs.config_constants import HistoryFilePath, IsStubMode
from form.form import Form
from language.translate import Translate
import importlib
import distutils.util as utils
import json

DEFAULT_ENCODING: str = "utf-8"
GAME_TURN_INTENT_NAME: str = "Turn"


class Assistant:
    __MARK: str = "mark"
    __REQUEST: str = "request"
    __FORMATTED_ANSWER: str = "formatted_answer"
    __ANSWER_KEY: str = "answer_key"
    __DIALOG_STEP: str = "dialog_step"
    __NO_MARK: int = -1

    def __init__(self, language_model,  config, intent_detector: IntentDetector, **kargs):
        self.language_model = language_model
        self.__stack = []
        self.__history: OrderedDict = OrderedDict()
        self.__config = config
        self.__is_stub_mode = utils.strtobool(config[IsStubMode])
        self.__game_app = None
        self.__user_id = kargs.get("user_id", "console")
        self.__modules = {}
        self.__user_defined_lang = self.language_model.language_code
        self._translate_module = Translate(config)
        self.__dialog_step = 0
        self.__intent_detector = intent_detector

    def process_request(self, user_request_str):
        dest_lang = self.language_model.language_code
        if self.__user_defined_lang != dest_lang:
            user_request_str = self._translate_module.translate(user_request_str, self.__user_defined_lang, dest_lang)

        request_information = self.language_model.parse(user_request_str)
        app, intent_description = self.__intent_detector.detect_intent(request_information)

        if app is None or intent_description is None:
            if len(self.__stack) > 0:
                form = self.__stack.pop(0)
                app = form.get_app()
                answer = self.__process_intent(app, request_information, form)
            elif self.__game_app is not None:
                class_name = self.__game_app.get_impl()
                module = self.__get_module_by_class_name(class_name)
                if module.is_active:
                    app = self.__game_app
                    intent_description = self.__game_app.get_intent_by_name(GAME_TURN_INTENT_NAME)
                    form = Form(app, intent_description)
                    answer = self.__process_intent(app, request_information, form)
                else:
                    answer = AssistantAnswer(mc.DID_NOT_UNDERSTAND)
            else:
                answer = AssistantAnswer(mc.DID_NOT_UNDERSTAND)
        else:
            if app.get_intent_by_name(GAME_TURN_INTENT_NAME) is not None:
                self.__game_app = app
            form = Form(app, intent_description)
            answer = self.__process_intent(app, request_information, form)

        if answer is None:
            answer = AssistantAnswer(mc.DID_NOT_UNDERSTAND)
        formatted_answer = self.format_answer(answer)
        answer.message = formatted_answer

        step_desc: Dict[str, Any] = {
            Assistant.__REQUEST: user_request_str,
            Assistant.__FORMATTED_ANSWER: formatted_answer,
            Assistant.__ANSWER_KEY: answer.message_key,
            Assistant.__MARK: Assistant.__NO_MARK,
            Assistant.__DIALOG_STEP: self.__dialog_step
        }
        self.__history[self.__dialog_step] = step_desc
        answer.dialog_step = self.__dialog_step
        self.__dialog_step += 1
        return answer

    def mark(self, dialog_step: int, mark: int) -> AssistantAnswer:
        step_desc: Dict[str, Any] = self.__history.get(dialog_step)
        answer = None
        if step_desc and step_desc[Assistant.__MARK] == -1:
            step_desc[Assistant.__MARK] = mark
            answer = AssistantAnswer(mc.FEEDBACK)
            formatted_answer = self.format_answer(answer)
            answer.message = formatted_answer
        return answer

    def mark_last(self, mark: int):
        print("Keys:",self.__history.keys())
        return self.mark(list(self.__history.keys())[-1], mark)

    def __get_module_by_class_name(self, clazz):
        module = self.__modules.get(clazz, None)
        if module is None:
            module_name, class_name = clazz.rsplit(".", 1)
            MyClass = getattr(importlib.import_module(module_name), class_name)
            module = MyClass(self.__config)
            self.__modules[clazz] = module
        return module

    def __process_intent(self, app, request_information, form):
        answer = form.process(request_information)
        if form.is_finish():
            answer = self.__execute_request(app, form.get_parameters_value())
        else:
            # save_form
            self.__stack.insert(0, form)
        return answer

    def __execute_request(self, app, parameters_dict):
        if app.get_integration_type() == IntegrationType.Module:
            class_name = app.get_impl()
            module = self.__get_module_by_class_name(class_name)
            answer = module.run(self, parameters_dict)
        elif not self.__is_stub_mode:
            url = app.get_endpoint_url()
            try:
                response = requests.post(url, data=json.dumps(parameters_dict))
                if response.status_code == 200:
                    response_dict = response.json()
                    message_source: Dict[str, str] = response_dict.get("answer")
                    if not message_source:
                        message_source = response_dict.get("error")
                    answer = AssistantAnswer(message_source["message_key"], message_str=message_source["message"])
                else:
                    answer = AssistantAnswer(mc.ERROR_RESPONSE_CODE, parameters_dict={"code": response.status_code})
            except Exception:
                answer = AssistantAnswer(mc.SERVICE_DOES_NOT_WORK)
        else:
            answer = "AppName: " + app.get_name()
            for key, value in parameters_dict.items():
                answer += "| " + key + "=" + value
            answer = AssistantAnswer(None, message_str=answer)
        return answer

    def stop(self):
        if len(self.__history) > 0:
            path = Path(self.__config[HistoryFilePath].format(self.__user_id))
            columns: Dict[str, Any] = {
                Assistant.__MARK: [],
                Assistant.__FORMATTED_ANSWER: [],
                Assistant.__ANSWER_KEY: [],
                Assistant.__REQUEST: [],
                Assistant.__DIALOG_STEP: []
            }
            for dialog_step, desc in self.__history.items():
                for column_name, value in desc.items():
                    columns[column_name].append(value)

            pd.DataFrame(data=columns).to_csv(path, index=False, encoding=DEFAULT_ENCODING)

    def format_answer(self, answer):
        message: str = None
        if answer.message_key is not None:
            message = self.__config[answer.message_key]
            if message:
                params = answer.parameters
                if params is not None:
                    message = message.format(**params)
        if not message:
            message = answer.message
        dest_lang = self.language_model.language_code
        if self.__user_defined_lang != dest_lang:
            message = self._translate_module.translate(message, dest_lang, self.__user_defined_lang)

        return message

    @property
    def user_defined_language(self):
        return self.__user_defined_lang

    @user_defined_language.setter
    def user_defined_language(self, lang):
        if lang is not None:
            self.__user_defined_lang = lang.lower()
