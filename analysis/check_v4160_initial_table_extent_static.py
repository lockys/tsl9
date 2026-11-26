"""First post-bootstrap allocation/table extent: static case proof only.

No heap/list objects, target registers, MMIO, allocator or device execution.
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import check_v4160_task_registration_static as previous
import check_v4160_heap_bootstrap_static as heap
import check_v4160_allocation_core_static as core
import check_v4160_post_config_static as post
import check_v4160_config_buffer_source_static as source

init,sparse,check=previous.init,previous.sparse,previous.check
OUT=Path(__file__).with_name('v4160-initial-table-extent-static.json')
H,L=0x2000418c,0x7000
A,B,E=0x200043ac,0x200045ac,0x2000b184
P,T=0x200045b4,0x200047f4
SELECT={22:24,24:38,56:100,76:110,112:114,116:120,134:138}


def core_case(raw,index):
    pc=core.ENTRY;n=core.decode(raw);s=core.specs(core.DETAILS[index])
    check(set(n)==set(s),'initial allocation whole core boundaries')
    for p,f in s.items():core.message.guard(n,p,'initial allocation core operand '+hex(p-pc),**f)
    check(len(raw)==208 and sha256(raw).hexdigest()==core.DETAILS[index][-1],'initial allocation whole core identity')
    edges={}
    for p,d in n.items():
        if d['op']=='jr':q=[]
        elif d['op']=='jump':q=[d['target']]
        elif d['op'] in ('beqz','bnez','bne','bltu','bgeu'):q=[p+d['size'],d['target']]
        else:q=[p+d['size']]
        check(all(v in n for v in q),'initial allocation whole CFG');edges[p]=q
    selected={p:([pc+SELECT[p-pc]] if p-pc in SELECT else q) for p,q in edges.items()}
    pending=[pc];seen=set()
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(selected[p])
    check(all(len(selected[p])==1 for p in seen if p!=pc+202) and selected[pc+202]==[],'initial allocation case single chain')
    check(pc+96 not in seen and pc+204 not in seen and pc+176 in seen and pc+168 in seen,'initial allocation split/no-search/no-fallback path')
    incoming={p:0 for p in seen}
    for p in seen:
        for q in selected[p]:incoming[q]+=1
    check(incoming[pc]==0 and all(v==1 for p,v in incoming.items() if p!=pc),'initial allocation case acyclic chain')
    return {'runtime_entry':hex(pc),'whole_body_sha256':sha256(raw).hexdigest(),
        'selected_successors':{hex(pc+p):hex(pc+q) for p,q in SELECT.items()},
        'selected_instruction_PCs':[hex(p) for p in sorted(seen)],'selected_instruction_count':len(seen),
        'fallback_or_search_backedge_on_selected_path':False,'whole_operand_identity_reused':True}


def facts():
    g=heap.geometry(H,L)
    check((g['small_head'],g['large_head'],g['sentinel'],g['small_size'],g['large_size'])==(A,B,E,504,27600),'initial table nominal geometry')
    check(H<A<B<E and E+8==H+L and P==B+8 and P+27600==E,'initial table nonwrapping header/payload geometry')
    check(T==P+576 and 504+27600==28104,'initial table offset/accounting geometry')
    capacities=set();records=[]
    for byte in range(256):
        n=14+3*((byte>>2)+(byte&3));q=576+6*n;r=(q+3)&~3
        check(14<=n<=212 and n<=255 and 660<=q<=1848 and q<=r<=1848 and r%4==0,'initial table request domain')
        check(r==((q+3)&65535)&0xfffc and r>52,'initial table noU16wrap/large-head selection')
        gap=27600-r;remainder=gap-8
        check(gap>8 and 25744<=remainder<=26932,'initial table always split and positive remainder')
        check(P+r+8+remainder==E and P+q<=P+r and P+r<E,'initial table split remainder and payload bound')
        check(T+4*n+2*n==P+q and T+4*n<=P+r,'initial table callback/event partition fits allocation')
        capacities.add(n)
        records.append({'input_byte':byte,'N0':n,'request':q,'rounded_payload':r,
            'split_header':hex(P+r),'split_payload_size':remainder,'payload_end':hex(P+r),
            'table_end':hex(T+4*n),'event_end':hex(P+q)})
    check(capacities==set(range(14,213,3)),'initial table exact67 capacities')
    return records


def derive(app,carriers,header,coverage):
    parent=previous.derive(app,carriers,header,coverage)
    hp=heap.derive(app,carriers,header);pp=post.derive(app,carriers,header)['profiles']
    operand,geometry=heap.app_operands(app);check((int(operand['H'],16),int(operand['L'],16))==(H,L),'initial table APP H/L source operands')
    rows=facts();profiles=[]
    for i,(data,hprof,prof,registration) in enumerate(zip(carriers,hp['profiles'],pp,parent['profiles'])):
        pc=int(prof['target'],16);ctx=int(prof['count_byte'],16)-1;state=ctx+80;hook=int(registration['hook_word'],16)
        nodes={d['pc']:d for d in prof['instructions']}
        bootstrap=next(b for b in hprof['bodies'] if b['role']=='bootstrap')
        walker=next(b for b in hprof['bodies'] if b['role']=='walker')
        # These are the complete already-pinned nominal bootstrap writes, not a
        # constructed heap image or an interpreter traversal of header objects.
        check(int(hprof['config_base'],16)==state and core.DETAILS[i][5]==ctx,'initial table shared config/account base')
        case=core_case(init.binding.take(data,core.DETAILS[i][0],208),i)
        init.g(nodes,pc+118,'initial table capacity store',op='store',rs1=8,rs2=10,imm=2,width=1)
        init.g(nodes,pc+136,'initial table reply store',op='store',rs1=9,rs2=10,imm=state+64-0x20003000,width=4)
        init.g(nodes,pc+142,'initial table capacity N1 read',op='load',rd=12,rs1=8,imm=2,width=1)
        init.g(nodes,pc+164,'initial table Pprime read',op='load',rd=15,rs1=9,imm=state+64-0x20003000,width=4)
        init.g(nodes,pc+168,'initial table capacity N2 read',op='load',rd=14,rs1=8,imm=2,width=1)
        init.g(nodes,pc+174,'initial table T formation',op='addi',rd=15,rs1=15,imm=576)
        init.g(nodes,pc+180,'initial table T store',op='store',rs1=9,rs2=15,imm=ctx+40-0x20003000,width=4)
        init.g(nodes,pc+190,'initial table event-base store',op='store',rs1=14,rs2=15,imm=ctx+72-0x20003000,width=4)
        check(prof['table_slot']==registration['leaf']['table_pointer_word'] and prof['capacity_byte']==registration['leaf']['capacity_byte'],'initial table registration consumer same slots')
        prefix_calls=[c for c in prof['calls'] if pc+78<=int(c['window_start'],16)<pc+194]
        check([(c['role'],c['target']) for c in prefix_calls]==[('allocate','0x20000040'),('fill-reply','0x2000039c')],'initial table exact calls between bootstrap and late-init cut')
        fill_source=(0x4060c,0x4064c)[i]
        fill=source.fill_contract(init.binding.take(data,fill_source,46))
        check(fill['encoded_GPR_writes']==[10,14,15] and fill['encoded_S0_S1_S2_SP_RA_nonwrites'],'initial table fill register preservation')
        # At the original fixed H/L, every dynamic heap write on this first-fit
        # case is above all context fields. Account+6 and stack writes are kept
        # as separately classified conditions; no blanket callee nonwrite claim.
        globals_live=((ctx+2,1),(state+64,4),(ctx+40,4),(ctx+72,4),(hook,4))
        for a,w in globals_live:
            check(a+w<=H and previous.previous.separated(ctx+6,2,a,w),'initial table heap/account disjoint live globals')
        for r in rows:
            for a,w in globals_live:check(previous.previous.separated(P,r['request'],a,w),'initial table fill disjoint live globals')
        profiles.append({'label':registration['label'],'post_body_start':hex(pc),
            'prefix_start_after_bootstrap_return':hex(pc+78),'prefix_end_exclusive_before_late_init':hex(pc+194),
            'bootstrap_body_sha256':bootstrap['sha256'],'walker_body_sha256':walker['sha256'],
            'reused_fill_sha256':fill['sha256'],'first_fit_core_case':case,
            'capacity_byte':prof['capacity_byte'],'account_halfword':hex(ctx+6),'allocation_reply_word':prof['allocation_reply_slot'],
            'table_pointer_word':prof['table_slot'],'event_pointer_word':prof['event_table_slot'],'hook_word':hex(hook),
            'nominal_P':hex(P),'nominal_T':hex(T),
            'cut_before_call':prof['calls'][5],
            'all_source_premises_or_actual_installed_binding_proved':False})
    return {'schema':'TSL9-initial-table-extent-static-v1','profile':parent['profile'],'APP_sha256':sha256(app).hexdigest(),
        'scope':'new first-allocation/table-extent composition; existing full APP/heap/bootstrap/walker/core/fill/post/registration bytes reused, no newly reconstructed C bytes',
        'APP_heap_operand_witness':operand,'profiles':profiles,'capacity_cases':rows,
        'entry_premise':'at heap-bootstrap entry fresh config H=2000418c,L=7000, with matching code, normal accesses, valid frames disjoint from heap/globals and no adverse physical alias/external interference; original APP stores do not alone prove those fresh values',
        'bootstrap_facts':'A=200043ac,B=200045ac,E=2000b184; A.next=B,B.next=E,freeflags0,sizes504/27600; under stable coherent headers/global words walker has two nonsentinel nodes and sum28104, not universal traversal termination',
        'first_fit':'no intervening opaque call between bootstrap return and request formation; q=576+6*N0,R=roundup4(q),R>52; initial largeheadB!=E,flag0,size27600>=R,gap>8; no search/fallback; split and returnP=B+8=200045b4',
        'allocated_extent':'allocatedpayload[P,P+R), R660..1848; requestq<=R; remainderheaderP+R, remaindersize27600-R-8>=25744; nonwrapping within original large block',
        'snapshot_preservation_to_cut':'core success writes accountctx+6 and heapheaders plus childframe/MMIO; capacityctx+2 and replywordstate+64 do not overlap. Then fillwrites[P,P+q) andcontrolword4002420c, preservesS0/S1/SP/RA. Under statedphysical/frame/nointerference premises, N1=N2=N0,Pprime=P until post+194cut',
        'published_layout_to_cut':'callbacktableT=P+576=200047f4; eventbaseT+4*N0; callbackextent[T,T+4*N0), eventextent[T+4*N0,T+6*N0) bothinside[P,P+R); capacity0..255 truncation loses no N0 bits',
        'hook_exclusion_to_cut':'nominal heap/payload/table are above bothhookwords321c/326c and context countbytes; first allocation/core/fill/pointer publications do not directly touch hook under physicalnonaliaspremises',
        'registration_connection':'if later state preserves this T/capacity and owned allocation, n<c bounds the registration word inside table and away fromhook/count/frame; not asserted after remaining calls',
        'remaining_boundary':'proof ends before post+194 late-init andpost+198 config-I/O, later dynamicbuiltin stores, field44/intermediate services andregistrationcaller40080; all later writers/lifetimes still require proof',
        'remaining':['post+194/+198 callees and later table writers','fresh heapH/L/source-field preservation before bootstrap',
            'allocation ownership/lifetime andtable/capacity preservation toregistration','actual installed providers and MMIO/asynchronous effects'],
        'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    rows=facts();check(len(rows)==256,'initial table all source-byte cases')
    count=0
    for row in rows:
        n=row['N0'];r=row['rounded_payload'];q=row['request']
        for index in range(n):
            a=T+4*index
            check(P<=a and a+4<=T+4*n<=P+q<=P+r,'initial table every admitted word footprint within payload')
            check(T+4*n+2*n==P+q<=E,'initial table event extent closes partition')
            count+=1
    check(count==28928,'initial table admitted footprint census')
    # Only scalar range facts and a selected CFG chain; no heap state exists.
    cases=((38,1<<20),(46,4),(56,1<<20),(110,4),(114,4),(116,1<<20),(124,1<<20),
        (134,1<<20),(146,1<<20),(156,4),(166,4),(168,4),(176,4),(180,4),(192,1<<20))
    mutations=0
    for i,data in enumerate(carriers):
        raw=init.binding.take(data,core.DETAILS[i][0],208);nodes=core.decode(raw)
        for off,flip in cases:
            b=bytearray(raw);w=nodes[core.ENTRY+off]['size'];b[off:off+w]=(int.from_bytes(b[off:off+w],'little')^flip).to_bytes(w,'little')
            try:core_case(b,i)
            except RuntimeError as e:check(str(e).startswith('initial allocation core operand '),'specific first-fit mutation guard '+str(e))
            else:raise RuntimeError('initial allocation mutation escaped')
            mutations+=1
    check(mutations==30,'initial allocation mutation census')
    print('PASS:256 source bytes/67capacities;28928 admitted footprints; rounded/split/layout algebra;30 core operand mutations rejected')


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
    tests(carriers);output=(json.dumps(ledger,indent=1,ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'initial table exact ledger replay')
    print('PASS:original bootstrap/core/fill/post/registration joins; first-fit CFG and nominal table allocation extent tolate-init cut; exact ledger')
    print('PASS:NO target execution; actualfreshH/L/laterwriters/ownership/installedprovider UNPROVED')


if __name__=='__main__':main()
