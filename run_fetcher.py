# encoding: utf-8
"""
定时运行爬取器
"""

import time
from config import PROC_FETCHER_SLEEP
from config import FETCHER_MAP
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProxyPool.settings")
django.setup()
from proxy_api.models import Fetcher


def main():
    while True:
        for FetcherClass in FETCHER_MAP.values():
            fetcher_obj = Fetcher.objects.get(name=FetcherClass.name)
            if time.time() - fetcher_obj.last_fetch_time > PROC_FETCHER_SLEEP:
                fetcher = FetcherClass(fetcher_obj)
                fetcher.run()
        time.sleep(PROC_FETCHER_SLEEP/3)

if __name__ == '__main__':
    main()