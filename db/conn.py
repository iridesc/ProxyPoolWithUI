# encoding: utf-8

"""
封装的数据库接口
"""
import os
import django
import time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProxyPool.settings")
django.setup()
from proxy_api.models import Fetcher, Proxy


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