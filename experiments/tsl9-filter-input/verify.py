"""Read-only raw/ELF/typed-control verification; optional create-only receipt."""
from pathlib import Path
import argparse,hashlib,json,runpy
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
 s=json.loads((HERE/'spec.json').read_bytes())
 for name,h in s['pinned_experiment_inputs'].items():assert sha(HERE/name)==h,('experiment drift',name)
 firmware=ROOT/s['firmware'];assert sha(firmware)==s['firmware_sha256'];raw=firmware.read_bytes()
 r=runpy.run_path(str(HERE/'build-leaf.py'),run_name='ELF_reader_only');parse=r['elf']
 results=[]
 for mode in ['c','cpp']:
  for group,trial,object_name,ranges,expected_undef in [('input','input-v2','input.o',s['input_regions'],['tsl9_filter_program_18ba2']),
                                                   ('leaf','leaf-v2','leaf.o',s['leaf_regions'],[])]:
   p=HERE/'build'/trial/mode;receipt=json.loads((p/'measurement.json').read_bytes())
   for name,h in receipt['artifacts'].items():assert sha(p/name)==h['sha256'],('artifact drift',name)
   b,sections,symbols,relocs=parse(p/object_name)
   functions={x['name']:x for x in symbols if x['bind']==1 and x['type']==2 and x['section']!=0}
   assert set(functions)=={x[0]for x in ranges}
   for name,va,size in ranges:
    f=functions[name];sec=sections[f['section']]
    assert f['value']==0 and f['size']==size and sec['name']=='.text.'+name
    assert sec['flags']==6 and sec['size']==size and sec['align']==2
   assert sorted(x['name']for x in symbols if x['section']==0 and x['name'])==expected_undef
   assert not[x for x in symbols if x['section']==0xfff1 and x['bind']!=0]
   actual=sorted((x['section'],x['offset'],x['type'],x['target'],x['addend'])for x in relocs)
   expected=sorted(tuple(x)for x in s[group+'_relocations'])
   assert actual==expected,(group,'typed relocation mismatch')
  p=HERE/'build/input-v2'/mode
  b,sections,symbols,relocs=parse(p/'INPUT-LEAF-ONLY-NOT-FIRMWARE.elf')
  functions={x['name']:x for x in symbols if x['bind']==1 and x['type']==2}
  assert set(functions)=={x[0]for x in s['input_regions']+s['leaf_regions']}
  assert not[x for x in symbols if x['section']==0 and x['name']]
  assert not[x for x in symbols if x['section']==0xfff1 and x['bind']!=0]
  checked=[]
  for group,rs in [('input',s['input_regions']),('filter',s['leaf_regions'])]:
   lo=rs[0][1];hi=rs[-1][1]+rs[-1][2]
   sec=next(x for x in sections if x['name']=='.'+group)
   assert sec['address']==lo and sec['size']==hi-lo and sec['flags']==6
   code=b[sec['offset']:sec['offset']+sec['size']]
   assert code==raw[lo-0x8000:hi-0x8000]
   for name,va,size in rs:
    f=functions[name];assert f['section']==sec['index']and f['value']==va and f['size']==size
   checked.append(dict(group=group,VA=[hex(lo),hex(hi)],bytes=len(code),sha256=hashlib.sha256(code).hexdigest()))
  results.append(dict(mode=mode,ranges=checked,strong_FUNC=len(functions),typed_control_relocations=12,
                      full_native_bytes_equal=True,global_ABS_provider=False,undefined_symbols=[]))
 assert (HERE/'build/input-v2/c/INPUT-LEAF-ONLY-NOT-FIRMWARE.elf').read_bytes()==(HERE/'build/input-v2/cpp/INPUT-LEAF-ONLY-NOT-FIRMWARE.elf').read_bytes()
 report=dict(schema='TSL9-filter-input-static-verification-v1',passed=True,spec_sha256=sha(HERE/'spec.json'),
             firmware_sha256=sha(firmware),results=results,original_function_count=2,architecture_regions=26,
             complete_native_bytes=418,original_instruction_records=139,
             unresolved_indirect_resident_ports=s['resident_ports'],ordinary_C_ABI_proved=False,
             resident_identity_or_clobber_ABI_proved=False,universal_semantic_proof=False,
             hardware_validated=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,network=False,
             combined_ELF_sha256=sha(HERE/'build/input-v2/c/INPUT-LEAF-ONLY-NOT-FIRMWARE.elf'))
 out=HERE/'verification.json'
 if a.write:
  assert not out.exists(),'create-only receipt'
  out.write_bytes((json.dumps(report,indent=2,sort_keys=True)+'\n').encode())
 else:assert json.loads(out.read_bytes())==report
 print(json.dumps(report))
if __name__=='__main__':main()
