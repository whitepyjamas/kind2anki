# -*- coding: utf-8 -*-
"""
Translator module that uses the Google Translate API.

Adapted from Terry Yin's google-translate-python.
Language detection added by Steven Loria.
"""
from __future__ import absolute_import

import ctypes
import json

from google.cloud import translate_v2 as translate
from textblob.compat import PY2, request, urlencode
from textblob.exceptions import TranslatorError, NotTranslated

class Translator(object):
    def __init__(self):
        self._client = translate.Client()

    def translate(self, source, from_lang='auto', to_lang='en'):
        result = self._client.translate(values=source, target_language=to_lang, source_language=from_lang)
        self._validate_translation(source, result)
        return result

    def detect(self, source, host=None, type_=None):
        """Detect the source text's language."""
        if PY2:
            source = source.encode('utf-8')
        if len(source) < 3:
            raise TranslatorError('Must provide a string with at least 3 characters.')
        data = {"q": source}
        url = u'{url}&sl=auto&tk={tk}'.format(url=self.url, tk=_calculate_tk(source))
        response = self._request(url, host=host, type_=type_, data=data)
        result, language = json.loads(response)
        return language

    def _validate_translation(self, source, result):
        """Validate API returned expected schema, and that the translated text
        is different than the original string.
        """
        if not result:
            raise NotTranslated('Translation API returned and empty response.')
        if PY2:
            result = result.encode('utf-8')
        if result.strip() == source.strip():
            raise NotTranslated('Translation API returned the input string unchanged.')

    def _request(self, url, host=None, type_=None, data=None):
        encoded_data = urlencode(data).encode('utf-8')
        req = request.Request(url=url, headers=self.headers, data=encoded_data)
        if host or type_:
            req.set_proxy(host=host, type=type_)
        resp = request.urlopen(req)
        content = resp.read()
        return content.decode('utf-8')

def _calculate_tk(source):
    """Reverse engineered cross-site request protection."""
    # Source: https://github.com/soimort/translate-shell/issues/94#issuecomment-165433715
    # Source: http://www.liuxiatool.com/t.php

    tkk = [406398, 561666268 + 1526272306]
    b = tkk[0]

    if PY2:
        d = map(ord, source)
    else:
        d = source.encode('utf-8')

    def RL(a, b):
        for c in range(0, len(b) - 2, 3):
            d = b[c + 2]
            d = ord(d) - 87 if d >= 'a' else int(d)
            xa = ctypes.c_uint32(a).value
            d = xa >> d if b[c + 1] == '+' else xa << d
            a = a + d & 4294967295 if b[c] == '+' else a ^ d
        return ctypes.c_int32(a).value

    a = b

    for di in d:
        a = RL(a + di, "+-a^+6")

    a = RL(a, "+-3^+b+-f")
    a ^= tkk[1]
    a = a if a >= 0 else ((a & 2147483647) + 2147483648)
    a %= pow(10, 6)

    tk = '{0:d}.{1:d}'.format(a, a ^ b)
    return tk
