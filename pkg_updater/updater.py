import subprocess
from argparse import Namespace
from subprocess import PIPE
from subprocess import Popen
from subprocess import check_output
from threading import Condition

from PyQt6.QtCore import QThread

from pkg_updater import logger

# hide flashing console when using pythonw
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE


def get_is_up_to_date(pkg_name: str, extra_index_url: str = ""):
    cmd = ["pip", "install", "--upgrade", pkg_name]
    if extra_index_url:
        cmd += ["--extra-index-url", extra_index_url]
    cmd += ["--dry-run"]
    logger.info("Checking for updates...")
    stdout = check_output(cmd, stderr=PIPE, startupinfo=startupinfo).decode()
    return "Would install" not in stdout


def install_updates(pkg_name: str, extra_index_url: str = ""):
    cmd = ["pip", "install", "--upgrade", pkg_name]
    if extra_index_url:
        cmd += ["--extra-index-url", extra_index_url]

    logger.info("Installing updates...")
    with Popen(
        cmd, stdout=PIPE, stderr=PIPE, text=True, startupinfo=startupinfo
    ) as p:
        if p.stdout:
            for line in p.stdout:
                line = line.strip()
                if line:
                    logger.info(line)
        if p.stderr:
            for line in p.stderr:
                line = line.strip()
                if line and "[notice]" not in line:
                    logger.info(line)


class UpdaterThread(QThread):
    def __init__(self, args: Namespace, update_condition: Condition):
        super().__init__()
        self.update_condition = update_condition
        self.args = args

    def run(self):
        logger.info(f"Next update in {self.args.delay_first}s...")
        with self.update_condition:
            self.update_condition.wait(self.args.delay_first)
        while True:
            try:
                if get_is_up_to_date(
                    self.args.package_name, self.args.extra_index_url
                ):
                    logger.info("Already up to date.")
                else:
                    install_updates(
                        self.args.package_name, self.args.extra_index_url
                    )
                    logger.info("Complete.")
            except Exception:
                logger.exception("Unhandled exception occurred.")
            logger.info(f"Next update in {self.args.interval}s...")
            with self.update_condition:
                self.update_condition.wait(self.args.interval)
