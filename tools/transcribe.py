import sys, json, os, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=2)
for f in sys.argv[1:]:
    out = f[:-4] + ".words.json"
    if os.path.exists(out): continue
    pcm = subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
    a = np.frombuffer(pcm, np.int16).astype(np.float32)/32768
    segs,_ = m.transcribe(a, word_timestamps=True, vad_filter=True, language="en")
    w=[{"w":x.word.strip(),"s":round(x.start,2),"e":round(x.end,2)} for s in segs for x in (s.words or [])]
    json.dump(w,open(out,"w")); print(out, len(w), flush=True)
