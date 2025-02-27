import re
import time

import requests
from pyquery import PyQuery as pq

from fetchers.BaseFetcher import BaseFetcher


class KaiXinFetcher(BaseFetcher):
    """
    http://www.kxdaili.com/dailiip.html
    代码由 [Zealot666](https://github.com/Zealot666) 提供
    """

    def fetch(self):
        """
        执行一次爬取，返回一个数组，每个元素是(protocol, ip, port)，portocol是协议名称，目前主要为http
        返回示例：[('http', '127.0.0.1', 8080), ('http', '127.0.0.1', 1234)]
        """

        urls = []
        urls = urls + [f'http://www.kxdaili.com/dailiip/1/{page}.html' for page in range(1, 11)]
        urls = urls + [f'http://www.kxdaili.com/dailiip/2/{page}.html' for page in range(1, 11)]

        proxies = []
        ip_regex = re.compile(r'^\d+\.\d+\.\d+\.\d+$')
        port_regex = re.compile(r'^\d+$')

        for url in urls:
            html = requests.get(url, timeout=10, verify=False).text
            doc = pq(html)
            for line in doc('tr').items():
                tds = list(line('td').items())
                if len(tds) >= 2:
                    ip = tds[0].text().strip()
                    port = tds[1].text().strip()
                    if re.match(ip_regex, ip) is not None and re.match(port_regex, port) is not None:
                        self.proxies.append(('http', ip, int(port)))


if __name__ == '__main__':
    f = KaiXinFetcher()
    ps = f.fetch()
    print(ps)
