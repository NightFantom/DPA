from yandex_translate import YandexTranslate
from configs.config_constants import YandexTranslatorAPIKey


class Translate:

    def __init__(self, config):
        self.__config = config
        self._translator = YandexTranslate(self.__config[YandexTranslatorAPIKey])

    def translate(self, text, source_lang, dest_lang):
        json = self._translator.translate(text, source_lang + "-" + dest_lang)
        text = json["text"][0]
        return text
