"""Exactly one native-only always_inline experiment; no profile/flag sweep."""
import argparse,hashlib,json,subprocess,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',required=True,type=Path);p.add_argument('--build-root',type=Path);a=p.parse_args();root=a.project_root.resolve();model=root/'experiments/tsl9-v4160-event-callback';base=a.build_root.resolve() if a.build_root else model/'build'/('inline-'+uuid.uuid4().hex);assert not base.exists() and base.is_relative_to(model/'build');base.mkdir(parents=True);pins={p.name:sha(p) for p in(model/'src').glob('*') if p.is_file()};commands=[];results={}
    for kind in('baseline','always_inline'):
        source=base/(kind+'-src');source.mkdir()
        for name in('callback.c','callback.h','io.h'):(source/name).write_bytes((model/'src'/name).read_bytes())
        h=source/'io.h';text=h.read_text();plain='static inline void cb_native_call(';inlined='static __attribute__((always_inline)) inline void cb_native_call(';assert text.count(inlined)==1 and plain not in text
        if kind=='baseline':h.write_bytes(text.replace(inlined,plain).encode())
        argv=[sys.executable,'-B',str(Path(__file__).with_name('probe_native.py')),'--project-root',str(root),'--tool-dir',str(a.tool_dir.resolve()),'--source-dir',str(source),'--build-root',str(base/kind),'--language','both'];r=subprocess.run(argv,cwd=root,capture_output=True,timeout=180);(base/(kind+'.log')).write_bytes(r.stdout+r.stderr);assert r.returncode==0;commands.append(dict(argv=argv,exit=r.returncode,log=kind+'.log',sha256=sha(base/(kind+'.log'))));results[kind]=json.loads(r.stdout)['results']
    assert all(sha(model/'src'/n)==pin for n,pin in pins.items());record=dict(schema='TSL9-callback-single-native-inline-experiment-v1',source_pins=pins,commands=commands,results=results,shared_algorithm_changed=False,HOST_semantics_changed=False,target_execution=False);(base/'comparison.json').write_bytes((json.dumps(record,indent=2)+'\n').encode());print(json.dumps(dict(receipt=str(base/'comparison.json'),results=results)))
if __name__=='__main__':main()
