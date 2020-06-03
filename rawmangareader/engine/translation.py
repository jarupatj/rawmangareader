import requests
import json
import uuid

class Translator():
    ENDPOINT = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"

    @staticmethod
    def getSupportedLanguages():
        return ['en', 'ja', 'th']

    def __init__(self, subscriptionKey=None):
        self.setSubscriptionKey(subscriptionKey)

    def hasSubscriptionKey(self):
        return self.subscriptionKey is not None and self.subscriptionKey != ''

    def setSubscriptionKey(self, subscriptionKey):
        self.subscriptionKey = subscriptionKey
        self.headers = {
            'Ocp-Apim-Subscription-Key': subscriptionKey,
            'Content-type': 'application/json',
        }

    def translate(self, listOfStrings, toLang, fromLang = None):
        """ Translate strings.

        Arguments:
            listOfStrings {list[string]} -- List of strings to be translated.
            toLang {string} -- Language code for the translated language.

        Keyword Arguments:
            fromLang {string} -- Language code of the original string. (default: {None})

        Returns:
            list[string] -- List of translated strings.
        """

        params = "&ClientTraceId=" + str(uuid.uuid4())
        params = params + f"&to={toLang}"

        if fromLang is not None:
            params = params + f"&from={fromLang}"

        constructed_url = Translator.ENDPOINT + params

        textList = [{"Text": text} for text in listOfStrings]
        jsonData = json.dumps(textList, ensure_ascii=False).encode('utf-8')

        request = requests.post(constructed_url, headers=self.headers, data=jsonData)
        response = request.json()

        result = []
        for res in response:
            translations = res
            result.append(translations['translations'][0]['text'])

        return result
