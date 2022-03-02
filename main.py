import sys
import time
import traceback
from multiprocessing import Process

from loger import log

import manage
import run_validator
import run_fetcher
from config import PROCESS_MAX_RUN_TIME

def main():
    processes = [
        Process(target=run_fetcher.main, name='fetcher'),
        Process(target=run_validator.main, name='validator'),
        Process(target=manage.run, name='api'),
    ]

    while True:
        for i, process in enumerate(processes):
            if not process.is_alive() or time.time() - process.start_time > PROCESS_MAX_RUN_TIME:
                log(f'启动{process.name}进程')
                p = Process(target=process._target, name=process.name, daemon=True)
                p.start()
                p.start_time = time.time()
                processes[i] = p
        time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        log('========FATAL ERROR=========', 1)
        traceback.print_exc()
        sys.exit(1)
