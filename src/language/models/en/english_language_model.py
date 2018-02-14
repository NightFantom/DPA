from pycorenlp import StanfordCoreNLP

from configs.config_constants import CoreNLPServerAddress
from language.models.named_entity_recognition import NERType
from language.models.part_of_speech import POS
from language.models.token import Token
from language.models.language_model import LanguageModel


class EnglishLanguageModel(LanguageModel):

    __name = "English"

    def __init__(self, config):
        self.__server = StanfordCoreNLP(config[CoreNLPServerAddress])
        self.pos_map = {"VB": POS.VERB,
                        "VBD": POS.VERB,
                        "VBN": POS.VERB,
                        "VBP": POS.VERB,
                        "NN": POS.NOUN,
                        "NNS": POS.NOUN,
                        "ADJ": POS.ADJ,
                        "CD": POS.CARDINAL_NUMBER,
                        "RP": POS.PARTICLE
                        }

        self.ner_map = {"DATE": NERType.DATE,
                        "PERSON": NERType.PERSON,
                        "NUMBER": NERType.NUMBER}

        self.__question_words = {"where", "who", "what", "when", "why", "whose", "which", "how"}

    def get_language_name(self):
        return EnglishLanguageModel.__name

    def tokenize(self, string):
        output = self.__server.annotate(string, properties={
            'annotators': 'tokenize,pos,lemma,ner',
            'outputFormat': 'json'})

        tokens_description = output["sentences"][0]["tokens"]
        token_list = []
        for description in tokens_description:
            lemma = description["lemma"].lower()
            word = description["originalText"]
            pos_tag = description["pos"]
            pos_tag = self.convert_pos(pos_tag)
            token = Token(word, lemma, pos_tag)
            token_list.append(token)

            ner_type = description.get("ner", None)
            if ner_type is not None:
                ner_type = self.convert_ner(ner_type)
                token.set_NER_type(ner_type)

        temp_list = []
        stop = len(token_list)
        for i in range(stop - 1):
            if token_list[i].get_pos() == POS.VERB and token_list[i + 1].get_pos() == POS.PARTICLE:
                verb_token = token_list[i]
                particle_token = token_list[i+1]
                word = verb_token.get_word() + " " + particle_token.get_word()
                lemma = verb_token.get_lemma() + " " + particle_token.get_lemma()
                token = Token(word, lemma, verb_token.get_pos())
                temp_list.append(token)
            else:
                temp_list.append(token_list[i])

        if token_list[stop - 1].get_pos() != POS.PARTICLE:
            temp_list.append(token_list[stop - 1])

        merge_list = []
        pos = 0
        while pos < len(temp_list):
            if temp_list[pos].get_NER_type() != NERType.DATE:
                merge_list.append(temp_list[pos])
                pos += 1
            else:
                end_pos = pos
                value = ""
                while end_pos < len(temp_list) and temp_list[end_pos].get_NER_type() == NERType.DATE:
                    value += temp_list[end_pos].get_word() + " "
                    end_pos += 1
                token = Token(value, value, POS.NOUN)
                token.set_NER_type(NERType.DATE)
                merge_list.append(token)
                pos = end_pos

        return merge_list

    def convert_pos(self, pos_str):
        return self.pos_map.get(pos_str, POS.UNKOWN)

    def convert_ner(self, ner):
        ner = ner.upper()
        return self.ner_map.get(ner, None)

    def is_question(self, tokens_list):
        lemma = tokens_list[0].get_lemma()
        return lemma in self.__question_words
