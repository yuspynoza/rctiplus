from urllib.parse import urljoin

import httpx
import m3u8
from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse

app = FastAPI()


def get_m3u8(url: str):
    res = httpx.get(url, headers={"Referer": "https://www.rctiplus.com/"})
    if res.text == "":
        return ""
    clean_path = url.rsplit("/", 1)[0]

    playlist = m3u8.loads(res.text)

    if len(playlist.playlists) != 0:
        for pl in playlist.playlists:
            pl.uri = urljoin(clean_path, pl.uri)
    elif len(playlist.segments) != 0:
        for pl in playlist.segments:
            pl.uri = urljoin(clean_path, pl.uri)

    return playlist


def select_best_quality(playlist: m3u8.M3U8):
    resolutions = []

    for pl in playlist.playlists:
        resolutions.append(pl.stream_info.resolution[0])

    best = resolutions.index(max(resolutions))

    return playlist.playlists[best].uri


@app.get("/{name}", response_class=PlainTextResponse)
def channel(name: str):
    idx = 0

    if name == "rcti":
        idx = 1
    elif name == "mnctv":
        idx = 2
    elif name == "gtv":
        idx = 3
    elif name == "inews":
        idx = 4
    else:
        return ""

    res = httpx.get(
        f"https://zeus.rcti.plus/video/live/api/v1/live/{idx}/url?appierid=null",
        headers={
            "Referer": "https://www.rctiplus.com/",
            "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWQiOjgyMjY2ODUsInBsIjoid2ViIiwiZGV2aWNlX2lkIjoid2ViLTY3M2M2OTBjMGQ0Y2IiLCJsdHlwZSI6ImVtYWlsIiwianRpIjoiZjE2Mzg3ZDQtYjE2OS00ZDg3LWIwYzAtYTk4MDkxYjVhYjA4IiwiaWF0IjoxNzMyMDEyMzAwfQ.qu8DtyVVj1He911SMVMsjIkhDfaxQ525Nr_BKYGd_gs",
            "apikey": "k1DzR0yYWIyZgvTvixiDHnb4Nl08wSU0",
        },
    )

    a = get_m3u8(res.json()["data"]["url"])

    if isinstance(a, str):
        return a

    best_url = select_best_quality(a)

    b = get_m3u8(best_url)

    if b == "":
        return "not found"

    return Response(b.dumps(), media_type="application/vnd.apple.mpegurl")
