from urllib.parse import urljoin

import httpx
import m3u8

headers = {"Referer": "https://www.rctiplus.com/"}

res = httpx.get(
    "https://zeus.rcti.plus/video/live/api/v1/live/2/url?appierid=null",
    headers={
        "Referer": "https://www.rctiplus.com/",
        "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWQiOjgyMjY2ODUsInBsIjoid2ViIiwiZGV2aWNlX2lkIjoid2ViLTY3M2M2OTBjMGQ0Y2IiLCJsdHlwZSI6ImVtYWlsIiwianRpIjoiZjE2Mzg3ZDQtYjE2OS00ZDg3LWIwYzAtYTk4MDkxYjVhYjA4IiwiaWF0IjoxNzMyMDEyMzAwfQ.qu8DtyVVj1He911SMVMsjIkhDfaxQ525Nr_BKYGd_gs",
        "apikey": "k1DzR0yYWIyZgvTvixiDHnb4Nl08wSU0",
    },
)

url = res.json()["data"]["url"]

res = httpx.get(url, headers=headers)

clean_path = url.rsplit("/", 1)[0]

print(clean_path)

pl = m3u8.loads(res.text)
# print(pl.dumps())

child_url = urljoin(clean_path, pl.playlists[0].uri)
print(child_url)

res = httpx.get(child_url, headers=headers)

pl2 = m3u8.loads(res.text)

for i in pl2.segments:
    i.uri = urljoin(clean_path, i.uri)
    print(i.uri)

# pl2.base_path = clean_path + "/"
print(pl2.dumps())
