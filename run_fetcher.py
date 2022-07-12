# encoding: utf-8
"""
定时运行爬取器
"""

import time
import os
import django
import importlib
from fetchers.BaseFetcher import BaseFetcher
from config import MAX_ALIVE_PROXY_AMOUNT

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProxyPool.settings")
django.setup()
from proxy_api.models import Fetcher, StatusRecode, Proxy


def main():
    while True:
        proxies = Proxy.objects.filter(
            to_validate_time__lt=time.time()).order_by("validated").order_by("to_validate_time")
        if proxies.count() >= MAX_ALIVE_PROXY_AMOUNT:
            time.sleep(BaseFetcher.fetch_gap / 3)
            continue

        any_fetcher_run = False
        for fetcher_file in os.listdir("fetchers"):
            # 过滤掉非目标的文件 和 基础类
            if not fetcher_file.endswith("Fetcher.py") or fetcher_file == "BaseFetcher.py":
                continue

            # 获取类名
            fetcher_class_name = fetcher_file.split(".")[0]
            # 根据类名获取FetcherClass
            FetcherClass = getattr(importlib.import_module(f"fetchers.{fetcher_class_name}"), fetcher_class_name)
            # 根据类名检查是否已经同步到数据库
            fetcher_objs = Fetcher.objects.filter(name=fetcher_class_name)
            if fetcher_objs.count() == 0:
                # 没有同步 则创建
                fetcher_obj = Fetcher()
                fetcher_obj.name = fetcher_class_name
                fetcher_obj.save()
            else:
                # 已存在则取出
                fetcher_obj = fetcher_objs[0]

            if time.time() - fetcher_obj.last_fetch_time > FetcherClass.fetch_gap and fetcher_obj.enable:
                fetcher = FetcherClass(fetcher_obj)
                fetcher.run()
                any_fetcher_run = True

        # 记录系统状态
        if any_fetcher_run:
            StatusRecode.make_recode()


if __name__ == '__main__':
    main()
