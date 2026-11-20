# Clip brief (Mats, 20 Nov 2026) - follow strictly

What worked: ~25 s KreekCraft clips with a teasing caption (1,527 and 1,701 IG views, ~30% swipe-away in first 3 s). Raw 22-46 s Kai clips got 2-19 views.

## Volume and mix (Brussels time)
- Account 1 (TikTok + Instagram @spottedgta6 + YouTube Spotted GTA6): 6 clips/day at 14:00, 16:00, 18:00, 20:00, 22:00, 00:00 (00:00 = next calendar day). Mix: 4 KreekCraft, 1 Kai Cenat, 1 Clix. Suggested order: 14 Kreek, 16 Kreek, 18 Kai, 20 Kreek, 22 Clix, 00 Kreek.
- Account 2 (TikTok @streamsnipes.dail, Instagram + YouTube @streamsnipessdaily): 3 clips/day at 15:00, 19:00, 23:00, mostly KreekCraft (default 3 KreekCraft).
- Every account gets its OWN clips: never the same clip on two accounts on the same app. A KreekCraft clip may be posted at most 5 times in total across all accounts/apps.

## Campaign rules (breaking = rejected)
KreekCraft ($1/1K views, min payout $5 -> needs 5K+ views): logo overlay (kreek_overlay.png) clearly visible the WHOLE clip; only his official GTA 6 streams/replays; caption must contain "Watch KreekCraft on YouTube and Twitch" and "#GTA6 #KreekCraft #GrandTheftAutoVI"; hook in first 1-2 s; no low-effort recordings/random gameplay; original edits, no fake context or misleading titles; >=0.8% engagement, likes visible; posts stay public 30 days; >=40% US/UK/CA/AU viewers.
Kai Cenat: Kai playing GTA 6 is the main focus, from his GTA 6 marathon; caption contains #KaiCenat; needs 1K views per clip.
Clix: from his GTA 6 marathon; caption contains #clix; 500 views per clip; full rules reachclipping.com/ClixGTA.

## Editing (render5.py does most of this)
1. Open on the peak moment (cold open), cut all setup before it.
2. Hook text 0-2 s, 4-8 words, big, high contrast, with STAKES / a bet / a challenge ("bet a FREE copy of GTA 6 he wouldn't get eaten by a crocodile", "went shark hunting").
3. Length 20-30 s; cut pauses > 0.4 s, walking, menus, loading.
4. Word-by-word captions for all speech, clear of bottom 20% and right edge.
5. 1080x1920, facecam top, gameplay below cropped to the action, streamer overlay kept in frame, no black bars/blur.
6. Visible edit: punch-in zoom on reaction, SFX on key beats, short replay of the best moment (cold open does this).
7. End on the punchline, no outro; loop back if possible.
8. Mute/avoid copyrighted music (in-game radio, stream music) - skip clips where music is prominent.
9. Never use these words in titles/captions/on-screen text: vape, drugs, weed, drunk, sexual words, slurs.

## Moments
Pick: bets and challenges, animals, police chases, crashes, big fails, streamer losing it / screaming. Skip: calm exploring, menus, moments needing earlier context.

## Captions
One teasing line + required campaign line + required hashtags, end with a short question to drive comments ("Would you take that bet?"). Never #fyp or #reels.

## Extra campaigns (added 20 Nov)
Per account per day: 2 Dylan Page + 2 Gattouz (on top of the 6 / 3 above).
- Account 1 extra slots: 15:00 Dylan, 17:00 Gattouz, 19:00 Dylan, 21:00 Gattouz.
- Account 2 extra slots: 16:00 Dylan, 18:00 Gattouz, 20:00 Dylan, 22:00 Gattouz.

### Dylan Page ($1 CPM, TikTok/IG/YouTube) — campaign 39753a1a-f1f3-491b-a8f6-0cfee0af0c97
- 120-hour GTA 6 marathon on YouTube, channel UCzPpbeK8ANcNKg5aoMB0miw (/streams). Dylan must be visible. Caption must include #DylanPage.
- YouTube blocks the cloud: download on the Mac shell (device_bash) with `python3 -m yt_dlp` (pip install --user yt-dlp) in $HOME (deletes are blocked under mnt); `--download-sections "*START-END"`; copy result into ~/mnt/Documents/GTA6-page/media/dylan/src/ and device_stage_files it. Background processes die after each call: keep each call < 170 s.
- Signals: live chat replay (`--write-subs --sub-langs live_chat`, ~20 s per VOD) -> W/LOL spikes.
- Gameplay layout: cam top-right, spec cam [0.684,0.115,0.314,0.304], game_shift -0.12. IRL segments: spec "full": true, "full_x" (0-1 horizontal centre of Dylan), "cam": [0,0,1,1]; use "hook_y": 1480 if the hook would cover faces.
- Dylan = blond guy (tank top / black long-sleeve); co-hosts Alex (beard, cap) and Elliot.

### Gattouz / 1WIN ($0.35 CPM, min $35, TikTok + Instagram only) — campaign 0123c725-0bb8-49fc-b60a-5affd894b66d
- Kick: https://kick.com/api/v2/channels/gattouz0/videos (VOD HLS 'source'), clips: /api/v2/channels/gattouz0/clips?sort=view&time=week, clip video_url via /api/v2/clips/<id>.
- Signals: the VOD has English auto-subtitles: <source dir>/subtitles/en/playlist.m3u8 (download all .vtt, scan keywords). Avoid his many strip-club / nudist / sexual segments.
- The 1WIN branding is his "1win" chain pendant: keep his chest in the cam crop and set "hook_y": 760 so the hook never covers it. Never add a logo.
- Nov 19 layout cam top-left [0.0,-0.02,0.305,0.28]; Nov 18 cam top-left with girlfriend [0.04,-0.02,0.16,0.25] or bottom-left [0.085,0.66,0.22,0.3]. Check every day.
- Captions in English (tr_en.py = whisper translate). Caption must tag @gattouze and disclose: "Gattouz is live on Kick: kick.com/gattouz0 @gattouze #ad" + "#Gattouz #GTA6 #GTAVI #1win".

## Scheduling safety (added 20 Nov)
- The Mac uploaders rewrite their CSV when they finish (TikTok acc 1 job at :40, account-2/YouTube job at :52). Rows appended while a job runs get LOST. Only edit the Mac CSVs between :00 and :35, then re-read them to confirm every new row is there.
- No IRL content (Mats, 20 Nov): gameplay with facecam only. No whoosh / "shhh" SFX (removed from render5).
- Pick FUN moments: a visible event with a payoff (crash, escape, fail, fight, scare, landing) and a loud reaction. Skip calm driving/talking clips.

## Schedule from 22 Nov (Mats, 21 Nov: "focus even more on KreekCraft")
- Account 1: 14 Kreek, 15 Dylan, 16 Kreek, 17 Gattouz, 18 Kreek, 19 Dylan, 20 Kreek, 21 Gattouz, 22 Kreek, 00 Kreek.
- Account 2: 15 Kreek, 16 Dylan, 17 Kreek, 18 Gattouz, 19 Kreek, 20 Dylan, 21 Kreek, 22 Gattouz, 23 Kreek.
- Kai Cenat / Clix only when there is an exceptional moment (then it replaces one Kreek slot). Otherwise all-KreekCraft in those slots.
- Quality over quantity: if after a long search a slot has no clip that passes the bar in tools/LEARNINGS.md, leave the slot empty and say so. Never fill with a weak clip.
