"""Scan a Twitch VOD's audio for hype peaks (sudden loudness bursts) without downloading the video.

usage: python3 peaks.py <vod_id> <start_s> <end_s> <out_prefix> [--top 8] [--gap 180]
Writes <out_prefix>_peaks.json: [{t, score}] with t = absolute VOD second.
"""
import argparse, json, subprocess, sys, os, tempfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import urllib.request


def playlist(vod, fmt):
    url = subprocess.check_output([sys.executable, "-m", "yt_dlp", "-g", "-f", fmt,
                                   f"https://www.twitch.tv/videos/{vod}"], stderr=subprocess.DEVNULL).decode().split()[0]
    txt = urllib.request.urlopen(url, timeout=30).read().decode()
    base = url.rsplit("/", 1)[0]
    segs, t, d = [], 0.0, 0
    init = None
    for l in txt.splitlines():
        if l.startswith("#EXT-X-MAP"):
            init = l.split('URI="')[1].split('"')[0]
        if l.startswith("#EXTINF"):
            d = float(l[8:].rstrip(","))
        elif l and not l.startswith("#"):
            segs.append((t, d, l)); t += d
    return base, init, segs


def fetch(base, name, dest):
    for _ in range(3):
        try:
            with urllib.request.urlopen(f"{base}/{name}", timeout=60) as r, open(dest, "wb") as f:
                f.write(r.read())
            return
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vod"); ap.add_argument("start", type=float); ap.add_argument("end", type=float); ap.add_argument("out")
    ap.add_argument("--top", type=int, default=8); ap.add_argument("--gap", type=float, default=180)
    a = ap.parse_args()
    base, init, segs = playlist(a.vod, "audio_only/bestaudio/worst")
    segs = [s for s in segs if a.start <= s[0] < a.end]
    tmp = tempfile.mkdtemp()
    names = []
    with ThreadPoolExecutor(12) as ex:
        for i, (t, d, n) in enumerate(segs):
            p = os.path.join(tmp, f"{i:05d}.seg"); names.append(p)
            ex.submit(fetch, base, n, p)
    raw = os.path.join(tmp, "all.bin")
    with open(raw, "wb") as f:
        if init:
            fetch(base, init, os.path.join(tmp, "init")); f.write(open(os.path.join(tmp, "init"), "rb").read())
        for p in names:
            if os.path.exists(p):
                f.write(open(p, "rb").read())
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", raw, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    n = len(x) // 8000
    db = 20 * np.log10(np.sqrt((x[: n * 8000].reshape(n, 8000) ** 2).mean(1) + 1e-9))
    db = np.maximum(db, -50)
    s = np.convolve(db, np.ones(3) / 3, mode="same")
    # local baseline: rolling median over 5 min
    k = 300
    base_l = np.array([np.median(s[max(0, i - k):i + k]) for i in range(0, n)])
    print("coverage dB>-49:", float((db > -49).mean()), "secs", n, file=sys.stderr)
    score = s - base_l
    # sustain bonus: loud for several seconds
    score = np.convolve(score, np.ones(4) / 4, mode="same")
    order = np.argsort(-score)
    picks = []
    for i in order:
        if score[i] <= 0:
            break
        if all(abs(i - p) >= a.gap for p in picks):
            picks.append(int(i))
        if len(picks) >= a.top:
            break
    res = [{"t": round(a.start + p, 1), "score": round(float(score[p]), 2)} for p in sorted(picks)]
    json.dump(res, open(f"{a.out}_peaks.json", "w"), indent=1)
    print(json.dumps(res))
    subprocess.run(["rm", "-rf", tmp])


if __name__ == "__main__":
    main()
