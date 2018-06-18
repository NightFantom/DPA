from typing import Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from assistant.answer import AssistantAnswer
from assistant.intent_detector import IntentDetector
from configs.config_constants import StartMessageKey, TokenKey, PrintMessages
from assistant.assistant import Assistant
from interface.base_interface import BaseInterface
from interface.Messenger import Messenger
from interface.Messenger import *

socks = None


class Telegram(Messenger):

    def __init__(self, language_model, intent_detector: IntentDetector, config):
        super().__init__(language_model, intent_detector,  config)
        self.__token = self.config[TokenKey]
        self.__updater = Updater(self.__token, request_kwargs=socks)
        self.__START_MESSAGE_KEY = self.config[StartMessageKey]
        dp = self.__updater.dispatcher
        dp.add_handler(CommandHandler("start", self.slash_start), group=0)
        dp.add_handler(CommandHandler("stop", self.slash_stop), group=0)
        dp.add_handler(CallbackQueryHandler(self.evaluate))
        dp.add_handler(MessageHandler(Filters.text, self.idle_main))

    def idle_main(self, bot, update):
        request = update.message.text.strip()
        user_id = update.message.chat_id
        user_name = update.message.from_user.username
        answer = super().proccess_request(user_id, user_name, request)
        buttons = self.get_buttons(answer.dialog_step)
        bot.sendMessage(user_id, text=answer.message, reply_markup=buttons)
        if answer.picture is not None:
            image = answer.picture
            if hasattr(image, 'read'):
                bot.sendPhoto(user_id, photo=image)

    def slash_start(self, bot, update):
        bot.sendMessage(update.message.chat_id, text=self.config[self.__START_MESSAGE_KEY])

    def slash_stop(self, bot, update):
        user_id: int = update.message.chat_id
        assistant: Assistant = self.user_assistant_dict.get(user_id, None)
        if assistant is not None:
            assistant.stop()
            del self.user_assistant_dict[user_id]
            bot.sendMessage(update.message.chat_id, text=self.config[STOP_MESSAGE_KEY])

    def evaluate(self, bot: Bot, update):
        query = update.callback_query
        user_id = query.message.chat_id
        raw_data = query.data
        data_list = raw_data.split("_")
        mark = data_list[0]
        dialog_step = int(data_list[1])
        ans = self.evaluate_request(user_id, mark,step=dialog_step)
        if ans != None:
            bot.sendMessage(user_id, text=ans)

    def start(self):
        self.__updater.start_polling()

    def stop(self):
        self.__updater.stop()
        for assistant in self.user_assistant_dict.values():
            assistant.stop()

    def get_buttons(self, message_id) -> InlineKeyboardMarkup:
        button_list = [[
            InlineKeyboardButton("👎", callback_data="0_{}".format(message_id)),
            InlineKeyboardButton("👍", callback_data="1_{}".format(message_id))
        ]]
        buttons = InlineKeyboardMarkup(button_list)
        return buttons
