# encoding: utf-8

"""
配置文件，一般来说不需要修改
如果需要启用或者禁用某些网站的爬取器，可在网页上进行配置
"""

import os
from fetchers.IP66Fetcher import IP66Fetcher
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
from fetchers.MivipFetcher import MivipFetcher

# 进程最大运行时间
PROCESS_MAX_RUN_TIME = 12*60*60

# 验证器每次睡眠的时间，单位秒
PROC_VALIDATOR_SLEEP = 10

# 验证线程数量
VALIDATE_THREAD_NUM = 100

# 超时时间，单位s
VALIDATE_TIMEOUT = 5

# 超时时间，单位s
VALIDATE_TIME_GAP = 30*60

# 验证允许失败次数
VALIDATE_MAX_FAILS = 1

# 验证器 验证目标
VALIDATE_TARGETS_CN = [
    {
        "url": "www.baidu.com",
        "codes": [200, 301],
        "keys": ["百度一下", "baidu", "百度"]
    },
    {
        "url": "www.sogou.com",
        "codes": [200, 301],
        "keys": ["搜狗搜索", "搜狗", "sogou"]
    },
    {
        "url": "weibo.com",
        "codes": [200, 301],
        "keys": ["微博", "sina", "weibo"]
    },
    {
        "url": "zhihu.com",
        "codes": [200, 301],
        "keys": ["知乎", "zhihu"]
    },
]

VALIDATE_TARGETS_OVERSEA = [
    {
        "url": "google.com",
        "codes": [200, 301],
        "keys": ["google", "谷歌"]
    },
    {
        "url": "duckduckgo.com",
        "codes": [200, 301],
        "keys": ["duckduckgo"]
    },
    {
        "url": "facebook.com",
        "codes": [200, 301],
        "keys": ["facebook"]
    },
    {
        "url": "twitter.com",
        "codes": [200, 301],
        "keys": ["twitter"]
    },
]
