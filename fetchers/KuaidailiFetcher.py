# encoding: utf-8

from fetchers.BaseFetcher import BaseFetcher
import time
import requests
from bs4 import BeautifulSoup

class KuaidailiFetcher(BaseFetcher):
    """
    https://www.kuaidaili.com/free
    """
    name = "www.kuaidaili.com"

    def fetch(self):
        """
        执行一次爬取，返回一个数组，每个元素是(protocol, ip, port)，portocal是协议名称，目前主要为http
        返回示例：[('http', '127.0.0.1', 8080), ('http', '127.0.0.1', 1234)]
        """
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}

        urls = []
        urls = urls + [f'https://www.kuaidaili.com/free/inha/{page}/' for page in range(1, 11)]
        urls = urls + [f'https://www.kuaidaili.com/free/intr/{page}/' for page in range(1, 11)]

        proxies = []

        for url in urls:
            r = requests.get(url, headers=headers, timeout=10, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            for item in soup.tbody.find_all("tr"):
                tds = item.find_all("td")
                ip = tds[0].get_text()
                port = tds[1].get_text()
                protocol = tds[3].get_text().lower()
                self.proxies.append((protocol, ip, port))
            time.sleep(2)



if __name__ == '__main__':
    f = KuaidailiFetcher()
    ps = f.fetch()
    print(ps)