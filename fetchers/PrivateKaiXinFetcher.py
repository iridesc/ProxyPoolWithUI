#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 已购买的开心代理
# 在开代理管理界面 配置如下
# 排序方式：按预计剩余存活时间从长到短
# 返回类型：JSON
import requests

from fetchers.BaseFetcher import BaseFetcher


class PrivateKaiXinFetcher(BaseFetcher):
    STATUS_OK = "10001"
    # 建议每10-30秒提取一次以尽量及时获取到新上线的代理IP
    fetch_gap = 15
    base_url = "***"
    username = ""
    password = ""

    def fetch(self):
        """
        执行一次爬取，返回一个数组，每个元素是(protocol, ip, port)，portocol是协议名称，目前主要为http
        返回示例：[('http', '127.0.0.1', 8080), ('http', '127.0.0.1', 1234)]
        """
        resp = requests.get(self.base_url, timeout=10, verify=False)
        if resp and resp.status_code == 200:
            resp = resp.json()
            data = resp["code"] == self.STATUS_OK and resp.get("data") or {}
            for proxy in data.get("proxy_list", []):
                self.proxies.append(("http", proxy["ip"], int(proxy["port"]), self.username, self.password))


if __name__ == '__main__':
    # f = PrivateKaiXinFetcher()
    # f.fetch()
    r = requests.get(PrivateKaiXinFetcher.base_url, timeout=10)
    print(r.json())
