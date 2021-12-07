# encoding: utf-8

"""
封装的数据库接口
"""
from loger import log
import os
import django
import time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProxyPool.settings")
django.setup()
from proxy_api.models import Fetcher, Proxy






def pushNewFetch(fetcher_name, protocol, ip, port):
    """
    爬取器新抓到了一个代理，调用本函数将代理放入数据库
    fetcher_name : 爬取器名称
    protocol : 代理协议
    ip : 代理IP地址
    port : 代理端口
    """
    if not Proxy.objects.filter(protocol=protocol, ip=ip, port=port).exists():
        proxy = Proxy()
        proxy.fetcher = Fetcher.objects.get(name=fetcher_name)
        proxy.protocol = protocol
        proxy.ip = ip
        proxy.port = port
        proxy.save()


def getToValidate(max_count=1):
    """
    从数据库中获取待验证的代理，根据to_validate_date字段
    优先选取已经通过了验证的代理，其次是没有通过验证的代理
    max_count : 返回数量限制
    返回 : list[Proxy]
    """
    proxies = Proxy.objects.filter(
        to_validate_time__lt=time.time()).order_by("validated").order_by("to_validate_time")[:max_count]
    return proxies


def pushValidateResult(proxy, success_cn, latency_cn, success_oversea, latency_oversea):
    """
    将验证器的一个结果添加进数据库中
    proxy : 代理
    success : True/False，验证是否成功
    latency : 本次验证所用的时间(单位毫秒)
    """

    def validate(proxy, success_cn, latency_cn, success_oversea, latency_oversea):
        """
        传入一次验证结果，根据验证结果调整自身属性，并返回是否删除这个代理
        success : True/False，表示本次验证是否成功
        返回 : True/False，True表示这个代理太差了，应该从数据库中删除
        """
        proxy.validated = success_cn or success_oversea

        proxy.validate_failed_count += 0 if proxy.validated else 1
        if proxy.validate_failed_count > 20:
            return True

        proxy.latency_cn = latency_cn
        proxy.latency_oversea = latency_oversea
        proxy.validate_time = time.time()
        # log(f"{proxy} {proxy.validated} {proxy.latency_cn} {proxy.latency_oversea}")
        # 10分钟之后继续验证
        proxy.to_validate_time = time.time() + 60*10 if proxy.validated else time.time() + proxy.validate_failed_count * 60*10

        return False

    should_remove = validate(proxy, success_cn, latency_cn, success_oversea, latency_oversea)
    if should_remove:
        proxy.delete()
    else:
        proxy.save()


def getValidatedRandom(max_count):
    """
    从通过了验证的代理中，随机选择max_count个代理返回
    max_count<=0表示不做数量限制
    返回 : list[Proxy]
    """
    if max_count > 0:
        r = conn.execute('SELECT * FROM proxies WHERE validated=? ORDER BY RANDOM() LIMIT ?', (True, max_count))
    else:
        r = conn.execute('SELECT * FROM proxies WHERE validated=? ORDER BY RANDOM()', (True,))
    proxies = [Proxy.decode(row) for row in r]
    r.close()
    return proxies


def pushFetcherResult(name, proxies_amount):
    """
    更新爬取器的状态，每次在完成一个网站的爬取之后，调用本函数
    name : 爬取器的名称
    proxies_cnt : 本次爬取到的代理数量
    """
    fetcher = Fetcher.objects.get(name=name)
    fetcher.last_proxies_amount = proxies_amount
    fetcher.sum_proxies_amount = Proxy.objects.filter(fetcher = fetcher).count()
    fetcher.last_fetch_time = time.time()
    fetcher.save()


def pushFetcherEnable(name, enable):
    """
    设置是否起用对应爬取器，被禁用的爬取器将不会被运行
    name : 爬取器的名称
    enable : True/False, 是否启用
    """
    c = conn.cursor()
    c.execute('BEGIN EXCLUSIVE TRANSACTION;')
    c.execute('SELECT * FROM fetchers WHERE name=?', (name,))
    row = c.fetchone()
    if row is None:
        raise ValueError(f'ERRROR: can not find fetcher {name}')
    else:
        f = Fetcher.decode(row)
        f.enable = enable
        c.execute('UPDATE fetchers SET enable=? WHERE name=?', (
            f.enable, f.name
        ))
    c.close()
    conn.commit()


def getAllFetchers():
    """
    获取所有的爬取器以及状态
    返回 : list[Fetcher]
    """

    return Fetcher.objects.all()


def getFetcher(name):
    """
    获取指定爬取器以及状态
    返回 : Fetcher
    """
    # r = conn.execute('SELECT * FROM fetchers WHERE name=?', (name,))
    # row = r.fetchone()
    # r.close()
    return Fetcher.objects.get(name=name)


def getProxyCount(fetcher_name):
    """
    查询在数据库中有多少个由指定爬取器爬取到的代理
    fetcher_name : 爬取器名称
    返回 : int
    """
    r = conn.execute('SELECT count(*) FROM proxies WHERE fetcher_name=?', (fetcher_name,))
    cnt = r.fetchone()[0]
    r.close()
    return cnt


def getProxiesStatus():
    """
    获取代理状态，包括`全部代理数量`，`当前可用代理数量`，`等待验证代理数量`
    返回 : dict
    """
    # r = conn.execute('SELECT count(*) FROM proxies')
    # sum_proxies_cnt = r.fetchone()[0]
    # r.close()

    all_query_set = Proxy.objects.all()
    sum_proxies_cnt = all_query_set.count()

    # r = conn.execute('SELECT count(*) FROM proxies WHERE validated=?', (True,))
    # validated_proxies_cnt = r.fetchone()[0]
    # r.close()

    validated_proxies_cnt = Proxy.objects.filter(validated=False).count()

    # r = conn.execute('SELECT count(*) FROM proxies WHERE to_validate_date<=?', (datetime.datetime.now(),))
    # pending_proxies_cnt = r.fetchone()[0]
    # r.close()

    pending_proxies_cnt = Proxy.objects.filter(to_validate_time__lt=time.time()).count()

    return dict(
        sum_proxies_cnt=sum_proxies_cnt,
        validated_proxies_cnt=validated_proxies_cnt,
        pending_proxies_cnt=pending_proxies_cnt
    )


def pushClearFetchersStatus():
    """
    清空爬取器的统计信息，包括sum_proxies_cnt,last_proxies_cnt,last_fetch_date
    """
    c = conn.cursor()
    c.execute('BEGIN EXCLUSIVE TRANSACTION;')
    c.execute('UPDATE fetchers SET sum_proxies_cnt=?, last_proxies_cnt=?, last_fetch_date=?', (0, 0, None))
    c.close()
    conn.commit()
