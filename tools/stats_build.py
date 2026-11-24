"""Build Clip Desk stats + per-clip views.
Inputs (cwd): stats_tt_yt.json (Mac stats_fetch.py), ig.json ([[account_name, caption, permalink, timestampUTC, views, likes], ...] from Windsor),
submissions.csv (Mac), clips.json ({doc_id: {data..., "_version": n}} from db_list clips), stats_version (int, current version of stats/accounts or 0).
Output: ops.json = db_write ops for the Clip Desk artifact (stats/accounts set + clips/* merge with ifVersion)."""
import json, csv, datetime, collections, re, sys, os
TT = json.load(open('stats_tt_yt.json')); IG = json.load(open('ig.json'))
clips = json.load(open('clips.json')) if os.path.exists('clips.json') else {}
sv = int(open('stats_version').read()) if os.path.exists('stats_version') else 0
NAME = {"spottedgta6": "SpottedGTA6", "streamsnipessdaily": "StreamSnipes Daily"}
HANDLE = {"SpottedGTA6": "spottedgta6", "StreamSnipes Daily": "streamsnipes.dail", "ClipNation": "clipnation.streamsnipes"}
ACCS = [("SpottedGTA6", "TikTok · Instagram · YouTube"), ("StreamSnipes Daily", "TikTok · Instagram · YouTube"), ("ClipNation", "TikTok · YouTube")]
items = []
for l, v in TT.items():
    if v.get('views') is None: continue
    if 'tiktok.com' in l: l = re.sub(r'tiktok\.com/@[^/]+/', f"tiktok.com/@{HANDLE[v['account']]}/", l)
    items.append(dict(a=v['account'], p=v['platform'], views=v['views'] or 0, likes=v.get('likes') or 0, date=v['post_at'][:10], link=l, file=v['file'], cap=v.get('caption', '')))
for acc, cap, l, ts, vw, lk in IG:
    d = (datetime.datetime.fromisoformat(ts[:16]) + datetime.timedelta(hours=1)).strftime('%Y-%m-%d')
    items.append(dict(a=NAME.get(acc, acc), p='Instagram', views=vw or 0, likes=lk or 0, date=d, link=l, file='', cap=cap or ''))
now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
days = [(now.date() - datetime.timedelta(i)).isoformat() for i in range(6, -1, -1)]
sub = collections.Counter()
if os.path.exists('submissions.csv'):
    for r in csv.DictReader(open('submissions.csv')):
        res = (r.get('result') or '').lower()
        if 'submitted' not in res and not res.startswith('ok'): continue
        p = ' '.join(str(x) for x in r.values()).lower()
        sub['StreamSnipes Daily' if ('acc2' in p or 'streamsnipes' in p) else 'ClipNation' if 'clipnation' in p else 'SpottedGTA6'] += 1
out = []
for n, pl in ACCS:
    it = [x for x in items if x['a'] == n]
    per = [{"p": p, "videos": len(q), "views": sum(x['views'] for x in q), "likes": sum(x['likes'] for x in q)}
           for p in ['TikTok', 'Instagram', 'YouTube'] if p in pl for q in [[x for x in it if x['p'] == p]]]
    best = max(it, key=lambda x: x['views'], default=None)
    out.append({"name": n, "platforms": pl, "videos": len(it), "views": sum(x['views'] for x in it), "likes": sum(x['likes'] for x in it),
                "earnings": float(os.environ.get('EARN_' + n.split()[0].upper(), 0)), "submitted": sub[n], "approved": int(os.environ.get('APPR_' + n.split()[0].upper(), 0)),
                "perPlatform": per, "best": (f"{best['p']}: {re.sub(r'#.*', '', best['cap'] or best['file'])[:38].strip()} ({best['views']})" if best else '–'),
                "days": [{"date": d, "views": sum(x['views'] for x in it if x['date'] == d)} for d in days]})
ops = [{"op": "set", "path": "stats/accounts", "data": {"updated": now.strftime('%d-%m %H:%M'), "accounts": out}, **({"ifVersion": sv} if sv else {})}]
for cid, c in clips.items():
    stem = c.get('file') or cid.split('-', 1)[1]
    stem = stem.replace('.mp4', '')
    cap = c.get('caption') or ''
    known = [u['url'] for u in c.get('links') or []]
    q = [x for x in items if (x['file'] and x['file'].replace('.mp4', '') == stem)
         or (x['p'] == 'Instagram' and ((cap and len(x['cap']) >= 15 and cap.startswith(x['cap'][:22])) or x['link'] in known))]
    if not q: continue
    data = {"views": sum(x['views'] for x in q), "likes": sum(x['likes'] for x in q), "perPlatform": [{"p": x['p'], "views": x['views']} for x in q],
            "links": [{"p": x['p'], "url": x['link']} for x in q]}
    if c.get('status') == 'gepland': data['status'] = 'gepost'
    if any(c.get(k) != data[k] for k in ('views', 'likes', 'links')) or 'status' in data:
        ops.append({"op": "merge", "path": "clips/" + cid, "data": data, "ifVersion": c['_version']})
json.dump(ops, open('ops.json', 'w'), ensure_ascii=False)
print(len(ops), 'ops'); [print(a['name'], a['videos'], a['views'], a['likes']) for a in out]
