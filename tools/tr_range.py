import sys, json, os, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=2)
# usage: tr_range.py src start end [src start end ...]  -> src.words.json (source time)
a=sys.argv[1:]
for i in range(0,len(a),3):
    f,s,e=a[i],float(a[i+1]),float(a[i+2])
    out=f[:-4]+".words.json"
    pcm=subprocess.run(["ffmpeg","-v","error","-ss",str(s),"-t",str(e-s),"-i",f,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
    x=np.frombuffer(pcm,np.int16).astype(np.float32)/32768
    segs,_=m.transcribe(x,word_timestamps=True,vad_filter=True,language="en")
    w=[{"w":z.word.strip(),"s":round(z.start+s,2),"e":round(z.end+s,2)} for sg in segs for z in (sg.words or [])]
    json.dump(w,open(out,"w"))
    print("==",f, ' '.join('[%d]%s'%(q['s'],q['w']) if j%8==0 else q['w'] for j,q in enumerate(w)),flush=True)
