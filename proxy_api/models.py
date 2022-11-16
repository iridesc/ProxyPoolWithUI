from django.db import models
from django.db.models import Min, Avg
import  json
import time


# Create your models here.

PROTOCOL_CHOICES = (
    ("socks4", "socks4"),
    ("socks5", "socks5"),
    ("http", "http"),
    ("https", "https"),
)


class Fetcher(models.Model):
    name = models.CharField(max_length=64, db_index=True, primary_key=True)
    enable = models.BooleanField(default=True)
    # sum_proxies_amount = models.IntegerField(default=0)
    last_proxies_amount = models.IntegerField(default=0)
    last_fetch_time = models.FloatField(default=0)


class Proxy(models.Model):
    fetcher = models.ForeignKey(Fetcher, on_delete=models.CASCADE)
    protocol = models.CharField(max_length=16, choices=PROTOCOL_CHOICES)
    ip = models.CharField(max_length=16)
    port = models.IntegerField()
    username = models.CharField(max_length=256, null=False, blank=True)
    password = models.CharField(max_length=256, null=False, blank=True)
    validated = models.BooleanField(default=False)
    latency_cn = models.FloatField(default=0)
    latency_oversea = models.FloatField(default=0)
    validate_time = models.FloatField(default=0)
    to_validate_time = models.FloatField(default=0)
    validate_failed_count = models.IntegerField(default=0)


class StatusRecode(models.Model):
    time = models.FloatField()
    fetchers_infos = models.TextField()

    fetcher_amount = models.IntegerField()
    proxy_amount = models.IntegerField()
    active_proxy_amount = models.IntegerField()

    @staticmethod
    def make_recode():
        all_fetcher_query_set = Fetcher.objects.all()
        all_proxy_query_set = Proxy.objects.all()
        active_proxy_query_set = all_proxy_query_set.filter(validated = True)

        recode = StatusRecode()
        recode.time = time.time()
        recode.fetcher_amount = all_fetcher_query_set.count()
        recode.proxy_amount = all_proxy_query_set.count()
        recode.active_proxy_amount = active_proxy_query_set.count()

        fetchers_infos = dict()
        for fetcher in all_fetcher_query_set:
            fetcher_active_proxy_query_set = active_proxy_query_set.filter(fetcher=fetcher)
            fetchers_infos[fetcher.name] = {
                "amount": all_proxy_query_set.filter(fetcher=fetcher).count(),
                "active_amount": fetcher_active_proxy_query_set.count(),

                "min_latency_cn": fetcher_active_proxy_query_set.aggregate(Min("latency_cn")),
                "avg_latency_cn": fetcher_active_proxy_query_set.aggregate(Avg("latency_cn")),

                "min_latency_oversea": fetcher_active_proxy_query_set.aggregate(Min("latency_oversea")),
                "avg_latency_oversea": fetcher_active_proxy_query_set.aggregate(Avg("latency_oversea")),
            }

        recode.fetchers_infos = json.dumps(fetchers_infos, ensure_ascii=False, indent=2)
        recode.save()
