import sys
import os
import requests
sys.path.append(os.path.dirname(__file__) + os.sep + '../')
from config import VALIDATE_TARGETS

for target in VALIDATE_TARGETS:
    url = target["url"]
    codes = target["codes"]
    print("--"*10)
    print(url)
    print(codes)
    r = requests.get(target["url"])
    print(r.status_code in codes)
