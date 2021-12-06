from django.shortcuts import render
from proxy_api.models import Fetcher, Proxy
from django.http import HttpResponse
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
    if request.method == "POST":
        print()


    return render()
