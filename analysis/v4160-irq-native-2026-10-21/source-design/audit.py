"""Read existing retained source/IR; never compile or execute target code."""
from pathlib import Path
import hashlib,json,re
H=Path(__file__).resolve().parent; R=H.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
    if not x:raise ValueError(m)
def run():
    prefix='apk-analysis/tsl9-v4160-placement-2026-10-21/compiler-review/'
    refs=['experiments/tsl9-v4160-interrupt-registers/src/'+n for n in ['interrupt_registers.c','interrupt_registers.h','irq_io.h']]
    refs += ['apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/abi-review/verification.json',prefix+'results.json',prefix+'final-audit.json']
    original=json.loads((R/refs[3]).read_text())
    helperfacts=[]
    for section in original['ranges'][1:]:
        rows=section['rows'];need(section['byte_count']==30 and rows[0]['opcode'].startswith('beqz a1'),'30-byte branch-first source')
        helperfacts.append(dict(start=section['start'],bytes=30,first_branch=rows[0],rows=rows))
    need(len(helperfacts)==4,'four helpers')
    facts=[]
    for name,rel in [
      ('original_c','build/blocked-ca0d54326f53496c858b4187a632a3a2-c/interrupt_registers.ll'),
      ('original_cpp','build/blocked-9271b6d5152243dd9f0c2cfa5aa28f61-cpp/interrupt_registers.ll'),
      ('return_c','build/return-commit-b1bc9c790e004e1b851a641436de6b1b/c/interrupt_registers.ll'),
      ('return_cpp','build/return-commit-b1bc9c790e004e1b851a641436de6b1b/cpp/interrupt_registers.ll')]:
        path=prefix+rel;refs.append(path);text=(R/path).read_text()
        funcs=re.findall(r'define[^\n]*@(tsl9_rebuild_rcc_registers_\w+)\([^\n]*\) [^{]*\{(.*?)\n\}',text,re.S)
        need(len(funcs)==4,'four retained helper IR bodies')
        for fn,body in funcs:
            terms=['load volatile i32',' = or i32',' = xor i32',' = and i32',' = select i1','store volatile i32','  br i1']
            sites=[body.index(t) for t in terms];need(sites==sorted(sites),'actual common load/select/store before branch')
            need('ret i32' in body,'return retained')
            facts.append(dict(profile=name,function=fn,ordered_terms=terms,positions=sites,value_return_bridge='tail call i32 asm' in body))
    index=json.loads((R/(prefix+'results.json')).read_text())
    need(len(index['results'])==8 and all(not f['native_compilation_succeeded'] for f in index['results']),'all eight recorded native failures')
    return dict(schema='TSL9-IRQ-native-source-design-v1',passed=True,
      inputs=[dict(path=p,sha256=sha(R/p)) for p in refs],original_helpers=helperfacts,retained_ir_facts=facts,
      recorded_native_failed_profiles=8,recorded_functions_failed_per_profile=5,
      proposal=dict(branch_local_RMW=True,offset_interface=True,branch_specific_output_only_base_LUI=True,dynamic_helper_mask_A0_identity=True,main_per_use_immediate_mask_output_A0=True,actual_return_is_bound_A0=True,
                    four_register_allocator_requires_exact_A1_proof=True,disable_observed_outliner_only_if_locally_documented=True),
      limits=dict(proposal_compiled=False,allocator_root_cause_fully_proved=False,no_stack_native_proved=False,RA_A2_A3_native_preservation_proved=False,normal_boundary_only=True,asynchronous_equivalence_proved=False,target_executed=False,network=False,hardware=False,BIN_created=False,parent_model_edited=False,compile_profile_search=False))
if __name__=='__main__':
    result=run();path=H/'verification.json'
    if path.exists():need(json.loads(path.read_text())==result,'read-only replay exact')
    else:path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,original_helpers=4,IR_helper_bodies=16,failed_profiles=8,verification_sha256=sha(path))))
