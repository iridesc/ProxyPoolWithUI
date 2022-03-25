
import time
from datetime import  datetime
import matplotlib.pyplot as plt

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProxyPool.settings")
django.setup()
from proxy_api.models import Fetcher, StatusRecode
import matplotlib.dates as mdates


def get_data():
    recodes = StatusRecode.objects.filter(time__gt = time.time() - 24*60*60*7)
    fetchers = Fetcher.objects.all()

    times = []
    fetcher_amounts = []
    proxy_amounts = []
    active_proxy_amounts = []
    for recode in recodes:
        # 时间轴
        times.append(datetime.fromtimestamp(recode.time))

        # 数据轴
        fetcher_amounts.append(recode.fetcher_amount)
        proxy_amounts.append(recode.proxy_amount)
        active_proxy_amounts.append(recode.active_proxy_amount)
        # proxy_amounts.append(recode.proxy_amount)
        # active_proxy_amounts.append(recode.active_proxy_amount)
        # .append(recode.)
        # .append(recode.)
        # .append(recode.)
        # .append(recode.)
    show(times, proxy_amounts)
    show(times, active_proxy_amounts)
    show(times, fetcher_amounts)


def show(times,y_data):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    # 指定X轴的以日期格式（带小时）显示
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m%d%H'))
    # X轴的间隔为小时
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xlabel('Time')
    plt.ylabel('Data Amount')

    plt.gcf().autofmt_xdate()
    # plt.title(title)
    plt.plot(times, y_data, "b+")
    # plt.xticks(rotation=90)
    plt.show()


if __name__ == "__main__":
    get_data()

