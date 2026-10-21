#!/usr/bin/env python3
"""Portable dry-run / synthetic loopback port. Intentionally has no live mode."""
from pathlib import Path
import argparse
import hashlib
import http.client
import ipaddress
import json
import re
import secrets
import uuid
from urllib.parse import urlencode, urlsplit

LIMIT = 262144
SYNTHETIC_UID = '00112233445566778899AABB'
MARKER = '接收OK'


class Stop(Exception):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def catalog_entry(path, firmware_id):
    raw = path.read_bytes()
    doc = json.loads(raw.decode('utf-8-sig'))
    rows = doc.get('options')
    if not isinstance(rows, list):
        raise Stop('catalog_invalid')
    matches = [r for r in rows if isinstance(r, dict) and type(r.get('FirmwareID')) is int and r['FirmwareID'] == firmware_id]
    if len(matches) != 1:
        raise Stop('firmware_id_not_unique_in_returned_catalog')
    labels = [s for s in matches[0].get('version_labels', []) if isinstance(s, str) and re.fullmatch(r'V[0-9]+\.[0-9]+\.[0-9]+', s)]
    return (labels[0] if len(labels) == 1 else None), digest(raw)


def mock_endpoint(value):
    try:
        url = urlsplit(value)
        ip = ipaddress.ip_address(url.hostname or '')
        port = url.port if url.port is not None else 80
        if url.scheme != 'http' or not ip.is_loopback or url.username is not None or url.password is not None or url.query or url.fragment or not 1 <= port <= 65535:
            raise ValueError()
        return ip.compressed, port, url.path or '/'
    except (ValueError, TypeError):
        raise Stop('invalid_mock_uri') from None


def decode_response(raw):
    if len(raw) > LIMIT:
        raise Stop('response_too_large')
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        raise Stop('invalid_response_utf8') from None
    if text.count(MARKER) != 1 or not text.endswith(MARKER):
        raise Stop('invalid_terminal_marker')
    text = text[:-len(MARKER)]
    if text.endswith('\r\n'):
        text = text[:-2]
    rows = text.split('\r\n')
    if not 1 <= len(rows) <= 96:
        raise Stop('invalid_hex_page_count')
    if any(re.fullmatch(r'[0-9a-fA-F]{2048}', row) is None for row in rows):
        raise Stop('invalid_hex_page')
    encoded = b''.join(bytes.fromhex(row) for row in rows)
    decoded = bytes(value ^ 0xB7 for value in encoded)
    return encoded, decoded, ('\r\n'.join(rows) + '\r\n').encode('utf-8'), len(rows)


def persist(root, firmware_id, label, raw, encoded, decoded, normalized, pages, catalog_sha, endpoint):
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    folder = root / f'ID-{firmware_id}-{uuid.uuid4().hex}'
    folder.mkdir(exist_ok=False)
    basename = f'ID-{firmware_id}' + (f'-{label}' if label else '')
    outputs = {'http-response.txt': raw, 'download.hex': normalized, 'server-encoded.dat': encoded, basename + '-decoded.bin': decoded}
    files = {}
    for name, content in sorted(outputs.items()):
        with (folder / name).open('xb') as stream:
            stream.write(content)
        back = (folder / name).read_bytes()
        if back != content:
            raise Stop('local_readback_failed')
        files[name] = {'bytes': len(back), 'sha256': digest(back)}
    receipt = {'schema': 'TSL-portable-mock-download-v1', 'status': 'mock_downloaded_and_verified', 'FirmwareID': firmware_id, 'server_catalog_version_label': label, 'catalog_sha256': catalog_sha, 'endpoint': endpoint, 'action': 'GetFirmware', 'client_ver': 30, 'http_status': 200, 'request_attempts': 1, 'retries': 0, 'redirects_followed': 0, 'mock': True, 'uid_stored': False, 'pages': pages, 'page_bytes': 1024, 'decoding': 'hex pairs then byte XOR 0xB7; first-stage candidate only', 'files': files, 'firmware_executed': False, 'hardware_applicability_proved': False, 'target_ready': False, 'ota_verified': False, 'vendor_network_requests': 0}
    with (folder / 'receipt.json').open('xb') as stream:
        stream.write((json.dumps(receipt, indent=2) + '\n').encode('utf-8'))
    return {'status': receipt['status'], 'FirmwareID': firmware_id, 'directory': str(folder), 'bin': str(folder / (basename + '-decoded.bin')), 'bytes': len(decoded), 'sha256': digest(decoded), 'mock': True, 'target_ready': False, 'ota_verified': False, 'request_attempts': 1, 'vendor_network_requests': 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--firmware-id', type=int, required=True)
    parser.add_argument('--options-receipt', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, default=Path('firmware-downloads/mock'))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--mock-uri', help='HTTP literal loopback IP only; fixed synthetic identity')
    args = parser.parse_args(argv)
    attempts = 0
    connection = None
    status = None
    stage = 'catalog'
    try:
        if not 1 <= args.firmware_id <= 2147483647:
            raise Stop('invalid_firmware_id')
        label, catalog_sha = catalog_entry(args.options_receipt, args.firmware_id)
        if args.dry_run:
            report = {'schema': 'TSL-portable-download-dry-run-v1', 'status': 'dry_run', 'FirmwareID': args.firmware_id, 'catalog_sha256': catalog_sha, 'server_catalog_version_label': label, 'request_attempts': 0, 'vendor_network_requests': 0, 'output_created': False, 'live_mode_available': False, 'target_ready': False, 'ota_verified': False}
        else:
            stage = 'mock_endpoint'
            host, port, path = mock_endpoint(args.mock_uri)
            stage = 'request'
            connection = http.client.HTTPConnection(host, port, timeout=30)
            query = urlencode({'Temp': secrets.randbelow(9999) + 1})
            fields = urlencode({'action': 'GetFirmware', 'f_UID': SYNTHETIC_UID, 'f_FirmwareID': str(args.firmware_id), 'ver': '30'}).encode('ascii')
            attempts = 1
            # HTTPConnection follows no redirects, uses no proxy and performs no retry.
            connection.request('POST', path + '?' + query, fields, {'Content-Type': 'application/x-www-form-urlencoded'})
            response = connection.getresponse()
            status = response.status
            if status != 200:
                raise Stop(f'http_status_{status}')
            stage = 'response'
            size = response.getheader('Content-Length')
            if size is not None and (not size.isdecimal() or int(size) > LIMIT):
                raise Stop('response_too_large_or_invalid_length')
            raw = response.read(LIMIT + 1)
            stage = 'decode'
            encoded, decoded, normalized, pages = decode_response(raw)
            stage = 'save'
            report = persist(args.output_root, args.firmware_id, label, raw, encoded, decoded, normalized, pages, catalog_sha, args.mock_uri)
        print(json.dumps(report, separators=(',', ':')))
        return 0
    except Exception as exc:
        # Never stringify arbitrary replies, OS errors, request fields or identities.
        reason = str(exc) if isinstance(exc, Stop) else 'local_or_transport_error'
        print(json.dumps({'status': 'stopped', 'stage': stage, 'reason': reason, 'http_status': status, 'request_attempts': attempts, 'retries': 0, 'vendor_network_requests': 0}, separators=(',', ':')))
        return 1
    finally:
        if connection is not None:
            connection.close()


if __name__ == '__main__':
    raise SystemExit(main())
