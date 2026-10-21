"""Bounded header/launch-gate controls; no rejected executable is executed."""
import argparse,hashlib,importlib.util,json,struct,sys
from pathlib import Path
from unittest.mock import patch

H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--rv32',type=Path,required=True);p.add_argument('--build-root',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();base=a.build_root.resolve();rv=a.rv32.resolve()
    need(base.is_relative_to(root) and not base.exists(),'create-only controls inside project');base.mkdir(parents=True)
    runner=root/'experiments/tsl9-v4160-flash-native/verify_host.py';pin=sha(runner);spec=importlib.util.spec_from_file_location('guarded_flash_host',runner);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);rows=[]
    def rejected(name,path):
        launches=[]
        def forbidden(*args,**kwargs):launches.append(True);raise AssertionError('rejected target reached subprocess')
        with patch.object(m.subprocess,'run',forbidden):
            try:m.execute([path],base,name,{},host_test=True)
            except ValueError as e:reason=str(e)
            else:raise ValueError('negative accepted '+name)
        need(not launches and not (base/(name+'.log')).exists(),'reject before subprocess/log '+name)
        rows.append(dict(case=name,path=str(path),sha256=sha(path),rejected_before_subprocess=True,subprocess_calls=0,reason=reason))
    data=rv.read_bytes();need(data[:4]==b'\x7fELF' and len(data)>=52 and int.from_bytes(data[18:20],'little')==243,'actual RV32 component ELF identity')
    rejected('actual_RV32_component',rv)
    malformed={
        'unknown_format':b'not an executable',
        'truncated_DOS':b'MZ'+bytes(12),
        'PE_offset_outside_file':b'MZ'+bytes(58)+struct.pack('<I',0xfffffff0),
        'ELF_truncated':b'\x7fELF'+bytes(8),
        'RISC_V_header':b'\x7fELF'+bytes([1,1,1])+bytes(11)+struct.pack('<H',243)+bytes(32),
    }
    for name,raw in malformed.items():
        path=base/(name+'.fixture');path.write_bytes(raw);rejected(name,path)
    # Only header parsing is simulated for other OSes; these fixtures are never launched.
    structural=[]
    for platform_name,arch,machine in [('linux','x86_64',62),('linux','arm64',183),('darwin','x86_64',0x1000007),('darwin','arm64',0x100000c)]:
        if platform_name=='linux':
            raw=bytearray(64);raw[:7]=b'\x7fELF\x02\x01\x01';struct.pack_into('<HH',raw,16,2,machine)
        else:raw=bytearray(struct.pack('<IIIIIIII',0xfeedfacf,machine,0,2,0,0,0,0))
        path=base/(platform_name+'-'+arch+'.fixture');path.write_bytes(raw)
        with patch.object(m.sys,'platform',platform_name),patch.object(m,'host_architecture',lambda:arch):
            result=m.host_executable(path);need(result['machine']==machine,'matching header acceptance')
            bad=bytearray(raw);struct.pack_into('<H' if platform_name=='linux' else '<I',bad,18 if platform_name=='linux' else 4,243 if platform_name=='linux' else 7);wrong=base/(platform_name+'-'+arch+'-wrong.fixture');wrong.write_bytes(bad);rejected(platform_name+'_'+arch+'_wrong_machine',wrong)
        structural.append(dict(platform=platform_name,arch=arch,accepted_header=result,executed=False))
    need(sha(runner)==pin,'stable runner during controls')
    report=dict(schema='ID2966-host-machine-guard-controls-v1',passed=True,runner_sha256=pin,script_sha256=sha(Path(__file__)),rejections=rows,matching_cross_platform_header_fixtures=structural,actual_RV32_component_sha256=sha(rv),target_execution=False,subprocess_calls=0,foreign_OS_execution=False)
    (base/'verification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(dict(passed=True,receipt=str(base/'verification.json'),sha256=sha(base/'verification.json'),rejections=len(rows),matching_header_fixtures=len(structural),subprocess_calls=0)))
if __name__=='__main__':main()
