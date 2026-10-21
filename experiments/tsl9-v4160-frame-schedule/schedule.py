"""Schedule only source-owned automatic C.SWSP saves in a new C/C++ object.

No opcode generation, original BIN input, target execution or ISA emulation.
The final object is compiler output plus this explicit ABI scheduling step.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_parser(root):
    candidates = (root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',
                  root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py')
    path = next((p for p in candidates if p.is_file()), None)
    need(path is not None and digest(path.read_bytes()) == PARSER_SHA, 'Pinned bounded ELF parser')
    spec = importlib.util.spec_from_file_location('frame_schedule_elf', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ELF


def decode_stack_add(word):
    need(word & 0xe003 == 0x0001 and (word >> 7) & 31 == 2, 'Unchanged two-byte C.ADDI SP')
    value = ((word >> 2) & 31) | (((word >> 12) & 1) << 5)
    return value - 64 if value & 32 else value


def decode_save(word):
    need(word & 0xe003 == 0xc002, 'Only compiler-generated two-byte C.SWSP')
    register = (word >> 2) & 31
    offset = (((word >> 9) & 15) << 2) | (((word >> 7) & 3) << 6)
    return register, offset


def plan(elf, policy, selected):
    need(elf.kind == 1 and elf.flags == 1, 'RV32 RVC soft-float ET_REL source object')
    need(struct.unpack_from('<H', elf.raw, 44)[0] == 0, 'Relocatable object has no program headers')
    need(policy['schema'] == 'TSL9-source-owned-frame-schedule-v1', 'Explicit source-owned frame policy')
    need(not any(s['size'] and s['name'].startswith(('.eh_frame', '.debug_frame', '.sframe', '.orc_unwind', '.note.gnu.build-id'))
                 for s in elf.sections), 'No unwind/frame/build-id metadata may become stale')
    patches, proofs = [], []
    shoff = struct.unpack_from('<I', elf.raw, 32)[0]
    shend = shoff + len(elf.sections)*40
    for name in selected:
        rule = policy['functions'][name]
        symbols = [s for s in elf.symbols if s['name'] == rule['symbol']]
        need(len(symbols) == 1, 'One actual source-defined C/C++ function '+name)
        symbol = symbols[0]
        need(symbol['info'] == 18 and symbol['other'] == 0 and symbol['value'] == 0 and symbol['size'] == rule['bytes']
             and 0 < symbol['index'] < len(elf.sections), 'Actual full function at its section entry')
        section = elf.sections[symbol['index']]
        need(sum(s['name'] == rule['section'] for s in elf.sections) == 1,
             'One unambiguous selected executable section name')
        need(section['name'] == rule['section'] and section['type'] == 1 and section['flags'] == 6
             and section['size'] == rule['bytes'], 'Only the exact source-owned executable section')
        old_order = [tuple(x) for x in rule['compiler_order']]
        required = [tuple(x) for x in rule['required_order']]
        need(3 <= len(old_order) <= 4 and len(set(old_order)) == len(old_order) and set(old_order) == set(required)
             and len(required) == len(old_order) and old_order != required, 'A permutation of unique existing saves')
        need(all(reg in (1,8,9,18) and offset % 4 == 0 and 0 <= offset <= rule['frame_bytes']-4 for reg,offset in old_order)
             and len({offset for reg,offset in old_order}) == len(old_order), 'Disjoint four-byte slots in the declared frame')
        data = elf.data(section)
        need(decode_stack_add(struct.unpack_from('<H',data)[0]) == -rule['frame_bytes'], 'Declared compiler frame size')
        lo, hi = 2, 2+2*len(old_order)
        actual = [decode_save(struct.unpack_from('<H',data,at)[0]) for at in range(lo,hi,2)]
        need(actual == old_order, 'Exact observed compiler save order; reject reapplication')
        need(not any(s['index'] == section['index'] and lo <= s['value'] < hi for s in elf.symbols),
             'No named or mapping symbol anchors inside the scheduled saves')
        for relocation in elf.relocations:
            need(not (relocation['owner'] == section['name'] and 0 <= relocation['offset'] < hi), 'No relocation site in the prologue')
            target = relocation['symbol']
            need(not (target['index'] == section['index'] and lo <= target['value']+relocation['addend'] < hi),
                 'No recorded reference targets a scheduled interior')
        start, end = section['offset']+lo, section['offset']+hi
        need(start >= 52 and not (start < shend and shoff < end), 'No ELF header/table overlap')
        for other in elf.sections:
            if other['index'] != section['index'] and other['type'] != 8 and other['size']:
                need(not (start < other['offset']+other['size'] and other['offset'] < end), 'No aliased section storage')
        words = {pair:data[lo+2*i:lo+2*i+2] for i,pair in enumerate(actual)}
        replacement = b''.join(words[pair] for pair in required)
        patches.append((start,end,replacement))
        proofs.append(dict(function=name,source_symbol=rule['symbol'],section=section['name'],
                           frame_bytes=rule['frame_bytes'],scheduled_section_interval=[lo,hi],
                           compiler_order=[list(x) for x in actual],required_order=[list(x) for x in required],
                           compiler_words=[words[x].hex() for x in actual],scheduled_words=[words[x].hex() for x in required],
                           all_instructions_are_existing_compiler_saves=True))
    need(len(selected) == len(set(selected)) and selected, 'Unique explicit selected functions')
    patches.sort()
    need(all(a[1] <= b[0] for a,b in zip(patches,patches[1:])), 'Disjoint output intervals')
    result = bytearray(elf.raw)
    for start,end,replacement in patches:
        result[start:end] = replacement
    changed = [i for i,(a,b) in enumerate(zip(elf.raw,result)) if a != b]
    need(len(result) == len(elf.raw) and all(any(lo <= i < hi for lo,hi,_ in patches) for i in changed), 'Only declared byte permutations')
    return bytes(result), proofs, changed


def transform(root, source, destination, receipt, selected):
    root = root.resolve()
    source,destination,receipt = (path.resolve() for path in (source,destination,receipt))
    for path in (source,destination,receipt):
        need(path.resolve().is_relative_to(root), 'All explicit artifacts remain inside the project')
    need(not destination.exists() and not receipt.exists() and len({source,destination,receipt}) == 3, 'Three distinct paths and create-only outputs')
    policy_path = HERE/'frame-policy.json'
    policy = json.loads(policy_path.read_text(encoding='utf8'))
    ELF = load_parser(root)
    before = ELF(source)
    payload, proofs, changed = plan(before,policy,selected)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('xb') as out:
        out.write(payload)
    after = ELF(destination)
    need(before.sections == after.sections and before.symbols == after.symbols and before.relocations == after.relocations,
         'All section metadata, symbols and relocations remain identical')
    for proof in proofs:
        data = after.data(after.byname[proof['section']])
        lo,hi = proof['scheduled_section_interval']
        need([list(decode_save(struct.unpack_from('<H',data,at)[0])) for at in range(lo,hi,2)] == proof['required_order'], 'Actual output save order')
    value = dict(schema='TSL9-explicit-ABI-frame-scheduling-receipt-v1',passed=True,
                 tool_sha256=digest(Path(__file__).read_bytes()),policy_sha256=digest(policy_path.read_bytes()),parser_sha256=PARSER_SHA,
                 input=dict(path=source.relative_to(root).as_posix(),bytes=len(before.raw),sha256=digest(before.raw)),
                 output=dict(path=destination.relative_to(root).as_posix(),bytes=len(payload),sha256=digest(payload)),
                 functions=proofs,changed_file_offsets=changed,section_metadata_symbols_RELA_identical=True,
                 original_BIN_read_for_generation=False,new_opcodes_generated=False,padding_added=False,
                 pipeline='C/C++ compiler output followed by explicit source-owned ABI frame scheduling',
                 compiler_alone_emitted_scheduled_order=False,computed_interior_entries_proved_absent=False,
                 target_execution=False,ISA_emulation=False,hardware=False,OTA_ready=False)
    receipt.parent.mkdir(parents=True,exist_ok=True)
    with receipt.open('xb') as out:
        out.write((json.dumps(value,indent=2)+'\n').encode('utf8'))
    return value


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,default=HERE.parents[1])
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--receipt',required=True,type=Path)
    p.add_argument('--functions',choices=['irq','quarter'],nargs='+',default=['irq','quarter'])
    a = p.parse_args()
    result = transform(a.project_root.resolve(),a.input.resolve(),a.output.resolve(),a.receipt.resolve(),a.functions)
    print(json.dumps(dict(passed=True,functions=len(result['functions']),changed_bytes=len(result['changed_file_offsets']),
                         receipt=str(a.receipt),original_BIN_read_for_generation=False,target_execution=False,OTA_ready=False)))
