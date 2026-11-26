"""Run on the Mac shell (device_bash). Grab one window of a long YouTube VOD via its HLS segments (download-sections hangs on 4h+ VODs).
usage: python3 hg.py name start_s dur_s videoid [video_format=312 (1080p60 avc) | 311 (720p60)]
-> $HOME/seg/<name>.mp4, copied to ~/mnt/Documents/GTA6-page/media/raw/d<date>/ (edit the path below)."""
import sys,subprocess,urllib.request,os
name,st,du,vid=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
vf=sys.argv[5] if len(sys.argv)>5 else '312'
U=subprocess.run(['python3','-m','yt_dlp','-g','-f',f'{vf}+233/{vf}+234/{vf}','https://www.youtube.com/watch?v='+vid],capture_output=True,text=True).stdout.split()
def grab(url,out):
    pl=urllib.request.urlopen(url,timeout=30).read().decode()
    t=0;segs=[];dur=None
    for l in pl.splitlines():
        if l.startswith('#EXTINF'): dur=float(l.split(':')[1].split(',')[0])
        elif l and not l.startswith('#'):
            if t+dur>=st-1 and t<=st+du+1: segs.append((t,l))
            t+=dur
    with open(out,'wb') as f:
        for _,u in segs: f.write(urllib.request.urlopen(u,timeout=30).read())
    return segs[0][0]
tv=grab(U[0],name+'_v.ts'); ta=grab(U[1],name+'_a.ts') if len(U)>1 else None
cmd=['ffmpeg','-v','error','-y','-ss',str(st-tv),'-i',name+'_v.ts']
if ta is not None: cmd+=['-ss',str(st-ta),'-i',name+'_a.ts','-map','0:v','-map','1:a']
subprocess.run(cmd+['-t',str(du),'-c','copy',name+'.mp4'],check=True)
os.system(f'cp {name}.mp4 $HOME/mnt/Documents/GTA6-page/media/raw/d20261126/ && echo copied {name}')
