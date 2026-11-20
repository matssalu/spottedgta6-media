# Daily clip pipeline (Spotted GTA6)
Copy this folder to /home/claude/work (scripts expect that path; fonts in fonts/), then:
1. `pip install --break-system-packages faster-whisper opencv-python-headless yt-dlp pillow numpy` (if missing)
2. Find moments from the MOST RECENT stream of each streamer:
   - newest VOD: `yt-dlp --flat-playlist -J "https://www.twitch.tv/<channel>/videos?filter=archives&sort=time"`
   - chat spikes: `python3 chatpeaks.py <vod> <start> <end> scan/x.json --top 20` (last ~12h of the VOD)
   - viewer clips: `yt-dlp --flat-playlist -J "https://www.twitch.tv/<channel>/clips?filter=clips&range=7d"` then keep only timestamp >= now-30h, sort by views
   - windows: `python3 grabwin.py <vod> name t1,t2 --pre 22 --post 12`; transcripts: `python3 transcribe.py files...`
3. Render with render5.py (style v5, see docstring). Spec: src,out,hook,start,end,climax,cam,[overlay for KreekCraft]
   Cam boxes: Kai ~[0,0.416,0.20,0.22]; Clix ~[0,0.075,0.25,0.26]; KreekCraft ~[0,0.12,0.28,0.35] + game_shift 0.05 + overlay kreek_overlay.png
Rules: streamer facecam visible and the main focus; no nudity/sexual scenes; accurate (no fabricated context); hook 4-8 words;
captions = 1-line hook caption + 3-5 specific hashtags (never #fyp/#reels); KreekCraft caption must include "Watch KreekCraft on YouTube and Twitch" + #GTA6 #KreekCraft #GrandTheftAutoVI.
