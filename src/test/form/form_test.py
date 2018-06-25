import unittest
from form.form import Form
from language.models.named_entity_recognition import NERType
from application.application import Application
from language.models.language_model import RequestInformation
from language.models.en.english_language_model import EnglishLanguageModel
from language.models.request_type import RequestType
from application.parameter import Parameter
from application.data_type import DataType
from application.intent import *
from unittest.mock import Mock

#corenlp = {'CoreNLPServerAddress': 'http://localhost:9000'}
#
class FormTest(unittest.TestCase):
    def test1(self):
        app = Mock()
        intent_description = Mock()
        intent_description.get_name = Mock(return_value="my_mock_name")
        param = Mock()
        param.get_name = Mock(return_value="some_param_name")
        param.get_data_type = Mock(return_value=DataType.DATE)
        param.is_obligatory = Mock(return_value=True)
        params = [param]
        intent_description.get_parameters_list = Mock(return_value=params)

        request = Mock()
        token = Mock()
        token.get_NER_type = Mock(return_value=NERType.DATE)
        token.get_word = Mock(return_value="2018")
        tokens = [token]
        request.get_tokens_list = Mock(return_value=tokens)

        form = Form(app, intent_description)

        ans = form.process(request)
        self.assertIsNone(ans)
        self.assertTrue(form.is_finish())

    def test2(self):
        app = Mock()
        intent_description = Mock()
        intent_description.get_name = Mock(return_value="my_mock_name")
        param = Mock()
        param.get_name = Mock(return_value="Play")
        param.get_data_type = Mock(return_value=DataType.STR)
        param.is_obligatory = Mock(return_value=True)
        param.get_clarifying_question=Mock(return_value='Question')
        param.group_ids=[]
        params = [param]
        intent_description.get_parameters_list = Mock(return_value=params)

        request = Mock()
        token = Mock()
        token.get_NER_type = Mock(return_value=None)
        token.get_word = Mock(return_value="Word")
        tokens = [token]
        request.get_tokens_list = Mock(return_value=tokens)

        form = Form(app, intent_description)

        ans = form.process(request)
        self.assertIsNotNone(ans)
        self.assertEqual(ans.message,param.get_clarifying_question())
        self.assertFalse(form.is_finish())

    def test3(self):
        app = Mock()
        tokens = []
        token = Mock()
        token.get_NER_type = Mock(return_value=None)
        token.get_word = Mock(return_value="Goodbye")
        tokens.append(token)

        param = Mock()
        param.get_name = Mock(return_value="Param")

        param.get_data_type = Mock(return_value=[])
        param.is_obligatory = Mock(return_value=False)
        params = [param]

        intent_description = Mock()
        intent_description.get_name = Mock(return_value="Say goodbye")
        intent_description.get_parameters_list = Mock(return_value=[])
        intent_description.description = Mock(return_value='Action for telling goodbye')
        intent_description.get_samples = Mock(
            return_value=[['goodbye'], ['bye'], ['see', 'you'], ['i', 'need', 'to', 'go', ',']])
        request = Mock()
        request.get_tokens_list = Mock(return_value=tokens)

        form = Form(app, intent_description)

        ans = form.process(request)
        self.assertIsNone(ans)
        self.assertTrue(form.is_finish())
        self.assertEqual(form.get_parameters_value(),{'action_name': 'Say goodbye'})

    def test4(self):
        app = Mock()
        intent_description = Mock()
        intent_description.get_name = Mock(return_value="my_mock_name")
        param = Mock()
        param.get_name = Mock(return_value="name")
        param.get_data_type = Mock(return_value=DataType.NUMBER)
        param.is_obligatory = Mock(return_value=True)
        param.get_clarifying_question = Mock(return_value='Question')
        param.group_ids = []
        params = [param]
        intent_description.get_parameters_list = Mock(return_value=params)

        request = Mock()
        token = Mock()
        token.get_NER_type = Mock(return_value=NERType.NUMBER)
        token.get_word = Mock(return_value="request")
        tokens = [token]
        request.get_tokens_list = Mock(return_value=tokens)

        form = Form(app, intent_description)

        ans = form.process(request)
        self.assertIsNone(ans)
        self.assertTrue(form.is_finish())

if __name__ == '__main__':
    unittest.main()
