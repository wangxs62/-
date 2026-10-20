#!/usr/bin/env python3
"""Apply human-approved EDL. Conservative precise trims and concat; no generative repair."""
import argparse,json,pathlib,subprocess,shutil,tempfile

def cmd(args):subprocess.run(args,check=True)
def main():
 p=argparse.ArgumentParser(description='Render cuts from explicitly approved edit decision list')
 p.add_argument('edl');p.add_argument('--output',required=True);p.add_argument('--approve',action='store_true',help='Explicit approval required to render');a=p.parse_args()
 spec=json.loads(pathlib.Path(a.edl).read_text(encoding='utf8'))
 clips=spec.get('clips',[])
 if not clips:raise ValueError('EDL has no clips')
 output=pathlib.Path(a.output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
 if not a.approve:
  print(json.dumps({'status':'dry_run','clips':clips,'output':str(output),'action':'rerun with --approve to render'},ensure_ascii=False,indent=2));return
 if not shutil.which('ffmpeg'):raise RuntimeError('ffmpeg required')
 with tempfile.TemporaryDirectory() as tmp:
  paths=[]
  for i,c in enumerate(clips):
   source=pathlib.Path(c['source']).resolve();start=float(c['start']);end=float(c['end'])
   if not source.is_file() or start<0 or end<=start:raise ValueError(f'invalid clip #{i}')
   dst=pathlib.Path(tmp)/f'clip_{i:03d}.mp4'
   # Video-only by design: avoids failures caused by unmatched audio stream layouts.
   cmd(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-ss',str(start),'-i',str(source),'-t',str(end-start),'-map','0:v:0','-an','-vf','fps=30,scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p','-c:v','libx264','-preset','fast','-crf','18','-y',str(dst)])
   paths.append(dst)
  manifest=pathlib.Path(tmp)/'list.txt';manifest.write_text(''.join(f"file '{f.as_posix()}'\n" for f in paths))
  cmd(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-f','concat','-safe','0','-i',str(manifest),'-c','copy','-movflags','+faststart','-y',str(output)])
 print('Rendered:',output,'NOTE: no audio; use editing DAW/NLE for original audio and mix')
if __name__=='__main__':main()
