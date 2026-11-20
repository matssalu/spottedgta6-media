import sys,json,subprocess,wave,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("small",compute_type="int8")
for f in sys.argv[1:]:
    subprocess.run(["ffmpeg","-v","error","-y","-i",f,"-ac","1","-ar","16000","/tmp/a.wav"])
    w=wave.open('/tmp/a.wav');a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    out={}
    for task in ("transcribe","translate"):
        seg,info=m.transcribe(a,task=task,word_timestamps=True)
        ws=[{"word":x.word,"start":x.start,"end":x.end} for s in seg for x in s.words]
        out[task]=ws
    base=f.rsplit('.',1)[0]
    json.dump(out["translate"],open(base+".words.json","w"))
    json.dump(out["transcribe"],open(base+".fr.json","w"))
    print("==",f,info.language)
    print("FR:"," ".join(f"{x['start']:.0f}:{x['word'].strip()}" for x in out["transcribe"])[:700])
    print("EN:"," ".join(f"{x['start']:.0f}:{x['word'].strip()}" for x in out["translate"])[:700])
