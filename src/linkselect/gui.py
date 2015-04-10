#
# Copyright (C) 2015  Michal Belica <devel@beli.sk>
#
# This file is part of LinkSelect.
#
# LinkSelect is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinkSelect is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinkSelect.  If not, see <http://www.gnu.org/licenses/>.
#
import sys
import time
import shlex
import argparse
import subprocess
import configparser

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QAction, QIcon

from .defs import *
from .core import LinkSelect


class LinkSelectWidget(QtGui.QMainWindow):
    def __init__(self, linkselect, app_title, app_description, app_icon=None, changehook=None):
        self.app_title = app_title
        self.app_description = app_description
        self.linkselect = linkselect
        self.app_icon = app_icon
        self.last_status = 0
        self.changehook = changehook
        super().__init__()
        self.initUI()

    def initUI(self):
        self.window = QtGui.QWidget()
        self.setCentralWidget(self.window)
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        label = QtGui.QLabel(self.app_description)

        # buttons
        applyBtn = QtGui.QPushButton('&Apply')
        applyBtn.setToolTip('Apply settings.')
        applyBtn.setDefault(True)
        applyBtn.clicked.connect(self.apply)
    
        reloadBtn = QtGui.QPushButton('&Reload')
        reloadBtn.setToolTip('Reload current status and choices.')
        reloadBtn.clicked.connect(self.reload)

        closeBtn = QtGui.QPushButton('&Close')
        closeBtn.setToolTip('Close application without applying settings.')
        closeBtn.clicked.connect(self.close)

        # selector
        self.selector = QtGui.QComboBox()
        self.reload()

        # layout
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(applyBtn)
        hbox.addWidget(reloadBtn)
        hbox.addWidget(closeBtn)

        vbox = QtGui.QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addSpacing(10)
        vbox.addStretch(1)
        vbox.addWidget(label)
        vbox.addWidget(self.selector)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.window.setLayout(vbox)

        self.statusBar()

        # actions
        exitAction = QAction(QIcon.fromTheme('application-exit'), 'E&xit', self.window)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        self.window.addAction(exitAction)

        # menu bar
        #menubar = self.menuBar()
        #fileMenu = menubar.addMenu('&File')
        #fileMenu.addAction(exitAction)

        self.setWindowTitle(self.app_title)
        if self.app_icon:
            self.setWindowIcon(QIcon(self.app_icon))

        self.show()

    def status(self, msg):
        if self.last_status > int(time.time())-2:
            # there are recent messages
            message = msg + ' || ' + self.statusBar().currentMessage()
        else:
            message = msg
        self.statusBar().showMessage(message)
        self.statusBar().setToolTip(message)
        self.last_status = int(time.time())

    def reload(self):
        self.linkselect.refresh()
        self.selector.clear()
        current_index, current_value = self.linkselect.get_current_choice()
        for i, v in enumerate(self.linkselect.get_choices()):
            d, p = v
            self.selector.addItem(d)
            if current_index == i:
                self.selector.setCurrentIndex(i)
        self.status('Reloaded.')
        if current_index is None:
            self.status('Current value: {}'.format(current_value))

    def apply(self):
        p = self.linkselect.get_choices()[self.selector.currentIndex()][1]
        try:
            self.linkselect.set_link(p)
        except:
            self._show_error()
        else:
            self.status('Applied configuration.')
            if self.changehook:
                try:
                    subprocess.check_call(self.changehook, shell=True)
                except:
                    self._show_error()
                else:
                    self.status('Change hook success.')
        self.reload()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _show_error(self):
        e_type, e_value, e_tb = sys.exc_info()
        message = '{}: {}'.format(e_type.__name__, e_value)
        self.status(message)


def main():
    parser = argparse.ArgumentParser(description=app_name_desc)
    parser.add_argument('-c', '--config', required=True, help='Configuration file')
    args, unknown = parser.parse_known_args()

    conf = configparser.ConfigParser(defaults={
        'title': 'Link select',
        'description': '',
        'icon': None,
        'desc_from_content': False,
        'desc_parse_lines': 1,
        'desc_regexp': None,
        'changehook': None,
        })
    with open(args.config, 'r') as f:
        conf.read_file(f)

    conf = conf['linkselect']

    unknown.insert(0, sys.argv[0])
    app = QtGui.QApplication(unknown)
    pcw = LinkSelectWidget(
            LinkSelect(conf['link'], conf['pattern'], conf['base'], refresh=False,
                desc_from_content=conf.getboolean('desc_from_content'),
                desc_parse_lines=conf.getint('desc_parse_lines'),
                desc_regexp=conf['desc_regexp'],
                ),
            conf['title'], conf['description'], conf['icon'],
            changehook=conf['changehook'],
            )
    sys.exit(app.exec_())

