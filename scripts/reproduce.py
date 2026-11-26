"""Run with system Python 3. Dedicated worker PID only; no other Isaac session is touched."""
from pathlib import Path
import argparse,subprocess,os,json,time,sys
V5=Path(__file__).resolve().parents[1];ROOT=V5.parent;Q=V5/'progress'
p=argparse.ArgumentParser();p.add_argument('--isaac',default='/home/fufa/isaacsim');p.add_argument('--phase',choices=['all','render','models','sedd','report'],default='all');p.add_argument('--resume-native',action='store_true');a=p.parse_args()
PY=str(Path(a.isaac)/'python.sh');env={**os.environ,'OMP_NUM_THREADS':'4','OPENBLAS_NUM_THREADS':'4'}
def run(script,*args):
    subprocess.run([PY,str(V5/'scripts'/script),*args],cwd=ROOT,env=env,check=True)
def job(name,script,**kwargs):
    output=Q/(name+'_result.json')
    if output.exists():output.unlink()
    tmp=Q/'request.tmp';tmp.write_text(json.dumps({'id':name,'script':str(V5/'scripts'/script),**kwargs}));tmp.replace(Q/'request.json')
    limit=time.monotonic()+1800
    while not output.exists():
        if worker.poll() is not None:raise RuntimeError('Dedicated worker exited; inspect v5/logs/reproduce_worker.log')
        if time.monotonic()>limit:raise TimeoutError(name)
        time.sleep(.25)
    result=json.loads(output.read_text())
    if not result['ok']:raise RuntimeError(result['error'])
    print(name,'completed in',round(result['elapsed_s'],1),'s',flush=True)
if a.phase in ['all','render']:
    Q.mkdir(exist_ok=True);ready=Q/'ready.json'
    if ready.exists():
        old=json.loads(ready.read_text())
        try:os.kill(old['pid'],0)
        except ProcessLookupError:pass
        else:raise RuntimeError('Existing v5 worker is alive; use that queue or stop it before a new reproduction')
        ready.unlink()
    if (Q/'request.json').exists():raise RuntimeError('Pending v5 request exists; inspect it before reproducing')
    with (V5/'logs/reproduce_worker.log').open('w') as log:
        worker=subprocess.Popen([PY,'-u',str(V5/'scripts/isaac_worker.py')],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        try:
            limit=time.monotonic()+120
            while not ready.exists():
                if worker.poll() is not None:raise RuntimeError('Worker failed to start')
                if time.monotonic()>limit:raise TimeoutError('Worker startup')
                time.sleep(.25)
            job('convert_reproduction','prepare_assets.py');job('build_reproduction','build_lab.py')
            job('native_reproduction','capture_native.py',resume=a.resume_native)
            job('motion_profiles_reproduction','capture_motion_and_profiles.py')
        finally:
            if worker.poll() is None:
                (Q/'request.json').write_text(json.dumps({'id':'quit','quit':True}))
                try:worker.wait(timeout=30)
                except subprocess.TimeoutExpired:worker.terminate();worker.wait(timeout=10)
if a.phase in ['all','models']:run('capture_models.py');run('verify_models.py')
if a.phase in ['all','sedd']:run('evaluate_sedd.py')
if a.phase in ['all','report']:
    run('build_coverage.py');run('build_report.py');run('build_figures.py');run('validate_outputs.py')
