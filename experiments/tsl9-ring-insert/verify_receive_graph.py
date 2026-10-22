#!/usr/bin/env python3
"""Link/replay seven original-layout code spans; never execute this ELF."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
OBJECT='NOT-A-FIRMWARE-RECEIVE-GRAPH.elf'
ELF_PIN='86a8aa3dd403666b7928d7966350f643ba0ed14e0e57bc2fb620d82b83161f27'
AGGREGATE_PIN='ea0695de5c5abe95f730285256d89dd5e63f265b7d83f5a70687e08f6e4e828f'
LINKER_PIN='1aa23340bbeec3c7c9fb35f8d50d17e6921d509b63bb921de0bef5c8e30316e5'
PIPE_CHECKER='experiments/tsl9-packet-receive/verify_pipeline.py'
PIPE_PIN='45df02f193dc1f74e08b585fe4d311d58a7f01a9b7e8f131ce01ca594f806ea4'
RING_PIN='36099956b928fb6c7af0a171ed0306f7d42e3236243dce029103e6701f7b41b6'
SPI_PIN='8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8'
PARENT_RECEIPTS={'c':'7bdd8ba401febb256ab77bcf73db6fe73492da5701b70c421e0added3b541867',
 'cpp':'cb7a96f812a8fe396338bdea22de44650e0e3a261d67a95d488b2cde5b05e4a7'}
RING_RECEIPTS={'c':'c61f793250cb0c51fce0cc1756300fc5dec58274261827f24dbd0734d3161115',
 'cpp':'451182a600184814316a8cc728753a3d3144ebdec0e0b2679779bddfde2fdb3f'}
SPI_RECEIPTS={'c':'6df89fcec081df6256e34434fb5c933411af72957b02b70a7ec632854541b3e5',
 'cpp':'633ab1bb645a87ee29c38d99d28ca5f7ee20a6f936f4bcf472dda92996b1c319'}
SPECS=[
 ('consumer','.consumer',0x17002,62,[('tsl9_flag_consumer_entry_17002',0,8),('tsl9_flag_consumer_body',8,54)]),
 ('receiver','.receiver',0x16b0a,70,[('tsl9_receive_entry_16b0a',0,14),('tsl9_receive_body',14,56)]),
 ('read','.read',0x16994,72,[('tsl9_register_read_entry_16994',0,4),('tsl9_register_read_body',4,68)]),
 ('write','.write',0x16a30,76,[('tsl9_register_write_entry_16a30',0,4),('tsl9_register_write_body',4,72)]),
 ('spi','.spi',0x16896,72,[('tsl9_spi_transfer_entry_16896',0,8),('tsl9_spi_tx_poll_1689e',8,8),
   ('tsl9_spi_tx_ready_168a6',16,16),('tsl9_spi_rx_poll_168b6',32,8),('tsl9_spi_rx_done_168be',40,10),
   ('tsl9_spi_tx_wait_168c8',50,8),('tsl9_spi_timeout_168d0',58,4),('tsl9_spi_rx_wait_168d4',62,10)]),
 ('packet','.packet',0x16a7c,142,[('tsl9_receive_buffer_entry_16a7c',0,14),('tsl9_packet_receive_body',14,116),
   ('tsl9_packet_receive_finish_16afe',130,12)]),
 ('ring','.ring',0x12bc8,92,[('tsl9_ring_insert_entry_12bc8',0,8),('tsl9_ring_init_12bd0',8,16),
   ('tsl9_ring_scan_12be0',24,50),('tsl9_ring_finish_12c12',74,10),('tsl9_ring_advance_12c1c',84,8)])]
SECTION_ROWS=[('',0,0,0,0,0,0,0,0,0),
 ('.ring',1,6,0x12bc8,3016,92,0,0,2,0),('.spi',1,6,0x16896,18582,72,0,0,2,0),
 ('.read',1,6,0x16994,18836,72,0,0,2,0),('.write',1,6,0x16a30,18992,76,0,0,2,0),
 ('.packet',1,6,0x16a7c,19068,142,0,0,2,0),('.receiver',1,6,0x16b0a,19210,70,0,0,2,0),
 ('.consumer',1,6,0x17002,20482,62,0,0,2,0),('.text',1,6,0x17040,20544,0,0,0,2,0),
 ('.symtab',2,0,0,20544,1008,11,39,4,16),('.shstrtab',3,0,0,21552,85,0,0,1,0),
 ('.strtab',3,0,0,21637,891,0,0,1,0)]
PROGRAM_HEADERS=[[6,52,73780,73780,128,128,4,4],[1,0,73728,73728,180,180,4,4096],
 [1,3016,76744,76744,17528,17528,5,4096],[1685382481,0,0,0,0,0,6,0]]


def need(ok,message):
    if not ok:raise ValueError(message)


def sha(data):return hashlib.sha256(data).hexdigest()
def digest(path):return sha(Path(path).read_bytes())


def dependencies(language,llvm):
    need(digest(ROOT/PIPE_CHECKER)==PIPE_PIN,'frozen 494B checker')
    need(digest(HERE/'verify.py')==RING_PIN,'frozen ring checker')
    need(digest(ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py')==SPI_PIN,'frozen SPI checker/reader')
    need(digest(HERE/'receive_graph.ld')==LINKER_PIN,'frozen original-layout linker')
    parent=runpy.run_path(str(ROOT/PIPE_CHECKER));ring=runpy.run_path(str(HERE/'verify.py'))
    spi=runpy.run_path(str(ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'))
    parent_dir=ROOT/'experiments/tsl9-packet-receive/build/pipeline-verified-v2'/language
    ring_dir=HERE/'build/verified-v1'/language
    spi_dir=ROOT/'experiments/tsl9-spi-transfer-leaf/build/verified-v3'/language
    modules=[('494B',parent_dir,PARENT_RECEIPTS[language],parent),('ring',ring_dir,RING_RECEIPTS[language],ring),
             ('SPI',spi_dir,SPI_RECEIPTS[language],spi)]
    expected={ROOT/PIPE_CHECKER:PIPE_PIN,HERE/'verify.py':RING_PIN,
              ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py':SPI_PIN,HERE/'receive_graph.ld':LINKER_PIN,
              Path(__file__).resolve():digest(__file__)}
    records=[];inventories={}
    for name,directory,pin,module in modules:
        receipt=directory/'verification.json';need(digest(receipt)==pin,'frozen '+name+' receipt')
        if name=='494B':record,encoded=module['evaluate'](language,llvm,directory)
        else:record,encoded=module['evaluate'](ROOT,llvm,directory,language)
        if isinstance(encoded,str):encoded=encoded.encode()
        need(receipt.read_bytes()==encoded,'complete '+name+' LF receipt replay')
        if name=='494B':
            for path,pin_value in record['inputs_before'].items():expected[parent['resolve'](path,llvm)]=pin_value
            for d,values in record['dependency_inventories'].items():
                inventories[d]=values
                expected.update({parent['resolve'](d,llvm)/n:v for n,v in values.items()})
            values=dict(record['artifacts'])
            commands=record['commands']+[job for component in record['dependency_replays'] for job in component['commands']]
            controls=record['negative_controls']
        else:
            for item in record['inputs']:expected[parent['resolve'](item['path'],llvm)]=item['sha256']
            values={Path(item['path']).name:item['sha256'] for item in record['artifacts']}
            commands=record['recipes'];controls=record['negative_controls']
        values['verification.json']=pin
        need(parent['inventory'](directory)==values,'exact '+name+' artifact inventory joined to receipt')
        expected.update({directory/n:v for n,v in values.items()});inventories[str(directory)]=values
        records.append(dict(component=name,receipt=str(receipt),receipt_sha256=pin,replayed=True,
                            controls=len(controls),commands=commands))
    inputs={n:ROOT/'experiments/tsl9-register-providers/build/verified-v3'/language/(n+'.o') for n in ['consumer','receiver','read','write']}
    inputs.update(spi=spi_dir/'native.o',packet=ROOT/'experiments/tsl9-packet-receive/build/verified-v2'/language/'native.o',ring=ring_dir/'native.o')
    need(all(path in expected for path in inputs.values()),'all seven native inputs have replayed parent receipt pins')
    need(parent['snapshots'](expected)==expected,'all replayed source/header/tool/artifact pins equal actual pre-link snapshot')
    objects={n:spi['ELF'](path) for n,path in inputs.items()}
    return dict(parent=parent,ring=ring,spi=spi,ELF=spi['ELF'],expected=expected,inventories=inventories,
                records=records,inputs=inputs,objects=objects)


def sx(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value


def control(word,kind,pc):
    if kind==17:
        need(word&127==0x6f,'JAL opcode')
        imm=((word>>31)<<20)|(((word>>21)&1023)<<1)|(((word>>20)&1)<<11)|(((word>>12)&255)<<12)
        rd=(word>>7)&31;need(rd in (0,1),'JAL architectural rd')
        return ('jal',rd),pc+sx(imm,21),word&0xfffff000,4,pc+4 if rd==1 else None
    if kind==16:
        need(word&127==0x63,'B opcode');f3=(word>>12)&7;need(f3 in (0,1,4,5,6,7),'B condition')
        imm=((word>>31)<<12)|(((word>>7)&1)<<11)|(((word>>25)&63)<<5)|(((word>>8)&15)<<1)
        return ('branch',f3,(word>>15)&31,(word>>20)&31),pc+sx(imm,13),word&0xfe000f80,4,None
    if kind==44:
        need(word&3==1 and word>>13 in (6,7),'compressed branch opcode')
        imm=(((word>>12)&1)<<8)|(((word>>10)&3)<<3)|(((word>>5)&3)<<6)|(((word>>3)&3)<<1)|(((word>>2)&1)<<5)
        return ('c.branch',word>>13,8+((word>>7)&7)),pc+sx(imm,9),word&0x1c7c,2,None
    if kind==45:
        need(word&3==1 and word>>13==5,'C.J opcode, no fabricated link')
        imm=(((word>>12)&1)<<11)|(((word>>11)&1)<<4)|(((word>>9)&3)<<8)|(((word>>8)&1)<<10)|(((word>>7)&1)<<6)|(((word>>6)&1)<<7)|(((word>>3)&7)<<1)|(((word>>2)&1)<<5)
        return ('c.j',0),pc+sx(imm,12),word&0x1ffc,2,None
    raise ValueError('supported native symbolic relocation family')


def model(dep):
    definitions={};locals_expected=[('',0,0,0,0,0)];native_sections={};sites=[]
    final_indices={s[0]:i for i,s in enumerate(SECTION_ROWS)}
    for unit,section,va,size,regions in SPECS:
        e=dep['objects'][unit];need(e.header[0]==1 and e.header[6]==1,'actual RVC native ET_REL input')
        expected={n:(0,z,18,0,'.text.'+n) for n,_,z in regions}
        actual={s['name']:(s['value'],s['size'],s['info'],s['other'],e.sections[s['section']]['name'])
                for s in e.symbols if s['info']&15==2 and s['size']}
        need(actual==expected,'exact genuine native FUNC ownership/extent')
        alloc=[s for s in e.sections if s['flags']&2 and s['size']]
        need(sum(s['size'] for s in alloc)==size and len(alloc)==len(regions) and
             all(s['flags']==6 and s['type']==1 and s['align']==2 for s in alloc),'no extra native data/allocation')
        for n,start,z in regions:
            need(n not in definitions,'one actual definition per graph provider')
            definitions[n]=(va+start,z,18,0,final_indices[section]);native_sections['.text.'+n]=(unit,section,va+start,z)
        for s in e.symbols:
            if s['index']==0:continue
            if s['info']>>4:
                need(s['section']!=65521,'no native ABS providers')
                if s['section']==0:need(s['value']==s['size']==s['other']==0 and s['info']==16,'genuine native UND reference')
            else:
                need(s['info'] in (0,4),'native local metadata type')
                if s['section']==65521:locals_expected.append((s['name'],s['value'],s['size'],s['info'],s['other'],65521))
                else:
                    name=e.sections[s['section']]['name']
                    if name in ('.comment','.riscv.attributes'):
                        need(s['name'].startswith('$d.') and s['value']==s['size']==s['info']==s['other']==0,
                             'exact discarded native metadata mapping')
                        if name=='.riscv.attributes':locals_expected.append((s['name'],0,0,0,0,65521))
                        continue
                    need(name in native_sections,'native code mapping owner')
                    _,_,address,_=native_sections[name]
                    locals_expected.append((s['name'],address+s['value'],s['size'],s['info'],s['other'],final_indices[section]))
        for relocation in e.relocations:
            owner=e.sections[relocation['section']];need(owner['name'] in native_sections and relocation['addend']==0,'actual native relocation owner/addend')
            _,_,pc,size=native_sections[owner['name']];offset=relocation['offset'];symbol=e.symbols[relocation['symbol']]
            width=2 if relocation['type'] in (44,45) else 4
            need(offset%2==0 and offset+width<=size,'native symbolic site bounds')
            word=int.from_bytes(e.data(owner)[offset:offset+width],'little');signature,_,immediate,w,ra=control(word,relocation['type'],pc+offset)
            need(immediate==0 and width==w,'native symbolic placeholder immediate zero')
            sites.append(dict(unit=unit,owner=owner['name'],pc=pc+offset,offset=offset,type=relocation['type'],
                              name=symbol['name'],before_word=word,width=width,signature=signature,return_address=ra))
    need(len(definitions)==24 and len(sites)==26,'actual 24 native definitions/26 symbolic sites')
    need(all(site['name'] in definitions for site in sites),'every native symbolic target has a genuine graph FUNC definition')
    return definitions,locals_expected,sites


def contract(e,dep,full=True):
    need(e.header==[2,243,1,0x17002,52,22528,1,52,32,4,40,12,10] and len(e.raw)==23008,
         'whole original-layout ELF header/file extent')
    need(e.program_headers==PROGRAM_HEADERS,'exact ELF container program headers, not a flat image')
    keys=['name','type','flags','address','offset','size','link','info','align','entsize']
    need([tuple(s[k] for k in keys) for s in e.sections]==SECTION_ROWS and
         [s['name_offset'] for s in e.sections]==[0,1,7,12,18,25,33,43,53,59,67,77],
         'exact seven AX spans and complete section metadata, no added data')
    definitions,local_rows,sites=model(dep);sk=['name','value','size','info','other','section']
    need(len(local_rows)==39 and [tuple(s[k] for k in sk) for s in e.symbols[:39]]==local_rows,
         'exact native-derived local FILE/mapping metadata')
    actual={s['name']:tuple(s[k] for k in sk[1:]) for s in e.symbols[39:]}
    need(len(e.symbols)==63 and len(actual)==24 and actual==definitions and not e.relocations,
         '24 strong real FUNC definitions, no UND/ABS/RELA/aliases')
    checked=[];excluded={}
    for site in sites:
        section=next(s for s in e.sections if s['address']<=site['pc']<s['address']+s['size'] and s['flags']&2)
        at=site['pc']-section['address'];word=int.from_bytes(e.data(section)[at:at+site['width']],'little')
        signature,target,_,width,ra=control(word,site['type'],site['pc'])
        need(signature==site['signature'] and target==definitions[site['name']][0] and ra==site['return_address'],
             'resolved native control preserves opcode/registers/genuine target/RA continuation')
        excluded.setdefault(section['name'],set()).update(range(at,at+width))
        checked.append(dict(owner=site['owner'],pc=site['pc'],type=site['type'],target_function=site['name'],
                            target=target,signature=signature,return_address=ra,
                            before_hex=site['before_word'].to_bytes(width,'little').hex(),after_hex=word.to_bytes(width,'little').hex()))
    ring=e.data('.ring')
    need(ring[54:60]==bytes.fromhex('b7070400fc47') and ring[68:70]==bytes.fromhex('8297'),
         'unknown resident pointer LW[0004004C] followed by C.JALR A5 is retained')
    original=(ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
    need(sha(original)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','whole official BIN identity')
    spans=[];joined=b'';instructions=0
    for unit,section,va,size,regions in sorted(SPECS,key=lambda row:row[2]):
        code=e.data(section);need(code==original[va-0x8000:va-0x8000+size],'all original bytes in each bounded span')
        native=b''.join(dep['objects'][unit].data('.text.'+n) for n,_,_ in regions)
        need(all(code[i]==native[i] for i in range(size) if i not in excluded.get(section,set())),
             'unchanged native noncontrol projection after real relocation')
        i=0;count=0
        while i<size:i+=4 if code[i]&3==3 else 2;count+=1
        need(i==size,'complete span instruction boundaries');instructions+=count;joined+=code
        spans.append(dict(section=section,start=va,end=va+size,bytes=size,instructions=count,sha256=sha(code)))
    need(len(joined)==586 and instructions==210 and sha(joined)==AGGREGATE_PIN,'seven original spans aggregate586B210i')
    if full:need(sha(e.raw)==ELF_PIN,'complete measured ELF metadata pin')
    return dict(allocated_bytes=586,instructions=210,genuine_FUNCs=24,UND=[],RELA=[],ABS_providers=[],
                original_spans=spans,original_aggregate_sha256=sha(joined),resolved_native_symbolic_sites=checked,
                resident_call=dict(pointer_word_address=0x4004c,call_pc=0x12c0c,source_register='A5',
                                   link_register='RA',return_address=0x12c0e,target_identity='UNKNOWN',ABI_closed=False),
                executable_LOAD_span_bytes=17528,unvalidated_LOAD_gap_bytes=17528-586,
                flat_firmware_image=False,firmware_ready=False,sections=e.sections,symbols=e.symbols,
                program_headers=e.program_headers)


def negatives(e,dep):
    results=[]
    def add(name,position,fmt,value):
        b=bytearray(e.raw);struct.pack_into(fmt,b,position,value)
        try:contract(dep['ELF'](b),dep,full=False)
        except (ValueError,IndexError,KeyError,StopIteration) as exc:
            results.append(dict(name=name,rejected=True,whole_hash_enabled=False,reason=str(exc)))
        else:raise ValueError('negative accepted '+name)
    byname={s['name']:s for s in e.symbols if s['info']>>4}
    for name in ['tsl9_ring_insert_entry_12bc8','tsl9_spi_transfer_entry_16896','tsl9_receive_buffer_entry_16a7c']:
        at=20544+byname[name]['index']*16
        for tag,delta,fmt,value in [('ABS',14,'<H',65521),('UND',14,'<H',0),('weak',12,'<B',34),('value',4,'<I',byname[name]['value']+2),('size',8,'<I',2)]:
            add(tag+'_'+name,at+delta,fmt,value)
    add('local_FUNC_alias',20544+2*16+12,'<B',2)
    add('wrong_entry',24,'<I',0x8000);add('ET_REL',16,'<H',1);add('wrong_RVC_flags',36,'<I',0)
    add('writable_RX_LOAD',52+2*32+24,'<I',6)
    for name,si,field,value in [('ringRW',1,8,7),('spiSize',2,20,70),('packetAddress',5,12,0x16a7e),('dataALLOC',9,8,2),('wrongAlignment',6,32,4)]:
        add(name,22528+40*si+field,'<I',value)
    _,_,sites=model(dep)
    for index,site in enumerate(sites):
        section=next(s for s in e.sections if s['flags']&2 and s['address']<=site['pc']<s['address']+s['size'])
        position=section['offset']+site['pc']-section['address'];word=int.from_bytes(e.raw[position:position+site['width']],'little')
        bit=21 if site['type']==17 else 8 if site['type']==16 else 3
        add('control_target_'+str(index),position,'<I' if site['width']==4 else '<H',word^(1<<bit))
        bit=7 if site['type']==17 else 12 if site['type']==16 else 13
        add('control_rd_or_condition_'+str(index),position,'<I' if site['width']==4 else '<H',word^(1<<bit))
    add('resident_pointer_address_changed',3016+58,'<H',int.from_bytes(e.raw[3074:3076],'little')^4)
    add('resident_JALR_register_changed',3016+68,'<H',0x9702)
    for index in range(1,8):
        section=e.sections[index];position=section['offset'];add('native_noncontrol_'+str(index),position,'<B',e.raw[position]^4)
    return results


def recipes(dep,llvm,out):
    inputs=[str(dep['inputs'][n]) for n,_,_,_,_ in SPECS]
    return [('link',[str(llvm/'ld.lld.exe'),'--no-relax','-T',str(HERE/'receive_graph.ld'),*inputs,'-o',str(out/OBJECT)]),
            ('object',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(out/OBJECT)])]


def evaluate(language,llvm,out):
    dep=dependencies(language,llvm);parent=dep['parent'];before=dep['expected'];inv=parent['inventory'](out)
    need(set(inv) in [{OBJECT,'link.log','object.log','recipes.json'},{OBJECT,'link.log','object.log','recipes.json','verification.json'}],
         'exact receive graph artifact inventory')
    commands=[dict(label=n,argv=parent['portable'](a,llvm),returncode=0) for n,a in recipes(dep,llvm,out)]
    need(json.loads((out/'recipes.json').read_bytes())==commands and not (out/'link.log').read_bytes(),
         'actual exact successful linker/reader recipe and empty diagnostics')
    log=(out/'object.log').read_text();need(str(out/OBJECT) in log and all(n in log for n in model(dep)[0]),'retained disassembly binds actual ELF/all FUNCs')
    e=dep['ELF'](out/OBJECT);facts=contract(e,dep);controls=negatives(e,dep)
    need(parent['snapshots'](before)==before,'complete input/artifact/source/header/tool snapshots stable')
    for directory,values in dep['inventories'].items():
        need(parent['inventory'](parent['resolve'](directory,llvm))==values,'complete inherited artifact inventory stable')
    need(parent['inventory'](out)==inv,'receive graph outputs unchanged while reading')
    record=dict(schema='TSL9-original-layout-receive-graph-v1',language=language,firmware_ready=False,
                target_executed=False,ISA_emulated=False,inputs_before={str(k):v for k,v in before.items()},
                inputs_after={str(k):digest(k) for k in before},dependency_inventories=dep['inventories'],
                dependency_replays=dep['records'],native_inputs=[dict(unit=n,path=str(p),sha256=digest(p)) for n,p in dep['inputs'].items()],
                commands=commands,artifacts={n:v for n,v in inv.items() if n!='verification.json'},facts=facts,
                negative_controls=controls,limitations=[
                 'Only seven bounded original code spans match; this ELF includes unvalidated LOAD gaps and is not a flat firmware image.',
                 'Twenty-six symbolic control sites resolve to genuine defined FUNCs; the resident call through LW[0004004C] remains UNKNOWN.',
                 'Resident/full private ABI, incoming interior/cold entries, IRQ/fault/alias effects, physical memory and hardware are not proved.',
                 'No firmware BIN, target/ISA/MMIO execution, OTA acceptance or flash validation.'])
    record=parent['portable'](record,llvm);encoded=(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
    need(not re.search(rb'(?i)[a-z]:[/\\]|/(?:users|home)/',encoded),'portable LF evidence has no host path')
    return record,encoded


def main():
    p=argparse.ArgumentParser(description=__doc__);action=p.add_mutually_exclusive_group(required=True)
    action.add_argument('--out-dir',type=Path);action.add_argument('--replay',type=Path)
    p.add_argument('--language',choices=['c','cpp']);p.add_argument('--llvm-bin',type=Path,
       default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    p.add_argument('--require-firmware-ready',action='store_true');a=p.parse_args();llvm=a.llvm_bin.resolve()
    if a.replay:
        receipt=a.replay.resolve();out=receipt.parent;saved=json.loads(receipt.read_bytes());language=saved['language']
        need(a.language is None or a.language==language,'replay language')
    else:need(a.language is not None,'build language');language=a.language;out=a.out_dir.resolve()
    need(out.is_relative_to(HERE/'build') and out.parent.name.startswith('receive-graph-verified-') and out.name==language,'owned receive graph output')
    if not a.replay:
        need(not out.exists(),'fresh output only');dep=dependencies(language,llvm);out.mkdir(parents=True);actual=[]
        for label,argv in recipes(dep,llvm,out):
            child=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (out/(label+'.log')).write_bytes(child.stdout);actual.append(dict(label=label,argv=dep['parent']['portable'](argv,llvm),returncode=child.returncode))
            need(child.returncode==0,'actual native recipe failed '+label)
        (out/'recipes.json').write_bytes((json.dumps(actual,indent=2)+'\n').encode())
        need(dep['parent']['snapshots'](dep['expected'])==dep['expected'],'stable complete dependency closure across actual link')
    record,encoded=evaluate(language,llvm,out)
    if a.replay:need(saved==record and receipt.read_bytes()==encoded,'complete canonical LF receive graph replay')
    else:(out/'verification.json').write_bytes(encoded)
    print(json.dumps(dict(result='PASS',language=language,bytes=586,instructions=210,FUNCs=24,resolved_symbolic_sites=26,
                          UND=0,RELA=0,resident_target='UNKNOWN',controls=len(record['negative_controls']),
                          ELF_sha256=ELF_PIN,receipt_sha256=sha(encoded),firmware_ready=False)))
    if a.require_firmware_ready:
        print('REJECTED: resident ABI, full image/IRQ/memory/hardware and flashability remain unproved.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,IndexError,KeyError,StopIteration) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
