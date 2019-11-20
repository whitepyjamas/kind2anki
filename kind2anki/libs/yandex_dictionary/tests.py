#!/usr/bin/python
# coding: utf-8
import unittest
from yandex_dictionary import YandexDictionary, YandexDictionaryException


class YandexDictionaryTest(unittest.TestCase):

    def setUp(self):
        self.translate = YandexDictionary("trnsl.1.1.20130421T140201Z.323e508a"
                                          "33e9d84b.f1e0d9ca9bcd0a00b0ef71d82e6cf4158183d09e")

    def test_directions(self):
        directions = self.translate.directions
        self.assertGreater(len(directions), 1)

    def test_langs(self):
        languages = self.translate.langs
        self.assertEqual(languages, set(
            [
                u"el", u"en", u"ca", u"it",
                u"hy", u"cs", u"et", u"az",
                u"es", u"ru", u"nl", u"pt",
                u"no", u"tr", u"lv", u"lt",
                u"ro", u"pl", u"be", u"fr",
                u"bg", u"hr", u"de", u"da",
                u"fi", u"hu", u"sr", u"sq",
                u"sv", u"mk", u"sk", u"uk",
                u"sl"
            ]
        ))

    def test_blocked_key(self):
        translate = YandexDictionary("trnsl.1.1.20130723T112255Z.cfcd2b1ebae9f"
                                     "ff1.86f3d1de3621e69b8c432fcdd6803bb87ef0e963")
        with self.assertRaises(YandexDictionaryException, msg="ERR_KEY_BLOCKED"):
            languages = translate.detect("Hello!")

    def test_lookup(self):
        result = self.translate.lookup(u"Hello", "ru")
        self.assertEqual(result, u'{"head":{},"def":[{"text":"hello","pos":"noun","ts":"ˈheˈləʊ","tr":[{"text":"привет","pos":"существительное","syn":[{"text":"приветствие","pos":"существительное","gen":"ср"}],"mean":[{"text":"hi"},{"text":"greeting"}]}]},{"text":"hello","pos":"verb","ts":"ˈheˈləʊ","tr":[{"text":"поздороваться","pos":"глагол","asp":"сов","syn":[{"text":"здороваться","pos":"глагол","asp":"несов"}],"mean":[{"text":"salute"}]}]}]}')


    # Yandex.Translate tries to translate this as chineese-to-russian
    def test_translate_error(self):
        with self.assertRaises(YandexDictionaryException,
                               msg="ERR_LANG_NOT_SUPPORTED"):
            self.translate.lookup("なのです", "zh", "ru")

    def test_without_key(self):
        with self.assertRaises(YandexDictionaryException,
                               msg="Please, provide key for "
                                   "Yandex.Translate API: "
                                   "https://translate.yandex.ru/apikeys"):
            translate = YandexDictionary()

    def test_error_long_text(self):
        with self.assertRaises(YandexDictionaryException, msg="ERR_TEXT_TOO_LONG"):
            self.translate.lookup("hi! " * 4098, "en", "ru")

    def test_invalid_key(self):
        with self.assertRaises(YandexDictionaryException, msg="ERR_KEY_INVALID"):
            translate = YandexDictionary("my-invalid-key")
            languages = translate.langs()

if __name__ == "__main__":
    unittest.main()
