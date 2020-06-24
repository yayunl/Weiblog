import json
import requests
from flask_babel import _
from flask import current_app

# // Pass secret key using headers
# curl -X POST "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=es" \
#      -H "Ocp-Apim-Subscription-Key:<your-key>" \
#      -H "Content-Type: application/json" \
#      -d "[{'Text':'Hello, what is your name?'}]"


def translate(text, language):
    if 'MS_TRANSLATION_KEY' not in current_app.config or \
            not current_app.config['MS_TRANSLATION_KEY']:
        return _('Error: the translation service is not configured.')

    headers = {'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATION_KEY'],
               'Content-Type': 'application/json',
               'Ocp-Apim-Subscription-Region': 'australiaeast'}

    data = json.dumps([{'Text': text}])
    r = requests.post('https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={lang}'.format(
                        lang=language), headers=headers, data=data)
    if r.status_code != 200:
        return _('Error: the translation service failed.')
    return json.loads(r.content.decode('utf-8-sig'))[0].get('translations')[0].get('text')


# if __name__ == '__main__':
#     translate('你好', 'en')