import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProxyPool.settings")
django.setup()
from proxy_api.models import Fetcher

from fetchers import fetchers

def init():
    """
    初始化数据库
    """   
    # 注册所有的爬取器
    for item in fetchers:
        if not Fetcher.objects.filter(name = item.name).exists():
            fetcher = Fetcher()
            fetcher.name = item.name
            fetcher.save()
