# encoding: utf-8
"""
验证器逻辑
"""

import random
import threading
from queue import Queue
from loger import log
from retry import retry
from func_timeout import func_set_timeout
import time
import requests
from db import conn
from config import PROC_VALIDATOR_SLEEP, VALIDATE_THREAD_NUM, VALIDATE_TARGETS
from config import VALIDATE_TIMEOUT, VALIDATE_MAX_FAILS


def main():
    """
    验证器
    主要逻辑：
    创建VALIDATE_THREAD_NUM个验证线程，这些线程会不断运行
    While True:
        检查验证线程是否返回了代理的验证结果
        从数据库中获取若干当前待验证的代理
        将代理发送给前面创建的线程
    """

    in_que = Queue()
    out_que = Queue()
    running_proxies = set()  # 储存哪些代理正在运行，以字符串的形式储存

    threads = []
    for _ in range(VALIDATE_THREAD_NUM):
        thread = threading.Thread(target=validate_thread, args=(in_que, out_que))
        threads.append(thread)
        thread.start()

    while True:
        out_cnt = 0
        while not out_que.empty():
            proxy, success, latency = out_que.get()
            conn.pushValidateResult(proxy, success, latency)
            uri = f'{proxy.protocol}://{proxy.ip}:{proxy.port}'
            assert uri in running_proxies
            running_proxies.remove(uri)
            out_cnt = out_cnt + 1
        if out_cnt > 0:
            log(f"验证完成：{out_cnt}")

        # 如果正在进行验证的代理足够多，那么就不着急添加新代理
        if len(running_proxies) >= VALIDATE_THREAD_NUM:
            time.sleep(PROC_VALIDATOR_SLEEP)
            continue

        # 找一些新的待验证的代理放入队列中
        added_cnt = 0
        for proxy in conn.getToValidate(VALIDATE_THREAD_NUM):
            uri = f'{proxy.protocol}://{proxy.ip}:{proxy.port}'
            # 这里找出的代理有可能是正在进行验证的代理，要避免重复加入
            if uri not in running_proxies:
                running_proxies.add(uri)
                in_que.put(proxy)
                added_cnt += 1

        if added_cnt == 0:
            time.sleep(PROC_VALIDATOR_SLEEP)


@func_set_timeout(VALIDATE_MAX_FAILS*VALIDATE_TIMEOUT*2)
@retry(tries=VALIDATE_MAX_FAILS)
def validate_once(proxy):
    """[随机选择一个验证目标验证一次代理]

    Returns:
        [bool]: [代理是否可用]
        [float]: [可用则返回延时， 否则返回None]
    """

    target = random.choice(VALIDATE_TARGETS)
    start_time = time.time()
    r = requests.get(
        url=target["url"],
        timeout=VALIDATE_TIMEOUT,
        proxies={
            'http': f'{proxy.protocol}://{proxy.ip}:{proxy.port}',
            'https': f'{proxy.protocol}://{proxy.ip}:{proxy.port}'
        }
    )
    r.raise_for_status()
    
    # 延时 加 传输耗时 对评估代理可用性更有价值
    time_cost = time.time() - start_time
    # 可用 = 整体耗时 < 预设耗时 and 状态码正常
    success = r.status_code in target["codes"] and time_cost <= VALIDATE_TIMEOUT
    return success, int(time_cost*1000) if success else None


def validate_thread(in_que, out_que):
    """
    验证函数，这个函数会在一个线程中被调用
    in_que: 输入队列，用于接收验证任务
    out_que: 输出队列，用于返回验证结果
    in_que和out_que都是线程安全队列，并且如果队列为空，调用in_que.get()会阻塞线程
    """

    while True:
        proxy = in_que.get()
        # 尝试验证代理 返回可用状态与 异常则返回不可用状态
        try:
            success, latency = validate_once(proxy)
        except Exception:
            success = False
            latency = None

        out_que.put((proxy, success, latency))
