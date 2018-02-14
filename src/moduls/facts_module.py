import language.models.message_constant as mc
from answer import AssistantAnswer

from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity
from random import randint

class FactModule:
    vectorizer = None
    vects = None

    def __init__(self, config):
        if FactModule.vectorizer is None:
            FactModule.facts = []
            with open("facts.txt", "r") as inp:
                FactModule.facts = inp.readlines()

            FactModule.vectorizer = TfidfVectorizer(stop_words=ENGLISH_STOP_WORDS.union(["fact", "tell", "about"]))
            FactModule.vectorizer.fit(FactModule.facts)
            FactModule.vects = FactModule.vectorizer.transform(FactModule.facts)


    def run(self, assistant, parameters_dict):
        intent = parameters_dict["Intent"]
        answer = None
        if intent == "Welcome":
            answer = AssistantAnswer(mc.FACTS_MODULE_INTRODUCTION_MESSAGE)
        elif intent == "Random fact":
            answer = AssistantAnswer(mc.FACTS_MODULE_DID_YOU_KNOW, {"answer": self.__random_fact()})
        elif intent == "Fact about":
            request = parameters_dict["Request"]
            answer = self.__ask(request)
        return answer


    def __ask(self, query):
        cosine = cosine_similarity(FactModule.vectorizer.transform([query]), FactModule.vects)
        amax = cosine[0].argmax()
        if cosine[0][amax] < 0.3:
            return AssistantAnswer(mc.FACTS_MODULE_DID_YOU_KNOW_NOT_FOUND, {"answer": self.__random_fact()})

        answer = AssistantAnswer(mc.FACTS_MODULE_DID_YOU_KNOW, {"answer": FactModule.facts[amax]})
        return answer

    def __random_fact(self, lst=None):
        if lst is None:
            lst = FactModule.facts
        return lst[randint(0, len(lst) - 1)]
