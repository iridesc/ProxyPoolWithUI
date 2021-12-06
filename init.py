
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProxyPool.settings")
django.setup()
from fetchers.ProxyScrapeFetcher import ProxyScrapeFetcher
from fetchers.ProxyListFetcher import ProxyListFetcher
from fetchers.XiaoShuFetcher import XiaoShuFetcher
from fetchers.XiLaFetcher import XiLaFetcher
from fetchers.KaiXinFetcher import KaiXinFetcher
from fetchers.ProxyscanFetcher import ProxyscanFetcher
from fetchers.IP89Fetcher import IP89Fetcher
from fetchers.IHuanFetcher import IHuanFetcher
from fetchers.JiangxianliFetcher import JiangxianliFetcher
from fetchers.IP3366Fetcher import IP3366Fetcher
from fetchers.IP66Fetcher import IP66Fetcher
from fetchers.GoubanjiaFetcher import GoubanjiaFetcher
from fetchers.KuaidailiFetcher import KuaidailiFetcher
from fetchers.UUFetcher import UUFetcher
from collections import namedtuple
from proxy_api.models import Fetcher as FO
Fetcher = namedtuple('Fetcher', ['name', 'fetcher'])


fetchers = [
    Fetcher(name='uu-proxy.com', fetcher=UUFetcher),
    Fetcher(name='www.kuaidaili.com', fetcher=KuaidailiFetcher),
    Fetcher(name='www.goubanjia.com', fetcher=GoubanjiaFetcher),
    Fetcher(name='www.66ip.cn', fetcher=IP66Fetcher),
    Fetcher(name='www.ip3366.net', fetcher=IP3366Fetcher),
    Fetcher(name='ip.jiangxianli.com', fetcher=JiangxianliFetcher),
    Fetcher(name='ip.ihuan.me', fetcher=IHuanFetcher),
    Fetcher(name='www.proxyscan.io', fetcher=ProxyscanFetcher),
    Fetcher(name='www.89ip.cn', fetcher=IP89Fetcher),
    Fetcher(name='www.kxdaili.com', fetcher=KaiXinFetcher),
    Fetcher(name='www.xiladaili.com', fetcher=XiLaFetcher),
    Fetcher(name='www.xsdaili.cn', fetcher=XiaoShuFetcher),
    Fetcher(name='www.proxy-list.download', fetcher=ProxyListFetcher),
    Fetcher(name='proxyscrape.com', fetcher=ProxyScrapeFetcher)
]


def init():
    """
    初始化数据库
    """
    # 注册所有的爬取器
    for item in fetchers:
        if not FO.objects.filter(name=item.name).exists():
            fetcher = FO()
            fetcher.name = item.name
            fetcher.save()


init()
