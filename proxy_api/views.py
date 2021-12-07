import json
import time
import random
from django.shortcuts import render
from django.forms.models import model_to_dict
from proxy_api.models import Fetcher, Proxy
from django.http import HttpResponse, JsonResponse
from config import VALIDATE_TIMEOUT
# Create your views here.


def get_pool_status():
    ret_data = dict()
    all_proxy_query_set = Proxy.objects.all()
    validated_proxy_query_set = all_proxy_query_set.filter(validated=True)
    oversea_proxy_query_set = validated_proxy_query_set.filter(latency_oversea__lt=VALIDATE_TIMEOUT*1000)
    cn_proxy_query_set = validated_proxy_query_set.filter(latency_cn__lt=VALIDATE_TIMEOUT*1000)

    ret_data["proxy_amount"] = all_proxy_query_set.count()
    ret_data["need_validate_proxy_amount"] = Proxy.objects.filter(to_validate_time__lt=time.time()).count() 
    ret_data["need_validate_proxy_ratio"] = round(ret_data["need_validate_proxy_amount"]/ret_data["proxy_amount"]*100, 2) if ret_data["proxy_amount"] else 0
    ret_data["validated_proxy_amount"] = validated_proxy_query_set.count()
    ret_data["validated_proxy_ratio"] = round(ret_data["validated_proxy_amount"]/ret_data["proxy_amount"]*100, 2) if ret_data["proxy_amount"] else 0

    ret_data["oversea_proxy_amount"] = oversea_proxy_query_set.count()
    ret_data["oversea_proxy_ratio"] = round(ret_data["oversea_proxy_amount"]/ret_data["validated_proxy_amount"]*100, 2) if ret_data["validated_proxy_amount"] else 0

    ret_data["cn_proxy_amount"] = cn_proxy_query_set.count()
    ret_data["cn_proxy_ratio"] = round(ret_data["cn_proxy_amount"]/ret_data["validated_proxy_amount"]*100, 2) if ret_data["validated_proxy_amount"] else 0

    return ret_data


def home(request):
    return JsonResponse(get_pool_status())


def api(request):
    ret_data = {
        "suc": False,
        "msg":"None",
    }
    if request.method == "POST":
        try:
            req_data = json.loads(request.body.decode())
        except Exception as e:
            ret_data["msg"] = "JSONDecodeError"
        else:
            reason = req_data.get("reason")
            if reason is None:
                ret_data["msg"] = "ReasonIsRequired"

            elif reason == "GetPoolStatus":
                ret_data.update(get_pool_status())
                ret_data["suc"] = True

            elif reason == "GetOneRandomProxy":
                query_set = Proxy.objects.filter(validated=True)

                accessable_area = req_data.get("accessable_area")
                if accessable_area == "oversea":
                    query_set = query_set.filter(latency_oversea__lt=VALIDATE_TIMEOUT*1000)
                else:
                    query_set = query_set.filter(latency_cn__lt=VALIDATE_TIMEOUT*1000)

                pool_size = query_set.count()
                random_index = random.randint(0, pool_size-1 if pool_size else pool_size)
                ret_data["proxy"] = model_to_dict(query_set[random_index]) if pool_size else None
                ret_data["pool_size"] = pool_size
                ret_data["suc"] = True
            else:
                ret_data["msg"] = "UnknownReason"
    return JsonResponse(ret_data)
