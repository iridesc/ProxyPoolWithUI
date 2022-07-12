from multiprocessing import cpu_count


# 进程最大运行时间
PROCESS_MAX_RUN_TIME = 12 * 60 * 60

# 验证器每次睡眠的时间，单位秒
VALIDATOR_SLEEP_TIME = 10

# 验证线程数
VALIDATE_THREAD_AMOUNT = cpu_count() * 4

# 超时时间，单位s
VALIDATE_TIMEOUT = 5

#  验证时间j间隔
VALIDATE_TIME_GAP = 15

# 单次验证时 尝试次数
VALIDATE_TRIES = 2

# 允许验证失败的次数 大于该次数 将会从数据库中删除
MAX_VALIDATE_FAILED_COUNT = 5

# 验证器 验证目标
VALIDATE_TARGETS_CN = [
    {
        "url": "www.baidu.com",
        "codes": [200, 301, 302],
        "keys": ["百度一下", "baidu", "百度"]
    },
    {
        "url": "www.sogou.com",
        "codes": [200, 301, 302],
        "keys": ["搜狗搜索", "搜狗", "sogou"]
    },
    {
        "url": "weibo.com",
        "codes": [200, 301, 302],
        "keys": ["微博", "sina", "weibo"]
    },
    {
        "url": "zhihu.com",
        "codes": [200, 301, 302],
        "keys": ["知乎", "zhihu"]
    },
]

VALIDATE_TARGETS_OVERSEA = [
    {
        "url": "google.com",
        "codes": [200, 301, 302],
        "keys": ["google", "谷歌"]
    },
    {
        "url": "duckduckgo.com",
        "codes": [200, 301, 302],
        "keys": ["duckduckgo"]
    },
    {
        "url": "facebook.com",
        "codes": [200, 301, 302],
        "keys": ["facebook"]
    },
    {
        "url": "twitter.com",
        "codes": [200, 301, 302],
        "keys": ["twitter"]
    },
]
