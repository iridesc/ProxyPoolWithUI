# encoding: utf-8

"""
配置文件，一般来说不需要修改
如果需要启用或者禁用某些网站的爬取器，可在网页上进行配置
"""

import os
from fetchers import IP66Fetcher
from fetchers.GoubanjiaFetcher import GoubanjiaFetcher
from fetchers.IHuanFetcher import IHuanFetcher
from fetchers.IP3366Fetcher import IP3366Fetcher
from fetchers.IP89Fetcher import IP89Fetcher
from fetchers.JiangxianliFetcher import JiangxianliFetcher
from fetchers.KaiXinFetcher import KaiXinFetcher
from fetchers.KuaidailiFetcher import KuaidailiFetcher
from fetchers.ProxyListFetcher import ProxyListFetcher
from fetchers.ProxyScrapeFetcher import ProxyScrapeFetcher
from fetchers.ProxyscanFetcher import ProxyscanFetcher
from fetchers.UUFetcher import UUFetcher
from fetchers.XiaoShuFetcher import XiaoShuFetcher
from fetchers.XiLaFetcher import XiLaFetcher

# 数据库文件路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

# 每次运行所有爬取器之后，睡眠多少时间，单位秒
PROC_FETCHER_SLEEP = 5 * 60

# 验证器每次睡眠的时间，单位秒
PROC_VALIDATOR_SLEEP = 10

# 验证线程数量
VALIDATE_THREAD_NUM = 100

# 超时时间，单位s
VALIDATE_TIMEOUT = 5

# 验证允许失败次数
VALIDATE_MAX_FAILS = 3

# 验证器 验证目标
VALIDATE_TARGETS_CN = [
    {
        "url": "http://www.baidu.com",
        "codes": [200],
    },
    {
        "url": "http://www.sogou.com",
        "codes": [200],
    },
    {
        "url": "http://weibo.com",
        "codes": [200],
    },
    {
        "url": "http://zhihu.com",
        "codes": [200],
    },
]

VALIDATE_TARGETS_OVERSEA = [
    {
        "url": "http://google.com",
        "codes": [200],
    },
    {
        "url": "http://duckduckgo.com",
        "codes": [200],
    },
    {
        "url": "http://facebook.com",
        "codes": [200],
    },
    {
        "url": "http://twitter.com",
        "codes": [200],
    },
]

FETCHER_MAP = {
    "www.xsdaili.cn": XiaoShuFetcher,
    "www.xiladaili.com": XiLaFetcher,
    "www.proxyscan.io": ProxyscanFetcher,
    "www.proxy-list.download": ProxyListFetcher,
    "www.kxdaili.com": KaiXinFetcher,
    "www.kuaidaili.com": KuaidailiFetcher,
    "www.ip3366.net": IP3366Fetcher,
    "www.goubanjia.com": GoubanjiaFetcher,
    "www.89ip.cn": IP89Fetcher,
    "www.66ip.cn": IP66Fetcher,
    "uu-proxy.com": UUFetcher,
    "proxyscrape.com": ProxyScrapeFetcher,
    "ip.jiangxianli.com": JiangxianliFetcher,
    "ip.ihuan.me": IHuanFetcher,
}
