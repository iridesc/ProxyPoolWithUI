import sys
import time
import traceback
from multiprocessing import Process

from loger import log

import manage
import run_validator
import run_fetcher
from config import PROCESS_MAX_RUN_TIME


class TProcess(Process):
    def __init__(self, target, name):
        self.target = target
        self.start_time = 0
        super().__init__(target=target, name=name)

    def start(self):
        super().start()
        self.start_time = time.time()


def main():
    processes = [
        TProcess(target=manage.run, name='api'),
        TProcess(target=run_fetcher.main, name='fetcher'),
        TProcess(target=run_validator.main, name='validator'),
    ]

    while True:
        for i, process in enumerate(processes):

            if process.is_alive() and time.time() - process.start_time > PROCESS_MAX_RUN_TIME:
                log(f'进程 {process.name} 运行超时')
                process.terminate()
                process.join()

            if not process.is_alive():
                log(f'启动{process.name}进程')
                p = TProcess(target=process.target, name=process.name)
                p.start()
                processes[i] = p
        time.sleep(3)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        log('========FATAL ERROR=========', 1)
        traceback.print_exc()
        sys.exit(1)
