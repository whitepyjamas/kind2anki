# coding=utf-8
# anki stuff import
from aqt.deckchooser import DeckChooser
from aqt.modelchooser import ModelChooser
from aqt import mw
from aqt.utils import showInfo, getFile, showText
from aqt.qt import *
from anki.importing import TextImporter
from PyQt5.QtCore import QThread, pyqtSignal

from os.path import dirname, realpath, join

# some python libs
import os
import sys
import sqlite3
import urllib
import datetime
import time
import platform
import string
import getpass


def get_yandex_api_key():
    path = join(dirname(realpath(__file__)),
                'yandex-dictionaries-api-key')
    with open(path, 'r') as file:
        return file.read()


os.environ["TRANSLATE_FROM_LANGUAGE"] = "en"
os.environ["YANDEX_API_KEY"] = get_yandex_api_key()

sys.path.insert(0, os.path.join(mw.pm.addonFolder(), "kind2anki"))
sys.path.insert(0, os.path.join(mw.pm.addonFolder(), "kind2anki", "kind2anki"))
sys.path.insert(0, os.path.join(mw.pm.addonFolder(), "kind2anki", "kind2anki", "libs"))

# addon's ui
from .kind2anki import kind2anki_ui

from .kind2anki.kindleimporter import KindleImporter


class ThreadTranslate(QThread):
    startProgress = pyqtSignal(object, object)
    done = pyqtSignal(object, object)

    def __init__(self, args=None):
        QThread.__init__(self)
        self.args = args
        self.dialog = None

    def __del__(self):
        self.wait()

    def run(self):
        self.startProgress.emit(self.dialog, "start")
        kindleImporter = KindleImporter(*self.args)
        kindleImporter.translateWordsFromDB()
        temp_file_path = kindleImporter.createTemporaryFile()
        self.done.emit(self.dialog, temp_file_path)

# moved from class beacause it cannot work as a slot :(
def importToAnki(dialog, temp_file_path):
    mw.progress.finish()
    if temp_file_path is not None:
        mw.progress.start(immediate=True, label="Importing...")
        dialog.selectDeck()
        dialog.setupImporter(temp_file_path)
        dialog.importer.run()
        mw.progress.finish()

        txt = _("Importing complete.") + "\n"
        if dialog.importer.log:
            txt += "\n".join(dialog.importer.log)

        os.remove(temp_file_path)
    else:
        txt = "Nothing to import!"
    showText(txt)


def startProgressBar(dialog, nth):
    mw.progress.start(immediate=True, label="Processing...")


class Kind2AnkiDialog(QDialog):
    def __init__(self):
        global mw
        QDialog.__init__(self, mw, Qt.Window)
        self.mw = mw
        self.frm = kind2anki_ui.Ui_kind2ankiDialog()
        self.frm.setupUi(self)

        self.t = ThreadTranslate()
        self.t.done.connect(importToAnki)
        self.t.startProgress.connect(startProgressBar)

        b = QPushButton(_("Import"))
        self.frm.button_box_standard_buttons.addButton(b, QDialogButtonBox.AcceptRole)
        self.model_chooser = ModelChooser(
            self.mw, self.frm.model_area, label=False)
        self.deck = DeckChooser(
            self.mw, self.frm.deck_area, label=False)
        self.frm.import_mode.setCurrentIndex(
                    self.mw.pm.profile.get('importMode', 1))

        self.daysSinceLastRun = self.getDaysSinceLastRun()
        self.frm.import_days.setValue(self.daysSinceLastRun)
        self.rejected.connect(self.cleanup)

        self.exec_()

    def accept(self):
        try:
            db_path = getDBPath()
            self.writeCurrentTimestampToFile()  # update lastRun timestamp

            target_language = self.frm.language_select.currentText()
            includeUsage = self.frm.include_usage.isChecked()
            doTranslate = self.frm.do_translate.isChecked()
            importDays = self.frm.import_days.value()

            #if doTranslate:
            #    showInfo("Translating words from database, it can take a while...")
            #else:
            #    showInfo("Fetching words from database, it can take a while...")

            self.t.dialog = self
            self.t.args = (
                db_path, target_language, includeUsage, doTranslate, importDays
                )

            self.t.start()

        except urllib.error.URLError:
            showInfo("Cannot connect")
        except IOError:
            showInfo("DB file not selected, exiting")
        except sqlite3.DatabaseError:
            showInfo("Selected file is not a DB")
        finally:
            self.close()
            self.cleanup()
            self.mw.reset()

    def setupImporter(self, temp_file_path):
        self.importer = TextImporter(self.mw.col, str(temp_file_path))
        self.importer.initMapping()
        self.importer.allowHTML = True
        self.importer.importMode = self.frm.import_mode.currentIndex()
        self.mw.pm.profile['importMode'] = self.importer.importMode
        self.importer.delimiter = ';'

    def selectDeck(self):
        deckid = self.deck.selectedId()
        models = self.mw.col.models
        models.current()['did'] = deckid
        models.save(models.current())
        self.mw.col.decks.select(deckid)

    def getDaysSinceLastRun(self):
        path = self.getLastRunFilePath()
        if os.path.isfile(path):
            with open(path, "r") as f:
                timestamp = int(f.read())
            days = self.getDaysSinceTimestamp(timestamp) + 1 # round up
        else:
            days = 10

        return days

    def getDaysSinceTimestamp(self, timestamp):
        now = datetime.datetime.now()
        previous = datetime.datetime.fromtimestamp(timestamp)
        return (now - previous).days

    def writeCurrentTimestampToFile(self):
        path = self.getLastRunFilePath()
        now = datetime.datetime.now()
        with open(path, "w") as f:
            f.write(str(int(time.mktime(now.timetuple()))))

    def getLastRunFilePath(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, "lastRun.txt")

    def cleanup(self):
        self.model_chooser.cleanup()


def getDBPath():
    global mw
    db_path = getKindleVocabPath() or getFile(
        mw, _("Select db file"), None, dir=None, key="Import", filter="*.db"
    )
    if not db_path:
        raise IOError
    db_path = str(db_path)
    return db_path


def getKindleVocabPath():
    try:
        sysm = platform.system()
        path = None
        if sysm == "Windows":
            for l in string.ascii_uppercase:
                path = r"{}:\system\vocabulary\vocab.db".format(l)
                if os.path.exists(path):
                    break
        elif sysm == "Darwin":
            path = "/Volumes/Kindle/system/vocabulary/vocab.db"
        elif sysm == "Linux":
            user = getpass.getuser()
            path = r"/media/{}/Kindle/system/vocabulary/vocab.db".format(user)
        if os.path.exists(path):
            return path
        return None
    except:
        return None

action = QAction("kind2anki", mw)
action.triggered.connect(Kind2AnkiDialog)
mw.form.menuTools.addAction(action)
