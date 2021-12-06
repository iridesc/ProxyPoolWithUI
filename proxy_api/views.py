import json
import random
from django.shortcuts import render
from django.forms.models import model_to_dict
from proxy_api.models import Fetcher, Proxy
from django.http import HttpResponse, JsonResponse
# Create your views here.


def make_proxies_html():
    line_html = ""
    for proxy in Proxy.objects.all().order_by("-validated"):
        line_html += f'''<tr>
        <td>{proxy.fetcher.name}</td>
        <td>{proxy.validated}</td>
        <td>{proxy.protocol}</td>
        <td>{proxy.ip}</td>
        <td>{proxy.port}</td>
        <td>{proxy.latency}</td>
        </tr>'''
    return f'<table border="1">{line_html}</table>'


def make_fetchers_html():
    return ""


def home(request):

    with open("proxy_api/templates/index.html") as f:
        template = f.read()

    template = template.format(proxies_html=make_proxies_html(), fetcher_html=make_fetchers_html())

    return HttpResponse(template)


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
            elif reason == "GetOneRandomProxy":
                query_set = Proxy.objects.filter(validated = True)
                amount = query_set.count()
                random_index = random.randint(0, amount-1 if amount else amount) 
                ret_data["proxy"] = model_to_dict(query_set[random_index]) if amount else None
                ret_data["suc"] = True
            else:
                ret_data["msg"] = "UnknownReason"
    return JsonResponse(ret_data)
