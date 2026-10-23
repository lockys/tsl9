#!/usr/bin/env python3
"""Read genuine partial-link artifacts and original operands; never execute them."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-queue-dispatch-component'
SCHEMA = 'TSL9-queue-dispatch-component-v1'
BUILD_SCHEMA = 'TSL9-queue-dispatch-build-v1'
FIRMWARE = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FW_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
Q = ['tsl9_queue_'+s for s in ('entry_12c58','scan_12c86','release_12ca6','validate_12cb4','advance_12cee',
     'finish_12cf8','zero_12d0e','emit_12d42','response_12d4c','other_12d78')]
F = ['tsl9_queue_external_82d2']+['tsl9_filter_'+s for s in ('scan_8308','pack_8328','emit_8358','test_836a','finish_836e','second_838a')]
S = ['tsl9_queue_external_81aa','tsl9_queue_external_820c']
NAMES = Q+F+S
OFFSETS = [0,46,78,92,150,160,182,234,244,288,314,368,400,448,466,470,498,502,508]
SIZES = [46,32,14,58,10,22,52,10,44,26,54,32,48,18,4,28,4,6,18]
UNDEFINED = sorted(['tsl9_queue_external_'+s for s in ('9454','9b36','12abe','12a08','14d2e')]+['tsl9_filter_external_8a56'])
MASKS = {16:(4,0x01fff07f),17:(4,0x00000fff),44:(2,0xe383),45:(2,0xe003)}
OWN = ['src/providers.c','component.ld','build.py','check.py','dependencies.json','README.md','readme.zh-TW.md','readme.en.md','verify.sh']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def load(path):
    return json.loads(Path(path).read_bytes())


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def portable(value, root, llvm):
    if isinstance(value, str):
        return value.replace(str(root).replace('\\','/'),'${TSL9_ROOT}').replace(str(root),'${TSL9_ROOT}').replace(str(llvm).replace('\\','/'),'${LLVM_BIN}').replace(str(llvm),'${LLVM_BIN}')
    if isinstance(value, (list,tuple)):
        return [portable(x, root, llvm) for x in value]
    if isinstance(value, dict):
        return {portable(k, root, llvm):portable(v, root, llvm) for k,v in value.items()}
    return value


def restore(value, root, llvm):
    return Path(value.replace('${TSL9_ROOT}',str(root)).replace('${LLVM_BIN}',str(llvm))).resolve()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)+'\n').encode()


def write_new(path, value):
    with path.open('xb') as stream:
        stream.write(encoded(value))


def dependencies(root):
    spec = load(HERE/'dependencies.json')
    need(spec['schema'] == 'TSL9-queue-dispatch-dependencies-v1', 'Frozen dependency manifest schema')
    need(all(sha(root/p) == h for p,h in spec['pins'].items()), 'Complete frozen dependency source pins')
    return spec


def inputs(root, llvm):
    spec = dependencies(root)
    small = module(root/spec['small_builder'], 'dispatch_small_builder')
    need(sha(root/FIRMWARE) == FW_SHA and (root/FIRMWARE).stat().st_size == 76800, 'Fresh full official V4.1.60 identity')
    tools = {n:llvm/(n+('.exe' if os.name == 'nt' else '')) for n in small.TOOLS}
    need(all(sha(tools[n]) == h for n,h in small.TOOLS.items()), 'Actual existing local LLVM tools')
    resource = llvm.parent/'lib/clang/18/include/stdint.h'
    need(sha(resource) == small.STDINT_SHA, 'Actual compiler stdint resource')
    paths = [HERE/p for p in OWN]+[root/p for p in spec['pins']]+[root/FIRMWARE,resource,*tools.values()]
    return {portable(str(p),root,llvm):sha(p) for p in sorted(set(paths))}


def upstream(root, llvm, queue, filt, mode):
    spec = dependencies(root)
    facts = {}
    for name,folder,key in [('queue',queue,'queue_checker'),('filter',filt,'filter_checker')]:
        need(folder.is_relative_to(root/'experiments') and folder.name == mode, 'Actual owned '+name+' folder')
        checker = module(root/spec[key], 'dispatch_'+name+'_checker')
        actual, text = checker.evaluate(root, llvm, folder, mode)
        receipt = folder/'verification.json'
        need(load(receipt) == actual and receipt.read_bytes() == text.encode(), 'Read-only actual '+name+' formal proof replay')
        facts[name] = dict(receipt=portable(str(receipt),root,llvm),sha256=sha(receipt),
                           native_sha256=sha(folder/'native.o'),inputs=actual['inputs'],
                           source_SSA_and_typed_operands_rechecked=True)
    return facts


def recipes(root, llvm, folder, mode, queue, filt):
    spec = dependencies(root)
    small = module(root/spec['small_builder'], 'dispatch_flags')
    exe = lambda n:llvm/(n+('.exe' if os.name == 'nt' else ''))
    source = HERE/'src/providers.c'
    return [('compiler-help',[exe('clang'),'--help']),('resource',[exe('clang'),'-print-resource-dir']),
            ('compile',[exe('clang'),*small.flags(mode),'-c','-MD','-MF',folder/'native.d','-MT','native.o',source,'-o',folder/'native.o']),
            ('IR',[exe('clang'),*small.flags(mode),'-S','-emit-llvm',source,'-o',folder/'native.ll']),
            ('adapter',[exe('llvm-objdump'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',folder/'native.o']),
            ('link',[exe('ld.lld'),'-r','--no-relax','-T',HERE/'component.ld',queue/'native.o',filt/'native.o',folder/'native.o','-o',folder/'dispatch.o']),
            ('dispatch',[exe('llvm-objdump'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',folder/'dispatch.o'])]


def elf(raw):
    """Independent bounded ELF32 reader with raw record offsets for controls."""
    need(len(raw) >= 52 and raw[:16] == b'\x7fELF\x01\x01\x01'+b'\0'*9, 'ELF32 LE identity')
    h = struct.unpack_from('<16sHHIIIIIHHHHHH',raw)
    need(h[1:5] == (1,243,1,0) and h[7:12] == (1,52,0,0,40), 'ET_REL RV32 RVC1 with no program load addresses')
    need(0 < h[12] < 128 and h[13] < h[12] and h[6]+40*h[12] <= len(raw), 'Section header bounds')
    sections = []
    for i in range(h[12]):
        fields = struct.unpack_from('<10I',raw,h[6]+i*40)
        section = dict(zip(('nameoff','type','flags','address','offset','size','link','info','align','entsize'),fields),index=i,record=h[6]+i*40)
        need(section['type'] != 8 and section['offset']+section['size'] <= len(raw), 'No NOBITS and complete section storage')
        sections.append(section)
    need(max([h[6]+40*h[12]]+[s['offset']+s['size'] for s in sections]) == len(raw), 'No unexplained trailing bytes')
    def data(s):
        return raw[s['offset']:s['offset']+s['size']]
    def string(buf,at):
        need(0 <= at < len(buf) and 0 in buf[at:], 'Bounded ELF string')
        return buf[at:buf.index(0,at)].decode('ascii')
    names = data(sections[h[13]])
    for s in sections:
        s['name'] = string(names,s['nameoff'])
    need(len({s['name'] for s in sections}) == len(sections), 'Unique section names')
    tables = [s for s in sections if s['type'] == 2]
    need(len(tables) == 1, 'One actual symbol table')
    table = tables[0]
    need(table['entsize'] == 16 and table['size']%16 == 0 and table['link'] < len(sections), 'Symbol table shape')
    strings = data(sections[table['link']])
    symbols = []
    for i,at in enumerate(range(table['offset'],table['offset']+table['size'],16)):
        n,v,z,info,other,si = struct.unpack_from('<IIIBBH',raw,at)
        need(si < len(sections) or si == 0xfff1, 'Symbol storage index')
        symbols.append(dict(name=string(strings,n),value=v,size=z,info=info,other=other,section=si,index=i,record=at))
    rels = []
    for s in sections:
        need(s['type'] != 9, 'No implicit-addend REL')
        if s['type'] != 4:
            continue
        need(s['link'] == table['index'] and s['info'] < len(sections) and s['entsize'] == 12 and s['size']%12 == 0, 'Complete RELA table')
        for at in range(s['offset'],s['offset']+s['size'],12):
            off,info,add = struct.unpack_from('<IIi',raw,at)
            need(info>>8 < len(symbols), 'Actual relocation symbol index')
            rels.append(dict(section=s['info'],offset=off,type=info&255,target=symbols[info>>8]['name'],symbol=info>>8,addend=add,record=at))
    return dict(raw=raw,sections=sections,symbols=symbols,relocations=rels)


def surface(e, names, offsets, sizes, combined):
    syms, sec = e['symbols'], e['sections']
    fs = [s for s in syms if s['info']&15 == 2]
    need(len(fs) == len(names) and {s['name'] for s in fs} == set(names), 'All genuine FUNCs including locals and unused functions')
    globals_ = [s for s in syms if s['info']>>4 in (1,2)]
    und = sorted(s['name'] for s in globals_ if s['section'] == 0)
    need(not [s for s in syms if s['section'] == 0xfff1 and s['info']>>4], 'No global ABS providers')
    need(not [s for s in globals_ if s['info']>>4 != 1 or s['other'] != 0], 'Only ordinary strong visible symbols')
    need({s['name'] for s in globals_} == set(names)|set(und), 'No hidden non-FUNC global definition')
    alloc = [s for s in sec if s['flags']&2 and s['size']]
    expected = [('.dispatch',526,6,1,0)] if combined else [('.text.'+n,z,6,1,0) for n,z in zip(names,sizes)]
    need(sorted((s['name'],s['size'],s['flags'],s['type'],s['address']) for s in alloc) == sorted(expected), 'Exact complete allocated code, no data/unwind/writable extras')
    codes, facts = {}, []
    for n,off,z in zip(names,offsets,sizes):
        s = next(s for s in fs if s['name'] == n)
        need(s['info'] == 18 and s['other'] == 0 and 0 < s['section'] < len(sec), 'Strong real stored FUNC '+n)
        section = sec[s['section']]
        need(s['value'] == (off if combined else 0) and s['size'] == z and s['value']+z <= section['size'], 'Exact function boundaries '+n)
        at = section['offset']+s['value']
        codes[n] = e['raw'][at:at+z]
        facts.append(dict(name=n,offset=off,size=z,section=section['name'],sha256=digest(codes[n])))
    return codes, facts, und


def sign(value,bits):
    return value-(1<<bits) if value&(1<<(bits-1)) else value


def control(code, offset, kind, original_pc):
    width,mask = MASKS[kind]
    word = int.from_bytes(code[offset:offset+width],'little')
    need(offset+width <= len(code), 'Complete relocated instruction')
    if kind == 16:
        need(word&127 == 0x63 and word>>12&7 in (0,1,4,5,6,7), 'Real conditional RV32 branch')
        imm = ((word>>31)<<12)|((word>>7&1)<<11)|((word>>25&63)<<5)|((word>>8&15)<<1)
        return dict(kind='BRANCH',width=width,funct3=word>>12&7,rs1=word>>15&31,rs2=word>>20&31,target=original_pc+sign(imm,13))
    if kind == 17:
        need(word&127 == 0x6f and word>>7&31 == 1, 'Genuine JAL with RA link, never tail-jump')
        imm = ((word>>31)<<20)|((word>>12&255)<<12)|((word>>20&1)<<11)|((word>>21&1023)<<1)
        return dict(kind='JAL',width=width,rd=1,target=original_pc+sign(imm,21))
    if kind == 44:
        need(word&3 == 1 and word>>13 in (6,7), 'Real compressed zero-branch')
        imm = ((word>>12&1)<<8)|((word>>5&3)<<6)|((word>>2&1)<<5)|((word>>10&3)<<3)|((word>>3&3)<<1)
        return dict(kind='C.BNEZ' if word>>13 == 7 else 'C.BEQZ',width=width,rs1=8+(word>>7&7),target=original_pc+sign(imm,9))
    need(word&3 == 1 and word>>13 in (1,5), 'Actual C.JAL or C.J, retaining link distinction')
    imm = ((word>>12&1)<<11)|((word>>8&1)<<10)|((word>>9&3)<<8)|((word>>6&1)<<7)|((word>>7&1)<<6)|((word>>2&1)<<5)|((word>>11&1)<<4)|((word>>3&7)<<1)
    return dict(kind='C.JAL' if word>>13 == 1 else 'C.J',width=width,rd=1 if word>>13 == 1 else 0,target=original_pc+sign(imm,12))


def count_instructions(code):
    at = 0
    rows = []
    while at < len(code):
        width = 4 if int.from_bytes(code[at:at+2],'little')&3 == 3 else 2
        need(at+width <= len(code), 'Complete instruction stream')
        rows.append((at,code[at:at+width].hex()))
        at += width
    return rows


def relation_rows(e, names, bases):
    starts = {s['section']:bases[s['name']] for s in e['symbols'] if s['name'] in names and s['info']&15 == 2}
    return sorted((starts[r['section']]+r['offset'],r['type'],r['target'],r['addend']) for r in e['relocations'])


def original_gate(root, code, relations):
    firmware = (root/FIRMWARE).read_bytes()
    need(digest(firmware) == FW_SHA and len(firmware) == 76800, 'Complete official image identity')
    spans = [(0,314,0x12c58),(314,188,0x82d2),(502,6,0x81aa),(508,18,0x820c)]
    original = b''.join(firmware[va-0x8000:va-0x8000+size] for _,size,va in spans)
    masks = bytearray(b'\xff'*526)
    typed = []
    for off,kind,target,addend in relations:
        need(kind in MASKS and addend == 0, 'Only genuine original control relocation families and zero addends')
        width,mask = MASKS[kind]
        need(all(x == 255 for x in masks[off:off+width]), 'Non-overlapping relocated operand extents')
        masks[off:off+width] = mask.to_bytes(width,'little')
        span = next((at,z,va) for at,z,va in spans if at <= off < at+z)
        pc = span[2]+off-span[0]
        facts = control(original,off,kind,pc)
        actual = control(code,off,kind,pc)
        need({k:v for k,v in facts.items() if k != 'target'} == {k:v for k,v in actual.items() if k != 'target'}, 'Actual RD/RS/family equal original')
        need(facts['target'] == int(target.rsplit('_',1)[1],16), 'Original immediate destination equals actual symbolic target identity')
        typed.append(dict(offset=off,original_PC=pc,original_target=facts['target'],target_symbol=target,
                          operand=facts,pending_raw_immediate_target=actual['target'],machine_operand_resolved=False))
    need(len(code) == len(original) == 526 and all(not((a^b)&m) for a,b,m in zip(code,original,masks)), 'All non-control immediate bits equal fresh original spans')
    spec = dependencies(root)
    small = module(root/spec['small_checker'],'dispatch_small_original')
    small.original_fields(code[502:508],code[508:526])
    return dict(firmware_sha256=FW_SHA,spans=[dict(offset=a,bytes=z,original_VA=va) for a,z,va in spans],
                masked_original_sha256=digest(bytes(a&m for a,m in zip(original,masks))),
                noncontrol_bits_equal=True,typed_control_operands=typed,small_full_bytes_equal=True)


def composition(e, queue_e, filter_e, adapter_e, root):
    codes,facts,und = surface(e,NAMES,OFFSETS,SIZES,True)
    need(und == UNDEFINED, 'Exactly six genuine strong unresolved providers')
    need({s['name'] for s in e['sections']} == {'','.dispatch','.text','.rela.dispatch','.llvm_addrsig','.symtab','.strtab','.shstrtab'}, 'Complete partial-link section inventory including empty text and address-significance metadata')
    empty = next(s for s in e['sections'] if s['name'] == '.text')
    need(empty['size'] == 0 and empty['flags'] == 6 and empty['type'] == 1, 'Empty inherited text contains no extra function')
    addrsig = next(s for s in e['sections'] if s['name'] == '.llvm_addrsig')
    need(addrsig['type'] == 0x6fff4c03 and addrsig['flags'] == 0x80000000 and addrsig['size'] == 19, 'Retained nonallocated actual address-significance metadata')
    combined = b''.join(codes[n] for n in NAMES)
    expected_codes = {}
    expected_relations = []
    for prior,names,bases in [(queue_e,Q,dict(zip(Q,OFFSETS[:10]))),(filter_e,F,dict(zip(F,OFFSETS[10:17]))),(adapter_e,S,dict(zip(S,OFFSETS[17:])) )]:
        for s in prior['symbols']:
            if s['name'] in names and s['info']&15 == 2:
                section = prior['sections'][s['section']]
                at = section['offset']+s['value']
                expected_codes[s['name']] = prior['raw'][at:at+s['size']]
        expected_relations.extend(relation_rows(prior,names,bases))
    need(codes == expected_codes, 'All nineteen actual input bodies preserved byte for byte, including unused FUNCs')
    relations = sorted((r['offset'],r['type'],r['target'],r['addend']) for r in e['relocations'])
    need(len(relations) == 32 and relations == sorted(expected_relations), 'All32 actual pending RELA records preserved with correct symbol remapping')
    section = next(s for s in e['sections'] if s['name'] == '.dispatch')
    need(all(r['section'] == section['index'] for r in e['relocations']), 'All pending controls belong to real dispatch code')
    syms = {s['name']:s for s in e['symbols'] if s['name']}
    bindings = []
    for name,off in zip([F[0],*S],[314,502,508]):
        need(syms[name]['section'] == section['index'] and syms[name]['value'] == off and syms[name]['info'] == 18, 'Real C FUNC definition resolves '+name)
        sites = [r['offset'] for r in e['relocations'] if r['target'] == name]
        need(sites, 'Actual consumer reference now targets genuine definition')
        bindings.append(dict(symbol=name,definition_offset=off,reference_offsets=sites,resolved_at_symbol_level=True,machine_operand_resolved=False))
    rows = count_instructions(combined)
    need(len(rows) == 184, 'Actual full526B stream is184 instructions')
    original = original_gate(root,combined,relations)
    return dict(bytes=526,instructions=184,FUNCs=19,private_architectural_regions=17,ordinary_small_C_functions=2,
                allocated=[dict(name='.dispatch',bytes=526,type=1,flags=6,address=0)],functions=facts,
                strong_UND=und,global_ABS=[],pending_RELA=32,relocations=[dict(offset=o,type=k,target=n,addend=a) for o,k,n,a in relations],
                real_symbol_bindings=bindings,code_sha256=digest(combined),original=original,
                VMA=0,original_physical_placement_proved=False,all_machine_controls_resolved=False), rows


class Text:
    def __init__(self,text):
        self.text = text
    def read_text(self,**unused):
        return self.text


def adapter_ir(root, text, mode):
    spec = dependencies(root)
    original_names = ('tsl9_queue_status_81aa','tsl9_queue_clear_820c')
    need(set(re.findall(r'^define[^\n]*@([^(]+)',text,re.M)) == set(S), 'Exactly two genuine renamed IR definitions')
    for actual,original in zip(S,original_names):
        text = text.replace(actual,original)
    small = module(root/spec['small_checker'],'dispatch_small_ir')
    return small.ir(Text(text),mode)


def md_contract(root, llvm, text):
    text = text.replace('\\\n',' ')
    need(text.startswith('native.o:'), 'Exact adapter MD target')
    values = text.split(':',1)[1].strip().split()
    paths = {str(Path(x).resolve()) for x in values}
    expected = {str((HERE/'src/providers.c').resolve()),str((root/'experiments/tsl9-queue-small-providers/src/providers.c').resolve()),str((llvm.parent/'lib/clang/18/include/stdint.h').resolve())}
    need(len(values) == 3 and paths == expected, 'Actual adapter plus ordinary source include plus compiler stdint closure, no hidden includes')
    return sorted(portable(x,root,llvm) for x in paths)


def llvm_rows(text, expected):
    found = []
    for line in text.splitlines():
        m = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)',line)
        if m:
            found.append((int(m[1],16),bytes.fromhex(m[2]).hex()))
    need(found == expected, 'Complete actual LLVM raw instruction readback, including post-RET cold regions')
    return len(found)


def negatives(e, queue, filt, adapter, root, text, mode, md, llvm):
    results = []
    def reject(name, action):
        try:
            action()
        except (ValueError,KeyError,IndexError,StopIteration,struct.error):
            results.append(name)
        else:
            raise ValueError('Accepted actual mutation '+name)
    def mutation(name,at,fmt,value):
        changed = bytearray(e['raw'])
        struct.pack_into(fmt,changed,at,value)
        reject(name,lambda:composition(elf(bytes(changed)),queue,filt,adapter,root))
    sec = next(s for s in e['sections'] if s['name'] == '.dispatch')
    symbols = {s['name']:s for s in e['symbols'] if s['name']}
    mutation('writable_dispatch',sec['record']+8,'<I',7)
    mutation('fake_ABS_clear',symbols[S[1]]['record']+14,'<H',0xfff1)
    mutation('weak_status',symbols[S[0]]['record']+12,'<B',34)
    mutation('lost_filter_body',symbols[F[0]]['record']+8,'<I',52)
    mutation('wrong_filter_position',symbols[F[0]]['record']+4,'<I',312)
    for target in [F[0],S[0],S[1]]:
        r = next(r for r in e['relocations'] if r['target'] == target)
        wrong = symbols[UNDEFINED[0]]['index']
        mutation('bad_binding_'+target,r['record']+4,'<I',(wrong<<8)|r['type'])
    call = next(r for r in e['relocations'] if r['type'] == 17)
    mutation('JAL_without_RA_link',sec['offset']+call['offset'],'<I',int.from_bytes(e['raw'][sec['offset']+call['offset']:sec['offset']+call['offset']+4],'little')&~0xf80)
    cjal = next(r for r in e['relocations'] if r['type'] == 45 and int.from_bytes(e['raw'][sec['offset']+r['offset']:sec['offset']+r['offset']+2],'little')>>13 == 1)
    mutation('C_JAL_changed_to_tail_C_J',sec['offset']+cjal['offset'],'<H',int.from_bytes(e['raw'][sec['offset']+cjal['offset']:sec['offset']+cjal['offset']+2],'little')^0x8000)
    mutation('RELA_nonzero_addend',call['record']+8,'<i',2)
    mutation('status_wrong_GP175',sec['offset']+502,'<I',int.from_bytes(e['raw'][sec['offset']+502:sec['offset']+506],'little')^(8<<20))
    mutation('clear_signed_branch',sec['offset']+510,'<I',int.from_bytes(e['raw'][sec['offset']+510:sec['offset']+514],'little')^0x2000)
    reject('trailing_unreported_bytes',lambda:composition(elf(e['raw']+b'\0\0'),queue,filt,adapter,root))
    code = e['raw'][sec['offset']:sec['offset']+526]
    relations = sorted((r['offset'],r['type'],r['target'],r['addend']) for r in e['relocations'])
    for name,offset,mask,width in [('typed_JAL_link_rd',call['offset'],128,4),
                                  ('typed_CJAL_link_rd',cjal['offset'],0x8000,2),
                                  ('typed_GP_status_offset',502,8<<20,4),
                                  ('typed_clear_unsigned_condition',510,0x2000,4)]:
        changed = bytearray(code)
        value = int.from_bytes(changed[offset:offset+width],'little')^mask
        changed[offset:offset+width] = value.to_bytes(width,'little')
        reject(name,lambda changed=changed:original_gate(root,bytes(changed),relations))
    for name,old,new in [('IR_GP175','add i32 %1, 167','add i32 %1, 175'),('IR_signed_index','icmp ugt','icmp sgt'),('IR_nonvolatile_store','store volatile i8','store i8')]:
        need(old in text, 'Actual compiled IR mutation seed '+name)
        reject(name,lambda old=old,new=new:adapter_ir(root,text.replace(old,new,1),mode))
    need('tsl9-queue-small-providers' in md, 'Actual ordinary include MD negative seed')
    missing = '\n'.join(line for line in md.splitlines() if 'tsl9-queue-small-providers' not in line)
    reject('MD_missing_original_C',lambda:md_contract(root,llvm,missing))
    return results


def inspect(root, llvm, folder):
    need(root/MODEL == HERE and folder.is_relative_to(HERE/'build') and folder.name in ('c','cpp'), 'Owned project and actual mode folder')
    before = inputs(root,llvm)
    record = load(folder/'compile-receipt.json')
    mode = record['mode']
    need(record['schema'] == BUILD_SCHEMA and folder.name == mode and record['inputs'] == before, 'Current fixed source/tool build receipt')
    queue, filt = (restore(record[k],root,llvm) for k in ('queue_folder','filter_folder'))
    upstream_facts = upstream(root,llvm,queue,filt,mode)
    commands = recipes(root,llvm,folder,mode,queue,filt)
    expected = [dict(label=n,argv=portable([str(x) for x in a],root,llvm),exit=0,log_sha256=sha(folder/(n+'.log'))) for n,a in commands]
    need(record['commands'] == expected, 'Every exact actual command recipe, successful exit and log hash')
    files = ['native.o','native.ll','native.d','dispatch.o']+[n+'.log' for n,_ in commands]
    need(record['artifacts'] == {n:sha(folder/n) for n in sorted(files)}, 'Every raw compile/link artifact and log hash')
    need({p.name for p in folder.iterdir()}-{'verification.json'} == set(files)|{'compile-receipt.json'}, 'Exact fresh output inventory')
    need(all(p.is_file() and not p.is_symlink() for p in folder.iterdir()), 'Ordinary actual files only')
    for label in ('compile','IR','link'):
        need((folder/(label+'.log')).read_bytes() == b'', 'Empty successful compiler/linker diagnostics')
    need((folder/'resource.log').read_text().strip().replace('\\','/') == str(llvm.parent/'lib/clang/18').replace('\\','/'), 'Actual resource-dir readback')
    helptext = (folder/'compiler-help.log').read_text()
    need('-ffixed-x' in helptext and '-mno-relax' in helptext, 'Actual compiler advertises required fixed-register and relaxation controls')
    q, f, a, linked = [elf(p.read_bytes()) for p in (queue/'native.o',filt/'native.o',folder/'native.o',folder/'dispatch.o')]
    codes,af,und = surface(a,S,[0,6],[6,18],False)
    need(not und and not a['relocations'], 'Two adapter definitions have no UND or relocation')
    text = (folder/'native.ll').read_text()
    ir = adapter_ir(root,text,mode)
    md = (folder/'native.d').read_text()
    closure = md_contract(root,llvm,md)
    result,rows = composition(linked,q,f,a,root)
    llvm_count = llvm_rows((folder/'dispatch.log').read_text(),rows)
    controls = negatives(linked,q,f,a,root,text,mode,md,llvm)
    need(before == inputs(root,llvm), 'All source/resource/tool inputs stable through review')
    output = dict(schema=SCHEMA,passed=True,mode=mode,inputs=before,upstream=upstream_facts,adapter=dict(functions=af,IR=ir,MD=closure),
                  result=result,full_LLVM_instruction_rows=llvm_count,negative_controls=controls,
                  commands=record['commands'],artifacts={p.name:sha(p) for p in sorted(folder.iterdir()) if p.name != 'verification.json'},
                  target_executed=False,ISA_emulated=False,HOST_execution=False,network=False,BIN_generated=False,
                  firmware_ready=False,physical_placement_proved=False,installed_ROM_proved=False,ordinary_C_ABI_proved=False)
    return json.loads(json.dumps(output))


def replay(root, llvm, receipt):
    value = inspect(root,llvm,receipt.parent)
    need(receipt.read_bytes() == encoded(value), 'Complete canonical read-only replay equals actual evidence')
    return value


def metadata(root):
    dependencies(root)
    seal = load(HERE/'seal.json')
    need(seal['schema'] == 'TSL9-queue-dispatch-source-seal-v1' and seal['files'] == {p:sha(HERE/p) for p in OWN}, 'Exact final authored source seal')
    need((HERE/'README.md').read_bytes() == (HERE/'readme.zh-TW.md').read_bytes(), 'TW default identity')
    for p in OWN:
        b = (HERE/p).read_bytes()
        need(b'\r' not in b and b.endswith(b'\n') and not b.endswith(b'\n\n') and all(x.rstrip(b' \t') == x for x in b.splitlines()), 'LF/single EOF/blank hygiene '+p)
    return dict(passed=True,metadata_only=True,files=len(OWN),seal_sha256=sha(HERE/'seal.json'),firmware_ready=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,default=HERE.parents[1])
    p.add_argument('--llvm-bin',type=Path)
    group = p.add_mutually_exclusive_group()
    group.add_argument('--folder',type=Path)
    group.add_argument('--replay',type=Path)
    p.add_argument('--receipt',type=Path)
    p.add_argument('--require-firmware-ready',action='store_true')
    a = p.parse_args()
    root = a.project_root.resolve()
    need(root/MODEL == HERE, 'Portable root locates this exact experiment')
    if not a.folder and not a.replay:
        need(a.receipt is None, 'Receipt requires actual folder mode')
        result = metadata(root)
    else:
        need(a.llvm_bin is not None, 'Actual existing LLVM directory required')
        llvm = a.llvm_bin.resolve()
        if a.replay:
            need(a.receipt is None, 'Replay is read-only')
            result = replay(root,llvm,a.replay.resolve())
        else:
            need(a.receipt is not None and a.receipt.resolve().parent == a.folder.resolve(), 'Create-only receipt in actual owned folder')
            result = inspect(root,llvm,a.folder.resolve())
            write_new(a.receipt.resolve(),result)
    print(json.dumps(dict(passed=True,mode=result.get('mode'),metadata_only=result.get('metadata_only',False),
                          result=result.get('result'),controls=len(result.get('negative_controls',[])),firmware_ready=False)))
    if a.require_firmware_ready:
        print('REJECTED: six external and dynamic providers, pending operands, original placement/ABI/physical gates remain open.',file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,StopIteration,struct.error) as error:
        print('FAIL: '+str(error),file=sys.stderr)
        sys.exit(1)
