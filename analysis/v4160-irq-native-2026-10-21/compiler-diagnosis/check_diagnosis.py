"""Static spill/SSA annotations and read-only diagnostic closure; no ISA execution."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from diagnose_stack import SOURCE_PINS, ENTRY, HELPERS, function_rows, load_parser, require

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def destination(raw):
    x = int.from_bytes(raw,"little")
    if len(raw) == 4:
        op = x & 127
        if op in (3,0x13,0x17,0x33,0x37,0x67):
            return ((x >> 7) & 31) or None
        if op in (0x23,0x63):
            return None
        if op == 0x73 and ((x >> 7) & 31) == 0:
            return None
    elif len(raw) == 2:
        q,f = x&3,x>>13
        if q == 0 and f == 2:
            return 8+((x>>2)&7)
        if q == 0 and f == 6:
            return None
        if q == 1 and f in (0,2,3):
            return ((x>>7)&31) or None
        if q == 1 and f == 4:
            return 8+((x>>7)&7)
        if q == 1 and f in (5,6,7):
            return None
        if q == 2 and f in (0,2):
            return ((x>>7)&31) or None
        if q == 2 and f == 6:
            return None
        if q == 2 and f == 4:
            if (x>>2)&31:
                return ((x>>7)&31) or None
            return 1 if x&0x1000 else None
    raise ValueError("unknown diagnostic raw destination: "+raw.hex())


def function_ir(text,name):
    m = re.search(r"^define\b[^\n]*@"+name+r"\([^\n]*\).*?\n\}",text,re.M|re.S)
    require(m is not None,"actual helper IR")
    return m.group()


def coverage_controls(text,elf):
    variants = {}
    for name in (ENTRY,HELPERS[0],"OUTLINED_FUNCTION_0"):
        marker = re.search(r"^([0-9a-f]+) <"+name+r">:\s*$",text,re.M)
        head,tail = text[:marker.end()],text[marker.end():]
        lines = tail.splitlines(keepends=True)
        indexes = []
        for index,line in enumerate(lines):
            if indexes and not line.strip():
                break
            if re.match(r"\s*[0-9a-f]+:",line):
                indexes.append(index)
        require(len(indexes)>3,"actual function transcript control source")
        middle = indexes[len(indexes)//2]
        variants["missing_middle_"+name] = head+"".join(line for i,line in enumerate(lines) if i != middle)
        if name == ENTRY:
            changed = list(lines)
            changed[indexes[1]] = re.sub(r"(:\s*)[0-9a-f]{2}",r"\g<1>00",changed[indexes[1]],count=1)
            variants["changed_raw_byte"] = head+"".join(changed)
        if name == HELPERS[0]:
            variants["truncated_last"] = head+"".join(line for i,line in enumerate(lines) if i != indexes[-1])
        if name == "OUTLINED_FUNCTION_0":
            changed = list(lines)
            changed.insert(middle,"    UNPARSED-INSTRUCTION\n")
            variants["unparsed_outline"] = head+"".join(changed)
    reports = []
    for name,changed in variants.items():
        require(changed != text,"actual changed coverage transcript")
        try:
            function_rows(changed,elf)
        except ValueError as error:
            reports.append(dict(case=name,rejected=True,reason=str(error)))
        else:
            raise ValueError("changed transcript admitted: "+name)
    return reports


def annotations(report,folder):
    ELF = load_parser()
    linked = folder/"STACK-DIAGNOSTIC-NOT-ACCEPTED.elf"
    require(sha(linked) == report["linked_ELF_sha256"],"actual diagnostic ELF pin")
    elf = ELF(linked)
    disassembly = (folder/"disassembly.log").read_text(encoding="utf-8")
    facts = function_rows(disassembly,elf)
    require(facts == report["functions"],"actual entire six-function ELF/disassembly replay")
    require(set(facts) == {ENTRY,*HELPERS,"OUTLINED_FUNCTION_0"},"actual unexpected local outlined implementation")
    registers = {"sp":2,"t0":5,"a0":10,"a1":11,"a4":14,"a5":15}
    raw_facts = {}
    for name,details in facts.items():
        written = []
        for row in details["rows"]:
            rd = destination(bytes.fromhex(row["bytes"]))
            nonwrite = row["mnemonic"] in ("sw","sb","beqz","bnez","j","jr","ret","csrc","csrs")
            displayed = None if nonwrite else registers.get(row["operands"].split(",")[0])
            require(rd == displayed,"independent encoded RD equals displayed diagnostic destination")
            if rd is not None:
                written.append(rd)
        raw_facts[name] = dict(written_registers=sorted(set(written)),T0_writes=written.count(5),SP_writes=written.count(2),A1_writes=written.count(11))
    outline = facts["OUTLINED_FUNCTION_0"]["rows"]
    require([(r["mnemonic"],r["operands"]) for r in outline] == [("mv","a4, a0"),("not","a0, a0"),("and","a0, a0, a5"),("sw","a5, 0xc(sp)"),("or","a5, a5, a4"),("mv","a4, a0"),("jr","t0")],"exact outlined before/OR/AND_NOT/spill pattern")
    ir = (folder/"interrupt_registers.ll").read_text(encoding="utf-8")
    require('"frame-pointer"' not in ir and not re.search(r"\balloca\b",ir),"no explicit frame-pointer attribute or IR stack allocation")
    helper_annotations = {}
    for name in HELPERS:
        rows = facts[name]["rows"]
        require(len(rows) == 21 and rows[0]["operands"] == "sp, sp, -0x10" and rows[-2]["operands"] == "sp, sp, 0x10","actual16byte helper frame")
        require([(rows[i]["mnemonic"],rows[i]["operands"]) for i in (7,8,13,14,16,17,18)] == [("sw","a5, 0x4(sp)"),("sw","a4, 0x8(sp)"),("lw","a0, 0x4(sp)"),("lw","a5, 0xc(sp)"),("li","a1, 0x0"),("lw","a4, 0xc(sp)"),("lw","a0, 0x8(sp)")],"exact OR/select/before spill-reload sites")
        require(rows[3]["mnemonic"] == "auipc" and rows[4]["mnemonic"] == "jalr" and "<OUTLINED_FUNCTION_0>" in rows[4]["operands"],"actual reserved-T0 outlined call")
        require([r["mnemonic"] for r in facts[name]["A1_operand_rows"]] == ["beqz","beqz","li"],"A1 directly tested, only disabled-zero assignment; no copy/spill/restore")
        body = function_ir(ir,name)
        loaded = re.search(r"(%\w+) = load volatile i32",body).group(1)
        OR = re.search(r"(%\w+) = or i32 "+re.escape(loaded)+r", %0",body).group(1)
        AND = re.search(r"(%\w+) = and i32 "+re.escape(loaded)+r", %\w+",body).group(1)
        selected = re.search(r"(%\w+) = select i1 %\w+, i32 "+re.escape(AND)+r", i32 "+re.escape(OR),body).group(1)
        require(body.index("store volatile i32 "+selected) < body.index("  br i1") and "ret i32 "+selected in body,"both expressions/select store before output branch, independent selected return lifetime")
        helper_annotations[name] = dict(frame_bytes=16,IR_fresh_before=loaded,IR_OR=OR,IR_AND_NOT=AND,IR_selected_return=selected,
                                       stack_slots={"4":dict(value="OR(before,mask)",store=rows[7]["address"],reload_enabled_A0=rows[13]["address"]),
                                                    "8":dict(value="enabled ? OR : AND_NOT; independently returned",store=rows[8]["address"],reload_return_A0=rows[18]["address"]),
                                                    "12":dict(value="fresh before",store_in_outline=outline[3]["address"],reload_enabled_A5=rows[14]["address"],reload_disabled_A4=rows[17]["address"])},
                                       A1_snapshot_or_restore=False,A1_false_zero_write=rows[16]["address"],encoded_T0_writes=raw_facts[name]["T0_writes"])
    main = facts[ENTRY]["rows"]
    require(main[0]["operands"] == "sp, sp, -0x10" and main[-2]["operands"] == "sp, sp, 0x10","actual16byte initializer frame")
    main_expected = {"0x8(sp)":("0x2020","a0, a0, 0x6",0x02020006),"0xc(sp)":("0x1","a0, a0, 0x1d",0x101d)}
    cached = []
    for operand,(upper,low,value) in main_expected.items():
        stores = [i for i,r in enumerate(main) if r["mnemonic"] == "sw" and r["operands"] == "a0, "+operand]
        reloads = [r for r in main if r["mnemonic"] == "lw" and r["operands"] == "a0, "+operand]
        require(len(stores) == len(reloads) == 1,"one constant cache spill/reload")
        index = stores[0]
        require((main[index-2]["mnemonic"],main[index-2]["operands"]) == ("lui","a0, "+upper) and (main[index-1]["mnemonic"],main[index-1]["operands"]) == ("addi",low),"actual repeated literal materialization immediately before spill")
        cached.append(dict(stack_operand=operand,value=value,store=main[index]["address"],reload=reloads[0]["address"]))
    return dict(mode=report["mode"],helper_spill_lifetimes=helper_annotations,initializer_constant_caches=cached,
                raw_destinations=raw_facts,all_six_function_raw_byte_coverage=True,all_functions_no_IR_alloca=True,
                coverage_transcript_controls=coverage_controls(disassembly,elf),
                explicit_frame_pointer_attribute=False,A1_spill_or_restore_observed=False,
                root_cause_confirmed_scope="Actual backend stack spills of helper OR/select/before values and initializer reused constants; no claim of complete allocator internals.",
                accepted_native_candidate=False,no_stack_gate_passed=False,no_hidden_calls_gate_passed=False,no_extra_clobbers_gate_passed=False,
                target_execution=False,ISA_emulation=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=HERE.parents[2])
    p.add_argument("--require-local-builds",action="store_true")
    p.add_argument("--generate-analysis",action="store_true",help="Print analysis from existing local selected artifacts, without writing")
    a = p.parse_args()
    root = a.project_root.resolve()
    for name,pin in SOURCE_PINS.items():
        require(sha(root/"experiments/tsl9-v4160-interrupt-registers/src"/name) == pin,"frozen original source unchanged")
    index = json.loads((HERE/"results.json").read_text(encoding="utf-8"))
    help_metadata = json.loads((HERE/"clang-help-hidden.json").read_text(encoding="utf-8"))
    require(help_metadata["exit"] == 0 and any("--enable-machine-outliner=<value>" in line for line in help_metadata["matched_lines"]) and any("=never" in line and "Disable all outlining" in line for line in help_metadata["matched_lines"]) and not help_metadata["profile_compiled"],"actual local hidden-help enum only, no new compilation")
    if (HERE/"clang-help-hidden.log").exists():
        require(sha(HERE/"clang-help-hidden.log") == help_metadata["raw_help_sha256"],"actual local raw-help pin")
    if not a.generate_analysis:
        seal = json.loads((HERE/"final-audit.json").read_text(encoding="utf-8"))
        for name,pin in seal["members"].items():
            require(sha(HERE/name) == pin,"sealed member unchanged: "+name)
    checks,unavailable = [],[]
    for item in index["results"]:
        require(sha(HERE/item["metadata"]) == item["sha256"],"exact selected receipt bytes")
        report = json.loads((HERE/item["metadata"]).read_text(encoding="utf-8"))
        require(not report["accepted_native_candidate"] and not report["goal_no_stack_gate_passed"],"diagnostic never promoted to accepted firmware")
        folder = HERE/item["artifact_dir"]
        if not folder.is_dir():
            unavailable.append(item["artifact_dir"])
            continue
        require(sha(folder/"verification.json") == item["sha256"],"historical original receipt pin")
        for name,key in (("interrupt_registers.o","object_sha256"),("interrupt_registers.ll","LLVM_IR_sha256"),("interrupt_registers.s","assembly_sha256")):
            require(sha(folder/name) == report[key],"actual diagnostic artifact pin")
        for command in report["commands"]:
            require(sha(folder/(command["label"]+".log")) == command["log_sha256"] and command["exit"] == 0,"actual command log pin")
        checks.append(annotations(report,folder))
    require(not a.require_local_builds or not unavailable,"required local diagnostic archives missing")
    if a.generate_analysis:
        print(json.dumps(dict(results=checks),indent=2))
    else:
        expected = json.loads((HERE/"analysis.json").read_text(encoding="utf-8"))
        if not unavailable:
            require(expected == dict(results=checks),"exact static spill/SSA annotations replay")
        print(json.dumps(dict(passed=True,seal_sha256=sha(HERE/"final-audit.json"),metadata_receipts=len(index["results"]),local_archives_replayed=len(checks),unavailable_archives=unavailable,
                              accepted_native_candidate=False,no_stack_gate_passed=False,no_hidden_calls_gate_passed=False,no_extra_clobbers_gate_passed=False,fresh_compilation=False,target_execution=False,ISA_emulation=False)))


if __name__ == "__main__":
    main()
