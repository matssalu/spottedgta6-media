"""Nightly step 1: list the most-viewed Twitch clips of the last 24h per streamer, skip clips used before,
download the top N, transcribe them, and make a contact sheet per clip for review.
usage: python3 fetch.py <used_ids.txt> kaicenat:30 clix:12
writes: r/clips/<ch>_<id>.mp4, .words.json, _sheet.jpg and r/candidates.json
"""
import json, subprocess, sys, os, time

WORK = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WORK, "r", "clips")
os.makedirs(OUT, exist_ok=True)
used = set(open(sys.argv[1]).read().split()) if os.path.exists(sys.argv[1]) else set()


def list_clips(ch, rng):
    for _ in range(4):
        try:
            d = json.loads(subprocess.check_output(
                ["yt-dlp", "--flat-playlist", "-J", f"https://www.twitch.tv/{ch}/clips?filter=clips&range={rng}"],
                stderr=subprocess.DEVNULL, timeout=150))
            if d.get("entries"):
                return d["entries"]
        except Exception:
            pass
        time.sleep(4)
    return []


cands = []
for arg in sys.argv[2:]:
    ch, n = arg.split(":")
    es = list_clips(ch, "24h")
    if len(es) < int(n):
        es += [e for e in list_clips(ch, "7d") if e["id"] not in {x["id"] for x in es}
               and (e.get("timestamp") or 0) > time.time() - 3 * 86400]
    if len([e for e in es if e["id"] not in used]) < int(n) * 2:
        es += [e for e in list_clips(ch, "7d") if e["id"] not in {x["id"] for x in es}]
    since = float(os.environ.get("SINCE_TS", "0"))  # campaign start (unix time); older clips are not allowed
    es = [e for e in es if e["id"] not in used and (e.get("duration") or 0) >= 10 and (e.get("timestamp") or 0) >= since]
    es.sort(key=lambda e: -(e.get("view_count") or 0))
    got = 0
    for e in es:
        if got >= int(n):
            break
        f = os.path.join(OUT, f"{ch}_{e['id']}.mp4")
        if not os.path.exists(f):
            subprocess.run(["yt-dlp", "-q", "-o", f, e["url"]], timeout=180)
        if os.path.exists(f):
            got += 1
            cands.append({"file": f, "streamer": ch, "id": e["id"], "twitch_title": e.get("title"),
                          "views": e.get("view_count"), "duration": e.get("duration")})
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-vf", "fps=1/4,scale=320:-1,tile=4x2",
                            "-frames:v", "1", f[:-4] + "_sheet.jpg"])
subprocess.run([sys.executable, os.path.join(WORK, "transcribe.py")] + [c["file"] for c in cands])
for c in cands:
    w = c["file"][:-4] + ".words.json"
    c["transcript"] = " ".join(x["w"] for x in json.load(open(w))) if os.path.exists(w) else ""
json.dump(cands, open(os.path.join(WORK, "r", "candidates.json"), "w"), indent=1, ensure_ascii=False)
print(len(cands), "candidates")
for c in cands:
    print(c["streamer"], c["id"], c["views"], round(c["duration"] or 0), "|", c["twitch_title"], "|", c["transcript"][:200])
