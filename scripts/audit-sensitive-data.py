#!/usr/bin/env python3
"""Offline bounded secret/privacy scan. Findings never include matched values."""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import subprocess
import zipfile

PATTERNS = {
    'provider_token': rb'(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{40,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,})(?![A-Za-z0-9_])',
    'aws_access_key': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'google_api_key': rb'\bAIza[0-9A-Za-z_-]{35}\b',
    'private_key_material': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\sA-Za-z0-9+/=]{64,}-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'jwt': rb'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}',
    'named_secret': rb'(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password|passwd|authorization)[\x22\x27]?\s*[:=]\s*[\x22\x27]([^\x22\x27\r\n]{6,256})[\x22\x27]',
    'device_uid': rb'\b[0-9A-Fa-f]{24}\b',
    'vehicle_vin': rb'\b[A-HJ-NPR-Z0-9]{17}\b',
    'device_mac': rb'\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b',
    'email_address': rb'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
}
RX = {k: re.compile(v) for k, v in PATTERNS.items()}
SENSITIVE_NAMES = {'.env', 'local.properties', 'key.properties', 'credentials.json', 'service-account.json'}
EXCLUDE = {'.git', '.gradle', '.idea', '.kotlin', '__pycache__', '.codex-remote-attachments', 'node_modules', 'build', 'tools', 'artifacts'}
MAX_MEMBER = 64 * 1024 * 1024
MAX_EXPANDED = 512 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def wx_entries(data):
    if len(data) < 18 or data[0] != 0xbe or data[13] != 0xed:
        raise ValueError('wxapkg header')
    _, index, body = struct.unpack_from('>III', data, 1)
    if len(data) != 14 + index + body:
        raise ValueError('wxapkg extent')
    count = struct.unpack_from('>I', data, 14)[0]
    if count > 10000:
        raise ValueError('wxapkg count')
    at = 18
    for _ in range(count):
        n = struct.unpack_from('>I', data, at)[0]; at += 4
        if n > 4096 or at + n + 8 > 14 + index:
            raise ValueError('wxapkg index')
        name = data[at:at+n].decode('utf-8'); at += n
        offset, length = struct.unpack_from('>II', data, at); at += 8
        if offset < 14 + index or length > MAX_MEMBER or offset + length > len(data):
            raise ValueError('wxapkg member extent')
        yield name, data[offset:offset+length]
    if at != 14 + index:
        raise ValueError('wxapkg index tail')


def scan_blob(name, data, findings, coverage, depth=0):
    coverage['scanned_payloads'] += 1; coverage['scanned_bytes'] += len(data)
    for kind, rx in RX.items():
        for m in rx.finditer(data):
            value = m.group(1) if kind == 'named_secret' else m.group()
            if kind == 'vehicle_vin' and (not any(48 <= c <= 57 for c in value) or len(set(value)) < 3):
                continue
            findings.append(dict(path=name, category=kind, byte_offset=m.start(),
                                 line=data.count(b'\n', 0, m.start()) + 1,
                                 value_length=len(value), value_omitted=True))
    if depth >= 2:
        return
    if name.lower().endswith(('.apk', '.zip', '.jar', '.mpp')):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                entries = [x for x in z.infolist() if not x.is_dir()]
                total = sum(x.file_size for x in entries)
                if len(entries) > 10000 or total > MAX_EXPANDED or any(x.file_size > MAX_MEMBER or x.flag_bits & 1 for x in entries):
                    raise ValueError('archive coverage limit or encrypted member')
                for entry in entries:
                    scan_blob(name + '!' + entry.filename, z.read(entry), findings, coverage, depth+1)
                coverage['archives_expanded'] += 1
        except (ValueError, zipfile.BadZipFile, RuntimeError, NotImplementedError):
            coverage['uninspected'].append(dict(path=name, reason='archive parser/coverage limit'))
    elif name.lower().endswith('.wxapkg'):
        try:
            for member, payload in wx_entries(data):
                scan_blob(name + '!' + member, payload, findings, coverage, depth+1)
            coverage['wxapkg_expanded'] += 1
        except (ValueError, struct.error, UnicodeDecodeError):
            coverage['uninspected'].append(dict(path=name, reason='wxapkg parser/coverage limit'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path)
    p.add_argument('--history', action='store_true', help='Scan each unique blob reachable from all local refs.')
    p.add_argument('--source-tree', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if bool(a.repo) == bool(a.source_tree) or a.output.exists() or (a.history and not a.repo):
        raise ValueError('Select one scan source and a new output')
    findings, files, excluded = [], {}, []
    coverage = dict(scanned_payloads=0, scanned_bytes=0, archives_expanded=0, wxapkg_expanded=0, uninspected=[])
    latest = set(); commit = None; identity = None
    if a.repo:
        root = a.repo.resolve()
        def git(*args):
            return subprocess.check_output(['git', '-C', str(root), *args])
        commit = git('rev-parse', 'HEAD').decode().strip()
        latest = {x.decode() for x in git('diff-tree', '--no-commit-id', '--name-only', '-r', '-z', 'HEAD').split(b'\0') if x}
        authors = git('show', '-s', '--format=%ae%n%ce', 'HEAD').decode().splitlines()
        identity = dict(email_metadata_present=bool(authors), non_noreply_email_present=any('@' in x and not x.endswith('noreply.github.com') for x in authors), values_omitted=True)
        rows = git('ls-tree', '-rz', '--full-tree', 'HEAD').split(b'\0')
        paths = []
        for row in rows:
            if not row: continue
            header, raw_name = row.split(b'\t', 1); mode, kind, oid = header.split()
            if kind != b'blob' or mode == b'120000':
                raise ValueError('Nonregular committed object')
            name = raw_name.decode(); path = root / name; data = path.read_bytes()
            actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest().encode()
            if actual != oid:
                raise ValueError('Committed/worktree bytes differ: ' + name)
            paths.append((name, path))
    else:
        root = a.source_tree.resolve(); paths = []
        for path in root.rglob('*'):
            if not path.is_file(): continue
            rel = path.relative_to(root); name = rel.as_posix()
            if set(rel.parts) & EXCLUDE:
                excluded.append(name); continue
            if path.is_symlink(): raise ValueError('Source symlink')
            paths.append((name, path))
    def record(name, data):
        path = Path(name); files[name] = dict(bytes=len(data), sha256=sha(data))
        if path.name in SENSITIVE_NAMES or path.suffix.lower() in {'.jks', '.keystore', '.p12', '.pfx', '.key'}:
            findings.append(dict(path=name, category='sensitive_filename', value_omitted=True))
        scan_blob(name, data, findings, coverage)
    reachable_commits = None
    if a.history:
        objects = []
        for line in git('rev-list', '--objects', '--all').splitlines():
            oid, _, path = line.partition(b' ')
            objects.append((oid, path.decode('utf-8')))
        batch = subprocess.Popen(['git', '-C', str(root), 'cat-file', '--batch'], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for oid, name in objects:
                batch.stdin.write(oid+b'\n'); batch.stdin.flush()
                header = batch.stdout.readline().split()
                if len(header) != 3 or header[0] != oid:
                    raise ValueError('Git object stream header')
                size = int(header[2]); data = batch.stdout.read(size)
                if len(data) != size or batch.stdout.read(1) != b'\n':
                    raise ValueError('Complete Git object stream')
                if header[1] == b'blob':
                    record('history/' + oid.decode() + '/' + name, data)
            batch.stdin.close()
            if batch.wait(timeout=30) != 0:
                raise ValueError('Git object stream exit')
        finally:
            if batch.poll() is None:
                batch.kill(); batch.wait()
        reachable_commits = int(git('rev-list', '--count', '--all'))
    else:
        for name, path in paths:
            record(name, path.read_bytes())
    result = dict(schema='TSL9-offline-sensitive-data-audit-v1', commit=commit, source=str(root),
                  files=files, reachable_history_scanned=a.history, reachable_commits=reachable_commits,
                  latest_commit_files=len(latest), latest_commit_findings=None if a.history else sum(x['path'].split('!',1)[0] in latest for x in findings),
                  findings=findings, categories=dict(Counter(x['category'] for x in findings)),
                  coverage=coverage, excluded_source_files=len(excluded), commit_identity=identity,
                  matched_values_retained=False, network=False, target_execution=False,
                  limitations=['Pattern scan cannot prove absence of every secret, especially encrypted/obfuscated or nonmatching data.',
                               'Certificates and client identifiers require context; no credentials are tested against any service.',
                               'History mode covers blobs reachable from local refs; unreachable/deleted remote objects are not verified.'])
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open('xb') as f: f.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps(dict(files=len(files),latest_commit_files=len(latest),findings=len(findings),categories=result['categories'],
                          coverage=coverage,commit_identity=identity,report=str(a.output)),ensure_ascii=False))


if __name__ == '__main__':
    main()
