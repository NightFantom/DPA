from configparser import ConfigParser
import os


class ConfigManager:
    def __init__(self, priority_list):
        self.__priority = priority_list
        self.__configs = []
        for i in priority_list:
            config_parser = ConfigParser()
            config_parser.read(i, encoding="utf-8")
            self.__configs.append(config_parser["DEFAULT"])

    def __getitem__(self, item):
        for config in self.__configs:
            if item in config:
                return config[item]
        raise KeyError
