import requests
from bs4 import BeautifulSoup


class SpeechRecognition:

    def __init__(self, key):
        self.__key = key

    def ask_yandex(self, wave_file, uid, lang="en-US"):
        # API doc
        # https://tech.yandex.ru/speechkit/cloud/doc/guide/concepts/asr-http-request-docpage/
        url = "https://asr.yandex.net/asr_xml?uuid={}&key={}&topic={}&lang={}&disableAntimat={}"
        url = url.format(uid, self.__key, "queries", lang, "true")

        # just read raw information of the container
        data = open(wave_file, "rb").read()
        headers = {'Content-Type': 'audio/x-wav', 'Content-Length': str(len(data))}

        # do post request of data
        resp = requests.post(url, data=data, headers=headers)

        # parse answers
        dom = BeautifulSoup(resp.text, "lxml")
        result = dict((var.string, float(var['confidence']))
                      for var
                      in dom.html.body.recognitionresults.findAll("variant"))
        return result
