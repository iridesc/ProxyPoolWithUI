import time
import django
import os
import traceback
from loger import log
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProxyPool.settings")
django.setup()
from proxy_api.models import Fetcher, Proxy


class BaseFetcher(object):
    """
    所有爬取器的基类
    """

    fetch_gap = 60  # 30*60

    def __init__(self, fetcher) -> None:
        self.proxies = []
        self.fetcher = fetcher

    def fetch(self):
        """
        执行一次爬取，返回一个数组，每个元素是(protocol, ip, port)，portocal是协议名称，目前主要为http
        返回示例：[('http', '127.0.0.1', 8080), ('http', '127.0.0.1', 1234)]
        """
        raise NotImplementedError()

    def run(self):
        log(f"{self.__class__.__name__} 爬取器开始运行...")
        try:
            self.fetch()
        except Exception:
            log(f"{self.__class__.__name__}运行爬取器出现异常:\n {traceback.format_exc()}", 1)
        else:
            self.save_proxies()
        self.update_fetcher()

    def save_proxies(self):
        def check(proxy):
            if len(proxy) == 3:
                protocol, ip, port = proxy
            else:
                protocol, ip, port, _, _ = proxy

            if protocol and ip and port:
                try:
                    int(port)
                except Exception:
                    pass
                else:
                    if not Proxy.objects.filter(ip=ip, port=port, protocol=protocol).exists():
                        return True
            return False

        saved = 0
        for proxy in self.proxies:
            #  验证代理必要字段
            if check(proxy):
                proxy_obj = Proxy()

                # 设置代理数据库对象各个字段值
                if len(proxy) == 3:
                    proxy_obj.protocol, proxy_obj.ip, proxy_obj.port = proxy
                    proxy_obj.username, proxy_obj.password = "", ""
                else:
                    proxy_obj.protocol, proxy_obj.ip, proxy_obj.port, proxy_obj.username, proxy_obj.password = proxy
                proxy_obj.fetcher = self.fetcher

                # 保存到数据库
                try:
                    proxy_obj.save()
                    saved += 1
                except Exception as e:
                    log(f"{self.__class__.__name__} 保存代理出现异常{proxy}:{e}", 1)
        # 设置代理数量
        self.fetcher.last_proxies_amount = len(self.proxies)
        log(f"{self.__class__.__name__} 完成: {saved}/{len(self.proxies)}", 4)

    def update_fetcher(self):
        self.fetcher.last_fetch_time = time.time()
        self.fetcher.save()
