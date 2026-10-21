"""Read the actual current image object before planning the twelfth source owner."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
BASELINE_SHA = '4e86cebc1119d30a726386cc520d73c5384920bb74bd97dbbc5dfa505c6bfbf2'
FIRMWARE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
OWNER = '.text.tsl9v4160.ota_handler_9b8e'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(value, message):
    if not value:
        raise ValueError(message)


def inspect(root, source, firmware):
    root, source, firmware = root.resolve(), source.resolve(), firmware.resolve()
    need(source.is_relative_to(root) and firmware.is_relative_to(root), 'Explicit project-local artifacts')
    need(sha(source) == BASELINE_SHA and sha(firmware) == FIRMWARE_SHA, 'Actual current baseline and original identities')
    parser = root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
    if not parser.is_file():
        parser = root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py'
    need(sha(parser) == PARSER_SHA, 'Pinned bounded ELF parser')
    spec = importlib.util.spec_from_file_location('reply_owner_inventory_elf',parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    elf = module.ELF(source)
    section = elf.byname[OWNER]
    need(elf.kind == 1 and section['type'] == 1 and section['flags'] == 6
         and section['size'] == 124 and section['alignment'] == 2, 'Actual original executable owner')
    body = elf.data(section)
    need(body == firmware.read_bytes()[0x9b8e-0x8000:0x9c0a-0x8000], 'Complete original reply stream remains in the raw owner')
    incoming = [r for r in elf.relocations if r['symbol']['index'] == section['index'] and r['owner'] != OWNER]
    outgoing = [r for r in elf.relocations if r['owner'] == OWNER]
    globals_ = [s for s in elf.symbols if s['index'] == section['index'] and s['name'] and s['info'] >= 16]
    need(len(incoming) == 1 and incoming[0]['owner'] == '.text.tsl9v4160.ota_handler_9c4a'
         and incoming[0]['offset'] == 426 and incoming[0]['type'] == 45
         and incoming[0]['symbol']['value'] == incoming[0]['addend'] == incoming[0]['symbol']['info'] == 0,
         'One recorded compressed incoming call to the local entry; preserve that role')
    need([(r['offset'],r['type']) for r in outgoing] == [(34,44),(82,17)], 'One private branch and one direct TX call')
    need(outgoing[0]['symbol']['value']+outgoing[0]['addend'] == 108
         and outgoing[1]['symbol']['name'] == '__tsl9v4160_call_8a56'
         and outgoing[1]['symbol']['info'] == 18 and outgoing[1]['symbol']['size'] == 280,
         'Actual null-path target and real section-backed TX function role')
    need(len(globals_) == 1 and globals_[0]['name'] == '__tsl9v4160_ota_code_9b8e'
         and globals_[0]['info'] == 16 and globals_[0]['value'] == globals_[0]['size'] == 0,
         'Original public entry is NOTYPE/size0, not FUNC124')
    allocations = [s for s in elf.sections if s['flags'] & 2 and s['size']]
    need(len(allocations) == 691 and len(elf.relocations) == 8270, 'Current entire-image allocation/relocation baseline')
    return dict(schema='TSL9-OTA-reply-original-owner-inventory-v1',passed=True,
                input=dict(path=source.relative_to(root).as_posix(),sha256=sha(source)),
                firmware_sha256=sha(firmware),parser_sha256=PARSER_SHA,
                section=section,original_bytes_sha256=hashlib.sha256(body).hexdigest(),
                original_public_symbols=globals_,recorded_incoming=incoming,original_outgoing=outgoing,
                measured_current=dict(allocations=691,RELA=8270,readable_functions=11,readable_function_bytes=526),
                conditional_next=dict(readable_functions=12,readable_function_bytes=650,retained_storage_sections=679,
                                      outside_RELA=8257,owned_JAL_RELA=12,total_RELA=8269,discharged_private_branches=11,
                                      incoming_recorded_entries=21,canonical_relative_binding_count='measure after actual typed merge'),
                prerequisites=['actual readable native implementation','original124B placement and instruction/call boundaries',
                               'preserve actual NOTYPE public and local incoming roles','actual compiler and dependency provenance',
                               'strict missing-ROM failure plus numeric-only witness','fresh section/LOAD/BIN and independent reviews'],
                integration_completed=False,new_compilation=False,computed_interior_entries_proved_absent=False,
                target_execution=False,emulation=False,hardware=False,OTA_ready=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--object',type=Path,required=True)
    parser.add_argument('--firmware',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args = parser.parse_args()
    result = inspect(args.project_root,args.object,args.firmware)
    need(args.receipt.resolve().is_relative_to(args.project_root.resolve()), 'Project-local create-only receipt')
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    with args.receipt.open('xb') as out:
        out.write((json.dumps(result,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(passed=True,original_bytes=124,recorded_incoming=1,outgoing_RELA=2,
                          public_entry_role='NOTYPE/size0',integration_completed=False,target_execution=False)))
