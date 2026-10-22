"""Independent R55 ELF32 body/operand/relocation checker; never executes code."""
import hashlib
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cstr(data, p):
    return data[p:data.index(b"\0", p)].decode()


def parse(path):
    data = Path(path).read_bytes()
    h = struct.unpack_from("<16sHHIIIIIHHHHHH", data)
    assert h[0][:7] == b"\x7fELF\x01\x01\x01" and h[1] == 1 and h[2] == 243 and h[4] == 0
    sections = [struct.unpack_from("<10I", data, h[6] + i*h[11]) for i in range(h[12])]
    ns = sections[h[13]]
    names = [cstr(data, ns[4]+s[0]) for s in sections]
    tables, symbols, exports, undefined, writable = {}, {}, [], [], []
    for index, s in enumerate(sections):
        if s[2] & 3 == 3 and s[5]:
            writable.append(names[index])
        if s[1] != 2:
            continue
        strings, table = sections[s[6]], []
        for off in range(s[4], s[4]+s[5], 16):
            value = struct.unpack_from("<IIIBBH", data, off)
            name = cstr(data, strings[4]+value[0])
            q = {"name": name, "value": value[1], "bytes": value[2],
                 "type": value[3]&15, "bind": value[3]>>4,
                 "visibility": value[4]&3, "section": value[5]}
            table.append(q)
            if name:
                symbols[name] = q
                if not q["section"]:
                    undefined.append(name)
                elif q["bind"] == 1:
                    exports.append(name)
        tables[index] = table
    relocs = []
    for s in sections:
        if s[1] not in (4, 9):
            continue
        assert s[1] == 4 and s[9] == 12
        for off in range(s[4], s[4]+s[5], 12):
            pos, info, addend = struct.unpack_from("<IIi", data, off)
            relocs.append({"section": s[7], "offset": pos, "type": info&255,
                           "symbol": tables[s[6]][info>>8], "addend": addend})
    return {"data": data, "sections": sections, "names": names, "symbols": symbols,
            "exports": exports, "undefined": undefined, "writable": writable, "relocs": relocs}


def body(e, name):
    q = e["symbols"][name]
    section = e["sections"][q["section"]]
    return e["data"][section[4]+q["value"]:section[4]+q["value"]+q["bytes"]]


def own_relocs(e, name):
    q = e["symbols"][name]
    return [dict(r, relative_offset=r["offset"]-q["value"]) for r in e["relocs"]
            if r["section"] == q["section"] and q["value"] <= r["offset"] < q["value"]+q["bytes"]]


def resolve(e, r, want, addend=0):
    actual, desired = r["symbol"], e["symbols"][want]
    if not desired["section"]:
        assert actual["name"] == want and not actual["section"] and r["addend"] == addend
        return False
    assert actual["section"] == desired["section"]
    assert actual["value"]+r["addend"] == desired["value"]+addend
    if actual["name"] == want:
        assert r["addend"] == addend
    return True


def retained_ops():
    ops = {}
    for name in ("candidate-evidence.json", "helpers-extended-evidence.json"):
        for r in json.loads((HERE/name).read_text())["ranges"]:
            for op in r["body"]:
                if op["addr"] in ops:
                    assert ops[op["addr"]] == op
                ops[op["addr"]] = op
    return ops


def check(e, red=False):
    # Parent specs provide linker names only after independent reconciliation of
    # every instruction/address/width and every original call/pair operand.
    specs = json.loads((HERE.parent/"native-specs.json").read_text())
    ops = retained_ops()
    results, pair_proofs, edge_proofs, mismatches = [], [], [], []
    for fn in specs["functions"]:
        name, start, length = fn["name"], fn["start"], fn["bytes"]
        original = b"".join(bytes.fromhex(ops[x]["bytes"]) for x in sorted(ops)
                            if start <= x < start+length)
        assert len(original) == length
        q, actual = e["symbols"][name], body(e, name)
        assert q["type"] == 2
        records = own_relocs(e, name)
        rel = {r["relative_offset"]: r for r in records}
        assert len(rel) == len(records)
        wanted, normalized = {}, []
        if red:
            assert actual == bytes.fromhex("8280") and not records
        else:
            assert len(actual) == length
            for p in fn["pairs"]:
                off, low = p["offset"], p["lo_offset"]
                hi, lo = rel[off], rel[low]
                assert hi["type"] == 23 and lo["type"] == p["lo_type"]
                assert lo["symbol"]["section"] == q["section"]
                assert lo["symbol"]["value"]+lo["addend"] == q["value"]+off
                defined = resolve(e, hi, p["symbol"], p["addend"])
                eh, oh = [struct.unpack_from("<I", x, off)[0] for x in (actual, original)]
                el, ol = [struct.unpack_from("<I", x, low)[0] for x in (actual, original)]
                mask = 0x1fff07f if p["lo_type"] == 25 else 0xfffff
                assert eh & 0xfff == oh & 0xfff and el & mask == ol & mask
                assert eh & 0xfffff000 == 0 and el & (0xffffffff ^ mask) == 0
                wanted[off], wanted[low] = 23, p["lo_type"]
                normalized.extend([(off, off+4), (low, low+4)])
                pair_proofs.append({"function": name, "hi_site": hex(start+off),
                                    "lo_site": hex(start+low), "original_target": hex(p["original_target"]),
                                    "symbol": p["symbol"], "addend": p["addend"],
                                    "lo_type": p["lo_type"], "own_AUIPC_anchor": True,
                                    "registers_opcode_and_zero_relocation_immediates": True,
                                    "defined_target": defined})
            for c in fn["calls"]:
                off, r = c["offset"], rel[c["offset"]]
                assert r["type"] == 17 and c["width"] == 4 and c["rd"] == 1
                defined = resolve(e, r, c["name"])
                emitted, old = [struct.unpack_from("<I", x, off)[0] for x in (actual, original)]
                assert emitted & 0xfff == old & 0xfff and emitted & 0xfffff000 == 0
                wanted[off] = 17
                normalized.append((off, off+4))
                edge_proofs.append({"function": name, "site": hex(start+off),
                                    "target": c["name"], "original_target": hex(c["target"]),
                                    "rd": 1, "width": 4, "type": 17, "defined_target": defined})
            assert {off: r["type"] for off, r in rel.items()} == wanted
        a, b = bytearray(actual), bytearray(original)
        for lo, hi in normalized:
            a[lo:hi], b[lo:hi] = bytes(hi-lo), bytes(hi-lo)
        match = a == b
        assert match != red
        if not match:
            mismatches.append(name)
        results.append({"symbol": name, "original_start": hex(start),
                        "original_end_exclusive": hex(start+length),
                        "emitted_bytes": len(actual), "expected_bytes": length,
                        "unrelocated_bytes_match": match,
                        "normalization_ranges": normalized,
                        "emitted_sha256": hashlib.sha256(actual).hexdigest(),
                        "normalized_sha256": hashlib.sha256(a).hexdigest(),
                        "relocations": len(records), "all_ROM_fresh_reads_and_stack_branches_unmasked": True})
    assert len(mismatches) == (7 if red else 0)
    if not red:
        assert len(pair_proofs) == 22 and len(edge_proofs) == 12
    return {"bodies": results, "PC_pair_proofs": pair_proofs,
            "direct_edge_proofs": edge_proofs, "body_mismatches": mismatches,
            "original_or_rebuilt_target_executed": False,
            "canonical_held_code_bytes_oracle": True, "data_contents_read": False}
