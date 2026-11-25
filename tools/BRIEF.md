# BRIEF — operational rules (from 23 Nov 2026)

The full strategy is in `tools/MASTER_INSTRUCTIONS.md` (Mats's master instructions — read it every run, it wins over this file if they differ).
What works / what doesn't: `tools/LEARNINGS.md`. Every published video: `tools/history.csv`. Competitor research: `tools/competitors.csv`.
Older campaigns (KreekCraft, Kai Cenat, Clix, Dylan Page, Gattouz) are FINISHED for us — never make content for them again.

## Campaigns (ONLY these two)
| | ClipUp — GTA VI ClipUp Logo | LUXDROP — LUXDROP Logo Clipping |
|---|---|---|
| Content Rewards | https://contentrewards.com/c/campaigns/802cf95a-ea84-4070-9a96-8a917831cb16 | https://contentrewards.com/c/campaigns/1b3065cb-29fd-4631-a252-ec3f6d28a583 |
| Full rules | Google Doc 1GeUEJhQ8HRnExpB7hiz527q5b_1qkZKVN39dUfnAtGw (export?format=txt) | https://reachclipping.com/LUXDROP |
| Source | any GTA 6 streamer gameplay ("post only streamer gameplay") | any GTA 6 gameplay/stream from BIG streamers (avg ≥ 3,000 viewers) |
| Logo | `logos_use/clipup.png` (official file, proportionally scaled, never recoloured/cropped/stretched), whole clip, never covered by captions, facecam, map or HUD | `logos_use/luxdrop.png` (official Watermark-2, native size) whole clip. **No other logos of any kind** on LUXDROP videos |
| Caption | must contain `#gta6 #Clipup` | must contain `#LUXDROP` |
| Pays | $0.30/1K Tier-1 views (US/UK/CA/AU), from 3,000 views, max $150; engagement ≥ 0.5% (likes+comments) | $0.75/1K, from 10,000 views (MVR), max $300; ≥ 50% audience US/CA/AU/UK/NZ |
| Other | keep posts up ≥ 60 days; no reuploads showing another creator's watermark; Instagram: upload analytics via https://forms.gle/3pwRKfejyz79vKtAA once min views reached (tell Mats) | no negative portrayal of LUXDROP; no botting/reposts/collab posts; no AI-generated content; English captions/on-screen text only; no misleading thumbnails |
| Submit | within 30 min of posting | within 30 min of posting |

**Status 25 Nov 2026 (checked on Content Rewards):** LUXDROP = "Joined · Paused — Out of budget since Nov 25" ($7,258 / $7,500). Do NOT make LUXDROP clips until it resumes; fill those slots with ClipUp. ClipUp: $3,125 / $15,000 used, min payout $0.90 (= 3K tier-1 views), caption must include #clipup.

A video is made for ONE campaign (its logo decides). Never put both logos on one video. Never submit a ClipUp-logo video to LUXDROP or vice versa.
render5: `"logo": "clipup"` or `"logo": "luxdrop"` adds the logo strip under the gameplay (nothing covers it).

## Accounts and daily slots (Brussels time; 4 clips per account: 2 ClipUp + 2 LUXDROP)
| Account | Platforms | Slots |
|---|---|---|
| SpottedGTA6 (GTA VI moments, NPCs, discoveries, reactions) | TikTok @spottedgta6, Instagram @spottedgta6, YouTube "Spotted GTA6" | 18:00, 19:00, 20:00, 21:00 |
| StreamSnipes Daily (personality: Speed, Kai, OhnePixel, big streamers; conversations, reactions, interactions) | TikTok @streamsnipes.dail, Instagram + YouTube @streamsnipessdaily | 18:00, 19:00, 20:00, 21:00 |
| ClipNation (curated best GTA VI streamer moments, broad mix) | TikTok + YouTube only (no Instagram) — needs `setup_clipnation.command` run once on the Mac | 18:00, 19:00, 20:00, 21:00 |
Each account gets its OWN clips (never the same moment on two accounts). The same video goes to all platforms of ONE account.
Target = 12 clips/day. Never fill a slot with a weak clip: leave it empty and say why.

## Where moments come from (in this order)
1. **Trending YouTube compilations / highlight videos** of streamers playing GTA 6 (Mats's idea): search YouTube on the Mac shell (`python3 -m yt_dlp "ytsearch30:<streamer> GTA 6 funny moments" --flat-playlist --print "%(id)s %(view_count)s %(upload_date)s %(title)s"`), pick recent ones with high views, read their chapters/transcripts to find the moments, then **trace each moment to the streamer's original VOD/clip** (Twitch/YouTube/Kick) and clip from the ORIGINAL — never use a compilation's or another clipper's finished footage. Log the competitor/compilation in competitors.csv.
2. Competitor clipping accounts (TikTok/Shorts/Reels in the GTA 6 streamer niche): their best-performing videos → reverse-search the original stream → our own edit.
3. Twitch viewer clips sorted by views (yt-dlp `/clips?range=7d`), chat spikes (chatpeaks.py), loudness peaks — for the streamers' latest streams.
Priority streamers (Mats, 24 Nov): IShowSpeed, Kai Cenat, **OhnePixel and Jynxzi (use them EVERY day — at least 1 OhnePixel + 1 Jynxzi clip per day)**, then other big GTA 6 streamers (≥ 3,000 avg viewers for LUXDROP). Jynxzi (Twitch jynxzi, YouTube "Jynxzi Live"/clips) and OhnePixel (Twitch ohnepixel) are both big enough for LUXDROP.
YouTube blocks the cloud: run yt-dlp on the Mac shell (device_bash, in $HOME, each call < 170 s), copy results into ~/mnt/Documents/GTA6-page/media/… and device_stage_files them.

## Editing (render5.py)
- Signature **animated neon facecam border** is on by default (`"neon": false` to disable; automatically off in `"full"` mode = no facecam).
- Cam box per streamer: measure on a frame; KreekCraft-style layout [x,y,w,h] relative. Check 1 fps strips: face visible, not covered by text, logo fully visible, captions in sync.
- Duration per story (8-15 s single joke … 25-40 s escalation; `max_len`), hook visible in the first 1-2 s, payoff must be shown, end on the punchline. No whoosh. No IRL-only footage. No nudity/sexual content, no slurs in hooks/captions.
- Score every candidate 0-100 with the rubric in MASTER_INSTRUCTIONS §7 + confidence + campaign eligibility. Publish ≥ 70 only (≥ 80 preferred).

## Captions
Teasing line ending with a question + campaign tags. ClipUp: `#gta6 #Clipup` + 2-3 specific tags. LUXDROP: `#LUXDROP #gta6` + 2-3 specific tags. English only. Never #fyp/#reels.

## Mac scheduling files (tools/uploader/)
Only edit between :00 and :35 (uploaders rewrite the files at :40 and :52), then re-read to confirm.
- schedule.csv = TikTok SpottedGTA6 (scheduled inside TikTok by the :40 job)
- schedule_acc2.csv = TikTok StreamSnipes; yt1_schedule.csv = YouTube SpottedGTA6; yt_schedule.csv = YouTube StreamSnipes
- schedule_cn.csv = TikTok ClipNation; yt_cn_schedule.csv = YouTube ClipNation (posted by the :52 job when due)
- Instagram (cloud task): repo ig_schedule.csv (SpottedGTA6) and ig2_schedule.csv (StreamSnipes), column caption = full caption.


## Clip Desk (Mats's web app) — READ IT EVERY RUN
App: https://claude.ai/artifact/3NV4dugDc4xiLxvQEtq4Nh  (artifact slug `133230d4-6122-41f3-8159-0da324771466`). Mats manages everything there; it wins over this file for schedule and style.
Read it with the claude-artifacts tools (ToolSearch "claude-artifacts db"): `db_get` / `db_list` with the slug. If those tools are not available in your run, use the last export in the repo: `tools/clipdesk.json` (schedule, sources, feedback) and `tools/styles.json` (styles), and say in your report that you used the export.
Collections/docs:
- `schedule/accounts` → per account `active`, `times` (HH:MM upload slots, Brussels) and `mix` (campaign split). Plan exactly these slots (skip inactive accounts). Overrides "4 per account 18-21".
- `sources` (Mats's compilations: url, streamers, priority hoog/normaal, note, status nieuw/gebruikt/afgewezen, reply) → research `hoog` first, trace each moment to the original VOD, then `db_write` merge `status` + `reply` (what you made from it, or why not).
- `feedback` (text, kind, optional clip/clipTitle, status, reply) → read ALL with status `nieuw` before making clips, apply them, add a rule to LEARNINGS.md, then merge `status: "verwerkt"` + a short Dutch `reply`.
- `presets/<streamer>` (`cam` = exact facecam crop [x,y,w,h] fractions of the 16:9 source, `gameShift`, optional `style`) and `style/global` (border colours/thickness/radius/pulse, captions y/font/size/colours/outline/words/upper, hook bg/colour/size) → before rendering, export them to `tools/styles.json` = {"global": <style/global>, "streamers": {name: {cam, gameShift, style}}} (drop `frame`). render5 reads it: pass `"streamer": "<name>"` in the spec (no `cam` key) and it uses the preset crop + style. New streamer without a preset: measure the cam yourself and ALSO `db_write` a `presets/<name>` doc (name, cam, gameShift) so Mats can fine-tune it.
- `clips/<id>` (write, admin): one doc per clip you schedule, id `d<MMDD>-<file stem>`: date, time, account, campaign, streamer, title, score, status (gepland/gepost/mislukt/vervangen), file (mp4 name), caption (full caption, used to match the Instagram post), links [{p, url}], views, likes, perPlatform [{p, views}]. The hourly stats task fills views/likes/links. Production run creates them; the nightly check updates status, links and views.
- `stats/accounts` (write): rewritten every hour by the stats task with tools/stats_build.py: {updated, accounts:[{name, platforms, videos (online), views, likes, earnings, submitted, approved, perPlatform:[{p, videos, views, likes}], best, days:[{date, views}]}]}.
After reading, also refresh the repo exports (tools/clipdesk.json, tools/styles.json) and commit them.
