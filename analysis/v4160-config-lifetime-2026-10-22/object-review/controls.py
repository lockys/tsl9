"""Four bounded source-object/IR/raw-field negatives; never execute target code."""
from pathlib import Path
import uuid
def run(R,root,folder):
    m=R.context(root);fields,_,ctx,_,E=m['context'](root);e=E(folder/'ota_handler.o');s=next(s for s in e.symbols if s['name']==R.NAME)
    body=e.function_bytes(s);rows=fields['rows'](body,0,ctx);text=(folder/'ota_handler.ll').read_text();out=R.HERE/'build'/('controls-'+uuid.uuid4().hex);out.mkdir(parents=True)
    result=[]
    def reject(label,value,check,needle,suffix):
        p=out/(label+suffix);p.write_bytes(value.encode() if isinstance(value,str) else value)
        try:check(value)
        except ValueError as err:
            R.need(needle in str(err),'Intended object gate '+label+': '+str(err));result.append(dict(case=label,rejected=True,actual_mutated_input_sha256=R.sha(p),reason=str(err)));return
        raise ValueError('Accepted object negative '+label)
    reject('IR_backing_shrunk_to2',text.replace('alloca [4 x i8]','alloca [2 x i8]',1),R.ir_object,'full4-byte aligned','.ll')
    changed=text.replace('phi i32 [ 2,','phi i32 [ 4,',1);R.need(changed!=text,'Actual length2 phi present')
    reject('packet_length_changed_to_backing4',changed,R.ir_object,'Only correlated S2/E0','.ll')
    # Claimed larger IR storage with identical observed2B accesses is insufficient:
    # its whole span must fit the actual machine frame, not just the first2B.
    enlarged=text.replace('alloca [4 x i8]','alloca [8 x i8]',1).replace('(i64 4, ptr nonnull','(i64 8, ptr nonnull')
    reject('safe_first2_but_claimed8B_overlaps_save',enlarged,lambda _:R.storage(rows,m['projection'],8),
           'aliases any declared backing byte','.ll')
    sec=e.sections[s['index']]
    restore=next(r for r in rows if r['op']=='lw' and r['rs1']==2 and r['rd']==22);found=None
    for bit in range(restore['bytes']*8):
        bad=bytearray(body);bad[restore['PC']+bit//8]^=1<<(bit%8)
        try:decoded=fields['rows'](bytes(bad),0,ctx);one=next(r for r in decoded if r['PC']==restore['PC'])
        except ValueError:continue
        if one['op']==restore['op'] and one['rd']==restore['rd'] and one['rs1']==2 and one['immediate']!=restore['immediate']:
            found=bad;break
    R.need(found is not None,'Actual single-field savedS6 restore mutation');blob=bytearray(e.raw);blob[sec['offset']:sec['offset']+len(body)]=found
    reject('savedS6_wrong_restore_slot',bytes(blob),lambda b:R.storage(fields['rows'](b[sec['offset']:sec['offset']+len(body)],0,ctx),m['projection']),
           'reload uses its own saved slot','.o')
    return result
