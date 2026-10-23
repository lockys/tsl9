#!/usr/bin/env python3
"""Read original bytes and genuine C/C++ artifacts; never run target code."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-queue-small-providers'
STATUS, CLEAR = 'tsl9_queue_status_81aa', 'tsl9_queue_clear_820c'
NAMES = (STATUS, CLEAR)
ORIGINAL = {STATUS:bytes.fromhex('03c5710a8280'), CLEAR:bytes.fromhex('894763e7a7009387010caa97a38007008280')}
SOURCE_SHA = '40fe794b59002d80057b0e4f70d3b0e51f528378bd5de6ca5cf81600411b7a13'
IR_HASHES = {
    'c':('10056d8b8288d6f0b367bbbc6786485b69603cc4ba8756e6f531532ec6a586d8','cc3bb5b12b0a10e4d763948178ca7a24215a7bcfbdd3268e49c14002e408ff54'),
    'cpp':('72c358c66fc4fb4da2e795eb6358ee1c883b00383e11d0c89a907b0b3fe9e20a','452fb6d6e94df1c64a0fc48a4d5a9e2f1475909cb42269e5e6b71c51069e5e76')}


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def builder():
    spec = importlib.util.spec_from_file_location('queue_provider_builder', HERE/'build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def original_fields(status, clear):
    need(len(status) == 6 and len(clear) == 18, 'Complete two original leaves')
    load = int.from_bytes(status[:4],'little')
    need((load&127,load>>12&7,load>>7&31,load>>15&31,load>>20) == (3,4,10,3,167), 'LBU A0,167(GP), not older GP+175')
    need(status[4:] == bytes.fromhex('8280'), 'Status RET via RA')
    li = int.from_bytes(clear[:2],'little')
    need((li&3,li>>13,li>>7&31,(li>>12&1)<<5|(li>>2&31)) == (1,2,15,2), 'C.LI A5,2')
    branch = int.from_bytes(clear[2:6],'little')
    immediate = (branch>>31)<<12|(branch>>7&1)<<11|(branch>>25&63)<<5|(branch>>8&15)<<1
    if immediate&4096:
        immediate -= 8192
    need((branch&127,branch>>12&7,branch>>15&31,branch>>20&31,2+immediate) == (0x63,6,15,10,16), 'Unsigned BLTU A5,A0 to real local RET')
    addi = int.from_bytes(clear[6:10],'little')
    need((addi&127,addi>>12&7,addi>>7&31,addi>>15&31,addi>>20) == (0x13,0,15,3,192), 'ADDI A5,GP,192')
    add = int.from_bytes(clear[10:12],'little')
    need((add&3,add>>13,add>>12&1,add>>7&31,add>>2&31) == (2,4,1,15,10), 'C.ADD A5,A5,A0')
    store = int.from_bytes(clear[12:16],'little')
    immediate = (store>>25)<<5|(store>>7&31)
    need((store&127,store>>12&7,store>>15&31,store>>20&31,immediate) == (0x23,0,15,0,1), 'SB ZERO,1(A5)')
    need(clear[16:] == bytes.fromhex('8280'), 'Clear RET via RA')
    return dict(status=dict(original_VA='[0x81AA,0x81B0)',bytes=6,instructions=2,load_width=8,GP_offset=167,own_written_GPRs=[10]),
                clear=dict(original_VA='[0x820C,0x821E)',bytes=18,instructions=6,own_written_GPRs=[15],
                           branch=dict(offset=2,kind='BLTU',rs1=15,rs2=10,target_offset=16),
                           normal_skip='u32(entry_A0)>2: no memory access; A5=2',
                           normal_store='u32(entry_A0)<=2: WRITE8(u32(live_GP+193+entry_A0),0); A5=u32(live_GP+192+entry_A0)',
                           entry_A0_preserved=True), original_callees=[], stack_accesses=[], GP_own_write=False)


def elf(raw, linked):
    need(raw[:7] == b'\x7fELF\x01\x01\x01','ELF32 little-endian identity')
    header = struct.unpack_from('<16sHHIIIIIHHHHHH',raw)
    need(header[1] == (2 if linked else 1) and header[2] == 243 and header[7] == 1,'Actual RV32 ET_REL/ET_EXEC RVC flags')
    sections = []
    for index in range(header[12]):
        at = header[6]+index*header[11]
        fields = struct.unpack_from('<10I',raw,at)
        item = dict(zip(('nameoff','type','flags','address','offset','size','link','info','align','entsize'),fields))
        item.update(index=index,header_at=at)
        need(item['type'] == 8 or item['offset']+item['size'] <= len(raw),'Section file bounds')
        sections.append(item)
    ns = sections[header[13]]
    names = raw[ns['offset']:ns['offset']+ns['size']]
    string = lambda data,at:data[at:data.index(0,at)].decode('utf-8')
    for item in sections:
        item['name'] = string(names,item['nameoff'])
    symbols = []
    for section in sections:
        if section['type'] != 2:
            continue
        ns = sections[section['link']]
        names = raw[ns['offset']:ns['offset']+ns['size']]
        for at in range(section['offset'],section['offset']+section['size'],section['entsize']):
            n,value,size,info,other,index = struct.unpack_from('<IIIBBH',raw,at)
            symbols.append(dict(name=string(names,n),value=value,size=size,info=info,index=index,other=other,record_at=at))
    functions = [s for s in symbols if s['info']&15 == 2 and s['size']]
    need(len(functions) == 2 and {s['name'] for s in functions} == set(NAMES),'Exactly two genuine functions including any local FUNC')
    need({s['name'] for s in symbols if s['name'] and s['info']>>4 in (1,2)} == set(NAMES),'Exact two public C definitions')
    need(not [s for s in symbols if s['name'] and s['index'] == 0],'No named UND')
    need(not [s for s in symbols if s['index'] == 0xfff1 and s['info']>>4 in (1,2)],'No global ABS provider')
    need(not [s for s in sections if s['type'] in (4,9) and s['size']],'Actual zero REL/RELA: assembler resolved local branch')
    allocated = [s for s in sections if s['flags']&2 and s['size']]
    expected = [('.text',24,6,1)] if linked else [('.text.'+STATUS,6,6,1),('.text.'+CLEAR,18,6,1)]
    need(sorted((s['name'],s['size'],s['flags'],s['type']) for s in allocated) == sorted(expected),'Exact allocation; no hidden code, writable/NOBITS/unwind data')
    facts, codes, positions = {}, {}, {}
    for function in functions:
        name = function['name']
        need(function['info']>>4 == 1 and function['other'] == 0 and 0 < function['index'] < len(sections),'Real public function section ownership')
        section = sections[function['index']]
        offset = function['value']-section['address']
        need(offset >= 0 and offset+function['size'] <= section['size'],'Complete function storage')
        at = section['offset']+offset
        code = raw[at:at+function['size']]
        need(code == ORIGINAL[name],'Entire genuine function equals fresh original bytes: '+name)
        need(function['value'] == ((0 if name == STATUS else 6) if linked else 0),'Explicit diagnostic VMA0 function positions')
        codes[name], positions[name] = code, at
        facts[name] = dict(value=function['value'],bytes=function['size'],section=section['name'],code_sha256=digest(code),symbol_record_at=function['record_at'],file_offset=at)
    original_fields(codes[STATUS],codes[CLEAR])
    if linked:
        need(header[4] == 0,'Actual diagnostic entry; no physical placement claim')
    return dict(kind=header[1],flags=header[7],functions=facts,allocated=[{k:s[k] for k in ('name','size','flags','type','address')} for s in allocated],
                UND=[],global_ABS=[],REL_RELA=[],branch_resolved_in_assembler=True), dict(sections=sections,functions=functions,positions=positions)


def llvm_readback(path, facts):
    expected, seen = {}, []
    for name in NAMES:
        function, code = facts['functions'][name], ORIGINAL[name]
        offsets = (0,4) if name == STATUS else (0,2,6,10,12,16)
        mnemonics = ('lbu','ret') if name == STATUS else ('li','bltu','addi','add','sb','ret')
        for offset,mnemonic in zip(offsets,mnemonics):
            size = 4 if int.from_bytes(code[offset:offset+2],'little')&3 == 3 else 2
            expected[(function['section'],function['value']+offset)] = (code[offset:offset+size],mnemonic,name,offset)
    section = None
    for line in path.read_text(encoding='utf-8').splitlines():
        head = re.match(r'Disassembly of section (.+):',line)
        if head:
            section = head[1]
        match = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)',line)
        if not match:
            continue
        key = (section,int(match[1],16))
        need(key in expected and key not in seen,'Only complete owned LLVM instruction rows')
        raw,mnemonic,name,offset = expected[key]
        need(bytes.fromhex(match[2]) == raw and match[3] == mnemonic,'LLVM raw bytes and typed mnemonic')
        operand = match[4]
        if name == STATUS and offset == 0:
            need(operand == 'a0, 0xa7(gp)','LLVM fresh GP+167 unsigned byte read')
        if name == CLEAR and offset == 2:
            need(operand.startswith('a5, a0, ') and int(operand.split(', ')[2].split(' ')[0],16) == facts['functions'][CLEAR]['value']+16,
                 'LLVM unsigned branch to actual local RET, with correct source registers')
        seen.append(key)
    need(set(seen) == set(expected),'Full two-function LLVM disassembly readback')
    return dict(instructions=8,whole_function_raw_readback=True,local_branch_target_is_real_RET=True)


def ir(path, mode):
    text = path.read_text(encoding='utf-8')
    need(set(re.findall(r'^define[^\n]*@([^(]+)',text,re.M)) == set(NAMES),'Only two actual IR definitions')
    facts = {}
    for name,pin in zip(NAMES,IR_HASHES[mode]):
        match = re.search(r'define[^\n]*@'+name+r'\([^)]*\)[^{]*\{(.*?)\n\}',text,re.S)
        need(match is not None,'Genuine actual function IR')
        lines = []
        for line in match[1].splitlines():
            line = line.split(';',1)[0].strip()
            line = re.sub(r', ![A-Za-z.]+ !\d+','',line)
            line = re.sub(r' #\d+\b','',line)
            if line:
                lines.append(re.sub(r'\s+',' ',line))
        body = '\n'.join(lines)+'\n'
        need(not re.search(r'asm sideeffect "[^"]+',body),'Only empty register ports, no ASM algorithm')
        need(not re.search(r'call\b[^\n]*@',body) and 'alloca ' not in body,'No helper call or hidden C stack object')
        if name == STATUS:
            need('add i32 %1, 167' in body and 'load volatile i8, ptr %3' in body
                 and '%5 = zext i8 %4 to i32' in body and 'ret i32 %5' in body,'Fresh GP+167 volatile byte/zext def-use')
            need(body.count('load volatile') == 1 and 'store ' not in body,'One status read, no store')
        else:
            need('icmp ugt i32 %2, %3' in body and '(i32 2)' in body and 'br i1 %4, label %13, label %5' in body,'Unsigned input versus fixed A5=2 with real skip edge')
            need('add i32 %6, 192' in body and '%9 = add i32 %8, %2' in body and '%11 = add i32 %10, 1' in body
                 and 'store volatile i8 0, ptr %12' in body,'C GP-relative pointer sum and byte zero-store')
            need('load ' not in body and body.count('store volatile') == 1
                 and '"{x10},~{memory}"(i32 %2)' in body,'No readback or additional memory sample; A0 retained through empty port')
        need(digest(body.encode()) == pin,'Complete reviewed SSA/CFG body: '+name)
        facts[name] = dict(normalized_body_sha256=pin,ordinary_C_accesses=True,only_empty_register_ports=True)
    return facts


def negatives(raw, linked):
    _, parsed = elf(raw,linked)
    tests = [('machine',18,2,243^62),
             ('GP167_to175',parsed['positions'][STATUS],4,8<<20),
             ('unsigned_branch_to_signed',parsed['positions'][CLEAR]+2,4,0x2000),
             ('store_offset1_to0',parsed['positions'][CLEAR]+12,4,0x80)]
    fn = next(x for x in parsed['functions'] if x['name'] == CLEAR)
    tests.append(('fake_ABS_function',fn['record_at']+14,2,fn['index']^0xfff1))
    section = next(x for x in parsed['sections'] if x['flags']&4 and x['size'])
    tests.append(('writable_alloc',section['header_at']+8,4,1))
    rejected = []
    for name,at,size,mask in tests:
        bad = bytearray(raw)
        word = int.from_bytes(bad[at:at+size],'little')^mask
        bad[at:at+size] = word.to_bytes(size,'little')
        try:
            elf(bytes(bad),linked)
        except (ValueError,IndexError,struct.error):
            rejected.append(name)
        else:
            raise ValueError('Accepted actual raw ELF mutation: '+name)
    return rejected


def ir_negatives(llpath, mode):
    class Text:
        def __init__(self,value):
            self.value = value
        def read_text(self,**unused):
            return self.value
    text = llpath.read_text(encoding='utf-8')
    ir_rejected = []
    for name,old,new in [('old_GP175','add i32 %1, 167','add i32 %1, 175'),
                         ('signed_index','icmp ugt i32 %2, %3','icmp sgt i32 %2, %3'),
                         ('nonvolatile_store','store volatile i8 0','store i8 0')]:
        need(old in text,'Actual compiled IR negative seed')
        try:
            ir(Text(text.replace(old,new,1)),mode)
        except ValueError:
            ir_rejected.append(name)
        else:
            raise ValueError('Accepted actual IR mutation: '+name)
    return ir_rejected


def authored_inputs():
    return {p.relative_to(HERE).as_posix():sha(p) for p in sorted(HERE.rglob('*'))
            if p.is_file() and p.name != 'seal.json' and not any(x in ('build','__pycache__') for x in p.relative_to(HERE).parts)}


def source_seal():
    path = HERE/'seal.json'
    if not path.exists():
        return False
    sealed = json.loads(path.read_bytes())
    need(sealed['schema'] == 'TSL9-queue-small-provider-source-seal-v1'
         and sealed['authored_source_closure'] == authored_inputs() and sealed['sealed'] is True,
         'Unchanged local source seal; metadata check does not claim build artifacts exist')
    need(sealed['firmware_ready'] is False and sealed['target_execution'] is False,'No firmware/hardware readiness escalation')
    return True


def inspect(root, folder):
    build = builder()
    record = json.loads((folder/'compile-receipt.json').read_bytes())
    need(record['schema'] == 'TSL9-queue-small-provider-build-v1' and record['mode'] in ('c','cpp'),'Actual fixed-profile compile receipt')
    need(folder.is_relative_to(HERE/'build'),'Owned actual artifact folder')
    mode = record['mode']
    firmware = Path(record['firmware'])
    tools = {n:Path(p) for n,p in record['tools'].items()}
    need(set(tools) == set(build.TOOLS) and all(sha(tools[n]) == h for n,h in build.TOOLS.items()),'Exact existing LLVM tools')
    need(record['inputs'] == build.inputs(firmware,tools),'Full unchanged compiler source/tool/resource input set')
    need(sha(HERE/'src/providers.c') == SOURCE_SHA,'Unchanged readable provider source')
    need(sha(firmware) == build.FIRMWARE_SHA and firmware.stat().st_size == 76800,'Fresh official V4.1.60 identity')
    image = firmware.read_bytes()
    source_status,source_clear = image[0x1aa:0x1b0],image[0x20c:0x21e]
    need(source_status == ORIGINAL[STATUS] and source_clear == ORIGINAL[CLEAR],'Both actual mapped original leaves')
    original = original_fields(source_status,source_clear)
    inventory = {p.name:sha(p) for p in folder.iterdir() if p.is_file() and p.name not in ('compile-receipt.json','verification.json')}
    need(record['artifacts'] == inventory,'Complete actual compiler artifact inventory')
    need(len(record['commands']) == len(build.recipes(tools,folder,mode)),'All declared tool commands')
    for actual,(label,args) in zip(record['commands'],build.recipes(tools,folder,mode)):
        need(actual == dict(label=label,argv=[str(x) for x in args],exit=0,log_sha256=sha(folder/(label+'.log'))),'Exact command recipe/exit/log')
    stdint = tools['clang'].parent.parent/'lib/clang/18/include/stdint.h'
    need(sha(stdint) == build.STDINT_SHA and Path((folder/'resource.log').read_text().strip())/'include/stdint.h' == stdint,'Actual pinned compiler resource directory')
    dep = (folder/'native.d').read_text().replace('\\\n',' ')
    target,sep,tail = dep.partition(':')
    paths = {Path(re.sub(r'\\(.)',r'\1',x)).resolve() for x in re.findall(r'(?:\\.|[^\s])+',tail)}
    need(sep and target == 'native.o' and paths == {HERE/'src/providers.c',stdint},'Full actual -MD/-MF source and stdint closure')
    facts,controls = [],[]
    for name,linked in [('native.o',False),('COMPONENT-ONLY-NOT-FIRMWARE.elf',True)]:
        raw = (folder/name).read_bytes()
        result,_ = elf(raw,linked)
        result['LLVM_readback'] = llvm_readback(folder/('disassemble-linked.log' if linked else 'disassemble-object.log'),result)
        facts.append(result)
        controls.append(dict(kind='linked' if linked else 'object',actual_raw_ELF_controls=negatives(raw,linked)))
    return dict(passed=True,schema='TSL9-queue-small-provider-review-v1',mode=mode,
                firmware_sha256=sha(firmware),analysis_base=0x8000,original=original,
                ELF_facts=facts,IR_facts=ir(folder/'native.ll',mode),negative_controls=controls,
                actual_IR_controls=ir_negatives(folder/'native.ll',mode),mutations_in_memory_only=True,
                compiler_dependencies={str(p):sha(p) for p in sorted(paths)},
                compile_receipt_sha256=sha(folder/'compile-receipt.json'),authored_source_closure=authored_inputs(),
                actual_tool_invocations='compile/link/static disassembly only; help availability is not a machine-effects proof',
                whole_function_bytes_equal_original=True,local_branch_resolved=True,relocation_count=0,
                diagnostic_linked_function_spans={STATUS:[0,6],CLEAR:[6,24]},physical_placement_proved=False,
                full_callsite_composition_proved=False,global_fault_IRQ_context_proved=False,
                installed_ROM_proved=False,firmware_ready=False,OTA_ready=False,rebuilt_flashable_BIN=False,
                target_execution=False,HOST_execution=False,ISA_emulation=False,MMIO_execution=False,network=False,BIN_generated=False)


def replay(root, receipt):
    source_seal()
    need(receipt.name == 'verification.json' and receipt.parent.is_relative_to(HERE/'build'),'Owned read-only review receipt')
    expected = json.loads(receipt.read_bytes())
    actual = inspect(root,receipt.parent)
    need(actual == expected,'Whole read-only original/object/IR/control replay equality')
    return actual


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--folder',type=Path)
    p.add_argument('--receipt',type=Path)
    p.add_argument('--replay',type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    need(HERE == root/MODEL,'Canonical experiment root')
    if a.replay:
        need(not a.folder and not a.receipt,'Read-only replay mode')
        actual = replay(root,a.replay.resolve())
    elif a.folder:
        folder = a.folder.resolve()
        actual = inspect(root,folder)
        if a.receipt:
            receipt = a.receipt.resolve()
            need(receipt == folder/'verification.json' and not receipt.exists(),'Create-only actual review receipt')
            with receipt.open('xb') as output:
                output.write((json.dumps(actual,indent=2)+'\n').encode())
            replay(root,receipt)
    else:
        need(not a.receipt,'A review receipt requires actual artifacts')
        need(sha(HERE/'src/providers.c') == SOURCE_SHA,'Source metadata pin')
        print(json.dumps(dict(passed=True,metadata_only=True,source_seal_validated=source_seal(),source_sha256=SOURCE_SHA,authored_source_closure=authored_inputs(),firmware_ready=False)))
        return
    print(json.dumps(dict(passed=True,mode=actual['mode'],function_bytes=[6,18],instructions=[2,6],
                         exact_object_and_linked=True,REL_RELA=0,raw_ELF_negatives=12,IR_negatives=3,
                         firmware_ready=False,target_execution=False,HOST_execution=False)))


if __name__ == '__main__':
    main()
