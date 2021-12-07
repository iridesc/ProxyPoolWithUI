# encoding: utf-8
"""
定时运行爬取器
"""

import threading
import traceback
from queue import Queue
import time
from db import conn
from config import PROC_FETCHER_SLEEP
from loger import log
from config import FETCHER_MAP

def run_thread(name, fetcher, que):
    """
    name: 爬取器名称
    fetcher: 爬取器class
    que: 队列，用于返回数据
    """
    try:
        f = fetcher()
        proxies = f.fetch()
        que.put((name, proxies))
    except Exception as e:
        log(f'运行爬取器{name}出错：' + str(e), 1)
        traceback.print_exc()
        que.put((name, []))

def main():
    """
    定时运行爬取器
    主要逻辑：
    While True:
        for 爬取器 in 所有爬取器:
            查询数据库，判断当前爬取器是否需要运行
            如果需要运行，那么启动线程运行该爬取器
        等待所有线程结束
        将爬取到的代理放入数据库中
        睡眠一段时间
    """
    while True:
        log('开始运行一轮爬取器')
        status = conn.getProxiesStatus()
    
        if status['pending_proxies_cnt'] > 2000:
            log(f"还有{status['pending_proxies_cnt']}个代理等待验证，数量过多，跳过本次爬取", 2)
            time.sleep(PROC_FETCHER_SLEEP)
            continue



        threads = []
        que = Queue()
        for fetcher_obj in conn.getAllFetchers():
            if fetcher_obj.enable:
                thread = threading.Thread(target=run_thread, args=(
                    fetcher_obj.name, FETCHER_MAP[fetcher_obj.name], que))
                thread.start()
                threads.append(thread)

        [t.join() for t in threads]
        for _ in range(len(threads)):
            assert not que.empty()
            fetcher_name, proxies = que.get()

            for proxy in proxies:
                try:
                    conn.pushNewFetch(fetcher_name, *proxy)
                except:
                    log(f"pushNewFetch 异常:{fetcher_name} {proxy}", 2)
            conn.pushFetcherResult(fetcher_name, len(proxies))

        log(f'完成运行{len(threads)}个爬取器，睡眠{PROC_FETCHER_SLEEP}秒', 1)
        time.sleep(PROC_FETCHER_SLEEP)


if __name__ == '__main__':
    main()