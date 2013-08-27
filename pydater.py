# -*- coding: utf-8 -*-
import os, sys
from hashlib import md5
import re
import stat
import subprocess
from PyQt4 import QtGui
from PyQt4 import QtCore
from lxml import  etree
import urllib2

class PyDater(QtGui.QWidget, object):
    def __init__(self):
        super(PyDater, self).__init__()

        self.updates = [] # list of urls for downloading
        self.xml_url = None # full url of xml file with hashes
        self.local_dir_prefix = QtCore.QDir().homePath()
        self.log_file = None
        self.run = None

        # widget layout
        self.layout = QtGui.QVBoxLayout()
        self.pbar = QtGui.QProgressBar()
        self.layout.addWidget(self.pbar)
        self.log_ = QtGui.QTextEdit()
        self.log_.setReadOnly(True)
        self.layout.addWidget(self.log_)

        self.setLayout(self.layout)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)

    def log(self, strg):
        self.log_.setText(self.log_.toPlainText() + strg)
        print strg
        if not self.log_file:
            up = os.path.join(str(self.local_dir_prefix), '.updater/')
            if not os.path.isdir(up):
                os.makedirs(up)
            try:
                self.log_file = open(os.path.join(up, 'updater.log'), 'w')
            except IOError:
                print "Can't open file %s" % os.path.join(up, 'updater.log')
        else:
            self.log_file.write(strg + "\n")

    def setXmlUrl(self, url):
        self.xml_url = url

    def getXmlUrl(self):
        return self.xml_url

    def set_local_prefix(self, prefix):
        self.local_dir_prefix = prefix

    def check(self):
        self.log("Checking for updates...\n")
        self.updates = []
        try:
            xml_file = urllib2.urlopen(self.xml_url, timeout=5)

            xml = xml_file.read()
            root = etree.fromstring(xml)
            self.run = root.attrib['run']

            for f in root:
                name_ = f.attrib['name'][1:] if f.attrib['name'][0] == '/' else f.attrib['name']
                fn = os.path.join(str(self.local_dir_prefix), name_)
                if os.path.exists(fn):
                    file = open(fn, 'rb')
                    hash = md5(file.read()).hexdigest()
                    self.log("Check " + name_ + '...\n')
                    if hash != f.attrib['hash']:
                        self.updates.append(name_)
                    file.close()
                else:
                    self.updates.append(name_)
            return self.updates

        except urllib2.HTTPError, e:
            print "Http Error: ", e.code
        except urllib2.URLError, e:
            print "URL Error: ", e.reason
        except etree.XMLSchemaParseError, e:
            print "XML Parse error %s", e.message

    def get_updates(self):
        if not self.updates:
            self.check()
        count = len(self.updates)
        if count == 0:
            self.log.setText(self.log.toPlainText() + "No new updates available!\n")
            return True
        chunk = 100.0 / count if count else 100.0
        self.pbar.setValue(0)
        # http://wp.surgpu.ru/media/program/linux.xml
        remote_path = ''
        m = re.search(r'((ht|f)tp://.*/)(\S+\.xml)', self.xml_url)
        if m:
            remote_path = m.group(1)

        i = 0
        for f in self.updates:
            try:
                self.log(f + '\n')
                content = urllib2.urlopen(remote_path + f)
                dir = os.path.dirname(os.path.join(str(self.local_dir_prefix), f[1:] if f[0] in '/\\' else f))
                if not os.path.exists(dir):
                    os.makedirs(dir)
                file = open(os.path.join(str(self.local_dir_prefix), f[1:] if f[0] in '/\\' else f), 'wb')
                file.write(content.read())
                file.close()
                i += 1
                self.pbar.setValue(i * chunk)

            except urllib2.HTTPError, e:
                print e.message
                break
            except IOError, e:
                print e.message
                break


    def run_process(self):
        if not self.run:
            return None
        file = os.path.join(str(self.local_dir_prefix), self.run[1:] if self.run[0] in '/\\' else self.run)
        os.chmod(file, stat.S_IRWXU | stat.S_IRWXG)
        ret = 1
        try:
            self.log('Trying to run process %s' % file)
            self.log_file.close()
            self.hide()
            ret = subprocess.check_call(file)
        except subprocess.CalledProcessError, e:
            print e.message
        finally:
            self.close()
            QtGui.QApplication.exit(ret)
            sys.exit(ret)
