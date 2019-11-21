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


class KindleImporter():
    def __init__(self, db_path, target_language, includeUsage=False,
                 doTranslate=True, importDays=5):
        self.translator = Translator(os.environ["YANDEX_API_KEY"])
        self.usages = []
        self.translated = []
        self.db_path = db_path
        self.to_lang = target_language
        self.from_lang=os.environ["TRANSLATE_FROM_LANGUAGE"]
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
                self.usages.append(usages[0] if usages else None)
            else:
                self.usages.append(" ")
            if self.doTranslate:
                try:
                    self.translated.append(
                        self.translator.translate(
                            source=word,
                            to_lang=self.to_lang,
                            from_lang=self.from_lang))
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
            # importer sets number of field by first line, so:
            f.write("word;usage;transcription;translations\n")
            for w, translated, u in zip(self.words, self.translated, self.usages):
                if translated:
                    f.write(self.to_anki_line(w, translated, u))
        return path

    @staticmethod
    def to_anki_line(word: str, t: [], usage: str) -> str:
        usage = usage or t.ex
        usage = usage.replace(";", ",")
        usage = usage.replace(word, f"<b>{word}</b>")
        return f'{word};{usage};{t.ts};{", ".join(t.tr)}\n'

