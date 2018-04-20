import language.models.message_constant as mc
from answer import AssistantAnswer
from constants import FORM_ACTION_NAME
import datetime


class SelfIntroductionModule:
    HEAD_PATTERN = "{} - {}"
    INTENT_PATTERN = "   -{}"
    INTENT_WITH_DESC_PATTERN = "   -{}: {}"

    def __init__(self, config):
        pass

    def run(self, assistant, parameters_dict):
        intent = parameters_dict[FORM_ACTION_NAME]
        answer = None
        if intent == "Ability demonstration":
            answer = self.ability_demonstration(assistant, parameters_dict)
        elif intent == "Say hi":
            answer = AssistantAnswer(mc.HI_MESSAGE)
        elif intent == "Say goodbye":
            answer = AssistantAnswer(mc.GOODBYE_MESSAGE)
        elif intent == "My affairs":
            answer = AssistantAnswer(mc.MY_AFFAIRS)
        elif intent == "Current time":
            time = datetime.datetime.now()
            params = {"hours": time.hour, "minutes": time.minute, "seconds": time.second}
            answer = AssistantAnswer(mc.CURRENT_TIME, parameters_dict=params)
        return answer

    def ability_demonstration(self, assistant, parameters_dict):
        apps = assistant.application_dict
        lines = []
        for app_name, app_desc in apps.items():
            lines.append(SelfIntroductionModule.HEAD_PATTERN.format(app_desc.get_name(), app_desc.get_description()))
            for intent in app_desc.get_intents_list():
                desc = intent.description
                if desc is None:
                    line = SelfIntroductionModule.INTENT_PATTERN.format(intent.get_name())
                else:
                    line = SelfIntroductionModule.INTENT_WITH_DESC_PATTERN.format(intent.get_name(), desc)
                lines.append(line)
        lines = "\n".join(lines)
        answer = AssistantAnswer(mc.INTRODUCTION_MESSAGE, parameters_dict={"desc": lines})
        return answer