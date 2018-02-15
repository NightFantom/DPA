import subprocess
import uuid
import wave
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from configs.config_constants import StartMessageKey, TokenKey, PrintMessages, SpeechKey
from assistant import Assistant
from interface.base_interface import BaseInterface
from language.models.en.speechrecognition import SpeechRecognition
import logging

USER_ASKS_PATTERN = "User {} {} asks: '{}'"
ASSISTANT_ANSWERS_PATTERN = "Answer for user {} {}: '{}'"
STOP_MESSAGE_KEY = "stop_message_key"

class Telegram(BaseInterface):

    def __init__(self, language_model, app_dict, w2v, message_bundle, config):
        super().__init__(message_bundle, config)

        self.__language_model = language_model
        self.__app_dict = app_dict
        self.__w2v = w2v
        self.__token = self.config[TokenKey]
        self.__START_MESSAGE_KEY = self.config[StartMessageKey]
        self.__s2t = SpeechRecognition(self.config[SpeechKey])
        self.__user_assistant_dict = {}

        self.__updater = Updater(self.__token)
        dp = self.__updater.dispatcher
        dp.add_handler(CommandHandler("start", self.slash_start), group=0)
        dp.add_handler(CommandHandler("stop", self.slash_stop), group=0)
        dp.add_handler(MessageHandler(Filters.voice, self.idle_main))
        dp.add_handler(MessageHandler(Filters.text, self.idle_main))

    def audio(self, bot, update):
        voice_file = bot.get_file(update.message.voice.file_id)
        if update.message.voice.duration > 10:
            return "Voice message too large (max 10 sec)"
        voice_file.download('voice.mp3')
        subprocess.call(['ffmpeg', '-i', 'voice.mp3',
                         'voice.wav'])
        wf = wave.open('voice.wav', 'rb')
        results = self.__s2t.ask_yandex('voice.wav', str(uuid.uuid4()).replace("-", ""), "en-US")
        os.remove('voice.mp3')
        os.remove('voice.wav')
        max_key = None
        max_value = None
        for item in results:
            if max_value is None or results.get(item) > max_value:
                max_key = item
                max_value = results.get(item)
        return max_key

    def idle_main(self, bot, update):
        if update.message.text is not None:
            request = update.message.text.strip()
        else:
            request = self.audio(bot, update)
        user_id = update.message.chat_id
        does_print = bool(self.config[PrintMessages])
        user_name = update.message.from_user.username
        if does_print:
            print((USER_ASKS_PATTERN.format(user_id, user_name, request)))
        assistant = self.__user_assistant_dict.get(user_id, None)
        if assistant is None:
            assistant = Assistant(self.__language_model, self.message_bundle, self.__app_dict,
                                  self.config, w2v=self.__w2v, user_id=user_id)
            self.__user_assistant_dict[user_id] = assistant
        answer = assistant.process_request(request)
        message = self.format_answer(answer)
        if does_print:
            print(ASSISTANT_ANSWERS_PATTERN.format(user_id, user_name, message))
        bot.sendMessage(update.message.chat_id, text=message)
        if answer.picture is not None:
            image = answer.picture
            if hasattr(image, 'read'):
                bot.sendPhoto(update.message.chat_id, photo=image)

    def slash_start(self, bot, update):
        bot.sendMessage(update.message.chat_id, text=self.message_bundle[self.__START_MESSAGE_KEY])

    def slash_stop(self, bot, update):
        user_id = update.message.chat_id
        assistant = self.__user_assistant_dict.get(user_id, None)
        if assistant is not None:
            del self.__user_assistant_dict[user_id]
            bot.sendMessage(update.message.chat_id, text=self.message_bundle[STOP_MESSAGE_KEY])

    def start(self):
        self.__updater.start_polling()

    def stop(self):
        self.__updater.stop()
        for assistant in self.__user_assistant_dict.values():
            assistant.stop()
