import time

import requests

from fetchers.BaseFetcher import BaseFetcher


class ProxyScrapeFetcher(BaseFetcher):
    """
    https://api.proxyscrape.com/?request=displayproxies&proxytype={{ protocol }}&_t={{ timestamp }}
    """
    name = "proxyscrape.com"

    def fetch(self):
        proxies = []
        type_list = ['socks4', 'socks5', 'http', 'https']
        for protocol in type_list:
            url = "https://api.proxyscrape.com/?request=displayproxies&proxytype=" + protocol + "&_t=" + str(
                time.time())
            resp = requests.get(url, verify=False).text
            for data in resp.split("\n"):
                flag_idx = data.find(":")
                ip = data[:flag_idx]
                port = data[flag_idx + 1:-1]
                self.proxies.append((protocol, ip, port))



if __name__ == '__main__':
    f = ProxyScrapeFetcher()
    ps = f.fetch()
    print(ps)