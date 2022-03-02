import re
import time
import random
from retry import retry

import requests
from bs4 import BeautifulSoup
import ddddocr

from BaseFetcher import BaseFetcher

ocr = ddddocr.DdddOcr()


class MivipFetcher(BaseFetcher):
    """
    http://proxy.mimvp.com/freeopen?proxy=in_hp    
    """
    base_url = "http://proxy.mimvp.com"

    @retry(tries=3, delay=2)
    def req(self, tag_name, page):
        r = requests.get(f"{self.base_url}/freeopen", params={"proxy": tag_name, "sort": "p_checkdtime", "page":page}, verify=False)
        r.raise_for_status()
        return r

    @staticmethod
    @retry(tries=3)
    def get_port(img_url: str):
        r = requests.get(img_url)
        return ocr.classification(r.content)


    def fetch(self):
        """
        执行一次爬取，返回一个数组，每个元素是(protocol, ip, port)，portocol是协议名称，目前主要为http
        返回示例：[('http', '127.0.0.1', 8080), ('http', '127.0.0.1', 1234)]
        """
        proxies = []
        for tag_name in ["in_hp", "in_socks", "out_hp", "out_socks"]:
            for page in range(1, 500):
                r = self.req(tag_name, page)
                soup = BeautifulSoup(r.text, "html.parser")
                table_tag = soup.find("table", class_="free-proxylist-tbl").find("tbody")
                proxy_line_tags = table_tag.find_all("tr")
                if not proxy_line_tags:
                    break
                outdate = False
                hided = False
                for proxy_line_tag in proxy_line_tags:
                    time_str = proxy_line_tag.find(class_="free-proxylist-tbl-proxy-checkdtime").get_text().strip()
                    time_array = time.strptime(time_str, "%Y-%m-%d %H:%M")
                    time_stamp = int(time.mktime(time_array))
                    if time.time() - time_stamp > 72*60*60:
                        outdate = True
                        break
                    else:
                        ip = proxy_line_tag.find(class_="free-proxylist-tbl-proxy-ip").get_text().lower().strip()
                        if "*" in ip:
                            hided = True
                            break
                        port = self.get_port(f"{self.base_url}{proxy_line_tag.img.get('src')}")
                        protocol = proxy_line_tag.find(class_="free-proxylist-tbl-proxy-type").get_text().lower().strip()
                        proxies.append((protocol, ip, port))
                if outdate or hided:
                    break
            time.sleep(0.5)

        return proxies


if __name__ == '__main__':

    f = MivipFetcher()
    ps = f.fetch()
    print(ps)
