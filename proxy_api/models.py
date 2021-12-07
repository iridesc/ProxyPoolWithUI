from django.db import models
from django.db.models.fields import CharField

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
    sum_proxies_amount = models.IntegerField(default=0)
    last_proxies_amount = models.IntegerField(default=0)
    last_fetch_time = models.FloatField(default=0)


class Proxy(models.Model):
    fetcher = models.ForeignKey(Fetcher, on_delete=models.CASCADE)
    protocol = models.CharField(max_length=16, choices=PROTOCOL_CHOICES)
    ip = models.CharField(max_length=16)
    port = models.IntegerField()
    validated = models.BooleanField(default=False)
    latency_cn = models.FloatField(default=0)
    latency_oversea = models.FloatField(default=0)

    validate_time = models.FloatField(default=0)
    to_validate_time = models.FloatField(default=0)
    validate_failed_count = 0

