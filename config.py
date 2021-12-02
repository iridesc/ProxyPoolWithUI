# encoding: utf-8

"""
配置文件，一般来说不需要修改
如果需要启用或者禁用某些网站的爬取器，可在网页上进行配置
"""

import os

# 数据库文件路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

# 每次运行所有爬取器之后，睡眠多少时间，单位秒
PROC_FETCHER_SLEEP = 5 * 60

# 验证器每次睡眠的时间，单位秒
PROC_VALIDATOR_SLEEP = 5

# 验证器的配置参数
VALIDATE_THREAD_NUM = 80  # 验证线程数量
VALIDATE_TARGETS = [
    {
        "url": "http://detectportal.firefox.com/success.txt",
        "codes": [204, 200],
    },
    {
        "url": "http://connectivitycheck.platform.hicloud.com/generate_204",
        "codes": [204, 200],
    },
    {
        "url": "http://connect.rom.miui.com/generate_204",
        "codes": [204, 200],
    },
    {
        "url": "http://wifi.vivo.com.cn/generate_204",
        "codes": [204, 200],
    },
    {
        "url": "http://www.msftconnecttest.com/connecttest.txt",
        "codes": [204, 200],
    },
    {
        "url": "http://www.apple.com/library/test/success.html",
        "codes": [204, 200],
    },
    {
        "url": "http://www.google-analytics.com/generate_204",
        "codes": [204, 200],
    }
]
VALIDATE_TIMEOUT = 2  # 超时时间，单位s
VALIDATE_MAX_FAILS = 3
