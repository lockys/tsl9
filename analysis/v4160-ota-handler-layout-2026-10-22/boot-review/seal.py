"""Create-only closure for the bounded static BOOT review; no target execution."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
NAMES = ('check.py', 'check.sh', 'evidence.json', 'selected-results.json',
         'README.md', 'readme.zh-TW.md', 'readme.en.md', 'seal.py')

def main():
    output = HERE / 'seal.json'
    if output.exists():
        raise ValueError('Seal already exists; preserve immutable bytes')
    selected = json.loads((HERE / 'selected-results.json').read_text(encoding='utf-8'))
    meta, actual = selected['metadata'], selected['actual_files']
    assert meta['passed'] and meta['metadata_only'] and not meta['actual_BOOT_read']
    assert actual['passed'] and not actual['metadata_only']
    assert actual['actual_BOOT_read'] and actual['actual_Runtime_read']
    assert (actual['selected_body_bytes'], actual['selected_body_instructions'], actual['raw_operand_controls']) == (414, 144, 5)
    assert all(c['rejected'] for c in actual['controls'])
    assert actual['numeric']['extra_numeric_pages'] == 21
    for name in ('storage_free_proved', 'NV_metadata_ownership_proved', 'physical_Flash_capacity_proved',
                 'installed_BOOT_identity_proved', 'whole_image_CRC_or_signature_acceptance_proved',
                 'whole_OTA_compatibility_proved', 'new_BIN_generated', 'compiler_or_HOST_run',
                 'target_execution', 'ISA_emulation', 'network', 'hardware'):
        assert meta[name] is False and actual[name] is False, name
    assert (HERE/'README.md').read_bytes() == (HERE/'readme.zh-TW.md').read_bytes()
    members = {}
    for name in NAMES:
        raw = (HERE / name).read_bytes()
        assert b'\r' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n'), name
        raw.decode('utf-8')
        members[name] = hashlib.sha256(raw).hexdigest()
    data = dict(schema='ID2580-BOOT-bounded-static-review-seal-v1', members=members,
                generated_build_members=False, readiness_claim=False)
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(passed=True, members=len(members), seal_sha256=hashlib.sha256(output.read_bytes()).hexdigest())))

if __name__ == '__main__':
    main()
