from django.contrib import admin
from proxy_api.models import Fetcher, Proxy, StatusRecode


@admin.register(Fetcher)
class FetcherAdmin(admin.ModelAdmin):
    list_display = ("enable", "name", "last_fetch_time")
    # search_fields = ("ip_asset_port_id", "ip_asset__ip", "task__customer_name", "domain_title", "man_domain_title",
    #                  "task__task_id")
    # list_filter = ("active", "url_active", "is_web_service", "abnormal_web_status", "abnormal_web_type",
    #                "identify_reason_status")
    # list_display_links = ("ip_asset_port_id", "port")
    # raw_id_fields = ("task", "ip_asset")

@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = ("fetcher", "protocol", "ip", "port", "validated", "latency_cn", "validate_time", "to_validate_time", "validate_failed_count")

@admin.register(StatusRecode)
class StatusRecodeAdmin(admin.ModelAdmin):
    list_display = ("time", "fetcher_amount", "proxy_amount", "active_proxy_amount")

