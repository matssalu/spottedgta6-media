"""TikTok-style title: black TikTok Sans text on white rounded per-line boxes, with color emoji."""
from PIL import Image, ImageDraw, ImageFont
import re, sys

FONT = "/home/claude/work/fonts/TikTokSans.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EMO = re.compile("([\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF][️‍\U0001F3FB-\U0001F3FF\U0001F300-\U0001FAFF☀-➿]*)")


def font(size):
    f = ImageFont.truetype(FONT, size)
    try:
        axes = {a["name"].decode() if isinstance(a["name"], bytes) else a["name"]: a for a in f.get_variation_axes()}
        vals = []
        for a in f.get_variation_axes():
            n = a["name"].decode() if isinstance(a["name"], bytes) else a["name"]
            vals.append({"Weight": 600, "Width": 100, "Slant": 0, "Optical size": min(max(size / 2, a["minimum"]), a["maximum"])}.get(n, a["default"]))
        f.set_variation_by_axes(vals)
    except Exception as e:
        print("variation:", e, file=sys.stderr)
    return f


def emoji_img(ch, h):
    ef = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=ef, embedded_color=True)
    bb = im.getbbox() or (0, 0, 1, 1)
    im = im.crop(bb)
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def split_emo(p):
    out = []
    for c in p:
        if c in "\uFE0F\u200D" or 0x1F3FB <= ord(c) <= 0x1F3FF:
            if out: out[-1] += c
        elif out and out[-1].endswith("\u200D"):
            out[-1] += c
        else:
            out.append(c)
    return out


def runs(text):
    out = []
    for p in EMO.split(text):
        if not p:
            continue
        out.append(("e", p) if EMO.fullmatch(p) else ("t", p))
    return out


def measure(text, f, eh):
    w = 0
    for k, p in runs(text):
        if k == "t":
            w += f.getlength(p)
        else:
            w += eh * 1.08 * len(split_emo(p))
    return w


def wrap(text, f, eh, maxw):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if measure(t, f, eh) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def render(text, out, size=64, maxw=900, bg=(255, 255, 255, 255), fg=(0, 0, 0, 255)):
    for a in ("Kai Cenat", "GTA 6", "Stable Ronaldo", "FOUGHT BACK"):
        text = text.replace(a, a.replace(" ", "\u00a0"))
    text = re.sub(r" ((?:%s)+)$" % EMO.pattern.strip("()"), "\u00a0\\1", text)
    f = font(size)
    asc, desc = f.getmetrics()
    eh = int(size * 1.0)
    lines = wrap(text, f, eh, maxw)
    padx, pady, r = 26, 10, 18
    lh = asc + desc + pady * 2
    widths = [measure(l, f, eh) for l in lines]
    W = int(max(widths)) + padx * 2 + 4
    H = lh * len(lines) + 4
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (l, w) in enumerate(zip(lines, widths)):
        x0 = (W - w) / 2 - padx; y0 = i * lh
        d.rounded_rectangle([x0, y0, x0 + w + padx * 2, y0 + lh + (2 if i < len(lines) - 1 else 0)], radius=r, fill=bg)
    for i, (l, w) in enumerate(zip(lines, widths)):
        x = (W - w) / 2; y = i * lh + pady
        for k, p in runs(l):
            if k == "t":
                d.text((x, y), p, font=f, fill=fg)
                x += f.getlength(p)
            else:
                for ch in split_emo(p):
                    e = emoji_img(ch, eh)
                    im.alpha_composite(e, (int(x + eh * 0.04), int(y + (asc + desc - eh) / 2 + 2)))
                    x += eh * 1.08
    im.save(out)
    return im.size


if __name__ == "__main__":
    print(render(sys.argv[1], sys.argv[2]))
