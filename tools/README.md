# Nightly clip pipeline (Spotted GTA6)
Copy this folder to /home/claude/work (scripts expect that path), then:
1. `pip install --break-system-packages faster-whisper opencv-python-headless yt-dlp pillow numpy` (if missing)
2. `SINCE_TS=<campaign start unix> python3 fetch.py used_ids.txt kaicenat:30 clix:14` -> r/candidates.json, r/clips/*_sheet.jpg
3. Optional VOD mining: `python3 peaks.py <vod> <start> <end> scan/x --top 10` then `python3 grabwin.py <vod> name t1,t2 --pre 26 --post 8` + `python3 transcribe.py win/*.mp4`
4. Write a spec per clip and `python3 render4.py spec.json` (keys: src,title,out,start,end,cam,layout=full,captions,cam_mult,game_shift)
Rules: streamer must be visible (facecam) and the main focus; no nudity/sexual scenes; no negative/false framing; English titles naming the streamer.
