"""One original-source -Oz diagnostic allowing A1 coalescing, no target execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import uuid
from elf32 import ELF, require
from verify_native import SOURCE_PINS, flags

HERE = Path(__file__).resolve().parent
ENTRY = "tsl9_rebuild_interrupt_registers_9a42"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def destination(raw):
    word = int.from_bytes(raw,"little")
    if len(raw) == 4:
        opcode = word & 127
        if opcode in (0x03,0x13,0x33,0x37):
            return ((word >> 7) & 31) or None
        if opcode in (0x23,0x63):
            return None
        if opcode == 0x73:
            require((word >> 7) & 31 == 0 and (word >> 12) & 7 in (2,3), "discard-oldvalue CSRRS/RC only")
            return None
    elif len(raw) == 2:
        quadrant, funct = word & 3, word >> 13
        if quadrant == 0 and funct == 2:
            return 8 + ((word >> 2) & 7)
        if quadrant == 0 and funct == 6:
            return None
        if quadrant == 1 and funct in (0,2,3):
            return ((word >> 7) & 31) or None
        if quadrant == 1 and funct == 4:
            return 8 + ((word >> 7) & 7)
        if quadrant == 1 and funct in (5,6,7):
            return None
        if quadrant == 2 and funct == 0:
            return ((word >> 7) & 31) or None
        if quadrant == 2 and funct == 4 and (word >> 2) & 31:
            return ((word >> 7) & 31) or None
        if word == 0x8082:
            return None
    raise ValueError("unknown instruction destination encoding: " + raw.hex())


def raw_facts(elf):
    require(not any(s["index"] == 0 and s["name"] for s in elf.symbols), "no native unresolved helper/libcall")
    require(not any(s["size"] and s["flags"] & 1 for s in elf.sections), "no writable native data")
    facts = {}
    for symbol in elf.symbols:
        if not symbol["index"] or symbol["info"] & 15 != 2 or not symbol["size"]:
            continue
        raw = elf.function_bytes(symbol)
        cursor, rows = 0, []
        while cursor < len(raw):
            width = 4 if raw[cursor] & 3 == 3 else 2
            require(cursor + width <= len(raw), "complete function instruction framing")
            code = raw[cursor:cursor + width]
            rd = destination(code)
            require(rd in (None,10,11,14,15), "only original A0/A1/A4/A5 encoded destinations")
            rows.append(dict(offset=cursor,bytes=code.hex(),encoded_rd=rd))
            cursor += width
        facts[symbol["name"]] = dict(bytes=len(raw),instructions=len(rows),code_sha256=hashlib.sha256(raw).hexdigest(),encoded_written_registers=sorted({r["encoded_rd"] for r in rows if r["encoded_rd"]}),A1_writes=sum(r["encoded_rd"] == 11 for r in rows),rows=rows)
    return facts


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=HERE.parents[2])
    p.add_argument("--tool-dir",type=Path,required=True)
    a = p.parse_args()
    source = a.project_root.resolve() / "experiments/tsl9-v4160-interrupt-registers/src"
    require({name:sha(source/name) for name in SOURCE_PINS} == SOURCE_PINS,"original frozen three-source pins")
    suffix = ".exe" if __import__("os").name == "nt" else ""
    tools = {name:a.tool_dir/(exe+suffix) for name,exe in (("clang","clang"),("linker","ld.lld"),("objdump","llvm-objdump"))}
    results = []
    for mode in ("c","cpp"):
        folder = HERE/"build"/("allow-a1-"+uuid.uuid4().hex+"-"+mode)
        folder.mkdir(parents=True)
        native_flags = [flag for flag in flags(mode) if flag != "-ffixed-x11"]
        commands = []
        def run(label,argv):
            proc = subprocess.run([str(v) for v in argv],capture_output=True,timeout=120)
            raw = proc.stdout+proc.stderr
            (folder/(label+".log")).write_bytes(raw)
            commands.append(dict(label=label,argv=[str(v) for v in argv],exit=proc.returncode,log_sha256=hashlib.sha256(raw).hexdigest()))
            return proc.returncode
        obj,ir,linked = folder/"interrupt_registers.o",folder/"interrupt_registers.ll",folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf"
        compiled = run("compile",[tools["clang"],*native_flags,"-c",source/"interrupt_registers.c","-o",obj]) == 0
        require(run("llvm-ir",[tools["clang"],*native_flags,"-S","-emit-llvm",source/"interrupt_registers.c","-o",ir]) == 0,"same-profile IR")
        functions = None
        if compiled:
            require(run("link",[tools["linker"],"--no-relax","--no-undefined","--entry="+ENTRY,"-Ttext=0x1000",obj,"-o",linked]) == 0,"no undefined component link")
            require(run("disassembly",[tools["objdump"],"--disassemble",linked]) == 0,"actual disassembly")
            functions = raw_facts(ELF(linked))
        helper_A1 = compiled and all(v["A1_writes"] == 0 for name,v in functions.items() if name != ENTRY)
        report = dict(schema="TSL9-IRQ-original-source-A1-coalescing-diagnostic-v1",mode=mode,native_compilation_succeeded=compiled,
                      helper_A1_preservation_raw_RD_passed=helper_A1, source_sha256=SOURCE_PINS,runner_sha256=sha(Path(__file__)),
                      source_flags_dependency_sha256=sha(HERE/"verify_native.py"),flags=native_flags,commands=commands,
                      tools={name:dict(path=str(path),sha256=sha(path)) for name,path in tools.items()},
                      LLVM_IR_sha256=sha(ir),object_sha256=sha(obj) if compiled else None,linked_ELF_sha256=sha(linked) if compiled else None,functions=functions,
                      candidate_accepted=False,full_native_normal_output_pattern_proved=False,original_ABI_proved=False,original_fixed_placement_proved=False,
                      target_execution=False,ISA_emulation=False,network=False,hardware=False)
        receipt = folder/"verification.json"
        receipt.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        results.append(dict(mode=mode,receipt=str(receipt),sha256=sha(receipt),native_compilation_succeeded=compiled,helper_A1_preservation_raw_RD_passed=helper_A1,
                            functions={name:{k:v for k,v in f.items() if k != "rows"} for name,f in functions.items()} if functions else None))
    require({name:sha(source/name) for name in SOURCE_PINS} == SOURCE_PINS,"parent source unchanged")
    print(json.dumps(dict(results=results)))


if __name__ == "__main__":
    main()
