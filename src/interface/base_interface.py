class BaseInterface:

    def __init__(self, config):
        self.__config = config

    def start(self):
        pass

    def stop(self):
        pass

    @property
    def config(self):
        return self.__config

    def __call__(self, *args, **kwargs):
        self.start()