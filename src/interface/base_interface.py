class BaseInterface:

    def __init__(self, message_bundle, config):
        self.__config = config
        self.__message_bundle = message_bundle

    def start(self):
        pass

    def stop(self):
        pass

    @property
    def message_bundle(self):
        return self.__message_bundle

    @property
    def config(self):
        return self.__config

    def format_answer(self, assistant_answer):
        if assistant_answer.message_key is not None:
            message = self.__message_bundle[assistant_answer.message_key]
            params = assistant_answer.parameters
            if params is not None:
                message = message.format(**params)
        else:
            message = assistant_answer.message
        return message

    def __call__(self, *args, **kwargs):
        self.start()