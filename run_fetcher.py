# encoding: utf-8
"""
定时运行爬取器
"""

import time
from config import PROC_FETCHER_SLEEP
from config import FETCHER_MAP

def main():
    last_run_time = 0
    while True:
        check_time = time.time()
        if check_time - last_run_time > PROC_FETCHER_SLEEP:
            last_run_time = check_time
            for Fetcher in FETCHER_MAP.values():
                fetcher = Fetcher()
                fetcher.run()
        else:
            time.sleep(PROC_FETCHER_SLEEP/3)

if __name__ == '__main__':
    main()