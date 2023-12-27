import logging
import sys
from argparse import ArgumentParser
from argparse import Namespace
from logging import Formatter
from threading import Condition
from typing import Optional

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QMenu
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from pkg_updater.handlers import PyQtHandler
from pkg_updater.logger import root
from pkg_updater.updater import UpdaterThread


class MainWindow(QMainWindow):
    def __init__(self, instance: QCoreApplication, args: Namespace):
        super().__init__()

        # window configuration
        self.icon = QIcon("favicon.svg")
        self.setWindowTitle("Package Updater")
        self.setWindowIcon(self.icon)

        # tray actions
        minimize_action = QAction("Minimize", self)
        minimize_action.triggered.connect(self.hide)
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.showNormal)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(instance.quit)

        # tray menu
        tray_menu = QMenu()
        tray_menu.addAction(minimize_action)
        tray_menu.addAction(restore_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        # tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.icon)
        self.tray_icon.setVisible(True)
        self.tray_icon.show()
        self.tray_icon.setToolTip("Package Updater")
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)

        # widgets
        self.update_cv = Condition()
        self.check_for_updates = QPushButton("Check for updates")
        self.check_for_updates.clicked.connect(self.on_update)
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Lucida Console", 9))

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.check_for_updates)
        layout.addWidget(self.console)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # logger configuration
        formatter = Formatter("%(asctime)s %(message)s", "%H:%M:%S")
        handler = PyQtHandler()
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        handler.log.connect(self.console.appendHtml)
        root.addHandler(handler)

        # threads
        self.updater = UpdaterThread(args, self.update_cv)
        self.updater.start()

    def on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    def on_update(self):
        with self.update_cv:
            self.update_cv.notify_all()

    def closeEvent(self, a0: Optional[QCloseEvent]):
        if a0:
            a0.ignore()
        self.hide()


def main():
    parser = ArgumentParser()
    parser.add_argument("package_name")
    parser.add_argument("--extra-index-url", default="")
    parser.add_argument("--interval", default=900, type=int)
    parser.add_argument("--delay-first", default=900, type=int)
    parser.add_argument("--restart", action="store_true")
    parser.add_argument("--process-name", default="")
    parser.add_argument("--process-cmdline", default="")
    args = parser.parse_args()
    app = QApplication([])
    window = MainWindow(app, args)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
