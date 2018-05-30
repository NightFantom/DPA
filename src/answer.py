class AssistantAnswer:
    def __init__(self, message_key_str, parameters_dict=None, message_str=None, is_error=False, **kwargs):
        self.__message_key = message_key_str
        self.__parameters = parameters_dict
        self.__is_error = is_error
        self.__message = message_str
        self.__picture = kwargs.get("picture", None)
        self.__dialog_step = 0

    @property
    def message_key(self):
        return self.__message_key

    @property
    def parameters(self):
        return self.__parameters

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, message):
        self.__message = message

    def is_error(self):
        return self.__is_error

    @property
    def picture(self):
        return self.__picture

    @property
    def dialog_step(self)-> int:
        return self.__dialog_step

    @dialog_step.setter
    def dialog_step(self, val: int):
        self.__dialog_step = val