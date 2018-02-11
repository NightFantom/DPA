import wolframalpha
import language.models.message_constant as mc
from answer import AssistantAnswer
from configs.config_constants import WolframAlphaAppIdKey


IMG = 'img'
PLAIN_TEXT = 'plaintext'
SCR_TAG = '@src'
SUBPOD = 'subpod'
PATTERN = '%s'
POD = 'pod'


class MathModule:

    def __init__(self, config):
        self.__app_id = config[WolframAlphaAppIdKey]

    def run(self, assistant, parameters_dict):
        intent = parameters_dict["Intent"]
        answer = None
        if intent == "Welcome":
            answer = AssistantAnswer(mc.MATH_MODULE_INTRODUCTION_MESSAGE)
        elif intent == "Solving mathematical tasks":
            request = parameters_dict["Request"]
            answer = self.__ask(request)
        return answer

    def __ask(self, query, input_type="image"):
        client = wolframalpha.Client(self.__app_id)
        response = client.query(query)
        text = ''
        img_link = ''
        # Wolfram cannot resolve the question
        answer = None
        if response['@success'] == 'false':
            answer = AssistantAnswer(mc.MATH_MODULE_BAD_RESPONSE)
        # Wolfram was able to resolve question
        else:
            # pod[0] is the question
            pod0 = response[POD][0]
            # pod[1] may contains the answer
            pod1 = response[POD][1]
            # checking if pod1 has primary=true or title=result|definition

            title = pod1['@title'].lower()

            if ('definition' in title) or ('result' in title) or (pod1.get('@primary', 'false') == 'true'):
                # extracting result from pod1
                if isinstance(pod1[(PATTERN % SUBPOD)], list):
                    text = pod1[SUBPOD][0][PLAIN_TEXT]
                    img_link = pod1[SUBPOD][0][IMG][SCR_TAG]
                else:
                    text = pod1[SUBPOD][PLAIN_TEXT]
                    img_link = pod1[SUBPOD][IMG][SCR_TAG]
            else:
                # extracting wolfram question interpretation from pod0
                if isinstance(pod0[SUBPOD], list):
                    text = pod0[SUBPOD][0][(PATTERN % PLAIN_TEXT)]
                    img_link = pod0[SUBPOD][0][IMG][SCR_TAG]
                else:
                    text = pod0[SUBPOD][PLAIN_TEXT]
                    img_link = pod0[SUBPOD][IMG][(PATTERN % SCR_TAG)]
                    # removing unnecessary parenthesis
                    text = text.split('(')[0]
            input_type = input_type.lower()

            if input_type == "image" and img_link is not '':
                result = img_link
            else:
                result = text
            answer = AssistantAnswer(mc.MATH_MODULE_ANSWER, {"answer": result})
        return answer
