"""Reset/config-I/O shortcut -> builtin table publication, static proof only.

No target ISA, NV contents, heap/table memory, copy, callback or MMIO runner.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_initial_table_extent_static as previous
import check_v4160_config_io_static as io
import check_v4160_app_nv_callbacks_static as callbacks
import check_v4160_heap_bootstrap_static as heap
import check_v4160_post_config_static as post

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-post-shortcut-preservation-static.json')
CHOICES={'base_zero':{20:22},'read_callback_zero':{20:36,42:22},
 'write_callback_zero':{20:36,42:44,46:22},'equal_readback':{20:36,42:44,46:48,58:22}}


def reset_body(raw,index,ctx):
    pc=heap.DETAILS[index][2];n=io.decode(raw,pc)
    check(set(n)=={pc,pc+4,pc+8},'shortcut reset boundaries')
    for p,f in ((pc,dict(op='lui',rd=15,imm=0x20003000)),
        (pc+4,dict(op='store',rs1=15,rs2=0,imm=ctx-4-0x20003000,width=4)),
        (pc+8,dict(op='jr',rs1=1))):init.g(n,p,'shortcut reset operand '+hex(p-pc),**f)
    check(sha256(raw).hexdigest()==heap.DETAILS[index][-1],'shortcut reset whole identity')
    return {'start':hex(pc),'bytes':10,'sha256':sha256(raw).hexdigest(),'write':hex(ctx-4),'A0_SP_RA_S_GP_not_defined':True}


def shortcut(raw,index,ctx):
    pc,digest=io.DETAILS[index];n=io.decode(raw,pc);s=io.specs(pc,ctx+80,ctx)
    check(set(n)==set(s)|{pc+o+d for o in (72,100,118) for d in (0,4)},'shortcut full I/O boundaries')
    for p,f in s.items():init.g(n,p,'shortcut IO operand '+hex(p-pc),**f)
    for off,target in ((72,0x20000040),(100,0x2000039c),(118,0x20000110)):init.pair(n,pc+off,1,target,'shortcut IO direct pair')
    check(len(raw)==160 and len(n)==61 and sha256(raw).hexdigest()==digest,'shortcut full IO identity')
    edges={}
    for p,d in n.items():
        if d['op']=='jr':q=[]
        elif d['op']=='jump':q=[d['target']]
        elif d['op'] in ('beqz','bnez','beq','blt'):q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'shortcut whole IO CFG');edges[p]=q
    paths={}
    for name,choices in CHOICES.items():
        selected={p:([pc+choices[p-pc]] if p-pc in choices else q) for p,q in edges.items()}
        seen=set();pending=[pc]
        while pending:
            p=pending.pop()
            if p in seen:continue
            seen.add(p);pending.extend(selected[p])
        check(pc+34 in seen and all(len(selected[p])==1 for p in seen if p!=pc+34) and selected[pc+34]==[],'shortcut finite selected chain '+name)
        check(not any(p in seen for p in (pc+76,pc+104,pc+122,pc+84,pc+128,pc+132,pc+154,pc+156)),'shortcut no cache/heap/per-write effects '+name)
        calls=[p for p in seen if n[p]['op']=='call_indirect']
        check(calls==([pc+52] if name=='equal_readback' else []),'shortcut exact callback set '+name)
        stores=[d for p,d in n.items() if p in seen and d['op']=='store']
        check({(d['rs1'],d['imm'],d['width']) for d in stores}=={(2,o,4) for o in (16,20,24,28)},'shortcut only four saved-frame stores '+name)
        check(pc+22 in seen and all(not d.get('rd')==10 for p,d in n.items() if p in seen and p>pc+22 and p<pc+36),'shortcut forced reply1 '+name)
        paths[name]={'instruction_PCs':[hex(p) for p in sorted(seen)],'callback_PC':hex(pc+52) if calls else None,
            'heap_allocate_fill_free_or_per_write_call':False,'local_reply':1}
    return {'start':hex(pc),'bytes':160,'sha256':digest,'selected_paths':paths,'complete_local_IO_body_reused':True}


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage);pp=post.derive(app,carriers,header)['profiles']
    rd=next(d for d in callbacks.APP_BODIES if d[0]=='read');r,pc,size,count,digest=rd
    read=callbacks.body(app[pc-0x8000:pc-0x8000+size],r,pc,count,digest)
    check(read['encoded_GPR_writes']==[1,2,10,11,12,14,15],'shortcut read wrapper exact GPRs')
    bindings=callbacks.bindings(app)
    check(bindings[0]['value']=='0x8077c00' and bindings[1]['value']=='0x1979a','shortcut original NV/read source witnesses')
    rn={d['pc']:d for d in read['instructions']}
    init.g(rn,0x197a6,'shortcut read wordcount->bytes',op='slli',rd=12,rs1=11,imm=2)
    init.g(rn,0x197aa,'shortcut read source argument',op='mv',rd=11,rs2=10)
    init.g(rn,0x197ac,'shortcut read destination argument',op='mv',rd=10,rs2=14)
    profiles=[]
    for i,(data,prior,prof) in enumerate(zip(carriers,parent['profiles'],pp)):
        ctx=int(prof['count_byte'],16)-1;pc=int(prof['target'],16);hook=int(prof['input_byte'],16)-21+48
        reset=reset_body(init.binding.take(data,heap.DETAILS[i][2],10),i,ctx)
        config=shortcut(init.binding.take(data,io.DETAILS[i][0],160),i,ctx)
        check(prior['cut_before_call']['target']==reset['start'] and prof['calls'][6]['target']==config['start'],'shortcut actual post call joins')
        copy_source=(0x405a2,0x405e2)[i]
        copy=callbacks.body(init.binding.take(data,copy_source,58),'copy',0x20000332,18,init.binding.COPY_HASH)
        check(copy['encoded_GPR_writes']==[13,14,15,16] and init.binding.word(data,0x4004c)==0x20000332,'shortcut candidate read-copy join')
        # Initial fill40 owns count=0; all intervening known direct writes are
        # disjoint under the previous nominal heap/frame/nointerference premises.
        check({'address':hex(ctx),'bytes':40} in prof['fixed_zero_fill_requests'],'shortcut initial context zero40 witness')
        check(previous.previous.previous.separated(ctx-4,4,ctx+1,1),'shortcut reset excludes count')
        n={d['pc']:d for d in prof['instructions']}
        for off,fields in ((200,dict(op='load',rd=15,rs1=8,imm=1,width=1)),
            (202,dict(op='load',rd=13,rs1=9,imm=ctx+40-0x20003000,width=4)),
            (220,dict(op='store',rs1=14,rs2=12,imm=0,width=4)),
            (242,dict(op='store',rs1=14,rs2=12,imm=0,width=4)),
            (256,dict(op='store',rs1=8,rs2=14,imm=1,width=1)),
            (260,dict(op='store',rs1=15,rs2=12,imm=0,width=4))):init.g(n,pc+off,'shortcut builtin operand '+hex(off),**fields)
        check(not any(d.get('rd')==10 for p,d in n.items() if p>=pc+200),'shortcut post suffix preserves IO reply')
        check(all(previous.previous.previous.separated(previous.T+4*j,4,hook,4) and
            previous.previous.previous.separated(previous.T+4*j,4,ctx+1,1) for j in range(3)),'shortcut builtin words exclude hook/count')
        profiles.append({'label':prior['label'],'post_start':hex(pc),'reset':reset,'config_IO':config,
            'reused_copy_sha256':copy['sha256'],'copy_source':hex(copy_source),
            'count_byte':prof['count_byte'],'capacity_byte':prof['capacity_byte'],'table_pointer_word':prof['table_slot'],
            'hook_word':hex(hook),'nominal_P':hex(previous.P),'nominal_T':hex(previous.T),
            'builtin_word_stores':[{'address':hex(previous.T+4*j),'value':value} for j,value in enumerate(prof['registered_literals'])],
            'post_suffix_count':3,'conditional_post_reply':1,'actual_source_data_or_installed_binding_proved':False})
    return {'schema':'TSL9-post-shortcut-preservation-static-v1','profile':parent['profile'],'APP_sha256':sha256(app).hexdigest(),
        'scope':'extend previous nominal first-allocation proof through reset/config-I/O shortcuts andthreebuiltin stores topostRET; allfullsourcebodies reused',
        'profiles':profiles,'reused_read_wrapper':{'start':read['start'],'bytes':30,'sha256':read['sha256']},
        'shortcut_premise':'IO gateconfig+8/+56/+60 absent OR allgatesnonzero, initialreadtarget1979a andfresh4004c matchingcopy, completedfourbyte transfer whose LE result equals freshconfig+8; no actualNVvalue orshortcutreachability proved',
        'read_contract':'num1 ->bytes4; outputIO-SP+12..15; readwrapper16Bchild onlysavedRAatIO-SP-4..-1; matching58Bcopy writes4outputbytes and4002420c only, no S/GP/SP/RA definitions',
        'frame_contract':'IO savesfourwords atIO-SP+16..31; output+12..15 disjoint; readwrappersavedRA belowIOframe. Frames/code/globals/ownedheap andMMIO mustnotadverselyalias; allsavedwords valid andrequiredcontexts preserved',
        'readback_boundary':'source copiedasfour separate LBU/SB transfers, not atomicNVwordread; coherence/stability or exactfourbyte-result premise needed; callbackA0forced0 isignored byIO compare',
        'closed_shortcut_effects':'resetonlywritesctx-4; IO localstores onlyfoursavedwords; equalcase onlyreadwrapper/copy called; noallocation/fill/free/per-writecallback/cacheclears orpayloadstore',
        'preservation':'underprevious freshH/L andnominalheap/noalias/noexternalinterference premises plusmatchingcompletedshortcut, initialcontextfill40 givescount0, reset/core/fill/shortcut do not changeit; table/capacity/P/allocatedheader survive to post+200',
        'builtin_publication':'freshn=0,Tprime=T; threeorderedwordstores atT,T+4,T+8 carryprofileliterals; bytecount3 writtenbeforethirdword; N0>=14 ensuresall3wordsinsidecallbacktable anddisjointhook/count/header',
        'extent_at_post_return':'P=200045b4 allocationnotfreed byshortcut; T=200047f4,c=N0,count3 remainvalidnominalpayloadfacts throughpostRET understatedpremises; postA0=1, not NV/hardware success',
        'boundary':'doesnotcover mismatchallocation/iteration/freepath, outerinitializer/APP19106/interveningtaskregistration orotherwriters; no actualallocationownership/time/providerclaim',
        'remaining':['mismatchpathalloc/fill/write/free effects andprivatefree20000110','outerinitializer/APP continuation table/hook preservation',
            'freshNV/callback/slot sourcevalues andactualinstalledproviders','MMIO/pollprogress, aliases/asynchronouswriters andobjectlifetime'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(app,carriers):
    # Signed/byte/address intervals and predicates only, no NV/frame/table model.
    output=set(range(12,16));saved=set(range(16,32));read_ra=set(range(-4,0))
    check(not output&saved and not output&read_ra and not saved&read_ra,'shortcut three frame extents disjoint')
    check(1<<2==4 and int.from_bytes(bytes.fromhex('007c0708'),'little')==0x08077c00,'shortcut wordcount/little-endian oracle')
    for row in previous.facts():
        cap=row['N0'];r=row['rounded_payload'];check(3<cap and previous.T+12<=previous.T+4*cap<=previous.P+r,'shortcut three builtins andnextindex3 fit')
    count=0
    for i,data in enumerate(carriers):
        pc=io.DETAILS[i][0];ctx=(0x2000319c,0x200031ec)[i];raw=init.binding.take(data,pc,160);nodes=io.decode(raw,pc)
        for off in (0,12,20,22,24,26,28,30,32,34,36,40,42,44,46,48,50,52,54,56,58):
            d=nodes[pc+off];w=d['size'];b=bytearray(raw);b[off:off+w]=(int.from_bytes(b[off:off+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
            try:shortcut(b,i,ctx)
            except RuntimeError as e:check(str(e).startswith('shortcut IO operand '),'specific shortcut IO mutation guard '+str(e))
            else:raise RuntimeError('shortcut IO mutation escaped')
            count+=1
        rp=heap.DETAILS[i][2];b=bytearray(init.binding.take(data,rp,10));b[4:8]=(int.from_bytes(b[4:8],'little')^(1<<20)).to_bytes(4,'little')
        try:reset_body(b,i,ctx)
        except RuntimeError as e:check(str(e).startswith('shortcut reset operand '),'specific shortcut reset mutation guard')
        else:raise RuntimeError('shortcut reset mutation escaped')
        count+=1
    raw=app[0x1979a-0x8000:0x197b8-0x8000];nodes=callbacks.decode(raw,0x1979a)
    for off in (0,4,12,16,18,20,24):
        d=nodes[0x1979a+off];w=d['size'];b=bytearray(raw);b[off:off+w]=(int.from_bytes(b[off:off+w],'little')^(1<<20 if w==4 else 4)).to_bytes(w,'little')
        try:callbacks.body(b,'read',0x1979a,13,callbacks.APP_BODIES[0][4])
        except RuntimeError as e:check(str(e).startswith('read instruction '),'specific read-wrapper mutation guard '+str(e))
        else:raise RuntimeError('shortcut read mutation escaped')
        count+=1
    check(count==51,'shortcut mutation census')
    print('PASS:4shortcut CFG chains/profile; three-frame/LE/count/layout algebra;51 IO/reset/read operand mutations rejected')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');o=parser.parse_args()
    app=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,size,digest in init.binding.PROFILES:
        raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==size and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
    coverage=sparse.derive(app,carriers,header,raw_hex,sparse.parser())
    ledger=derive(app,carriers,header,coverage);ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract()
    tests(app,carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'post shortcut exact ledger replay')
    print('PASS:reset/IO/read/copy/post suffix joins; conditional table/capacity/allocation/count3 to postRET; exact ledger')
    print('PASS:NO target execution; actualNV/otherIOpaths/laterwriters/installedprovider/lifetime UNPROVED')


if __name__=='__main__':main()
