"""Pure, bounded validation of one reported redaction row; no I/O."""
from dataclasses import dataclass
import hashlib
import json
import math

MAX_MANIFEST = 32 * 1024 * 1024
MAX_REDACTION = 8 * 1024 * 1024
MAX_BLOB = 2 * 1024 * 1024
MAX_ROWS = 200_000


class Invalid(ValueError):
    """Input does not satisfy the selected specification."""


@dataclass(frozen=True)
class Spec:
    path: str
    parent: str
    commit: str
    old_sha256: str
    new_sha256: str
    old_size: int
    new_size: int
    old_oid: str
    new_oid: str
    redaction_oid: str


PIN = Spec(
    'analysis/v4160-adc-caller-2026-10-22/abi-review/actual-c.json',
    'e3406c69dc76db553eec685f4b9fa2fafa344646',
    'f23f6bd2b943da416e3e595cefe407fe52554505',
    'c0f156e81338337267c642c8d251f493d5d392ef28671631347f29267591b508',
    '68dbc8865098b03e4f1789805fe8122f0c22a020c9342ff59b24349bcb4715e5',
    30389, 29967,
    'ace375f2f965fefbf5b6ff8f30a7fae06f59fd8c',
    '691ff77c4f77f333bbbc7dceacca0c16c3ad0625',
    '83f407daf0fdda34634817db40931b4590402e4a',
)


def require(condition, message):
    if not condition:
        raise Invalid(message)


def git_blob_oid(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def _float(value):
    number = float(value)
    require(math.isfinite(number), 'non-finite JSON number')
    return number


def _json(data, limit):
    require(type(data) is bytes and len(data) <= limit, 'invalid input size or type')
    try:
        text = data.decode('utf-8', errors='strict')
        return json.loads(text, object_pairs_hook=_pairs, parse_float=_float,
                          parse_constant=lambda _: (_ for _ in ()).throw(Invalid('non-finite JSON number')))
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise Invalid('invalid JSON or UTF-8') from exc


def _publication(data, path):
    doc = _json(data, MAX_MANIFEST)
    require(type(doc) is dict and type(doc.get('files')) is list, 'publication files must be an array')
    rows = doc['files']
    require(len(rows) <= MAX_ROWS, 'too many rows')
    seen = set()
    selected = None
    for row in rows:
        require(type(row) is dict and type(row.get('path')) is str, 'invalid row path')
        name = row['path']
        require(name not in seen, 'duplicate row')
        seen.add(name)
        require(type(row.get('bytes')) is int and row['bytes'] >= 0, 'invalid row bytes')
        digest = row.get('sha256')
        require(type(digest) is str and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest), 'invalid row sha256')
        if name == path:
            selected = row
    require(selected is not None, 'row missing')
    return selected


def validate_with_spec(old_manifest, new_manifest, redaction, old_blob, new_blob, parent_id, commit_id, spec):
    """Validate caller bytes against spec; custom specs are for synthetic tests only."""
    require(type(spec) is Spec, 'invalid spec')
    require(parent_id == spec.parent and commit_id == spec.commit, 'unexpected IDs')
    old = _publication(old_manifest, spec.path)
    new = _publication(new_manifest, spec.path)
    require((old['sha256'], old['bytes']) == (spec.old_sha256, spec.old_size), 'old row mismatch')
    require((new['sha256'], new['bytes']) == (spec.new_sha256, spec.old_size), 'new row mismatch')
    require(spec.old_size != spec.new_size, 'expected stale length')
    for blob, size, digest, oid in ((old_blob, spec.old_size, spec.old_sha256, spec.old_oid),
                                    (new_blob, spec.new_size, spec.new_sha256, spec.new_oid)):
        require(type(blob) is bytes and len(blob) <= MAX_BLOB, 'invalid blob size or type')
        try:
            blob.decode('utf-8', errors='strict')
        except UnicodeError as exc:
            raise Invalid('blob is not UTF-8') from exc
        require(len(blob) == size and hashlib.sha256(blob).hexdigest() == digest and git_blob_oid(blob) == oid, 'blob mismatch')
    doc = _json(redaction, MAX_REDACTION)
    require(git_blob_oid(redaction) == spec.redaction_oid, 'redaction oid mismatch')
    require(type(doc) is dict and doc.get('schema') == 'TSL9-public-path-redaction-v1', 'redaction schema mismatch')
    require(doc.get('original_HEAD') == spec.parent and doc.get('original_receipts_preserved_privately') is True and doc.get('Git_history_rewritten') is False, 'redaction metadata mismatch')
    files = doc.get('files')
    require(type(files) is dict and len(files) <= MAX_ROWS, 'invalid redaction files')
    row = files.get(spec.path)
    require(type(row) is dict, 'redaction row missing')
    require(row.get('original_sha256') == spec.old_sha256 and row.get('public_sha256') == spec.new_sha256, 'redaction digest mismatch')
    require(type(row.get('original_bytes')) is int and row['original_bytes'] == spec.old_size and type(row.get('public_bytes')) is int and row['public_bytes'] == spec.new_size, 'redaction size mismatch')
    require(all(row.get(k) is True for k in ('personal_path_or_label_changed', 'dependent_text_hash_pins_changed', 'native_editor_LF_representation')), 'redaction flags mismatch')
    require(row.get('status') == 'anonymized historical/public derivative; not the original receipt', 'redaction status mismatch')
    return True


def validate(old_manifest, new_manifest, redaction, old_blob, new_blob, parent_id, commit_id):
    """Use fixed historical pins without an accidental caller spec override."""
    return validate_with_spec(old_manifest, new_manifest, redaction, old_blob, new_blob, parent_id, commit_id, PIN)
