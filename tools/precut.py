import sys,json,subprocess,re
src,out=sys.argv[1],sys.argv[2]; rng=json.loads(sys.argv[3])
n=len(rng);inp=[]
for a,b in rng: inp+=["-ss",str(a),"-t",str(b-a),"-i",src]
fc="".join(f"[{i}:v][{i}:a]" for i in range(n))+f"concat=n={n}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",fc,"-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast","-crf","13","-c:a","aac","-b:a","256k",out],check=True)
W=json.load(open(src.rsplit('.',1)[0]+".words.json")); res=[];off=0
CEN={"fuck":"f*ck","fucking":"f*cking","shit":"sh*t","bitch":"b*tch","ass":"a**"}
for a,b in rng:
    for w in W:
        if a<=w["start"]<b-0.05:
            t=w["word"]; k=re.sub(r"[^a-z]","",t.lower())
            if "nigg" in k: continue
            for c,r in CEN.items():
                if k==c or k.endswith(c) and c in("fuck","shit"): t=re.sub(c,r,t,flags=re.I)
            res.append({"word":t,"start":w["start"]-a+off,"end":min(w["end"],b)-a+off})
    off+=b-a
json.dump(res,open(out.rsplit('.',1)[0]+".words.json","w")); print(out,round(off,1))
