"""Offline positive compile-only requirements audit; never execute firmware.

Reads two exact official images and a caller-selected saved SDK header.
Produces fresh RV32 ET_REL files with no allocated code/data and a receipt.
No network, negative/fault tests, ROM reads, emulator, linker, BIN, or hardware.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FW_DIR = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs'
PINS = {
    'current': '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
    'legacy': '32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc',
    'source_map': '31c5965cce82f511cf3687091a419b715a095945c7b1af24d41434e0fb33ddc0',
    'reader': '2f7a5dc2d4eeb823e0e4c63f81b3c4fdcffe7cbb39262dc7f6731be675016b15',
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'stdint': '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34',
    'sdk_header': 'fab43e7b8e351596a14d2a434eea4fa79587a8b9bba12738897d35ee2c3dbf2e',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pinned(path, name):
    data = path.read_bytes()
    require(sha(data) == PINS[name], 'input digest mismatch: ' + name)
    return data


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def word(image, pc):
    at = pc - 0x8000
    require(0 <= at <= len(image) - 4, 'instruction outside image')
    return struct.unpack_from('<I', image, at)[0]


def auipc_addi(image, pc, register):
    first, second = word(image, pc), word(image, pc + 4)
    require(first & 127 == 0x17 and (first >> 7) & 31 == register,
            'AUIPC instruction/register mismatch')
    require(second & 127 == 0x13 and (second >> 12) & 7 == 0 and
            (second >> 7) & 31 == register and (second >> 15) & 31 == register,
            'ADDI instruction/register mismatch')
    return (pc + signed(first & 0xfffff000, 32) + signed(second >> 20, 12)) & 0xffffffff


def jal(image, pc, register):
    value = word(image, pc)
    require(value & 127 == 0x6f and (value >> 7) & 31 == register, 'JAL shape')
    immediate = (((value >> 31) & 1) << 20 | ((value >> 12) & 255) << 12 |
                 ((value >> 20) & 1) << 11 | ((value >> 21) & 1023) << 1)
    return (pc + signed(immediate, 21)) & 0xffffffff


def branch(image, pc, funct3, rs1, rs2, target):
    value = word(image, pc)
    require(value & 127 == 0x63 and (value >> 12) & 7 == funct3 and
            (value >> 15) & 31 == rs1 and (value >> 20) & 31 == rs2, 'branch shape')
    immediate = (((value >> 31) & 1) << 12 | ((value >> 7) & 1) << 11 |
                 ((value >> 25) & 63) << 5 | ((value >> 8) & 15) << 1)
    require((pc + signed(immediate, 13)) & 0xffffffff == target, 'branch target')


def startup(image, reset):
    require(len(image) == 76800 and jal(image, 0x8000, 0) == reset, 'entry/version binding')
    gp = auipc_addi(image, reset, 3)
    sp = auipc_addi(image, reset + 8, 2)
    source = auipc_addi(image, reset + 16, 10)
    end = auipc_addi(image, reset + 56, 11)
    require(word(image, reset + 24) == 0x00018593, 'mv a1,gp setup')
    # Derive each version's length; V4.1.00 copies 136 bytes, not 128.
    copy_setup, zero_setup = word(image, reset + 28), word(image, reset + 52)
    require(copy_setup & 0xfffff == 0x18613 and zero_setup & 0xfffff == 0x18513,
            'copy/zero GP-relative ADDI shape')
    initialized = signed(copy_setup >> 20, 12)
    require(initialized == signed(zero_setup >> 20, 12) and initialized > 0 and initialized % 4 == 0,
            'copy length and zero start must agree')
    branch(image, reset + 32, 7, 11, 12, reset + 52)
    branch(image, reset + 48, 6, 11, 12, reset + 36)
    branch(image, reset + 64, 7, 10, 11, reset + 78)
    branch(image, reset + 74, 6, 10, 11, reset + 68)
    for offset, expected in ((36, 0x00052283), (40, 0x0055a023), (68, 0x00052023)):
        require(word(image, reset + offset) == expected, 'word copy/zero load and stores')
    require(image[reset + 44 - 0x8000:reset + 48 - 0x8000] == bytes.fromhex('11059105') and
            image[reset + 72 - 0x8000:reset + 74 - 0x8000] == bytes.fromhex('1105'), 'word loop steps')
    return dict(reset_pc=reset, initial_gp=gp, initial_sp=sp, initializer_source=source,
                initialized_bytes=initialized, copy_end=gp + initialized, zero_end=end,
                initialization_span_bytes=end - gp, zero_bytes=end - gp - initialized,
                numeric_gap_to_initial_sp=sp - end)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True, help='new output directory only')
    ap.add_argument('--sdk-header', type=Path, required=True, help='previously saved pinned wchble_rom.h')
    ap.add_argument('--llvm-bin', type=Path, default=Path.home() / 'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    args = ap.parse_args()
    current_path = FW_DIR / 'ID-2966-V4.1.60-decoded.bin'
    legacy_path = FW_DIR / 'ID-2581-V4.1.00-decoded.bin'
    current, legacy = pinned(current_path, 'current'), pinned(legacy_path, 'legacy')
    source_map_path = ROOT / 'experiments/tsl9-original-startup/source-map-v1.json'
    source_map = json.loads(pinned(source_map_path, 'source_map'))
    witnesses = [row for row in source_map['instructions'] if 0x186aa <= row['PC'] <= 0x18734]
    require(len(witnesses) == 38, 'startup witness count')
    for row in witnesses:
        raw = bytes.fromhex(row['bytes'])
        require(current[row['PC'] - 0x8000:row['PC'] - 0x8000 + len(raw)] == raw,
                'source-map byte witness mismatch')
    now, old = startup(current, 0x186aa), startup(legacy, 0x183fe)
    require(now['zero_end'] - old['zero_end'] == 8, 'version-specific endpoint difference')
    require(now['initialization_span_bytes'] == 35160 and old['initialization_span_bytes'] == 35152,
            'current/legacy spans')
    require(now['initialized_bytes'] == 128 and old['initialized_bytes'] == 136 and
            now['zero_bytes'] - old['zero_bytes'] == 16, 'version-specific copy/zero split')
    for pc, expected in ((0x186fa, 0xbc029073), (0x18700, 0x80429073), (0x1871c, 0x30529073),
                         (0x1872c, 0x34129073), (0x18734, 0x30200073)):
        require(word(current, pc) == expected, 'CSR/return instruction')
    vector_base = auipc_addi(current, 0x18710, 5)
    mepc = auipc_addi(current, 0x18724, 5)
    resident = jal(current, 0x18730, 0)
    require(word(current, 0x18718) == 0x0032e293, 'mtvec low-bit setup')
    require((vector_base, mepc, resident) == (0x8038, 0x9008, 0x40000), 'transfer addresses')

    sdk = pinned(args.sdk_header, 'sdk_header').decode('gb18030').splitlines()
    sdk_checks = {2714: '#define LIB_FLASH_BASE_ADDRESSS 0x00040000',
                  2721: '#define FUNCITON_BASE_ADDRESSS (LIB_FLASH_BASE_ADDRESSS+0x34)',
                  2725: '#define BLE_LIB_JT(n) (*(uint32_t*)( FUNCITON_BASE_ADDRESSS+n*4 ))'}
    for line, expected in sdk_checks.items():
        require(' '.join(sdk[line - 1].split()) == expected, 'saved SDK macro correspondence')
    for line, name, index in ((2776, 'tmos_memset', 5), (2777, 'tmos_memcpy', 6)):
        require(name in sdk[line - 1] and 'BLE_LIB_JT(%d)' % index in sdk[line - 1], 'saved SDK slot index')

    header_path = HERE / 'requirements-v1.h'
    header = header_path.read_text()
    numbers = {m[0]: int(m[1], 0) for m in re.findall(r'^#define (TSL9_\w+) UINT32_C\((0x[0-9a-f]+|[0-9]+)\)$', header, re.M)}
    expected_numbers = {'TSL9_FW_BASE': 0x8000, 'TSL9_FW_END': 0x1ac00,
                        'TSL9_RESET_PC': now['reset_pc'], 'TSL9_INITIAL_GP': now['initial_gp'],
                        'TSL9_INITIAL_SP': now['initial_sp'], 'TSL9_INITIALIZER_SOURCE': now['initializer_source'],
                        'TSL9_INITIALIZED_BYTES': now['initialized_bytes'], 'TSL9_ZERO_END': now['zero_end'],
                        'TSL9_VECTOR_BASE': vector_base, 'TSL9_INITIAL_MEPC': mepc,
                        'TSL9_RESIDENT_ENTRY': resident, 'TSL9_CANDIDATE_RAM_BASE': 0x20000000,
                        'TSL9_CANDIDATE_RAM_END': 0x20010000, 'TSL9_SDK_TABLE_BASE': 0x40034,
                        'TSL9_SDK_SLOT_STRIDE': 4, 'TSL9_SDK_MEMSET_SLOT': 0x40048, 'TSL9_SDK_MEMCPY_SLOT': 0x4004c}
    require(numbers == expected_numbers and PINS['current'] in header, 'C requirements drift from decoded evidence')

    reader_path = ROOT / 'experiments/tsl9-feature-dispatch-tree/elf_reader-v4.py'
    pinned(reader_path, 'reader')
    module_spec = importlib.util.spec_from_file_location('tsl9_contract_elf_reader', reader_path)
    reader = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(reader)
    clang = args.llvm_bin / 'clang.exe'
    pinned(clang, 'clang')
    stdint = args.llvm_bin.parent / 'lib/clang/18/include/stdint.h'
    pinned(stdint, 'stdint')
    output = args.output.resolve()
    require(not output.exists(), 'output must be a fresh directory')
    output.mkdir(parents=True)
    modes = {}
    for mode, language, standard in (('c', 'c', 'c11'), ('cpp', 'c++', 'c++17')):
        object_path = output / (mode + '-requirements.o')
        flags = ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32',
                 '-ffreestanding', '-fno-ident', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                 '-Wall', '-Wextra', '-Werror', '-x', language, '-std=' + standard]
        result = subprocess.run([str(clang), *flags, '-c', 'experiments/tsl9-memory-rom-contract/layout-contract-v1.c',
                                 '-o', str(object_path)], cwd=ROOT, capture_output=True)
        require(result.returncode == 0, 'positive ' + mode + ' requirements compilation failed')
        require(not result.stdout and not result.stderr, 'unexpected compiler diagnostics')
        elf = reader.ELF(object_path)
        allocated = [s for s in elf.sections if s['flags'] & 2 and s['size']]
        undefined = [s for s in elf.symbols if s['section'] == 0 and s['name']]
        require(elf.header[0] == 1 and elf.header[3] == 0 and not elf.program_headers,
                'compile-only ET_REL with entry zero and no program headers required')
        require(not allocated and not undefined and not elf.relocations, 'contract emitted executable/data requirements')
        modes[mode] = dict(language=language, standard=standard, flags=flags,
                           object=object_path.name, sha256=sha(object_path.read_bytes()),
                           elf_type='ET_REL', entry=0, program_headers=0,
                           nonempty_allocated_sections=0, allocated_code_data_bytes=0,
                           relocations=0, undefined_symbols=0)
    evidence = dict(schema='TSL9-memory-ROM-requirements-v1', passed=True,
                    inputs={name: {'path': path.relative_to(ROOT).as_posix(), 'sha256': PINS[name]}
                            for name, path in (('current', current_path), ('legacy', legacy_path),
                                               ('source_map', source_map_path), ('reader', reader_path))},
                    sdk_header={'reference': '${ANALYSIS_WORKSPACE}/apk-analysis/tsl9-function-hardware/hardware/wchble_rom.h',
                                'sha256': PINS['sdk_header'], 'source_url': 'https://raw.githubusercontent.com/openwch/ch32v20x/baef0054588f4826548429ff4e7a9257d752ef2f/EVT/EXAM/BLE/LIB/wchble_rom.h',
                                'checked_lines': [2714, 2721, 2725, 2776, 2777],
                                'default_table_base': 0x40034, 'slot_stride': 4,
                                'memset_pointer_slot': 0x40048, 'memcpy_pointer_slot': 0x4004c,
                                'installed_library_identity_proved': False},
                    current=now, legacy=old, zero_end_difference_bytes=8,
                    initialized_length_difference_bytes=-8, zero_length_difference_bytes=16,
                    startup_source_map_byte_witnesses=len(witnesses),
                    independent_decoding={'auipc_addi_pairs': 10, 'jal_targets': 3, 'loop_branch_targets': 8,
                                          'load_store_words': 6, 'csr_return_words': 5, 'compressed_word_step_sites': 6},
                    transfers={'vector_base': vector_base, 'mtvec_value': vector_base | 3,
                               'initial_mepc': mepc, 'external_resident_entry': resident},
                    compiler={'reference': '${LLVM_BIN}/clang.exe', 'sha256': PINS['clang'], 'stdint_sha256': PINS['stdint']},
                    authored_inputs={p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
                                     for p in (header_path, HERE / 'layout-contract-v1.c', Path(__file__))},
                    modes=modes,
                    limits={'scope': 'Exact-image startup numeric requirements and saved SDK default profile only.',
                            'candidate_RAM_bytes': 65536, 'candidate_chip_identified': False,
                            'RAM_ownership_proved': False, 'gap_is_validated_stack_budget': False,
                            'installed_ROM_body_or_ABI_proved': False, 'interrupt_runtime_proved': False,
                            'OTA_compatibility_proved': False, 'target_or_host_model_or_ISA_executed': False,
                            'hardware_accessed': False, 'network_accessed': False, 'BIN_created': False,
                            'new_reconstructed_firmware_bytes': 0})
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'current_initialization_span_bytes': now['initialization_span_bytes'],
                      'legacy_initialization_span_bytes': old['initialization_span_bytes'],
                      'zero_end_difference_bytes': 8, 'C_CPP_compile_only_passed': True,
                      'allocated_code_data_bytes': 0, 'new_firmware_bytes': 0}))


if __name__ == '__main__':
    main()
