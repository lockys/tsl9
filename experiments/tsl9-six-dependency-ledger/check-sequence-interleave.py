"""Pin sequence loop instructions and its allowed conditional data window."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
windows = {
    (0x12020, 0x8a): '1225b6a684484e6c5a3fc6b38f57214729a7e3d6029095e66784c9bb31841e82',
    (0x1a638, 48): '234dd45cce8b151ef80ba9455735ac58f2757372e0fca8633569995e542330cf',
}
with image.open('rb') as stream:
    for (address, size), expected in windows.items():
        stream.seek(address - 0x8000)
        data = stream.read(size)
        if hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit('Original sequence window changed')
        if address == 0x1a638:
            patterns = [data[offset:offset + 6] for offset in range(0, 48, 6)]
            if len(set(patterns)) != 8:
                raise SystemExit('Conditional sequence patterns are not distinct')
marker = [v for v in range(256) if ((v + 1) & 255) > 1]
if marker != list(range(1, 255)) or ((255 + 1) & 255) != 0:
    raise SystemExit('Fresh state marker-branch arithmetic changed')
print('Sequence instruction and allowed data windows verified; target not executed.')
