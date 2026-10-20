#!/usr/bin/env python3
# Local evidence extraction only; no visual quality judgment.
import argparse, subprocess, json, pathlib, shutil, sys, csv

def run(args):
    r=subprocess.run(args,capture_output=True,text=True)
    if r.returncode: raise RuntimeError(r.stderr.strip()[-1200:])
    return r.stdout

def main():
    a=argparse.ArgumentParser(description='Video review evidence pack')
    a.add_argument('video');a.add_argument('--out',default='review-evidence');a.add_argument('--interval',type=float,default=1.0);a.add_argument('--max-frames',type=int,default=80)
    args=a.parse_args()
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'): sys.exit('ERROR: ffmpeg and ffprobe required')
    if args.interval<=0 or args.max_frames<1: sys.exit('ERROR: interval must be >0 and max-frames >=1')
    video=pathlib.Path(args.video).resolve();out=pathlib.Path(args.out).resolve()
    if not video.is_file():sys.exit('ERROR: video file not found')
    out.mkdir(parents=True,exist_ok=True);frames=out/'frames';frames.mkdir(exist_ok=True)
    probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]))
    (out/'probe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2),encoding='utf8')
    dur=float(probe.get('format',{}).get('duration') or 0)
    if dur<=0:sys.exit('ERROR: cannot determine video duration')
    # Deterministic sampling from timestamps; covers endpoints while respecting maximum.
    import math
    count=min(args.max_frames,max(2,math.ceil(dur/args.interval)+1))
    stamps=sorted(set(round(i*dur/(count-1),3) for i in range(count)))
    rows=[]
    for i,t in enumerate(stamps):
        t=min(t,max(0,dur-0.001));name=f'frame_{i:04d}_{t:09.3f}s.png'
        run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(video),'-frames:v','1','-threads','1','-y',str(frames/name)])
        rows.append([f'{t:.3f}',str(pathlib.Path('frames')/name)])
    with (out/'frame_index.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.writer(f);w.writerow(['time_seconds','relative_path']);w.writerows(rows)
    (out/'REVIEW_INSTRUCTIONS.md').write_text('''# 审片证据包\n\n这是抽帧证据，不是自动审片结论。把原视频（若Agent支持视频）和本目录关键帧、项目分镜/参考图交给Agent；逐条引用时间码和可见证据。帧间动作、音频、运镜路径不能仅凭稀疏抽帧确定。对可疑片段重新缩小间隔抽帧或人工复核。\n\n未看到的细节一律标记「无法判断」，禁止臆测。\n''',encoding='utf8')
    print(f'OK: {len(rows)} frames, duration={dur:.3f}s, output={out}')
if __name__=='__main__':
    try:main()
    except Exception as e:sys.exit(f'ERROR: {e}')
