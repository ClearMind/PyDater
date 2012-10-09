# -*- coding: utf-8 -*-

from PyQt4 import QtGui
import sys
from pydater import PyDater

app = QtGui.QApplication(sys.argv)

updater = PyDater()
updater.show()
updater.setXmlUrl('http://wp.surgpu.ru/media/program/linux.xml')
updater.set_local_prefix('/home/student/bin/wp/')
updater.check()
updater.get_updates()
updater.hide()
updater.run_process()

app.exec_()
