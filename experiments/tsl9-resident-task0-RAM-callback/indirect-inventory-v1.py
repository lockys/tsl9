"""Inventory original instructions of the actual verified candidate;never execute them."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1];P=R/'experiments/tsl9-resident-root-chain-callees'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory(expected_sha256):
    pins=json.loads((HERE/'evidence-v1.json').read_bytes());need(all(sha(R/p)==h for p,h in json.loads((R/'experiments/tsl9-resident-callback-slot-binding/evidence-v1.json').read_bytes())['whole_reader_inputs'].items())and sha(R/pins['mapping_proof'])==pins['mapping_proof_sha256'],'Exact frozen whole readers and conditional mapping proof')
    e=json.loads((HERE/'evidence-v1.json').read_bytes());obj=HERE/'build/composition-v1/c/candidate.o';need(len(expected_sha256)==64 and sha(obj)==expected_sha256 and sha(HERE/'build/composition-v1/cpp/candidate.o')==expected_sha256,'Exact actual C/C++ object witnesses');O=runpy.run_path(str(P/'verify-ownership-v3.py'),run_name='native_ownership');q=O['inspect'](obj);assert q['passed'];owned=set(q['_byte_map']);raw=(R/e['firmware']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['firmware_sha256'];intervals=[]
    for pc in sorted(owned):
        if intervals and intervals[-1][1]==pc:intervals[-1][1]+=1
        else:intervals.append([pc,pc+1])
    def read(pc,size):
        source=pc if 0x40000<=pc<0x6ea66 else pc-0x20000000+0x40270
        assert 0x40000<=source and source+size<=0x6ea66
        return raw[source-0x40000:source-0x40000+size]
    ops={}
    for start,end in intervals:
        pc=start
        while pc<end:
            b=read(pc,2);width=4 if b[0]&3==3 else 2;assert pc+width<=end;ops[pc]=dict(PC=pc,bytes=read(pc,width).hex(),width=width);pc+=width
    assert len(owned)==36852 and len(ops)==12721
    typed=[json.loads(x)for x in q['_typed_relations']];rel={(x[0][1],x[1]):x[3]for x in typed if x[0][0]=='CODE'};rows=[];literals=[]
    for pc,o in sorted(ops.items()):
        word=int.from_bytes(bytes.fromhex(o['bytes']),'little');width=o['width'];rd=rs1=imm=None
        if width==4 and word&0x707f==0x67:rd=(word>>7)&31;rs1=(word>>15)&31;imm=word>>20;imm=imm-4096 if imm&2048 else imm
        elif width==2 and word&0xf07f in [0x8002,0x9002]and (word>>7)&31:rd=1 if word&0x1000 else 0;rs1=(word>>7)&31;imm=0
        if rd is not None:
            row=dict(**o,rd=rd,rs1=rs1,immediate=imm,role='return'if rd==0 and rs1==1 and imm==0 else'encoded-register-transfer',destination_proved=False)
            previous=ops.get(pc-4)
            if width==4 and previous and previous['width']==4:
                high=int.from_bytes(bytes.fromhex(previous['bytes']),'little')
                if high&127==0x17 and(high>>7)&31==rs1:
                    target=(pc-4+(high&0xfffff000)+imm)&0xfffffffe
                    assert rel.get((pc-4,23))==['CODE',target]and rel.get((pc,24))==['CODE',pc-4]
                    row.update(role='encoded-static-AUIPC-JALR-pair',pair_PC=pc-4,target=target,destination_bytes_included=target in owned,typed_HI_LO_roles_verified=True)
            rows.append(row)
        if width==4 and word&127==0x37 and (word>>7)&31:
            nxt=ops.get(pc+4);reg=(word>>7)&31
            if nxt and nxt['width']==4:
                low=int.from_bytes(bytes.fromhex(nxt['bytes']),'little')
                if low&0x707f==0x13 and(low>>7)&31==(low>>15)&31==reg:
                    val=low>>20;val=val-4096 if val&2048 else val;value=((word&0xfffff000)+val)&0xffffffff
                    if 0x40000<=value<0x6ea66 or 0x20000000<=value<0x20003618:literals.append(dict(PC=pc,value=value,register=reg,destination_bytes_included=value in owned,decoded_adjacent_sequence_only=True,function_pointer_role_proved=False))
    counts={k:sum(x['role']==k for x in rows)for k in ['return','encoded-static-AUIPC-JALR-pair','encoded-register-transfer']};unresolved=[x for x in rows if x['role']=='encoded-register-transfer'];literal=next(x for x in literals if x['PC']==0x55d2e);assert literal['value']==0x56cdc and literal['destination_bytes_included']
    out=dict(schema='TSL9-whole-native-original-instruction-indirect-inventory-v1',passed=True,source_object=obj.relative_to(R).as_posix(),source_object_sha256=sha(obj),SDK_firmware=e['firmware'],SDK_firmware_sha256=e['firmware_sha256'],CODE_bytes=len(owned),instructions=len(ops),CODE_intervals=intervals,indirect_transfers=rows,counts=counts,register_transfer_sites_requiring_separate_binding_analysis=unresolved,numeric_region_literal_sequences=literals,literal56CDC=literal,named_UND=q['named_UND'],static_pairs_do_not_prove_global_execution_or_actual_memory_mapping=True,prior_conditional_binding_proofs_not_overridden=True,register_transfer_count_is_not_a_missing_function_count=True,raw_literal_sequences_do_not_prove_function_pointer_roles=True,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args();saved=json.loads((HERE/'audit-result-v1.json').read_bytes());need(saved['inventory_checker_sha256']==sha(__file__),'Inventory checker matches full retained audit');v=inventory(saved['composition']['c']['object_sha256']);need(v==saved['indirect_inventory'],'Actual inventory equals full retained audit')
    if a.output:
        target=HERE/a.output;need(target.parent==HERE and not target.exists(),'Create-only inventory receipt');target.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,CODE_bytes=v['CODE_bytes'],instructions=v['instructions'],counts=v['counts'],register_transfer_count_is_not_missing_function_count=True,new_BIN=False)))
