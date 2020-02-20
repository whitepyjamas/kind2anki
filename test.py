import os
import sys
from os.path import dirname, realpath

os.environ["TRANSLATE_FROM_LANGUAGE"] = "en"
with open('yandex-dictionaries-api-key', 'r') as file:
    os.environ["YANDEX_API_KEY"] = file.read()

dir = dirname(realpath(__file__))
sys.path.insert(0, dir)
sys.path.insert(0, os.path.join(dir, "kind2anki"))
sys.path.insert(0, os.path.join(dir, "kind2anki", "libs"))

from libs.textblob.translate import Translator

translator = Translator(os.environ["YANDEX_API_KEY"])
translated = translator.translate('home', 'en', 'ru')

assert str(translated) == "ts: həʊm tr: ['домашний', 'родина', 'домой'] ex: home telephone number"

print("Translation OK 👍")

# {'def': [{'pos': 'adjective',
#           'text': 'home',
#           'tr': [{'ex': [{'text': 'home telephone number',
#                           'tr': [{'text': 'домашний телефон'}]},
#                          {'text': 'home computer network',
#                           'tr': [{'text': 'домашняя компьютерная сеть'}]},
#                          {'text': 'home theater system',
#                           'tr': [{'text': 'домашний кинотеатр'}]},
#                          {'text': 'home appliances',
#                           'tr': [{'text': 'бытовая техника'}]}],
#                   'mean': [{'text': 'household'}],
#                   'pos': 'adjective',
#                   'syn': [{'pos': 'adjective', 'text': 'бытовой'}],
#                   'text': 'домашний'},
#                  {'ex': [{'text': 'minister for home affairs',
#                           'tr': [{'text': 'министр внутренних дел'}]},
#                          {'text': 'home producer',
#                           'tr': [{'text': 'отечественный производитель'}]}],
#                   'mean': [{'text': 'internal'}, {'text': 'domestic'}],
#                   'pos': 'adjective',
#                   'syn': [{'pos': 'adjective', 'text': 'отечественный'}],
#                   'text': 'внутренний'},
#                  {'ex': [{'text': 'home city',
#                           'tr': [{'text': 'родной город'}]}],
#                   'mean': [{'text': 'native'}],
#                   'pos': 'adjective',
#                   'text': 'родной'},
#                  {'ex': [{'text': 'home office',
#                           'tr': [{'text': 'главный офис'}]}],
#                   'mean': [{'text': 'main'}],
#                   'pos': 'adjective',
#                   'text': 'главный'}],
#           'ts': 'həʊm'},
#          {'pos': 'noun',
#           'text': 'home',
#           'tr': [{'ex': [{'text': 'return home',
#                           'tr': [{'text': 'вернуться на родину'}]}],
#                   'gen': 'ж',
#                   'mean': [{'text': 'homeland'}],
#                   'pos': 'noun',
#                   'text': 'родина'},
#                  {'ex': [{'text': 'humble homes',
#                           'tr': [{'text': 'скромные жилища'}]},
#                          {'text': 'permanent home',
#                           'tr': [{'text': 'постоянное жилье'}]}],
#                   'gen': 'ср',
#                   'mean': [{'text': 'house'},
#                            {'text': 'housing'},
#                            {'text': 'residence'}],
#                   'pos': 'noun',
#                   'syn': [{'gen': 'ср', 'pos': 'noun', 'text': 'жилье'},
#                           {'gen': 'ср', 'pos': 'noun', 'text': 'проживание'}],
#                   'text': 'жилище'},
#                  {'ex': [{'text': 'broken home',
#                           'tr': [{'text': 'распавшаяся семья'}]}],
#                   'gen': 'ж',
#                   'mean': [{'text': 'family'}],
#                   'pos': 'noun',
#                   'text': 'семья'},
#                  {'mean': [{'text': 'hearth'}, {'text': 'family home'}],
#                   'pos': 'noun',
#                   'syn': [{'pos': 'noun', 'text': 'родной дом'},
#                           {'pos': 'noun', 'text': 'родной очаг'}],
#                   'text': 'домашний очаг'},
#                  {'gen': 'м',
#                   'mean': [{'text': 'at home'}],
#                   'pos': 'noun',
#                   'text': 'дома'},
#                  {'mean': [{'text': 'home conditions'}],
#                   'pos': 'noun',
#                   'text': 'домашние условия'},
#                  {'gen': 'м',
#                   'mean': [{'text': 'shelter'}],
#                   'pos': 'noun',
#                   'text': 'кров'}],
#           'ts': 'həʊm'},
#          {'pos': 'adverb',
#           'text': 'home',
#           'tr': [{'mean': [{'text': 'homeward'}],
#                   'pos': 'adverb',
#                   'text': 'домой'},
#                  {'pos': 'adverb', 'text': 'на родину'},
#                  {'pos': 'adverb', 'text': 'к себе'}],
#           'ts': 'həʊm'},
#          {'pos': 'verb',
#           'text': 'home',
#           'tr': [{'mean': [{'text': 'return home'}],
#
# 'pos': 'verb',
#                   'text': 'возвращаться домой'}],
#           'ts': 'həʊm'}],
#  'head': {}}