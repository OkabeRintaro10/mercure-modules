import requests

response = requests.get("127.0.0.1:80/")
print(response.json())
