import random
from loger import log
from retry import retry
import time
import traceback
import requests
from concurrent.futures import ThreadPoolExecutor as Pool
import os
import django
from dataclasses import dataclass
from requests.exceptions import ConnectionError, ConnectTimeout, ProxyError, ReadTimeout, HTTPError,\
    ChunkedEncodingError, InvalidSchema
from config import VALIDATOR_SLEEP_TIME, VALIDATE_THREAD_AMOUNT, VALIDATE_TARGETS_CN, VALIDATE_TARGETS_OVERSEA
from config import VALIDATE_TIMEOUT, VALIDATE_TRIES, VALIDATE_TIME_GAP, MAX_VALIDATE_FAILED_COUNT

requests.packages.urllib3.disable_warnings()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProxyPool.settings")
django.setup()
from proxy_api.models import Proxy


@dataclass
class CodeError(Exception):
    error_code: int
    allow_codes: list


@dataclass
class KeyNotFoundError(Exception):
    keys: list


PASS_ERRORS = (ConnectionError, ConnectTimeout, ProxyError, ReadTimeout, HTTPError, ChunkedEncodingError, InvalidSchema)
SHOW_ERRORS = (CodeError, KeyNotFoundError)


def check_content(content, target):
    for key in target["keys"]:
        if key.lower() in content.lower():
            return True
    # with open(f"{target['key']}-{hashlib.md5(content.encode('utf-8'))}.html", "w", encoding="utf8") as f:
    #     f.write(r.text)
    return False


@retry(tries=VALIDATE_TRIES)
def validate_once(proxy, targets, protocol) -> int:
    """随机选择一个目标来验证当前代理

    Args:
        proxy : 代理
        targets : 验证目标

    Returns:
        int: 代理耗时（ms）
    """

    # 获取验证目标
    target = random.choice(targets)

    # 构建代理
    proxies = {
        'http': f'{proxy.protocol}://{proxy.ip}:{proxy.port}',
        'https': f'{proxy.protocol}://{proxy.ip}:{proxy.port}',
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
        stream=True,
    )

    # 验证访问耗时
    time_cost = time.time() - start_time

    # 验证状态码
    if r.status_code not in target["codes"]:
        raise CodeError(r.status_code, target["codes"])

    # 检查关键字
    elif not check_content(r.text, target):
        raise KeyNotFoundError(target["keys"])

    else:
        log("验证通过", 4)
        # 可用 = 整体耗时 < 预设耗时 and 状态码正常
        return int(time_cost * 1000)


def get_latency(proxy, protocol, targets):
    # 尝试验证代理 返回延时
    try:
        return validate_once(proxy, targets, protocol)
    except PASS_ERRORS:
        return 9999
    except SHOW_ERRORS as e:
        log(str(e), 1)
        return 9999

    except Exception:
        log(f"未知异常: {traceback.format_exc()}")
        return 9999


def validate_thread(proxy):
    """
    验证函数
    """

    latency_cn, latency_oversea = 9999, 9999
    for protocol in ["http", "https"]:
        if latency_cn == 9999:
            latency_cn = get_latency(proxy=proxy, protocol=protocol, targets=VALIDATE_TARGETS_CN)

        if latency_oversea == 9999:
            latency_oversea = get_latency(proxy=proxy, protocol=protocol, targets=VALIDATE_TARGETS_OVERSEA)

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

    # 检查验证次数是否超限 超限 则 删除
    if proxy.validate_failed_count > MAX_VALIDATE_FAILED_COUNT:
        log(f"del: {proxy}", 2)
        proxy.delete()
    else:
        proxy.save()

    return proxy.validated


def main():
    """
    从数据库中选出需要验证的代理 进行验证.
    """
    while True:
        # 获取需要验证的代理
        proxies = Proxy.objects.filter(to_validate_time__lt=time.time()).order_by(
            "validated").order_by("to_validate_time")[:VALIDATE_THREAD_AMOUNT]

        if not proxies.count():
            # 没有需要验证的代理 则 等待一段时间再检查
            time.sleep(VALIDATOR_SLEEP_TIME)
            continue

        # 将获取的代理 放入线程池 进行验证
        with Pool() as pool:
            results = [result for result in pool.map(validate_thread, proxies)]

        log(f"passed: {sum(results)}/{len(results) }")


if __name__ == '__main__':
    main()
