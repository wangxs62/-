#!/usr/bin/env python3
"""Deterministic motion/cut/freeze candidate detection. No semantic AI claims."""
import argparse, csv, json, math, pathlib, subprocess
import cv2
import numpy as np

def probe(path):
    p=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)],capture_output=True,text=True,check=True)
    return json.loads(p.stdout)

def main():
    p=argparse.ArgumentParser(description='Find video anomaly candidates; emit evidence, not diagnoses')
    p.add_argument('video');p.add_argument('--out',default='analysis');p.add_argument('--sample-fps',type=float,default=10);p.add_argument('--width',type=int,default=320)
    p.add_argument('--cut-threshold',type=float,default=.48);p.add_argument('--freeze-seconds',type=float,default=.45)
    a=p.parse_args()
    if a.sample_fps<=0 or a.width<64 or not (0<a.cut_threshold<1) or a.freeze_seconds<=0: p.error('invalid numeric argument')
    src=pathlib.Path(a.video).resolve();out=pathlib.Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    info=probe(src);cap=cv2.VideoCapture(str(src))
    if not cap.isOpened():raise RuntimeError('Unable to decode video')
    fps=cap.get(cv2.CAP_PROP_FPS); n=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if not fps or fps<=0: raise RuntimeError('FPS unavailable')
    duration=float(info.get('format',{}).get('duration') or n/fps)
    step=max(1,round(fps/a.sample_fps));actual=fps/step
    prev=None;prev_hist=None;prev_t=None;records=[];idx=0
    while True:
        ret,frame=cap.read()
        if not ret:break
        if idx%step:idx+=1;continue
        t=idx/fps; h,w=frame.shape[:2];small=cv2.resize(frame,(a.width,max(1,round(h*a.width/w))))
        gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
        hist=cv2.calcHist([cv2.cvtColor(small,cv2.COLOR_BGR2HSV)],[0,1],None,[32,32],[0,180,0,256]);cv2.normalize(hist,hist)
        if prev is not None:
            diff=float(np.mean(cv2.absdiff(gray,prev))/255)
            histdist=float(cv2.compareHist(hist,prev_hist,cv2.HISTCMP_BHATTACHARYYA))
            flow=cv2.calcOpticalFlowFarneback(prev,gray,None,.5,3,15,3,5,1.2,0)
            magnitudes=np.linalg.norm(flow,axis=2)
            motion=float(np.median(magnitudes));motion_p90=float(np.percentile(magnitudes,90))
            records.append({'time':round(t,3),'prev_time':round(prev_t,3),'mean_frame_diff':round(diff,5),'hist_distance':round(histdist,5),'median_flow_px':round(motion,4),'p90_flow_px':round(motion_p90,4)})
        prev=gray;prev_hist=hist;prev_t=t;idx+=1
    cap.release()
    with (out/'motion_metrics.csv').open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=['time','prev_time','mean_frame_diff','hist_distance','median_flow_px','p90_flow_px']);writer.writeheader();writer.writerows(records)
    events=[];freeze_start=None
    motion_vals=np.array([r['p90_flow_px'] for r in records]);cutmask=[]
    med=float(np.median(motion_vals)) if len(motion_vals) else 0
    for r in records:
        iscut=r['hist_distance']>=a.cut_threshold and r['mean_frame_diff']>=.12
        cutmask.append(iscut)
        if iscut:events.append({'kind':'possible_cut','start':r['prev_time'],'end':r['time'],'score':r['hist_distance'],'evidence':'histogram distance and frame difference','status':'needs_review'})
        still=r['mean_frame_diff']<.002 and r['p90_flow_px']<.18
        if still and freeze_start is None:freeze_start=r['prev_time']
        if (not still or iscut) and freeze_start is not None:
            if r['prev_time']-freeze_start>=a.freeze_seconds:events.append({'kind':'possible_freeze','start':round(freeze_start,3),'end':r['prev_time'],'status':'needs_review','evidence':'low consecutive frame differences and optical flow'})
            freeze_start=None
    if freeze_start is not None and records and records[-1]['time']-freeze_start>=a.freeze_seconds:
        events.append({'kind':'possible_freeze','start':round(freeze_start,3),'end':records[-1]['time'],'status':'needs_review','evidence':'low consecutive frame differences and optical flow'})
    for i in range(1,len(records)):
        r=records[i];pre=records[i-1]
        if cutmask[i] or cutmask[i-1]:continue
        if r['p90_flow_px']>max(5.0,med*4) and r['mean_frame_diff']>.045:
            events.append({'kind':'motion_spike','start':r['prev_time'],'end':r['time'],'score':r['p90_flow_px'],'status':'needs_review','evidence':'high optical flow and frame change; may reflect subject rather than camera motion'})
    events.sort(key=lambda e:(e['start'],e['kind']))
    # Dense FFmpeg extraction around flagged intervals, bounded to avoid uncontrolled IO.
    frames=out/'suspect_frames';frames.mkdir(exist_ok=True)
    extracted=[]
    for i,e in enumerate(events[:30]):
        start=max(0,float(e['start'])-.3);end=min(duration,float(e['end'])+.3)
        if end<=start:continue
        folder=frames/f'{i:03d}_{e["kind"]}';folder.mkdir(exist_ok=True)
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-ss',f'{start:.3f}','-i',str(src),'-t',f'{end-start:.3f}','-vf','fps=12,scale=640:-2','-frames:v','50','-y',str(folder/'%04d.jpg')]
        result=subprocess.run(cmd,capture_output=True,text=True)
        extracted.append({'event_index':i,'folder':str(folder.relative_to(out)),'success':result.returncode==0})
    output={'schema_version':'1.0','video':str(src),'duration_seconds':duration,'sample_fps_actual':actual,'events':events,'dense_evidence':extracted,'limitations':['Events are candidates, not confirmed defects','No face/product/hand/logo recognition','A static intentional shot may trigger freeze','An intentional cut may trigger cut','Camera motion cannot be inferred reliably from flow alone','Sampling can miss sub-frame or short events'],'review_required':True}
    (out/'anomalies.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
    print(f'Analyzed {duration:.2f}s; {len(events)} candidate event(s). Output: {out}')
if __name__=='__main__':main()
