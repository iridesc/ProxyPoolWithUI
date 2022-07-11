# encoding: utf-8
"""
验证器逻辑
"""

import hashlib
import random
import threading
from queue import Queue
from loger import log
from retry import retry
from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut
import time
import requests

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProxyPool.settings")
django.setup()
from proxy_api.models import Fetcher, StatusRecode, Proxy

from requests.exceptions import ConnectionError, ConnectTimeout, ProxyError, ReadTimeout, HTTPError,\
    ChunkedEncodingError, InvalidSchema
from config import PROC_VALIDATOR_SLEEP, VALIDATE_THREAD_NUM, VALIDATE_TARGETS_CN, VALIDATE_TARGETS_OVERSEA
from config import VALIDATE_TIMEOUT, VALIDATE_MAX_FAILS, VALIDATE_TIME_GAP

pass_error = (ConnectionError, ConnectTimeout, ProxyError, ReadTimeout, HTTPError, FunctionTimedOut,
              ChunkedEncodingError, InvalidSchema)


def get_cpu_count(expand=4):
    from multiprocessing import cpu_count
    if VALIDATE_THREAD_NUM < int(expand):
        return VALIDATE_THREAD_NUM
    return cpu_count() * int(expand)


CPU_COUNT = get_cpu_count()


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
    while True:
        threads = []
        out_q = Queue()
        proxies = Proxy.objects.filter(
            to_validate_time__lt=time.time()).order_by("validated").order_by("to_validate_time")[:CPU_COUNT]
        for proxy in proxies:
            thread = threading.Thread(target=validate_thread, args=(proxy, out_q,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        saved_count = 0
        while not out_q.empty():
            saved_count += save_proxy(out_q.get())

        log(f"验证完成 a:{len(proxies)} s: {saved_count} d: {len(proxies) - saved_count}")
        if not len(proxies):
            time.sleep(PROC_VALIDATOR_SLEEP)


def save_proxy(proxy):
    # 如果失败次数大于100 则放弃该代理
    if proxy.validate_failed_count > 10:
        print(f"del: {proxy}")
        proxy.delete()
        return False
    else:
        proxy.save()
        return True


def validate_thread(proxy, out_q):
    """
    验证函数，这个函数会在一个线程中被调用
    in_que: 输入队列，用于接收验证任务
    out_que: 输出队列，用于返回验证结果
    in_que和out_que都是线程安全队列，并且如果队列为空，调用in_que.get()会阻塞线程
    """
    @func_set_timeout(VALIDATE_MAX_FAILS*VALIDATE_TIMEOUT*1.5)
    @retry(tries=VALIDATE_MAX_FAILS)
    def validate_once(proxy, targets, protocol) -> int:
        """_随机选择一个目标来验证当前代理_

        Args:
            proxy : _代理_
            targets : _验证目标_

        Returns:
            int: _代理耗时（ms）_
        """
        def check_content(content, target):
            for key in target["keys"]:
                if key.lower() in content.lower():
                    return True
            with open(f"{target['key']}-{hashlib.md5(content.encode('utf-8'))}.html", "w", encoding="utf8") as f:
                f.write(r.text)
            return False

        # 获取验证目标
        target = random.choice(targets)

        # proxies[proxy] = f'{proxy.protocol}://{proxy.ip}:{proxy.port}'
        proxies = {
            'http': f'{proxy.ip}:{proxy.port}',
            'https': f'{proxy.ip}:{proxy.port}',
        }

        # 记录验证耗时
        start_time = time.time()
        # 验证可访问性
        r = requests.get(
            url=f"{protocol}://{target['url']}",
            timeout=VALIDATE_TIMEOUT,
            headers={
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'},
            proxies=proxies,
            allow_redirects=False,
            verify=False,
        )

        # 验证访问延时
        time_cost = time.time() - start_time
        if time_cost > VALIDATE_TIMEOUT:
            raise Exception("请求超时")

        # 验证状态码
        elif r.status_code not in target["codes"]:
            raise Exception(f"状态码不允许：{r.status_code}")

        # 检查关键字
        elif not check_content(r.text, target):
            log("key not exist!", 1)
            raise Exception("key not in r.text")

        else:
            log("验证通过", 4)
            # 可用 = 整体耗时 < 预设耗时 and 状态码正常
            return int(time_cost*1000)

    latency_cn, latency_oversea = 9999, 9999
    for protocol in ["http", "https"]:
        if latency_cn == 9999:
            # 尝试验证代理 返回延时
            try:
                latency_cn = validate_once(proxy, VALIDATE_TARGETS_CN, protocol)
            except pass_error:
                pass
            except Exception as e:
                log(str(e), 1)
                log(e.__class__.__name__, 2)

        if latency_oversea == 9999:
            try:
                latency_oversea = validate_once(proxy, VALIDATE_TARGETS_OVERSEA, protocol)
            except pass_error:
                pass
            except Exception as e:
                log(str(e), 1)
                log(e.__class__.__name__, 2)

    # 记录延迟与 验证时间
    proxy.latency_cn = latency_cn
    proxy.latency_oversea = latency_oversea
    # 只要一个区域验证成功则认为成功
    proxy.validated = latency_cn != 9999 or latency_oversea != 9999
    # 根据是否成功 更新验证失败的次数
    proxy.validate_failed_count = 0 if proxy.validated else proxy.validate_failed_count + 1
    # 验证时间
    proxy.validate_time = time.time()
    # 计算下次验证时间
    proxy.to_validate_time = proxy.validate_time + VALIDATE_TIME_GAP * \
        (1 if proxy.validated else proxy.validate_failed_count ** 2)
    out_q.put(proxy)


if __name__ == '__main__':
    main()
