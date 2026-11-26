import sys,subprocess,os
# sheet.py src out.jpg start end step cols
src,out=sys.argv[1],sys.argv[2]; a=float(sys.argv[3]); b=float(sys.argv[4]); step=float(sys.argv[5]) if len(sys.argv)>5 else 2
n=int((b-a)/step)+1; cols=int(sys.argv[6]) if len(sys.argv)>6 else 4
rows=(n+cols-1)//cols
subprocess.run(["ffmpeg","-v","error","-y","-ss",str(a),"-t",str(b-a),"-i",src,"-vf",f"fps=1/{step},scale=480:-2,drawtext=text='%{{pts\\:hms}}':x=5:y=5:fontsize=22:fontcolor=yellow:box=1:boxcolor=black,tile={cols}x{rows}","-frames:v","1",out],check=True)
