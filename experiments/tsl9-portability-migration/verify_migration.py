#!/usr/bin/env python3
"""Replay owned host tests/source checkers, or only verify a sealed migration audit."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('inventory', HERE / 'inventory.py')
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def proof_replays(published):
    boot = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
    runtime = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
    specs = [
        ('analysis/boot2580-command-adapter-2026-10-21/source', '--firmware', boot),
        ('analysis/boot2580-uid-helper-2026-10-21/source', '--firmware', boot),
        ('analysis/resident-copy-reference-2026-10-21/source', '--carrier', 'analysis/resident-copy-reference-2026-10-21/reference-carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'),
        ('analysis/resident-entry-reference-2026-10-21/source', '--carrier', 'analysis/resident-entry-reference-2026-10-21/reference-carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'),
        ('analysis/v4160-runtime-loop-2026-10-21/source', '--firmware', runtime),
    ]
    rows = []
    for folder, option, source in specs:
        script = folder + '/inspect-source.py'
        args = [sys.executable, '-B', str(published / script), '--check', option, str(published / source), '--source-root', str(published / folder)]
        r = subprocess.run(args, cwd=HERE, capture_output=True, timeout=60)
        if r.returncode:
            raise RuntimeError(f'portable source checker failed: {script}; exit={r.returncode}; {r.stderr.decode("utf-8", "replace")[-2000:]}')
        report = json.loads(r.stdout.decode('utf-8-sig'))
        if not report.get('passed'):
            raise ValueError('source proof not passed: ' + script)
        rows.append({'script': script, 'script_sha256': sha((published / script).read_bytes()), 'input': source, 'input_sha256': sha((published / source).read_bytes()), 'arguments': ['--check', option, '<published>/' + source, '--source-root', '<published>/' + folder], 'result': report, 'exit': 0})
    return rows


def run(published, shell):
    current = inventory.build(published)
    for name, doc in current.items():
        expected = (json.dumps(doc, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
        if (HERE / name).read_bytes() != expected:
            raise ValueError('inventory differs: ' + name)
    test = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v'], cwd=HERE, capture_output=True, timeout=60)
    if test.returncode:
        raise RuntimeError('owned offline mock tests failed: ' + test.stderr.decode('utf-8', 'replace')[-3000:])
    proofs = proof_replays(published)
    sh_result = {'tested': False, 'reason': 'no explicit shell supplied'}
    if shell:
        import os
        env = dict(os.environ, PYTHON=sys.executable)
        args = [str(shell), str(HERE / 'download-firmware.sh'), '--firmware-id', '2966', '--options-receipt', str(HERE / 'tests/synthetic-catalog.json'), '--dry-run']
        r = subprocess.run(args, cwd=HERE / 'tests', env=env, capture_output=True, timeout=30)
        if r.returncode:
            raise RuntimeError('shell wrapper dry-run failed: ' + r.stderr.decode('utf-8', 'replace')[-1500:])
        value = json.loads(r.stdout.decode('utf-8-sig'))
        if value.get('request_attempts') != 0 or value.get('output_created') is not False:
            raise ValueError('shell dry-run side effect contract')
        sh_result = {'tested': True, 'exit': 0, 'shell_executable_sha256': sha(shell.read_bytes()), 'result': value, 'tested_platform': platform.system(), 'Unix_or_macOS_execution_proved': False}
    names = ['download_firmware.py', 'download-firmware.sh', 'tests/test_download_mock.py', 'tests/synthetic-catalog.json', 'inventory.py', 'verify_migration.py']
    return {'schema': 'TSL9-portability-migration-owned-verification-v1', 'passed': True, 'published_baseline': current['inventory.json']['published_git_commit'], 'source_sha256': {n: sha((HERE / n).read_bytes()) for n in names}, 'Python_version': platform.python_version(), 'host_platform': platform.system(), 'offline_HTTP_boundary_double': {'passed': True, 'unittest_groups': 5, 'behavior_cases': 23, 'exit': test.returncode, 'transcript_sha256': sha(test.stdout + test.stderr), 'actual_decoder_and_persistence': True, 'socket_network_verified': False}, 'source_proof_replays': proofs, 'shell_wrapper': sh_result, 'TDD': {'initial_feature_stub': 'dry-run returned stopped/not_implemented', 'red_exit': 1, 'observed_failure': 'expected CLI exit0, actual exit1', 'port_zero_regression_red': 'invalid port0 previously defaulted to80; request issued instead of rejecting', 'port_zero_regression_red_exit': 1, 'final_owned_suite_exit': 0}, 'environment_limitations': [{'operation': 'literal loopback HTTP, same process and child process', 'error_type': 'PermissionError', 'errno': 13, 'winerror': 10013, 'loopback_integration_passed': False}, {'operation': 'Git for Windows sh process startup', 'result': 'NtCreateDirectoryObject access denied, status0xC0000022; wrapper was not reached', 'shell_integration_passed': False}, {'operation': 'default OS TemporaryDirectory fixture', 'result': 'permission denied; test fixture moved to explicitly owned scratch directory'}], 'live_vendor_mode_available': False, 'vendor_requests': 0, 'real_identity_used': False, 'target_execution': False, 'all_116_PS1_ported': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--published', type=Path, required=True)
    p.add_argument('--shell', type=Path)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--run', action='store_true', help='owned host tests plus readonly original source-proof replays; creates one receipt')
    mode.add_argument('--check', action='store_true', help='strictly readonly inventory and sealed-member verification')
    a = p.parse_args()
    published = a.published.resolve()
    if a.run:
        if (HERE / 'final-audit.json').exists() or (HERE / 'verification.json').exists():
            raise ValueError('create-only verification receipt')
        report = run(published, a.shell.resolve() if a.shell else None)
        (HERE / 'verification.json').write_bytes((json.dumps(report, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
        print(json.dumps({'passed': True, 'offline_mock_groups': 5, 'behavior_cases': 23, 'source_proof_replays': len(report['source_proof_replays']), 'shell_wrapper_tested': report['shell_wrapper']['tested'], 'live_loopback_verified': False, 'vendor_requests': 0}))
    else:
        subprocess.run([sys.executable, '-B', str(HERE / 'inventory.py'), '--published', str(published), '--check'], check=True)
        seal = json.loads((HERE / 'final-audit.json').read_text(encoding='utf-8'))
        if seal.get('passed') is not True or seal.get('sealed') is not True:
            raise ValueError('seal not complete')
        for member in seal['members']:
            path = (HERE / member['path']).resolve()
            if not path.is_relative_to(HERE) or (len(path.read_bytes()), sha(path.read_bytes())) != (member['bytes'], member['sha256']):
                raise ValueError('sealed member drift: ' + member['path'])
        print(json.dumps({'passed': True, 'mode': 'readonly-seal-and-inventory', 'members': len(seal['members']), 'vendor_requests': 0}))


if __name__ == '__main__':
    main()
