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

# corenlp = {'CoreNLPServerAddress': 'http://localhost:9000'}
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
#
#     def test2(self):
#         req = "What can u do"
#         token_list = EnglishLanguageModel(config=corenlp).tokenize(req)
#         req = RequestInformation(token_list, None, rtype=RequestType.ACTION, raw_request=req)
#
#         app1 = Application(None, None, [], None)
#         app1.get_name = 'Module for introduction itself'
#
#         i1 = Intent('Ability demonstration', [], [], description='Representation of assistant ability')
#
#         form = Form(app1, i1)
#
#         ans = form.process(req)
#         self.assertEqual(ans, None)
#         self.assertEqual(form.is_finish(), True)
#         self.assertEqual(form.get_parameters_value(), {'action_name': 'Ability demonstration'})
#
#     def test3(self):
#         req = "Goodbye, see u"
#         token_list = EnglishLanguageModel(config=corenlp).tokenize(req)
#         req = RequestInformation(token_list, None, rtype=RequestType.ACTION, raw_request=req)
#
#         app1 = Application(None, None, [], None)
#         app1.get_name = 'Module for introduction itself'
#
#         i1 = Intent('Say goodbye', [], [], [['goodbye'], ['bye'], ['see', 'you'], ['i', 'need', 'to', 'go', ',']],
#                     description='Action for telling goodbye')
#
#         form = Form(app1, i1)
#
#         ans = form.process(req)
#         self.assertEqual(ans, None)
#         self.assertEqual(form.is_finish(), True)
#         self.assertEqual(form.get_parameters_value(), {'action_name': 'Say goodbye'})
#
#     def test4(self):
#         req = "What time is it?"
#         token_list = EnglishLanguageModel(config=corenlp).tokenize(req)
#         req = RequestInformation(token_list, None, rtype=RequestType.ACTION, raw_request=req)
#
#         app1 = Application(None, None, [], None)
#
#         i1 = Intent('Current time', [], [],
#                     [['what', 'be', 'time'], ['what', 'be', 'time'], ['what', 'time', 'be', 'it'],
#                      ['tell', 'i', 'time'], ['please', ',', 'prompt', 'i', 'time']],
#                     description='Action return current time')
#
#         form = Form(app1, i1)
#
#         ans = form.process(req)
#         self.assertEqual(ans, None)
#         self.assertEqual(form.is_finish(), True)
#         self.assertEqual(form.get_parameters_value(), {'action_name': 'Current time'})
#
#     def test5(self):
#         req = "Play tic-tac-toe"
#         token_list = EnglishLanguageModel(config=corenlp).tokenize(req)
#         req = RequestInformation(token_list, None, rtype=RequestType.ACTION, raw_request=req)
#
#         app1 = Application(None, None, [], None)
#
#         i1 = Intent('Start Tic-Tac-Toe Game', [], [],
#                     [['play', 'in', 'tic', 'tac', 'toe', 'game'], ['tic', 'tac', 'toe', 'game'],
#                      ['let', 'fight', 'in', 'tic', 'tac', 'toe', 'game'], ['restart', 'tic', 'tac', 'toe', 'game'],
#                      ['reset', 'tic', 'tac', 'toe', 'game'], ['let', 'play', 'in', 'tic', 'tac', 'toe', 'game'],
#                      ['play', 'in', 'tictactoe', 'game'], ['tictactoe', 'game'],
#                      ['let', 'fight', 'in', 'tictactoe', 'game'], ['restart', 'tictactoe', 'game'],
#                      ['reset', 'tictactoe', 'game'], ['let', 'play', 'in', 'tictactoe', 'game'], ['tictactoe'],
#                      ['tic', 'tac', 'toe'], ['tic-tac-toe'], ['i', 'want', 'to', 'play', 'tic-tac-toe', 'game'],
#                      ['i', 'want', 'to', 'play', 'tictactoe', 'game']],
#                     description=None)
#
#         form = Form(app1, i1)
#
#         ans = form.process(req)
#         self.assertEqual(ans, None)
#         self.assertEqual(form.is_finish(), True)
#         self.assertEqual(form.get_parameters_value(), {'action_name': 'Start Tic-Tac-Toe Game'})
#
#     def test6(self):
#         req = "Play matches games"
#         token_list = EnglishLanguageModel(config=corenlp).tokenize(req)
#         req = RequestInformation(token_list, None, rtype=RequestType.ACTION, raw_request=req)
#         p1 = Parameter('AmountOfMathches', DataType.NUMBER, False, 'How much matches do you want to see on board?')
#
#         i1 = Intent('Start Matches Game', [],[p1],
#            [['play', 'in', 'matches', 'game'], ['match', 'game'], ['let', 'fight', 'in', 'matches', 'game'],
#                         ['restart', 'matches', 'game'], ['reset', 'match', 'game'],
#                         ['let', 'play', 'in', 'matches', 'game'], ['let', 'play', 'in', 'match']],
#                     description=None)
#         app1 = Application(None, None,[i1], None)
#
#         form = Form(app1, i1)
#
#         ans = form.process(req)
#         self.assertEqual(ans, None)
#         self.assertEqual(form.is_finish(), True)
#         self.assertEqual(form.get_parameters_value(), {'action_name': 'Start Matches Game'})
#
#
# if __name__ == '__main__':
#     unittest.main()
