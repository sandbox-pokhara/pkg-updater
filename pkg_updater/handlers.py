import logging
from logging import Handler
from logging import LogRecord

from PyQt6.QtCore import QObject
from PyQt6.QtCore import pyqtSignal

COLORS = {
    logging.DEBUG: "#0071A6",
    logging.INFO: "#0071A6",
    logging.WARNING: " #6B6D00",
    logging.ERROR: "#D43131",
    logging.CRITICAL: "#D43131",
}


class PyQtHandler(Handler, QObject):
    log = pyqtSignal(str)

    def __init__(self):
        Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record: LogRecord):
        msg = self.format(record)
        color = COLORS[record.levelno]
        msg = msg.replace("\n", "<br/>")
        self.log.emit(f"<span style='color: {color};'>{msg}</span>")
