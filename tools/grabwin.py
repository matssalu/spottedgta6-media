"""Download short windows of a Twitch VOD (720p) without the rest.
usage: python3 grabwin.py <vod_id> <name> <t1,t2,...> [--pre 40 --post 20]
writes win/<name>_<t>.mp4 (window starts at t-pre)
"""
FMT="best[height<=1080]/best"
import argparse, os, subprocess, sys, tempfile, urllib.request
from concurrent.futures import ThreadPoolExecutor


def playlist(vod):
    global FMT
    url = subprocess.check_output([sys.executable, "-m", "yt_dlp", "-g", "-f", FMT,
                                   f"https://www.twitch.tv/videos/{vod}"], stderr=subprocess.DEVNULL).decode().split()[0]
    txt = urllib.request.urlopen(url, timeout=30).read().decode()
    base = url.rsplit("/", 1)[0]
    segs, t, d, init = [], 0.0, 0, None
    for l in txt.splitlines():
        if l.startswith("#EXT-X-MAP"):
            init = l.split('URI="')[1].split('"')[0]
        if l.startswith("#EXTINF"):
            d = float(l[8:].rstrip(","))
        elif l and not l.startswith("#"):
            segs.append((t, d, l)); t += d
    return base, init, segs


def get(url):
    for _ in range(4):
        try:
            return urllib.request.urlopen(url, timeout=60).read()
        except Exception:
            pass
    return b""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vod"); ap.add_argument("name"); ap.add_argument("times")
    ap.add_argument("--pre", type=float, default=40); ap.add_argument("--post", type=float, default=20); ap.add_argument("--fmt", default="best[height<=720]/best")
    a = ap.parse_args()
    global FMT; FMT = a.fmt
    base, init, segs = playlist(a.vod)
    os.makedirs("win", exist_ok=True)
    initb = get(f"{base}/{init}") if init else b""
    for t in [float(x) for x in a.times.split(",")]:
        s0, s1 = t - a.pre, t + a.post
        sel = [s for s in segs if s[0] + s[1] > s0 and s[0] < s1]
        if not sel:
            continue
        with ThreadPoolExecutor(8) as ex:
            parts = list(ex.map(lambda s: get(f"{base}/{s[2]}"), sel))
        tmp = tempfile.mktemp(suffix=".mp4" if init else ".ts")
        open(tmp, "wb").write(initb + b"".join(parts))
        off = s0 - sel[0][0]
        out = f"win/{a.name}_{int(t)}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, off):.2f}", "-i", tmp, "-t", f"{s1 - s0:.2f}",
                        "-c", "copy", out])
        os.remove(tmp)
        print(out, flush=True)


if __name__ == "__main__":
    main()
