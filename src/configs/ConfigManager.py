from configparser import ConfigParser
import os


class ConfigManager:
    # priority list = ["default_config","message_bundle"] or
    # ["message_bundle","default_config"]
    def __init__(self, priority_list):
        self.__priority = priority_list
        self.__configs = []
        self.__map = {"default_config": "configs/config.ini" if os.path.isfile("configs/config.ini")
        else "config/default_config.ini",
                      "message_bundle": "language/models/en/message.ini"}

        for i in priority_list:
            config_parser = ConfigParser()
            config_parser.read(self.__map[i], encoding="utf-8")
            self.__configs.append(config_parser["DEFAULT"])

    def __getitem__(self, item):
        for config in self.__configs:
            if config.__contains__(item):
                return config[item]
        raise KeyError
