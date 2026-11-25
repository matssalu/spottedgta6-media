"""Style v4: bigger facecam on top (auto-detected face), gameplay below, TikTok white-box title on the seam,
word-by-word captions on the gameplay, auto-trimmed to a max length that keeps the loudest moment.
usage: python3 render4.py spec.json
spec keys: src, title, out, optional: start, end, cam [x,y,w,h fractions, overrides face detect], cam_h (default 900),
           max_len (default 25), captions (default true), words (path to words.json, default <src>.words.json)
"""
import json, subprocess, sys, os, statistics
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tiktitle import render as title_png

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.join(HERE, "fonts")


def even(x):
    return int(x) // 2 * 2


def probe(src):
    d = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                            "stream=width,height:format=duration", "-of", "json", src]))
    return d["streams"][0]["width"], d["streams"][0]["height"], float(d["format"]["duration"])


def find_face(src, sw, sh, dur, t0, t1):
    """Return (cx, cy, fh) of the streamer's face in source pixels, using the most stable detection cluster."""
    casc = cv2.CascadeClassifier(os.path.join(HERE, "haarcascade_frontalface_default.xml"))
    cap = cv2.VideoCapture(src)
    hits = []
    for t in np.linspace(t0 + 0.5, t1 - 0.5, 12):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        if not ok:
            continue
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        for (x, y, w, h) in casc.detectMultiScale(g, 1.08, 5, minSize=(int(sh * 0.03), int(sh * 0.03))):
            hits.append((x + w / 2, y + h / 2, h))
    cap.release()
    if not hits:
        return None
    # cluster by position (streamer face barely moves; NPC faces do)
    best, bestn = None, 0
    for c in hits:
        grp = [h for h in hits if abs(h[0] - c[0]) < sw * 0.06 and abs(h[1] - c[1]) < sh * 0.08]
        if len(grp) > bestn:
            best, bestn = grp, len(grp)
    if bestn < 3:
        return None
    return (statistics.median(g[0] for g in best), statistics.median(g[1] for g in best),
            statistics.median(g[2] for g in best))


def cam_box(face, sw, sh, cam_h, mult=4.2):
    ar = W / cam_h
    cx, cy, fh = face
    h = min(sh, fh * mult)
    w = h * ar
    if w > sw:
        w = sw; h = w / ar
    x = min(max(0, cx - w / 2), sw - w)
    y = min(max(0, cy - h * 0.42), sh - h)
    return [even(w), even(h), even(x), even(y)]


def loud_peak(src, t0, t1):
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", src, "-ac", "1", "-ar", "8000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(out, dtype=np.int16).astype(np.float32)
    if len(a) < 8000:
        return t0
    win = 4000
    rms = np.sqrt(np.convolve(a ** 2, np.ones(win) / win, mode="valid"))
    return t0 + float(np.argmax(rms)) / 8000


def pick_window(src, words, dur, start, end, max_len):
    t0 = start if start is not None else 0.0
    t1 = end if end is not None else dur
    if start is None and words:
        first = next((w["start"] for w in words if w["start"] >= 0), 0)
        t0 = max(0.0, first - 0.3)
    if t1 - t0 > max_len:
        pk = loud_peak(src, t0, t1)
        if pk - t0 > max_len * 0.8:
            t0 = pk - max_len * 0.8
        t1 = t0 + max_len
        # end on a word boundary if possible
        ends = [w["end"] for w in words if t1 - 3 < w["end"] <= t1]
        if ends:
            t1 = min(max(ends) + 0.4, t0 + max_len)
    return round(t0, 2), round(min(t1, dur), 2)


BAD = {"FUCK": "F*CK", "FUCKING": "F*CKING", "SHIT": "SH*T", "BITCH": "B*TCH", "NIGGA": "N*GGA", "NIGGAS": "N*GGAS",
       "FUCKED": "F*CKED", "MOTHERFUCKER": "MOTHERF*CKER", "PUSSY": "P*SSY", "DICK": "D*CK", "ASS": "A*S"}


def censor(txt):
    import re
    return re.sub(r"[A-Za-z']+", lambda m: BAD.get(m.group(0).upper(), m.group(0)), txt)


def ass_time(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def write_ass(words, t0, t1, path, y):
    lines = []
    chunk = []
    for w in words:
        if w["end"] <= t0 or w["start"] >= t1:
            continue
        chunk.append(w)
        txt = w["word"].strip()
        if len(chunk) >= 3 or txt.endswith((".", "?", "!", ",")):
            lines.append(chunk); chunk = []
    if chunk:
        lines.append(chunk)
    ev = []
    for i, ch in enumerate(lines):
        s = ch[0]["start"] - t0
        e = (lines[i + 1][0]["start"] - t0) if i + 1 < len(lines) else ch[-1]["end"] - t0 + 0.3
        e = min(e, ch[-1]["end"] - t0 + 0.6)
        txt = " ".join(x["word"].strip() for x in ch).upper().replace("{", "").replace("}", "")
        txt = censor(txt)
        ev.append(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Cap,,0,0,0,,{{\\fscx85\\fscy85\\t(0,90,\\fscx100\\fscy100)}}{txt}")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,TikTok Sans,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,2,8,60,60,{y},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(path, "w").write(head + "\n".join(ev) + "\n")
    return len(ev)


def main():
    sp = json.load(open(sys.argv[1]))
    src = sp["src"]
    sw, sh, dur = probe(src)
    cam_h = sp.get("cam_h", 900)
    game_h = H - cam_h
    wpath = sp.get("words", os.path.splitext(src)[0] + ".words.json")
    words = json.load(open(wpath)) if os.path.exists(wpath) else []
    if isinstance(words, dict):
        words = words.get("words", [])
    words = [{"word": w.get("word", w.get("w", "")), "start": w.get("start", w.get("s", 0)), "end": w.get("end", w.get("e", 0))}
             for w in words]
    t0, t1 = pick_window(src, words, dur, sp.get("start"), sp.get("end"), sp.get("max_len", 25))
    if "cam" in sp:
        cx, cy, cw, ch = sp["cam"]
        face = (sw * (cx + cw / 2), sh * (cy + ch * 0.45), sh * ch / 4.2)
    else:
        face = find_face(src, sw, sh, dur, t0, t1)
        if face is None:
            print("NOFACE", src, flush=True)
            sys.exit(3)
    cam = cam_box(face, sw, sh, cam_h, sp.get("cam_mult", 4.2))
    gw = even(min(sw, sh * W / game_h))
    gx = even(min(max(0, (sw - gw) / 2 + sp.get("game_shift", 0) * sw), sw - gw))
    tpng = sp["out"] + ".title.png"
    tw, th = title_png(sp["title"], tpng, size=sp.get("title_size", 68), maxw=960)
    ty = even(cam_h - th * 0.55)
    vf_caps = ""
    if sp.get("captions", True) and words:
        apath = sp["out"] + ".ass"
        if write_ass(words, t0, t1, apath, y=cam_h + int(game_h * 0.62)):
            vf_caps = f",ass={apath}:fontsdir={FONTDIR}"
    d = t1 - t0
    if sp.get("layout") == "full":
        # one full-height 9:16 crop centred on the face (IRL / just-chatting moments)
        fw = even(min(sw, sh * W / H))
        fx = even(min(max(0, face[0] - fw / 2), sw - fw))
        ty = even(H * 0.30)
        vf_caps = ""
        if sp.get("captions", True) and words:
            apath = sp["out"] + ".ass"
            if write_ass(words, t0, t1, apath, y=int(H * 0.72)):
                vf_caps = f",ass={apath}:fontsdir={FONTDIR}"
        fc = (f"[0:v]crop={fw}:{sh}:{fx}:0,scale={W}:{H}:flags=lanczos[st];"
              f"[st][1:v]overlay=(W-w)/2:{ty}{vf_caps}[v];"
              f"[0:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    else:
      fc = (f"[0:v]split=2[a][b];"
            f"[a]crop={cam[0]}:{cam[1]}:{cam[2]}:{cam[3]},scale={W}:{cam_h}:flags=lanczos[cam];"
            f"[b]crop={gw}:{sh}:{gx}:0,scale={W}:{game_h}:flags=lanczos[game];"
            f"[cam][game]vstack[st];"
            f"[st][1:v]overlay=(W-w)/2:{ty}{vf_caps}[v];"
            f"[0:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    # captions use times relative to the cut, so seek with -ss before -i (timestamps reset to 0)
    extra_in = []
    if sp.get("overlay"):
        ow = sp.get("overlay_w", 640)
        oy = sp.get("overlay_y", int(H * 0.86))
        extra_in = ["-loop", "1", "-i", sp["overlay"]]
        fc = fc.replace("[v];", "[v0];", 1)
        fc += f";[2:v]scale={ow}:-1[lg];[v0][lg]overlay=(W-w)/2:{oy}:shortest=1[v]"
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.2f}", "-t", f"{d:.2f}", "-i", src, "-i", tpng, *extra_in,
           "-filter_complex", fc, "-map", "[v]", "-map", "[aout]", "-t", f"{d:.2f}", "-r", "30",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", sp["out"]]
    subprocess.run(cmd, check=True)
    for p in (tpng, sp["out"] + ".ass"):
        if os.path.exists(p):
            os.remove(p)
    print("ok", sp["out"], f"{t0}-{t1}", flush=True)


if __name__ == "__main__":
    main()
