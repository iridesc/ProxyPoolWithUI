import requests
r = requests.post("http://127.0.0.1:8000/api/", json={"reason":"GetOneRandomProxy"})
print(r.json())