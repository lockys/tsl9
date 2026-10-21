"""One rejected-goal stack diagnostic: remove only -ffixed-x2, never execute RV32."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import uuid

HERE = Path(__file__).resolve().parent
SOURCE_PINS = {"interrupt_registers.c": "d3000829bd171e12d7fd6fe9ba5532c76635dce730d64628b3044d06b3724321", "interrupt_registers.h": "da57cec48aa144786cd9a64c8d20aadd2bb02d9e91d43408eac6441f7ba3ae59", "irq_io.h": "2ced66889c82da11b595b9dab734c8af4fdd4bb365390a534ec3611f0d5398f7"}
PARSER_SHA = "00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141"
ENTRY = "tsl9_rebuild_interrupt_registers_9a42"
HELPERS = ["tsl9_rebuild_rcc_registers_"+s for s in ("19124","19142","19160","1917e")]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_parser():
    path = HERE / "elf32.py"
    require(sha(path) == PARSER_SHA,"exact tiny local ELF parser")
    spec = importlib.util.spec_from_file_location("diagnostic_elf",path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.ELF


def function_rows(disassembly,elf):
    results = {}
    functions = [s for s in elf.symbols if s["index"] and s["info"] & 15 == 2 and s["size"]]
    require({ENTRY,*HELPERS}.issubset({s["name"] for s in functions}),"all five requested functions present; record unexpected compiler implementation")
    for symbol in functions:
        name = symbol["name"]
        code = elf.function_bytes(symbol)
        marker = re.search(r"^([0-9a-f]+) <"+name+r">:\s*$",disassembly,re.M)
        require(marker is not None and int(marker.group(1),16) == symbol["value"],"ELF-bound actual function start")
        cursor, rows = 0, []
        for line in disassembly[marker.end():].lstrip("\r\n").splitlines():
            if not line.strip():
                break
            m = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*",line)
            require(m is not None,"no ignored interior or unparsed disassembly line")
            address, raw = int(m.group(1),16),bytes.fromhex(m.group(2))
            require(address == symbol["value"]+cursor and raw == code[cursor:cursor+len(raw)],"full contiguous raw ELF bytes")
            require(len(raw) in (2,4) and len(raw) == (4 if raw[0]&3 == 3 else 2),"whole instruction framing")
            rows.append(dict(address=address,offset=cursor,bytes=raw.hex(),mnemonic=m.group(3),operands=m.group(4)))
            cursor += len(raw)
        require(cursor == len(code),"complete function extent coverage")
        stack = [row for row in rows if re.search(r"\bsp\b",row["operands"])]
        a1 = [row for row in rows if re.search(r"\ba1\b",row["operands"])]
        calls = [row for row in rows if row["mnemonic"] in ("call","jal","jalr","auipc")]
        results[name] = dict(bytes=len(code),instruction_rows=len(rows),code_sha256=hashlib.sha256(code).hexdigest(),rows=rows,SP_operand_rows=stack,A1_operand_rows=a1,possible_call_setup_rows=calls)
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=HERE.parents[2])
    p.add_argument("--tool-dir",type=Path,required=True)
    p.add_argument("--language",choices=("c","cpp","both"),default="both")
    a = p.parse_args()
    root = a.project_root.resolve()
    source = root/"experiments/tsl9-v4160-interrupt-registers/src"
    require({n:sha(source/n) for n in SOURCE_PINS} == SOURCE_PINS,"frozen original source")
    suffix = ".exe" if os.name == "nt" else ""
    tools = {key:a.tool_dir/(name+suffix) for key,name in (("clang","clang"),("linker","ld.lld"),("objdump","llvm-objdump"))}
    tool_pins = {key:sha(path) for key,path in tools.items()}
    ELF = load_parser()
    results = []
    for mode in (("c","cpp") if a.language == "both" else (a.language,)):
        folder = HERE/"build"/("allow-sp-"+uuid.uuid4().hex+"-"+mode)
        folder.mkdir(parents=True)
        # Only x2 differs from the frozen rejected primary native profile.
        flags = ["--target=riscv32-unknown-elf","-march=rv32imac_zicsr","-mabi=ilp32","-Oz","-ffreestanding","-fno-builtin","-fno-stack-protector","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-mno-relax","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror",*["-ffixed-x"+str(reg) for reg in range(1,32) if reg not in {2,10,14,15}],"-x","c" if mode == "c" else "c++","-std=c11" if mode == "c" else "-std=c++17"]
        commands = []
        def run(label,argv):
            proc = subprocess.run([str(v) for v in argv],capture_output=True,timeout=120)
            raw = proc.stdout+proc.stderr
            (folder/(label+".log")).write_bytes(raw)
            require(proc.returncode == 0,"diagnostic "+label+" failed; retain actual log")
            commands.append(dict(label=label,argv=[str(v) for v in argv],exit=proc.returncode,log_sha256=hashlib.sha256(raw).hexdigest()))
            return raw.decode("utf-8",errors="replace")
        obj,ir,assembly,linked = folder/"interrupt_registers.o",folder/"interrupt_registers.ll",folder/"interrupt_registers.s",folder/"STACK-DIAGNOSTIC-NOT-ACCEPTED.elf"
        run("compile",[tools["clang"],*flags,"-c",source/"interrupt_registers.c","-o",obj])
        run("llvm-ir",[tools["clang"],*flags,"-S","-emit-llvm",source/"interrupt_registers.c","-o",ir])
        run("assembly",[tools["clang"],*flags,"-S",source/"interrupt_registers.c","-o",assembly])
        run("link",[tools["linker"],"--no-relax","--no-undefined","--entry="+ENTRY,"-Ttext=0x1000",obj,"-o",linked])
        disassembly = run("disassembly",[tools["objdump"],"--disassemble",linked])
        elf = ELF(linked)
        require(not any(s["index"] == 0 and s["name"] for s in elf.symbols),"no unresolved helper/libcall")
        require(not any(s["size"] and s["flags"]&1 for s in elf.sections),"no writable ELF allocations")
        facts = function_rows(disassembly,elf)
        require(all(facts[name]["SP_operand_rows"] for name in [ENTRY,*HELPERS]),"actual SP usage in all five requested functions explains frozen reserved-SP rejection")
        text = ir.read_text(encoding="utf-8")
        report = dict(schema="TSL9-IRQ-SP-only-compiler-diagnosis-v1",mode=mode,diagnostic_compilation_succeeded=True,
                      accepted_native_candidate=False,goal_no_stack_gate_passed=False,flags=flags,only_removed_reservation="-ffixed-x2",
                      source_sha256=SOURCE_PINS,runner_sha256=sha(Path(__file__)),ELF_parser_sha256=PARSER_SHA,
                      tools={key:dict(path=str(path),sha256=tool_pins[key]) for key,path in tools.items()},commands=commands,
                      object_sha256=sha(obj),LLVM_IR_sha256=sha(ir),assembly_sha256=sha(assembly),linked_ELF_sha256=sha(linked),functions=facts,
                      explicit_frame_pointer_attribute_in_IR='"frame-pointer"' in text,no_hidden_undefined_helpers=True,
                      unexpected_compiler_functions=sorted(set(facts)-{ENTRY,*HELPERS}),
                      no_hidden_calls_gate_passed=False,no_extra_clobbers_gate_passed=False,
                      original_ABI_proved=False,original_fixed_placement_proved=False,firmware_BIN_produced=False,
                      RV32_executed=False,ISA_emulation=False,network=False,hardware=False,OTA_ready=False)
        require({n:sha(source/n) for n in SOURCE_PINS} == SOURCE_PINS and {key:sha(path) for key,path in tools.items()} == tool_pins,"original inputs/tools unchanged")
        path = folder/"verification.json"
        path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        results.append(dict(mode=mode,receipt=str(path),sha256=sha(path),functions={name:{key:value for key,value in f.items() if key not in ("rows","A1_operand_rows")} for name,f in facts.items()}))
    print(json.dumps(dict(diagnostic_only=True,accepted_native_candidate=False,results=results)))


if __name__ == "__main__":
    main()
