import sys
import time
import traceback
from argparse import ArgumentParser
from msvcrt import getch
from msvcrt import kbhit
from subprocess import DEVNULL
from subprocess import PIPE
from subprocess import Popen
from subprocess import check_output

import psutil


def sleep(timeout: int):
    """
    Sleep for a given amount of time,
    Can be canceled at any time
    """
    start = time.time()
    while True:
        elapsed = int(time.time() - start)
        remaining = timeout - elapsed
        sys.stdout.write(
            f"\rNext update in {remaining}s, press enter to continue..."
        )
        sys.stdout.flush()
        if remaining <= 0:
            break
        if kbhit():
            if getch() == b"\r":
                break
        time.sleep(0.1)
    print()


def get_running_processes(text: str):
    proc_iter = psutil.process_iter()
    processes: list[psutil.Process] = []
    for i in proc_iter:
        try:
            for cmd in i.cmdline():
                if "--restart" in cmd:
                    # filter self
                    break
                if text in cmd:
                    processes.append(i)
        except psutil.Error:
            pass
    return processes


def get_is_up_to_date(pkg_name: str, extra_index_url: str = ""):
    cmd = ["pip", "install", "--upgrade", pkg_name]
    if extra_index_url:
        cmd += ["--extra-index-url", extra_index_url]
    cmd += ["--dry-run"]
    print("Checking for updates...")
    stdout = check_output(cmd, stderr=PIPE).decode()
    return "Would install" not in stdout


def install_updates(pkg_name: str, extra_index_url: str = ""):
    cmd = ["pip", "install", "--upgrade", pkg_name]
    if extra_index_url:
        cmd += ["--extra-index-url", extra_index_url]

    print("Installing updates...")
    with Popen(cmd, stdout=PIPE, stderr=PIPE, text=True) as p:
        if p.stdout:
            for line in p.stdout:
                print(line.strip())
        if p.stderr:
            for line in p.stderr:
                print(line.strip())


def main():
    parser = ArgumentParser()
    parser.add_argument("package_name")
    parser.add_argument("--extra-index-url")
    parser.add_argument("--interval", default=900, type=int)
    parser.add_argument("--delay-first", default=900, type=int)
    parser.add_argument("--restart")
    args = parser.parse_args()
    sleep(args.delay_first)
    while True:
        try:
            if get_is_up_to_date(args.package_name, args.extra_index_url):
                print("Already up to date.")
            else:
                if args.restart:
                    print("Gracefully shutting down running processes...")
                    processes = get_running_processes(args.restart)
                    data = [(i.cmdline(), i.cwd()) for i in processes]
                    for i in processes:
                        i.terminate()
                else:
                    data = []
                install_updates(args.package_name, args.extra_index_url)
                if args.restart:
                    print("Restarting closed processes...")
                    for cmd, cwd in data:
                        Popen(
                            cmd,
                            cwd=cwd,
                            stderr=DEVNULL,
                            stdout=DEVNULL,
                            start_new_session=True,
                        )
                print("Complete.")
        except Exception:
            traceback.print_exc()
        sleep(args.interval)


if __name__ == "__main__":
    main()