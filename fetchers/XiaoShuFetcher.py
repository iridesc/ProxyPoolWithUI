from operator import index
import re
import time
import random

import requests
from pyquery import PyQuery as pq

from fetchers.BaseFetcher import BaseFetcher

class XiaoShuFetcher(BaseFetcher):
    """
    http://www.xsdaili.cn/
    代码由 [Zealot666](https://github.com/Zealot666) 提供
    """
    index = 0

    def fetch(self):
        """
        执行一次爬取，返回一个数组，每个元素是(protocol, ip, port)，portocol是协议名称，目前主要为http
        返回示例：[('http', '127.0.0.1', 8080), ('http', '127.0.0.1', 1234)]
        """
        self.index += 1
        new_index = self.index % 10

        urls = set()
        proxies = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        }
        for page in range(new_index, new_index + 1):
            response = requests.get("http://www.xsdaili.cn/dayProxy/" + str(page) + ".html", headers=headers, timeout=10, verify=False)
            for item in pq(response.text)('a').items():
                try:
                    if "/dayProxy/ip" in item.attr("href"):
                        urls.add("http://www.xsdaili.cn" + item.attr("href"))
                except Exception:
                    continue
            for url in urls:
                response = requests.get(url, headers=headers, timeout=8)
                doc = pq(response.text)
                for item in doc(".cont").items():
                    for line in item.text().split("\n"):
                        ip = line.split('@')[0].split(':')[0]
                        port = line.split('@')[0].split(':')[1]
                        proxies.append(("http", ip, port))

        proxies = list(set(proxies))

        # 这个代理源数据太多了，验证器跑不过来
        # 所以只取一部分，一般来说也够用了
        if len(proxies) > 200:
            self.proxies = random.sample(proxies, 200)



if __name__ == '__main__':
    f = XiaoShuFetcher()
    ps = f.fetch()
    print(ps)