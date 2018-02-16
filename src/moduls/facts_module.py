import language.models.message_constant as mc
from configs.config_constants import FactsFilePath
from answer import AssistantAnswer

from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity
from random import randint


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FactGenerator(metaclass=Singleton):
    def __init__(self, config):
        facts = []
        with open(config[FactsFilePath], "r", encoding="utf-8") as inp:
            facts = inp.readlines()

        vectorizer = TfidfVectorizer(stop_words=ENGLISH_STOP_WORDS.union(["fact", "tell", "about"]))
        vects = vectorizer.fit_transform(facts)

        self.facts = facts
        self.vectorizer = vectorizer
        self.vects = vects

    def best_fact(self, query):
        cosine = cosine_similarity(self.vectorizer.transform([query]), self.vects)
        amax = cosine[0].argmax()
        return self.facts[amax], cosine[0][amax]

    def random_fact(self, lst=None):
        if lst is None:
            lst = self.facts
        return lst[randint(0, len(lst) - 1)]


class FactModule:
    def __init__(self, config):
        self.predictor = FactGenerator(config)

    def run(self, assistant, parameters_dict):
        intent = parameters_dict["Intent"]
        answer = None
        if intent == "Welcome":
            answer = AssistantAnswer(mc.FACTS_MODULE_INTRODUCTION_MESSAGE)
        elif intent == "Random fact":
            answer = AssistantAnswer(mc.FACTS_MODULE_DID_YOU_KNOW, {"answer": self.predictor.random_fact()})
        elif intent == "Fact about":
            request = parameters_dict["Request"]
            fact, cosine = self.predictor.best_fact(request)
            if cosine < 0.3:
                return AssistantAnswer(mc.FACTS_MODULE_DID_YOU_KNOW_NOT_FOUND, {"answer": self.predictor.random_fact()})

            return AssistantAnswer(mc.FACTS_MODULE_DID_YOU_KNOW, {"answer": fact})
        return answer
