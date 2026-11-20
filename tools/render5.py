"""Style v5 (Nov 20 feedback): payoff-first cold open, hook text in the top third, word-by-word captions mid-frame,
12-25 s with dead air cut out, facecam top ~38%, gameplay bottom ~62%, punch-in zoom + SFX on the key beat,
end on the punchline, -14 LUFS, clean high-bitrate 30 fps export.

usage: python3 render5.py spec.json
spec: src, out, hook (4-8 words), start, end (moment window in the source, seconds),
      climax (source second of the biggest beat; default = loudest point), cam [x,y,w,h] fractions (or auto face),
      optional: captions (true), cold_open (true), overlay (png that must stay visible, e.g. KreekCraft logo),
      overlay_w (620), game_shift (0), cam_mult (4.2), max_len (25), words (path to words.json)
"""
import json, os, re, subprocess, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tiktitle import render as title_png
import render4 as r4

W, H, CAM_H = 1080, 1920, 730
FPS = 30


def run(cmd):
    subprocess.run(cmd, check=True)


def silences(path, noise="-33dB", dur=0.55):
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", f"silencedetect=noise={noise}:d={dur}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(s, e + [None] * (len(s) - len(e))))


def keep_ranges(seg_len, sil, climax, pad=0.18):
    """Pieces of [0, seg_len] to keep: drop silent stretches (minus padding) longer than ~0.4 s, never around the climax."""
    cuts = []
    for a, b in sil:
        b = seg_len if b is None else b
        a2, b2 = a + pad, b - pad
        if b2 - a2 >= 0.4 and not (a2 - 1.0 < climax < b2 + 1.0):
            cuts.append((a2, b2))
    keep, t = [], 0.0
    for a, b in cuts:
        if a > t:
            keep.append((t, a))
        t = b
    if t < seg_len:
        keep.append((t, seg_len))
    return [(round(a, 3), round(b, 3)) for a, b in keep if b - a > 0.25]


def map_time(t, keep, offset):
    """segment time -> final timeline time (None if cut)."""
    acc = offset
    for a, b in keep:
        if a <= t <= b:
            return acc + (t - a)
        acc += b - a
    return None


def ass_captions(words, keep, offset, path, y):
    """Word-by-word captions: 1-3 word groups, the word being spoken in yellow."""
    ws = []
    for w in words:
        s, e = map_time(w["start"], keep, offset), map_time(w["end"], keep, offset)
        if s is None or e is None:
            continue
        txt = r4.censor(w["word"].strip().upper().replace("{", "").replace("}", ""))
        if txt:
            ws.append((s, e, txt))
    groups, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 3 or re.search(r"[.?!,]$", w[2]) or len(" ".join(x[2] for x in cur)) > 16:
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    ev = []
    for gi, g in enumerate(groups):
        g_end = groups[gi + 1][0][0] if gi + 1 < len(groups) else g[-1][1] + 0.35
        g_end = min(g_end, g[-1][1] + 0.6)
        for wi, (s, e, _) in enumerate(g):
            s2 = s if wi else s
            e2 = g[wi + 1][0] if wi + 1 < len(g) else g_end
            parts = [("{\\c&H00F0FF&}" + t + "{\\c&HFFFFFF&}") if j == wi else t for j, (_, _, t) in enumerate(g)]
            pop = "{\\fscx88\\fscy88\\t(0,80,\\fscx100\\fscy100)}" if wi == 0 else ""
            ev.append(f"Dialogue: 0,{r4.ass_time(s2)},{r4.ass_time(max(e2, s2 + 0.05))},Cap,,0,0,0,,{pop}{' '.join(parts)}")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,TikTok Sans,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,3,8,90,140,{y},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(path, "w").write(head + "\n".join(ev) + "\n")
    return len(ev)


def sfx(path, kind, dur):
    if kind == "whoosh":
        expr = "(random(0)*2-1)*0.5*sin(PI*t/%f)" % dur
        af = f"highpass=f=600,lowpass=f=6000,volume=1.6"
    else:  # boom
        expr = "0.9*sin(2*PI*(60-25*t)*t)*exp(-5*t)"
        af = "lowpass=f=300,volume=2.2"
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"aevalsrc={expr}:s=48000:d={dur}", "-af", af, "-ac", "2", path])


def main():
    sp = json.load(open(sys.argv[1]))
    src, out = sp["src"], sp["out"]
    tmp = tempfile.mkdtemp(prefix="r5_")
    sw, sh, dur = r4.probe(src)
    wpath = sp.get("words", os.path.splitext(src)[0] + ".words.json")
    words = json.load(open(wpath)) if os.path.exists(wpath) else []
    words = [{"word": w.get("word", w.get("w", "")), "start": w.get("start", w.get("s", 0)), "end": w.get("end", w.get("e", 0))} for w in words]
    t0 = float(sp.get("start", 0)); t1 = float(sp.get("end", min(dur, t0 + 30)))
    climax = float(sp["climax"]) if "climax" in sp else r4.loud_peak(src, t0, t1)
    # ---- 1. base vertical composite of the window (cam top, game bottom, punch-in on the cam at the climax)
    if "cam" in sp:
        cx, cy, cw, ch = sp["cam"]
        face = (sw * (cx + cw / 2), sh * (cy + ch * 0.45), sh * ch / 4.2)
    else:
        face = r4.find_face(src, sw, sh, dur, t0, t1)
        if face is None:
            print("NOFACE", src); sys.exit(3)
    cam = r4.cam_box(face, sw, sh, CAM_H, sp.get("cam_mult", 4.2))
    # keep the face in the upper third of the cam panel so the hook text never covers it
    cam[3] = r4.even(min(max(0, face[1] - cam[1] * 0.33), sh - cam[1]))
    game_h = H - CAM_H
    gw = r4.even(min(sw, sh * W / game_h))
    gx = r4.even(min(max(0, (sw - gw) / 2 + sp.get("game_shift", 0) * sw), sw - gw))
    rc = climax - t0
    zp = (f"zoompan=z='if(between(it,{rc - 0.25:.2f},{rc + 1.6:.2f}),1.16,1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d=1:s={W}x{CAM_H}:fps={FPS}")
    base = os.path.join(tmp, "base.mp4")
    fc = (f"[0:v]fps={FPS},split=2[a][b];"
          f"[a]crop={cam[0]}:{cam[1]}:{cam[2]}:{cam[3]},scale={W}:{CAM_H}:flags=lanczos,{zp}[cam];"
          f"[b]crop={gw}:{sh}:{gx}:0,scale={W}:{game_h}:flags=lanczos[game];[cam][game]vstack[v];"
          f"[0:a]aresample=48000[a0]")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.2f}", "-t", f"{t1 - t0:.2f}", "-i", src, "-filter_complex", fc,
         "-map", "[v]", "-map", "[a0]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-c:a", "pcm_s16le",
         base.replace(".mp4", ".mov")])
    base = base.replace(".mp4", ".mov")
    seg_len = t1 - t0
    # ---- 2. timeline: cold open (payoff first), then the moment with dead air removed
    keep = keep_ranges(seg_len, silences(base), rc)
    total = sum(b - a for a, b in keep)
    max_len = sp.get("max_len", 27)
    if total > max_len:  # trim from the front, keep the ending (punchline)
        need = total - max_len
        while need > 0 and keep:
            a, b = keep[0]
            if b - a <= need:
                need -= b - a; keep.pop(0)
            else:
                keep[0] = (a + need, b); need = 0
    cold = []
    if sp.get("cold_open", True):
        ca, cb = max(0, rc - 0.5), min(seg_len, rc + 0.9)
        cold = [(ca, cb)]
    pieces = cold + keep
    offset = sum(b - a for a, b in cold)
    final_len = sum(b - a for a, b in pieces)
    # ---- 3. assemble
    parts, n = [], len(pieces)
    for i, (a, b) in enumerate(pieces):
        parts.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[a{i}]")
    cat = "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]"
    hook_png = os.path.join(tmp, "hook.png")
    tw, th = title_png(sp["hook"], hook_png, size=sp.get("hook_size", 80), maxw=980)
    hy = r4.even(CAM_H - th / 2)  # hook sits on the seam between cam and gameplay, below the face
    chain = f"[vc][1:v]overlay=(W-w)/2:{hy}[vh]"
    last = "vh"
    inputs = ["-i", base, "-loop", "1", "-i", hook_png]
    idx = 2
    if sp.get("overlay"):
        inputs += ["-loop", "1", "-i", sp["overlay"]]
        chain += f";[{idx}:v]scale={sp.get('overlay_w', 620)}:-1[lg];[{last}][lg]overlay=(W-w)/2:{int(H * 0.79)}[vl]"
        last = "vl"; idx += 1
    if sp.get("captions", True) and words:
        apath = os.path.join(tmp, "cap.ass")
        if ass_captions(words, keep, offset, apath, y=int(H * 0.585)):
            chain += f";[{last}]ass={apath}:fontsdir={r4.FONTDIR}[vs]"
            last = "vs"
    # sfx: whoosh into the rewind after the cold open, boom on the climax in the main part
    whoosh, boom = os.path.join(tmp, "w.wav"), os.path.join(tmp, "b.wav")
    sfx(whoosh, "whoosh", 0.45); sfx(boom, "boom", 0.9)
    inputs += ["-i", whoosh, "-i", boom]
    wi, bi = idx, idx + 1
    mix = f";[{wi}:a]adelay={int(max(0, offset - 0.2) * 1000)}:all=1[wh]"
    beats = [0.0] + ([map_time(rc, keep, offset)] if map_time(rc, keep, offset) is not None else [])
    bl = []
    for k, t in enumerate(beats):
        mix += f";[{bi}:a]adelay={int(t * 1000)}:all=1[bm{k}]"
        bl.append(f"[bm{k}]")
    mix += f";[ac][wh]{''.join(bl)}amix=inputs={2 + len(bl)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
    fc2 = ";".join(parts) + ";" + cat + ";" + chain + mix
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc2, "-map", f"[{last}]", "-map", "[aout]",
         "-t", f"{final_len:.2f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print("ok", out, f"len={final_len:.1f}s pieces={len(pieces)} climax@{rc:.1f}", flush=True)


if __name__ == "__main__":
    main()
