"""Static source authoring for pinned startup spans; no target state or execution.

Emits fixed C statements and explicit architectural assembly ports. It neither
evaluates register/memory values nor contains an instruction execution loop.
Generated native bytes, not the authoring map's semantic labels, are the oracle.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAP = HERE / 'source-map-v1.json'
D = json.loads(MAP.read_bytes())
OPS = D['instructions']
BY_PC = {x['PC']: x for x in OPS}
REG = re.compile(r'\b(?:zero|ra|sp|gp|tp|t[0-6]|s[0-9]{1,2}|a[0-7])\b')
RESERVED_S = re.compile(r'\b(?:s[0-9]{1,2}|ra|fp|sp|gp|tp|t0|t2|t4|t5|t6)\b')


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parts(row):
    op, _, tail = row['op'].partition(' ')
    return op, [x.strip() for x in tail.split(',')] if tail else []


def control(row):
    op, args = parts(row)
    if op in ('j', 'jal', 'beq', 'bne', 'bltu', 'bgeu', 'bleu', 'bgtu', 'beqz', 'bnez', 'bgez'):
        return int(args[-1], 0)
    return None


def is_control(row):
    return control(row) is not None or parts(row)[0] in ('ret', 'jalr', 'jr', 'mret')


def architectural(row):
    op, args = parts(row)
    return bool(RESERVED_S.search(row['op'])) or op in ('nop','ebreak','csrw','csrs','mret') or (args and args[0] in ('sp', 'gp', 'tp'))


def pick_name(pc):
    if str(pc) in D.get('special_names', {}):
        return D['special_names'][str(pc)]
    candidates = D['parent_names'].get(str(pc), [])
    candidates = sorted(candidates, key=lambda x: (not x['defined'], not bool(x['size']), x['name']))
    if candidates:
        return candidates[0]['name']
    return ('tsl9_boot_' if pc in BY_PC else 'tsl9_boot_external_') + format(pc, 'x')


def source_and_spec():
    fw = (ROOT / D['firmware']).read_bytes()
    need(sha(fw) == D['firmware_sha256'], 'Pinned original firmware')
    need(len(BY_PC) == len(OPS), 'Unique original PC ownership')
    for start, end in D['ranges']:
        rows = [x for x in OPS if start <= x['PC'] < end]
        at = start
        for row in rows:
            b = bytes.fromhex(row['bytes'])
            need(row['PC'] == at and fw[at-0x8000:at-0x8000+len(b)] == b,
                 'Contiguous original instruction bytes')
            at += len(b)
        need(at == end, 'Complete bounded original range')

    # These are authoring partitions, not claims about ordinary C ABI entries.
    starts = set(D['entries'])
    for i, row in enumerate(OPS):
        next_pc = row['PC'] + len(bytes.fromhex(row['bytes']))
        target = control(row)
        if target in BY_PC:
            starts.add(target)
        if is_control(row) and next_pc in BY_PC:
            starts.add(next_pc)
        if i and row['PC'] == OPS[i-1]['PC'] + len(bytes.fromhex(OPS[i-1]['bytes'])):
            if not is_control(row) and not is_control(OPS[i-1]) and architectural(row) != architectural(OPS[i-1]):
                starts.add(row['PC'])
    # The one original function-address literal stays a real symbolic pair.
    pairs = []
    for a, b in zip(OPS, OPS[1:]):
        op, args = parts(a); bop, bargs = parts(b)
        if op == 'auipc' and bop == 'addi' and b['PC'] == a['PC'] + 4 and args[0] == bargs[0] == bargs[1]:
            target = (a['PC'] + (int(args[1], 0) << 12) + int(bargs[2], 0)) & 0xffffffff
            if target in D.get('literal_targets', D['entries']):
                need(b['PC'] not in starts, 'Actual same-region code-literal pair')
                pairs.append(dict(PC=a['PC'], target=target))
    pair_hi = {p['PC']: p for p in pairs}
    pair_lo = {p['PC']+4: p for p in pairs}
    groups = []
    for row in OPS:
        if row['PC'] in starts:
            groups.append([])
        need(groups, 'Owned region begins before every row')
        groups[-1].append(row)
    names = {row[0]['PC']: pick_name(row[0]['PC']) for row in groups}
    for pc in D['entries']:
        need(not any(x['defined'] for x in D['parent_names'].get(str(pc), [])), 'No duplicate existing true provider')

    out = ['#include <stdint.h>', '#if !defined(__riscv) || __riscv_xlen != 32',
           '#error Offline RV32 architectural regions only; never run on a HOST or device.', '#endif',
           '#ifdef __cplusplus', '#define ENTRY extern "C"', '#else', '#define ENTRY', '#endif',
           '#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))',
           '#define FRAME ENTRY __attribute__((used,naked,aligned(2)))',
           '#define INPUT(x) __asm__ volatile("" : "=r"(x) : : "memory")', '',
           '/* Complete original header/defaults/reset/IRQ ports/clock spans.',
           ' * C owns free-bank arithmetic/constants and ordinary memory.',
           ' * SP/GP/reserved-S/frame/PC/control effects remain explicit architecture ports.',
           ' * Regions require original placement and adjacency, not independent C ABI.',
           ' * Every opaque call ends a region; following regions resample live registers.',
           ' * No installed ROM, time units, field identities, bounds or IRQ assumptions.',
           ' * Static authoring only; native original-byte comparison is separate. */', '']
    regions = []
    indirect = []

    def asm_text(text, basic=False, outputs='', inputs=''):
        literal = json.dumps(text)
        return '    __asm__ volatile(' + literal + (');' if basic else ' : '+outputs+' : '+inputs+' : "memory");')

    for rows in groups:
        start = rows[0]['PC'];end = rows[-1]['PC']+len(bytes.fromhex(rows[-1]['bytes']))
        name = names[start]
        pure = all(architectural(x) or is_control(x) for x in rows)
        out += [f'/* Original0x{start:X}-0x{end:X}. */', ('FRAME' if pure else 'REGION')+' void '+name+'(void)', '{']
        regs = sorted({reg for row in rows if not is_control(row) and not architectural(row)
                       for reg in REG.findall(row['op']) if reg != 'zero'})
        for reg in regs:
            out.append(f'    register uint32_t {reg} __asm__("{reg}"); INPUT({reg});')
        free = [x for x in regs if x not in ('sp', 'gp', 'tp')]
        inputs = [x for x in regs if x in ('sp', 'gp', 'tp')]
        live = '    __asm__ volatile("" : '+', '.join('"+r"('+x+')' for x in free)+' : '+', '.join('"r"('+x+')' for x in inputs)+' : "memory");'
        for row in rows:
            pc = row['PC'];op,args = parts(row);width=len(bytes.fromhex(row['bytes']))
            if is_control(row):
                target=control(row)
                if target is None:
                    out.append(asm_text(row['op']+'\n', pure))
                    if op in ('jr','jalr'):
                        indirect.append(dict(PC=pc,bytes=row['bytes'],kind='call'if op=='jalr'else'tail',register=args[0],identity='unknown'))
                else:
                    kind = 45 if width==2 and op in ('j','jal') else 44 if width==2 else 17 if op in ('j','jal') else 16
                    label=f'.Levent_control_{pc:x}'
                    if op in ('j','jal'):
                        instruction=('c.jal' if op=='jal' else 'c.j')+' '+label if width==2 else 'jal '+('ra'if op=='jal'else'zero')+', '+label
                    else:
                        instruction=op+' '+', '.join(args[:-1]+[label])
                    directive={16:'R_RISCV_BRANCH',17:'R_RISCV_JAL',44:'R_RISCV_RVC_BRANCH',45:'R_RISCV_RVC_JUMP'}[kind]
                    text=label+':\n.option push\n.option '+('rvc'if width==2 else'norvc')+'\n'+instruction+'\n.option pop\n.reloc .-'+str(width)+', '+directive+', '+names.get(target,pick_name(target))+'\n'
                    out.append(asm_text(text,pure))
                continue
            rd=args[0] if args else None
            if architectural(row) and pc not in pair_hi and pc not in pair_lo:
                text='.option push\n.option '+('rvc'if width==2 else'norvc')+'\n'+row['op']+'\n.option pop\n'
                out.append(asm_text(text,pure));continue
            if pc in pair_hi:
                pair=pair_hi[pc];label=f'.Levent_hi_{pc:x}'
                out.append(asm_text(label+':\nauipc '+rd+', 0\n.reloc .-4, R_RISCV_PCREL_HI20, '+names.get(pair['target'],pick_name(pair['target']))+'\n',pure,'"=r"('+rd+')'))
            elif pc in pair_lo:
                pair=pair_lo[pc];label=f'.Levent_hi_{pair["PC"]:x}'
                out.append(asm_text('.option push\n.option norvc\naddi '+rd+', '+args[1]+', 0\n.option pop\n.reloc .-4, R_RISCV_PCREL_LO12_I, '+label+'\n',pure,'"+r"('+rd+')'))
            elif op=='auipc':
                out.append(asm_text(row['op']+'\n',False,'"=r"('+rd+')'))
            else:
                stmt=None
                def val(x):return '0u'if x=='zero'else x
                def const(x):return 'UINT32_C(0x'+format(int(x,0)&0xffffffff,'x')+')'
                if op in ('li','lui'):
                    value=int(args[1],0) << (12 if op=='lui'else 0)
                    stmt=f'{rd} = UINT32_C(0x{value&0xffffffff:x});'
                elif op=='mv':stmt=f'{rd} = {val(args[1])};'
                elif op in ('addi','andi','xori','ori'):
                    operator={'addi':'+','andi':'&','xori':'^','ori':'|'}[op]
                    stmt=f'{rd} = {val(args[1])} {operator} {const(args[2])};'
                elif op in ('add','sub','and','or','mul'):
                    operator={'add':'+','sub':'-','and':'&','or':'|','mul':'*'}[op]
                    stmt=f'{rd} = {val(args[1])} {operator} {val(args[2])};'
                elif op in ('slli','srli'):
                    stmt=f'{rd} = {val(args[1])} '+('<<'if op=='slli'else'>>')+f' {int(args[2],0)}u;'
                elif op=='seqz':stmt=f'{rd} = ({val(args[1])} == 0u);'
                elif op in ('lw','lhu','lbu','sw','sh','sb'):
                    mem=re.fullmatch(r'(-?(?:0x[0-9a-f]+|[0-9]+))\(([a-z][a-z0-9]*)\)',args[1])
                    need(mem is not None,'Known direct memory operand')
                    off,base=mem.groups();address=f'({base} + {const(off)})'
                    typ={'lw':'uint32_t','sw':'uint32_t','lhu':'uint16_t','sh':'uint16_t','lbu':'uint8_t','sb':'uint8_t'}[op]
                    access=f'*(volatile {typ} *)(uintptr_t){address}'
                    stmt=f'{rd} = {access};'if op.startswith('l')else f'{access} = ({typ}){val(rd)};'
                need(stmt is not None,'Unsupported static authoring opcode '+op)
                out.append('    '+stmt)
            if not pure:out.append(live)
        if not pure:out.append('    __builtin_unreachable();')
        out += ['}', '']
        raw=fw[start-0x8000:end-0x8000]
        regions.append(dict(name=name,start=start,end=end,bytes=len(raw),original_sha256=sha(raw)))
    source='\n'.join(out).rstrip()+'\n'
    spec={k:D[k]for k in ('firmware','firmware_sha256','reader','reader_sha256','curation_checker','curation_checker_sha256','tools','stdint_sha256','profile','flags')}
    spec.update(schema='TSL9-original-startup-normal-artifact-contract-v1',source='experiments/tsl9-original-startup/src/boot_original.v1.c',source_sha256=sha(source.encode()),author='experiments/tsl9-original-startup/author-v1.py',author_sha256=sha(Path(__file__).read_bytes()),source_map='experiments/tsl9-original-startup/source-map-v1.json',source_map_sha256=sha(MAP.read_bytes()),regions=regions,PC_relative_pairs=pairs,indirect_sites=indirect)
    return source,(json.dumps(spec,indent=2,ensure_ascii=True)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--emit',choices=('source','spec'))
    p.add_argument('--offset',type=int,default=0)
    p.add_argument('--limit',type=int,default=16000)
    a=p.parse_args();source,spec=source_and_spec()
    if a.emit:
        need(a.offset>=0 and 0<a.limit<=20000,'Bounded textual authoring slice')
        text=source if a.emit=='source'else spec
        print(json.dumps(text[a.offset:a.offset+a.limit]));return
    d=json.loads(spec)
    print(json.dumps(dict(source_characters=len(source),spec_characters=len(spec),regions=len(d['regions']),code_bytes=sum(x['bytes']for x in d['regions']),instructions=len(OPS),PC_relative_pairs=d['PC_relative_pairs'],indirect_sites=len(d['indirect_sites']))))


if __name__=='__main__':main()
