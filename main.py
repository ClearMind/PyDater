# -*- coding: utf-8 -*-

from PyQt4 import QtGui
import sys
from pydater import PyDater
from datetime import datetime

app = QtGui.QApplication(sys.argv)

updater = PyDater()
updater.show()
updater.log(str(datetime.today()))
updater.setXmlUrl('http://wp.surgpu.ru/media/program/win32.xml')
updater.check()
updater.get_updates()
updater.run_process()

app.exec_()
