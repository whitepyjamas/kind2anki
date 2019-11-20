# coding: utf-8

import requests
import requests.exceptions


class YandexDictionaryException(Exception):

    """
    Default YandexDictionary exception
    """
    error_codes = {
        401: "ERR_KEY_INVALID",
        402: "ERR_KEY_BLOCKED",
        403: "ERR_DAILY_REQ_LIMIT_EXCEEDED",
        404: "ERR_DAILY_CHAR_LIMIT_EXCEEDED",
        413: "ERR_TEXT_TOO_LONG",
        422: "ERR_UNPROCESSABLE_TEXT",
        501: "ERR_LANG_NOT_SUPPORTED",
        503: "ERR_SERVICE_NOT_AVAIBLE",
    }

    def __init__(self, status_code, *args, **kwargs):
        message = self.error_codes.get(status_code)
        super(YandexDictionaryException, self).__init__(
            message, *args, **kwargs)


class YandexDictionary(object):

    api_url = "https://dictionary.yandex.net/api/{version}/{service}/{endpoint}"
    api_version = "v1"
    api_endpoints = {
        "langs": "getLangs",
        "lookup": "lookup",
    }
    api_services = {
        'xml': 'dicservice',
        'json': 'dicservice.json'
    }

    def __init__(self, key=None, format='json'):
        """di
        >>> dic = YandexDictionary('<key_id>')
        >>> dic.api_endpoints.__len__()
        2

        """
        if not key:
            raise YandexDictionaryException(401)
        self.api_key = key
        self.api_format = format

    def url(self, endpoint):
        """
        Returns full URL for specified API endpoint
        >>> dic.url('langs')
        'https://dictionary.yandex.net/api/v1/dicservice.json/getLangs'
        >>> dic.url('lookup')
        'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'

        """
        return self.api_url.format(version=self.api_version,
                                   endpoint=self.api_endpoints[endpoint],
                                   service=self.api_services[self.api_format])

    @property
    def directions(self):
        """
        >>> json.loads(dic.directions).__len__()
        86

        """
        try:
            response = requests.get(
                self.url("langs"), params={"key": self.api_key})
        except requests.exceptions.ConnectionError:
            raise YandexDictionaryException(self.error_codes[503])

        status_code = response.status_code
        if status_code != 200:
            raise YandexDictionaryException(status_code)
        return response.text

    @property
    def langs(self):
        """
        >>> dic.langs
        {'tr', 'no', 'uk', 'el', 'be', 'da', 'pt', 'sv', 'ru', 'es', 'lt', 'nl', 'en', 'sk', 'pl', 'cs', 'bg', 'fr', 'tt', 'lv', 'fi', 'de', 'et', 'it'}

        """
        if self.api_format == 'json':
            import json
            return set(x.split("-")[0] for x in json.loads(self.directions))
        else:
            from lxml import etree
            return set(x.text.split("-")[0] for x in etree.fromstring(self.directions.encode('utf-8')))

    def lookup(self, text, from_lang, to_lang):
        """
        JSON FORMAT
        >>> dic.lookup('hello','en', 'ru')
        '{"head":{},"def":[{"text":"hello","pos":"noun","ts":"ˈheˈləʊ","tr":[{"text":"привет","pos":"существительное","syn":[{"text":"приветствие","pos":"существительное","gen":"ср"}],"mean":[{"text":"hi"},{"text":"greeting"}]}]},{"text":"hello","pos":"verb","ts":"ˈheˈləʊ","tr":[{"text":"поздороваться","pos":"глагол","asp":"сов","syn":[{"text":"здороваться","pos":"глагол","asp":"несов"}],"mean":[{"text":"salute"}]}]}]}'

        XML FORMAT
        >>> dic.lookup('hello','en', 'ru')
        '<?xml version="1.0" encoding="utf-8"?>\n<DicResult><head/><def pos="noun" ts="ˈheˈləʊ"><text>hello</text><tr pos="существительное"><text>привет</text><syn pos="существительное" gen="ср"><text>приветствие</text></syn><mean><text>hi</text></mean><mean><text>greeting</text></mean></tr></def><def pos="verb" ts="ˈheˈləʊ"><text>hello</text><tr pos="глагол" asp="сов"><text>поздороваться</text><syn pos="глагол" asp="несов"><text>здороваться</text></syn><mean><text>salute</text></mean></tr></def></DicResult>'


        """
        data = {
            "text": text,
            "lang": '%s-%s' % (from_lang, to_lang),
            "key": self.api_key
        }
        try:
            response = requests.post(self.url("lookup"), data=data)
        except ConnectionError:
            raise YandexDictionaryException(503)
        status_code = response.status_code
        if status_code != 200:
            raise YandexDictionaryException(status_code)
        return response.text

if __name__ == "__main__":
    import doctest
    doctest.testmod()
