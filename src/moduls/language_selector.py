from answer import AssistantAnswer


class LanguageSelector:
    lang_map = {
        "russian": "ru",
        "english": "en",
        "spain": "es",
        "poland": "pl"
    }
    def __init__(self, config):
        self.__config = config

    def run(self, assistant, parameters_dict):
        language = parameters_dict["language"].lower()
        assistant.user_defined_language = LanguageSelector.lang_map[language]
        param = {"language": language}
        return AssistantAnswer("Language_module.set_up_language", parameters_dict=param)
