import http.client
import requests

conn = http.client.HTTPSConnection("api.sunnah.com")

payload = "{}"

headers = { 'x-api-key': "SqD712P3E82xnwOAEOkGd5JZH8s9wRR24TqNFzjk" }

conn.request("GET", "/v1/hadiths/random", payload, headers)

res = conn.getresponse()



url = "https://api.sunnah.com/v1/hadiths"

payload = "{}"
headers = {'x-api-key': 'SqD712P3E82xnwOAEOkGd5JZH8s9wRR24TqNFzjk'}

response = requests.request("GET", url, data=payload, headers=headers)

print(response.text)