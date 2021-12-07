import run_validator
import run_fetcher
import manage
from multiprocessing import Process
import time
import sys
import os
sys.path.append(os.path.dirname(__file__) + os.sep + '../')
from loger import log

class Item:
    def __init__(self, target, name):
        self.target = target
        self.name = name
        self.process = None
        self.start_time = 0


def main():
    processes = [
        Item(target=run_fetcher.main, name='fetcher'),
        Item(target=run_validator.main, name='validator'),
        Item(target=manage.run, name='api'),
    ]

    while True:
        for p in processes:
            if p.process is None:
                p.process = Process(target=p.target, name=p.name, daemon=False)
                p.process.start()
                log(f'启动{p.name}进程，pid={p.process.pid}')
                p.start_time = time.time()

        for p in processes:
            if p.process is not None:
                if not p.process.is_alive():
                    log(f'进程{p.name}异常退出, exitcode={p.process.exitcode}')
                    p.process.terminate()
                    p.process = None
                elif p.start_time + 60 * 60 < time.time():  # 最长运行1小时就重启
                    log(f'进程{p.name}运行太久，重启', 2)
                    p.process.terminate()
                    p.process = None

        time.sleep(0.2)



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log('========FATAL ERROR=========', 1)
        log(e)
        sys.exit(1)
