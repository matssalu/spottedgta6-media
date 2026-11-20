"""Find viral moments in a Twitch VOD from its chat replay (chat speed + hype words), via Twitch's public GQL.

usage: python3 chatpeaks.py <vod_id> <start_s> <end_s> <out.json> [--top 15] [--gap 120] [--workers 8]
Score per 10-second bucket = messages + 2 * hype messages (LUL/KEKW/LMAO/NAH/😂/💀/"clip it"...),
normalised against the rolling median of the surrounding 10 minutes, so busy periods don't dominate.
Writes the top moments: [{t, score, msgs, sample}] with t = VOD second where the spike starts.
"""
import argparse, json, re, statistics, urllib.request
from concurrent.futures import ThreadPoolExecutor

HASH = "b70a3591ff0f4e0313d126c6a1502d79a1c02baebb288227c582044aa76adf6a"
HYPE = re.compile(r"(lul|kekw|omegalul|lmao|lmfao|icant|i can't|nah+|bro+|💀|😭|😂|🤣|clip|w+$|ww+|pog|holy|wtf|no way|deadass|aint no way|ayo|💀)", re.I)


def gql(var):
    body = json.dumps([{"operationName": "VideoCommentsByOffsetOrCursor", "variables": var,
                        "extensions": {"persistedQuery": {"version": 1, "sha256Hash": HASH}}}]).encode()
    r = urllib.request.Request("https://gql.twitch.tv/gql", data=body,
                               headers={"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko", "Content-Type": "text/plain"})
    for _ in range(3):
        try:
            return json.load(urllib.request.urlopen(r, timeout=20))[0]["data"]["video"]["comments"]
        except Exception:
            pass
    return None


def segment(args):
    vod, a, b = args
    out, var = [], {"videoID": vod, "contentOffsetSeconds": a}
    for _ in range(400):
        c = gql(var)
        if not c or not c["edges"]:
            break
        for e in c["edges"]:
            n = e["node"]
            t = n["contentOffsetSeconds"]
            if a <= t < b:
                out.append((t, "".join(f.get("text") or "" for f in n["message"]["fragments"])))
        last = c["edges"][-1]
        if last["node"]["contentOffsetSeconds"] >= b or not c.get("pageInfo", {}).get("hasNextPage", True):
            break
        var = {"videoID": vod, "cursor": last["cursor"]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vod"); ap.add_argument("start", type=int); ap.add_argument("end", type=int); ap.add_argument("out")
    ap.add_argument("--top", type=int, default=15); ap.add_argument("--gap", type=int, default=120)
    ap.add_argument("--workers", type=int, default=8); ap.add_argument("--seg", type=int, default=300)
    a = ap.parse_args()
    segs = [(a.vod, s, min(s + a.seg, a.end)) for s in range(a.start, a.end, a.seg)]
    msgs = []
    with ThreadPoolExecutor(a.workers) as ex:
        for part in ex.map(segment, segs):
            msgs += part
    msgs.sort()
    B = 10
    nb = (a.end - a.start) // B + 1
    cnt, hyp, txt = [0] * nb, [0] * nb, [[] for _ in range(nb)]
    for t, m in msgs:
        ms = m.strip()
        # ignore bot commands and poll votes ("!shoe", "1", "2") - they spike without anything funny happening
        if ms.startswith("!") or re.fullmatch(r"[\d\s]+", ms) or "giveaway" in ms.lower():
            continue
        i = (t - a.start) // B
        if 0 <= i < nb:
            cnt[i] += 1
            if HYPE.search(m):
                hyp[i] += 1
            if len(txt[i]) < 6:
                txt[i].append(m[:40])
    raw = [cnt[i] + 3 * hyp[i] for i in range(nb)]
    # 30-second smoothed score vs. 10-minute rolling median
    sm = [sum(raw[max(0, i - 1):i + 2]) for i in range(nb)]
    score = []
    for i in range(nb):
        win = sm[max(0, i - 30):i + 30]
        med = statistics.median(win) if win else 0
        score.append((sm[i] - med) / (med + 5))
    order = sorted(range(nb), key=lambda i: -score[i])
    picked = []
    for i in order:
        t = a.start + i * B
        if all(abs(t - p["t"]) > a.gap for p in picked):
            picked.append({"t": t, "score": round(score[i], 2), "msgs": sm[i], "sample": txt[i] + txt[min(i + 1, nb - 1)]})
        if len(picked) >= a.top:
            break
    json.dump({"vod": a.vod, "messages": len(msgs), "moments": picked}, open(a.out, "w"), indent=1, ensure_ascii=False)
    print(len(msgs), "messages")
    for p in picked:
        print(p["t"], p["score"], p["msgs"], p["sample"][:4])


if __name__ == "__main__":
    main()
