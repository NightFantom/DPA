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

    def __call__(self, *args, **kwargs):
        self.start()
