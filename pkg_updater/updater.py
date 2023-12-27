from argparse import Namespace
from subprocess import DEVNULL
from subprocess import PIPE
from subprocess import Popen
from subprocess import check_output
from threading import Condition

import psutil
from PyQt6.QtCore import QThread

from pkg_updater import logger


def get_running_processes(name: str, cmdline: str):
    proc_iter = psutil.process_iter()
    processes: list[psutil.Process] = []
    for i in proc_iter:
        try:
            i_cmdline = " ".join(i.cmdline())
            if "--restart" in i_cmdline:
                # filter self
                continue
            if name in i.name() and cmdline in i_cmdline:
                processes.append(i)
        except psutil.Error:
            pass
    return processes


def get_is_up_to_date(pkg_name: str, extra_index_url: str = ""):
    cmd = ["pip", "install", "--upgrade", pkg_name]
    if extra_index_url:
        cmd += ["--extra-index-url", extra_index_url]
    cmd += ["--dry-run"]
    logger.info("Checking for updates...")
    stdout = check_output(cmd, stderr=PIPE).decode()
    return "Would install" not in stdout


def install_updates(pkg_name: str, extra_index_url: str = ""):
    cmd = ["pip", "install", "--upgrade", pkg_name]
    if extra_index_url:
        cmd += ["--extra-index-url", extra_index_url]

    logger.info("Installing updates...")
    with Popen(cmd, stdout=PIPE, stderr=PIPE, text=True) as p:
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
                    if self.args.restart and self.args.process_name:
                        logger.info(
                            "Gracefully shutting down running processes..."
                        )
                        processes = get_running_processes(
                            self.args.process_name, self.args.process_cmdline
                        )
                        closed_processes = [
                            (i.cmdline(), i.cwd()) for i in processes
                        ]
                        for i in processes:
                            logger.info(f"Closing process: {i.name()}")
                            i.terminate()
                    else:
                        closed_processes = []
                    install_updates(
                        self.args.package_name, self.args.extra_index_url
                    )
                    if self.args.restart and self.args.process_name:
                        logger.info("Restarting closed processes...")
                        for cmd, cwd in closed_processes:
                            Popen(
                                cmd,
                                cwd=cwd,
                                stderr=DEVNULL,
                                stdout=DEVNULL,
                                start_new_session=True,
                            )
                    logger.info("Complete.")
            except Exception:
                logger.exception("Unhandled exception occurred.")
            logger.info(f"Next update in {self.args.interval}s...")
            with self.update_condition:
                self.update_condition.wait(self.args.interval)
