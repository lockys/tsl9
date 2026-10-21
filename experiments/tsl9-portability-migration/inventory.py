#!/usr/bin/env python3
"""Bounded static inventory of published tracked scripts; does not run a verifier."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
BASELINE = '99de4f9d4da22f0cd28e039e0197defebf48fb72'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True, encoding='utf-8').strip()


def lines(text, regex):
    return [{'line': number, 'text': line.strip()} for number, line in enumerate(text.splitlines(), 1) if re.search(regex, line, re.I)]


def top_param(text):
    match = re.search(r'\bparam\s*\(', text, re.I)
    if not match:
        return ''
    start = match.end()
    depth = 1
    quote = None
    for pos in range(start, len(text)):
        c = text[pos]
        if quote:
            if c == quote and (pos == 0 or text[pos - 1] != '`'):
                quote = None
        elif c in "'\"":
            quote = c
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return text[start:pos]
    raise ValueError('unbalanced top param')


def analyze(root, name):
    raw = (root / name).read_bytes()
    text = raw.decode('utf-8-sig')
    low = text.lower()
    suite_dir = (root / name).parent
    if re.search(r'Split-Path\s+-Parent\s+\$PSScriptRoot', text, re.I):
        suite_dir = suite_dir.parent
    params = top_param(text)
    quoted = [m.group(2) for m in re.finditer(r"(['\"])([^'\"\r\n]*)\1", text)]
    paths = sorted({s.replace('\\', '/') for s in quoted if re.search(r'\.(?:c|h|py|json|bin|hex|ps1)$', s, re.I) and not any(c in s for c in '$:*?')})
    source_refs = []
    for rel in paths:
        if not rel.startswith(('src/', 'tests/', 'fixtures/', 'evidence/')):
            continue
        target = suite_dir / rel
        if target.is_file():
            source_refs.append({'relative_to_suite': rel, 'published_path': target.relative_to(root).as_posix(), 'bytes': target.stat().st_size, 'sha256': sha(target.read_bytes())})
    inferred = []
    for stem in quoted:
        if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]*', stem):
            target = suite_dir / 'src' / (stem + '.c')
            if target.is_file():
                rel = target.relative_to(root).as_posix()
                if rel not in {r['published_path'] for r in source_refs}:
                    inferred.append({'published_path': rel, 'origin': 'quoted-stem plus existing src/<stem>.c; review required'})
    target = '--target=riscv32' in low or '-march=rv32' in low
    host = 'enter-vsdevshell' in low or 'msvc' in low or 'cl.exe' in low
    calls_ps1 = bool(re.search(r'&[^\r\n]*\.ps1|run-tests\.ps1|verify-.*\.ps1', text, re.I))
    has_network = any(s in low for s in ['httpclient', 'invoke-webrequest', 'invoke-restmethod'])
    if has_network:
        category = 'download'
    elif target and host:
        category = 'host-tests-plus-rv32-compile'
    elif target:
        category = 'native-rv32-elf'
    elif host:
        category = 'host-tests'
    else:
        category = 'orchestrator-or-evidence'
    barriers = []
    for needle, label in [('enter-vsdevshell', 'MSVC-PowerShell-DevShell'), ('devshell.dll', 'MSVC-DevShell-module'), ('windows-x86_64', 'Windows-NDK-tool-path'), ('hermes-agent', 'absolute-user-Python'), ('cl.exe', 'MSVC-command-and-flags'), ('.exe', 'Windows-executable-suffix'), ('[bitconverter]', 'dotnet-binary-parser'), ('resolve-path', 'PowerShell-path-semantics'), ('convertfrom-json', 'PowerShell-JSON-semantics')]:
        if needle in low:
            barriers.append(label)
    flags = sorted({s for s in quoted if s.startswith(('--target=', '-march=', '-mabi=', '-mno-', '-f', '-O', '-std=', '/std:', '/W', '/WX', '/Od', '/TC', '/TP'))})
    checks = {'hash': 'get-filehash' in low or 'hashdata' in low, 'source_range': any(s in low for s in ['source_ranges', 'raw_sha256', 'raw range', 'original_body_sha256']), 'elf': bool(re.search(r'ET_REL|ELF32|nativeSections|nativeShCount', text, re.I)), 'semantic_relocations': bool(re.search(r'relocation|pcrel|rela', text, re.I)), 'source_proof_seal': bool(re.search(r'final-audit\.json|source_seal', text, re.I)), 'python_validator': '.py' in low, 'host_executable': host, 'target_executed_claim': False}
    run_lines = lines(text, r'^\s*(?:\$\w+\s*=\s*)?&\s+\$\w*(?:Exe|Executable)\b')
    return {'path': name, 'suite_root': suite_dir.relative_to(root).as_posix(), 'bytes': len(raw), 'sha256': sha(raw), 'category': category, 'parameters': [{'type': t, 'name': n} for t, n in re.findall(r'\[(switch|string|int|uri)\]\s*\$(\w+)', params, re.I)], 'top_parameter_block': params.strip(), 'compiler_flags_literals': flags, 'compiler_invocation_lines': lines(text, r'&\s*\$\w*(?:Compiler|Clang|Cl)\b'), 'gates_to_preserve': checks, 'portability_barriers': barriers, 'calls_other_PowerShell': calls_ps1, 'source_and_fixture_path_literals': paths, 'local_existing_source_references': source_refs, 'inferred_source_stems': inferred, 'host_runtime_argument_lines': run_lines, 'python_invocation_lines': lines(text, r'&[^\r\n]*(?:Python|\.py\b)'), 'mapping_is_static_literal_inventory_not_a_PowerShell_AST': True, 'migrated': False}


def build(root, revision=BASELINE):
    head = git(root, 'rev-parse', revision)
    tracked = git(root, 'ls-tree', '-r', '--name-only', head).splitlines()
    scripts = sorted(p for p in tracked if p.lower().endswith('.ps1'))
    rows = [analyze(root, name) for name in scripts]
    pyrows = []
    for name in sorted(p for p in tracked if p.lower().endswith('.py')):
        raw = (root / name).read_bytes()
        text = raw.decode('utf-8-sig')
        pyrows.append({'path': name, 'bytes': len(raw), 'sha256': sha(raw), 'argparse': 'argparse' in text, 'readonly_check_option_literal': bool(re.search(r"['\"]--check['\"]", text)), 'hardcoded_windows_user_path': bool(re.search(r'[A-Za-z]:[/\\]Users[/\\]', text)), 'imports_or_invokes_PowerShell': bool(re.search(r"['\"](?:pwsh|powershell)(?:\.exe)?['\"]|PWSH\s*=", text, re.I)), 'network_code_candidate': bool(re.search(r'http\.client|urllib\.request|requests\.(get|post)|HttpClient', text)), 'target_execution_not_performed_by_inventory': True})
    bins = []
    for name in sorted(p for p in tracked if p.lower().endswith('.bin')):
        raw = (root / name).read_bytes()
        bins.append({'path': name, 'bytes': len(raw), 'sha256': sha(raw)})
    rootrow = next(r for r in rows if r['path'] == 'verify.ps1')
    validate = re.search(r'ValidateSet\((.*?)\)', rootrow['top_parameter_block'], re.S)
    suites = re.findall(r"'([^']+)'", validate.group(1)) if validate else []
    suite_rows = []
    bypath = {r['path']: r for r in rows}
    for suite in suites:
        path = f'experiments/tsl9-contract-model/verify-{suite}.ps1'
        row = bypath.get(path)
        suite_rows.append({'suite': suite, 'PowerShell_entry': path, 'exists': row is not None, 'category': row['category'] if row else None, 'parameters': row['parameters'] if row else [], 'sources': row['local_existing_source_references'] if row else [], 'inferred_sources': row['inferred_source_stems'] if row else [], 'host_runtime_argument_lines': row['host_runtime_argument_lines'] if row else [], 'all_original_gates_must_be_preserved': True})
    inv = {'schema': 'TSL9-published-PowerShell-portability-inventory-v1', 'published_git_commit': head, 'tracked_PowerShell_count': len(rows), 'categories': dict(sorted(Counter(r['category'] for r in rows).items())), 'scripts': rows, 'published_Python_count': len(pyrows), 'Python_validator_candidates': pyrows, 'published_BIN_count': len(bins), 'published_BINs': bins, 'tracked_file_count': len(tracked), 'scope': 'published tracked scripts and owned artifacts only; worktree hashes are explicit, not inferred from commit', 'scripts_executed': False, 'vendor_requests': 0, 'target_execution': False, 'all_116_ported': False}
    mapping = {'schema': 'TSL9-portable-suite-migration-map-v1', 'published_git_commit': head, 'root_dispatch_default_suite': 'gate-integration', 'root_dispatch_Cpp_switch': 'C++17 instead of C11', 'root_ValidateSet_count': len(suite_rows), 'root_ValidateSet_suite_map': suite_rows, 'modern_host_orchestrators': [r for r in rows if r['path'].startswith('experiments/') and 'tsl9-contract-model/' not in r['path'] and r['category'] != 'native-rv32-elf'], 'portable_entry_requirements': ['Keep evidence/raw firmware hashes and range checks before compile.', 'Resolve dependency files relative to explicit published root/suite root, not cwd or private Windows paths.', 'Host tests use CC/CXX on Unix; MSVC on Windows can be entered without PowerShell.', 'RV32 compile/ELF validation is a distinct gate; host test success cannot replace it.', 'Preserve original executable argv: repo root vs Runtime/BOOT vs zero args vs explicit Firmware/ProofRoot.', 'Source/test literal mappings may be incomplete for dynamically assembled PowerShell paths; retain original line evidence and review before enabling a suite.', 'Version-specific firmware hashes must remain separate: legacy Runtime32639d7d and V4.1.60 Runtime0ee64183.'], 'all_suites_migrated': False}
    return {'inventory.json': inv, 'suite-map.json': mapping}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--published', type=Path, required=True)
    p.add_argument('--revision', default=BASELINE, help='fixed published inventory baseline; no network')
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    a = p.parse_args()
    result = build(a.published.resolve(), a.revision)
    for name, doc in result.items():
        raw = (json.dumps(doc, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
        out = HERE / name
        if a.check:
            if out.read_bytes() != raw:
                raise ValueError('inventory drift: ' + name)
        else:
            if (HERE / 'final-audit.json').exists():
                raise ValueError('sealed scope')
            if out.exists() and out.read_bytes() != raw:
                raise ValueError('refuse differing output: ' + name)
            if not out.exists():
                out.write_bytes(raw)
    doc = result['inventory.json']
    print(json.dumps({'passed': True, 'readonly': a.check, 'PowerShell': doc['tracked_PowerShell_count'], 'categories': doc['categories'], 'Python': doc['published_Python_count'], 'BINs': doc['published_BIN_count'], 'dispatch_suites': result['suite-map.json']['root_ValidateSet_count'], 'all_116_ported': False}))


if __name__ == '__main__':
    main()
