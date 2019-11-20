# coding=utf-8
import sqlite3
import sys
import os
import tempfile
import codecs
import datetime
import time

from functools import partial

# idea taken from Syntax Highlighting for Code addon, thanks!
try:
    # Try to find the modules in the global namespace:
    from textblob import TextBlob
    from textblob.translate import Translator
except:
    # If not present, import modules from ./libs folder
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.join(dir_path, "libs"))
    from textblob import TextBlob


def translateWord(word, target_language):
    return TextBlob(word).translate(to=target_language)
    # """
    # translates word using transltr.org free api
    # """
    # url = "http://www.transltr.org/api/translate?text=%s&to=%s"
    # r = urllib2.urlopen(url=url % (word, target_language))
    # r_json = r.read().decode('utf-8')
    # return json.loads(r_json)['translationText']


class KindleImporter():
    def __init__(self, db_path, target_language, includeUsage=False,
                 doTranslate=True, importDays=5):
        self.translator = Translator(os.environ["YANDEX_API_KEY"])
        self.usages = []
        self.translated = []
        self.db_path = db_path
        self.target_language = target_language
        self.includeUsage = includeUsage
        self.doTranslate = doTranslate
        self.timestamp = self.createTimestamp(importDays) * 1000

    def createTimestamp(self, days):
        d = (datetime.date.today() - datetime.timedelta(days=days))
        return int(time.mktime(d.timetuple()))

    def translateWordsFromDB(self):
        self.getWordsFromDB()
        self.translateWords()

    def fetchWordsFromDBWithoutTranslation(self):
        self.getWordsFromDB()
        self.translated = len(self.words) * ['']

    def getWordsFromDB(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT word, id "
                  f"FROM words "
                  f"WHERE lang IS '{os.environ['TRANSLATE_FROM_LANGUAGE']}' "
                  f"AND timestamp > ?",
                  (str(self.timestamp),))
        words_and_ids = c.fetchall()
        self.words = [w[0] for w in words_and_ids]
        self.word_keys = [w[1] for w in words_and_ids]
        conn.close()

    def translateWords(self):
        self.translated = []
        self.usages = []
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for word, word_key in zip(self.words, self.word_keys):
            if self.includeUsage:
                c.execute("SELECT usage FROM LOOKUPS WHERE word_key = ?", [word_key])
                usages = c.fetchone()
                if usages:
                    usage = usages[0]
                    usage = usage.replace(word, f"<b>{word}</b>")
                    usage = usage.replace(";", ",")
                    self.usages.append(usage)
                else:
                    self.usages.append(None)
            else:
                self.usages.append(" ")
            if self.doTranslate:
                try:
                    self.translated.append(
                        self.translator.translate(
                            source=word,
                            to_lang=self.target_language,
                            from_lang=os.environ["TRANSLATE_FROM_LANGUAGE"]))
                except ValueError:
                    self.translated.append(None)
            else:
                self.translated.append(None)
        conn.close()
        return

    def createTemporaryFile(self):
        if len(self.words) == 0:
            return None
        path = os.path.join(tempfile.gettempdir(), "kind2anki_temp.txt")
        with codecs.open(path, "w", encoding="utf-8") as f:
            for w, translated, u in zip(self.words, self.translated, self.usages):
                if translated:
                    ankirow = self.to_anki_line(w, translated, u)
                    f.write(ankirow)
        return path

    @staticmethod
    def to_anki_line(word: str, translated, usage: str) -> str:
        return f'{word};{usage or translated.ex};{translated.ts};{";".join(translated.tr)};\n'
