"""Fresh five-function native static proof; never runs generated RV32 code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import uuid
from gates import ENTRY, HELPERS, SCRATCH, IMAGE_SHA, elf_gate, machine_gate, main_static_def_use, ir_gate
from elf32 import require

_paths = __import__("runpy").run_path(str(next(p for p in Path(__file__).resolve().parents if (p / "scripts/project_paths.py").is_file()) / "scripts/project_paths.py"))

HERE = Path(__file__).resolve().parent
SOURCE_PINS = {
    "experiments/tsl9-v4160-irq-native/src/interrupt_registers.c":"7bf0b338044ef635f132281c11abb516bb0b9a62108e7c8faa8857c1b5e928db",
    "experiments/tsl9-v4160-irq-native/src/native_io.h":"f98eda2e291d585b086f5e65cd4d8816855e7819350f7b93dd6002bb430a3d2e",
    "experiments/tsl9-v4160-interrupt-registers/src/interrupt_registers.h":"da57cec48aa144786cd9a64c8d20aadd2bb02d9e91d43408eac6441f7ba3ae59"}
PARSER_SHA = "00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141"
FIRMWARE = "exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin"
PUBLISHED_FIRMWARE = "firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin"
NDK = _paths["llvm_bin"]()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_tool(override,directory,name):
    path = override or (str(directory/(name+(".exe" if os.name == "nt" else ""))) if directory else shutil.which(name))
    require(path and Path(path).is_file(),"missing local LLVM tool: "+name)
    return Path(path).resolve()


def resolve_firmware(root,explicit=None,required=True):
    if explicit is not None:
        require(explicit.is_file(),"explicit offline --firmware file is missing")
        return explicit.resolve()
    for relative in (FIRMWARE,PUBLISHED_FIRMWARE):
        if (root/relative).is_file():
            return (root/relative).resolve()
    require(not required,"missing offline original BIN; supply --firmware")
    return None


def flags(mode):
    return ["--target=riscv32-unknown-elf","-march=rv32imac_zicsr","-mabi=ilp32","-Oz","-mllvm","-enable-machine-outliner=never","-ffreestanding","-fno-builtin","-fno-stack-protector","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-mno-relax","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror",*["-ffixed-x"+str(reg) for reg in range(1,32) if reg not in {10,11,14,15}],"-x","c" if mode == "c" else "c++","-std=c11" if mode == "c" else "-std=c++17"]


def linker_source():
    sections = ["  .rcc_"+hex(address)[2:]+" "+hex(address)+" : { *(.text."+name+") }" for name,address in HELPERS.items()]
    return "ENTRY("+ENTRY+")\nSECTIONS\n{\n"+"\n".join(sections)+"\n  .irq_scratch "+hex(SCRATCH)+" : { *(.text."+ENTRY+") }\n}\n"


def run(argv,folder,label):
    p = subprocess.run([str(v) for v in argv],capture_output=True,cwd=folder,timeout=120)
    raw = p.stdout+p.stderr
    (folder/(label+".log")).write_bytes(raw)
    require(p.returncode == 0,label+" failed; inspect retained local log")
    return dict(label=label,argv=[str(v) for v in argv],exit=p.returncode,log_sha256=hashlib.sha256(raw).hexdigest()),raw.decode("utf-8",errors="replace")


def compile_and_link(root,folder,tools,mode):
    source = root/"experiments/tsl9-v4160-irq-native/src/interrupt_registers.c"
    obj,ir,linked = folder/"irq.o",folder/"irq.ll",folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf"
    script = folder/"placements.ld"
    script.write_text(linker_source(),encoding="utf-8")
    commands = []
    for label,argv in [("compile",[tools["clang"],*flags(mode),"-c",source,"-o",obj]),
                       ("llvm-ir",[tools["clang"],*flags(mode),"-S","-emit-llvm",source,"-o",ir]),
                       ("link",[tools["linker"],"--no-relax","--no-undefined","-T",script,obj,"-o",linked]),
                       ("disassembly",[tools["objdump"],"--disassemble",linked])]:
        record,text = run(argv,folder,label);commands.append(record)
    return obj,ir,linked,text,commands


def static_checks(obj,ir,linked,text,image):
    object_result,linked_result = elf_gate(obj,False),elf_gate(linked,True)
    machine = machine_gate(text,linked,image)
    normal = main_static_def_use(machine)
    LLVM_IR = ir_gate(ir)
    return dict(object=object_result,linked=linked_result,machine=machine,initializer_static_def_use=normal,LLVM_IR=LLVM_IR)


def transcript_controls(text,linked,image):
    controls = []
    for name in [*HELPERS,ENTRY]:
        marker = re.search(r"^([0-9a-f]+) <"+name+r">:\s*$",text,re.M)
        require(marker is not None,"actual transcript function")
        head,tail = text[:marker.end()],text[marker.end():]
        lines = tail.splitlines(keepends=True)
        indexes = []
        for i,line in enumerate(lines):
            if indexes and not line.strip():
                break
            if re.match(r"\s*[0-9a-f]+:",line):
                indexes.append(i)
        require(len(indexes)>3,"actual instruction transcript")
        variants = {}
        for label,index in (("missing_first",indexes[0]),("missing_middle",indexes[len(indexes)//2]),("truncated_last",indexes[-1])):
            variants[label] = head+"".join(line for i,line in enumerate(lines) if i != index)
        changed = list(lines)
        changed[indexes[1]] = re.sub(r"(:\s*)[0-9a-f]{2}",r"\g<1>00",changed[indexes[1]],count=1)
        require(changed[indexes[1]] != lines[indexes[1]],"actual raw byte mutation")
        variants["changed_raw_byte"] = head+"".join(changed)
        for label,index in (("unparsed_middle",indexes[1]),("unparsed_trailing",indexes[-1]+1)):
            changed = list(lines);changed.insert(index,"    UNPARSED-INSTRUCTION\n")
            variants[label] = head+"".join(changed)
        for label,changed in variants.items():
            try:
                machine_gate(changed,linked,image)
            except ValueError as error:
                controls.append(dict(function=name,case=label,rejected=True,reason=str(error),transcript_sha256=hashlib.sha256(changed.encode()).hexdigest()))
            else:
                raise ValueError("modified transcript admitted: "+name+" / "+label)
    return controls


def compiled_controls(root,folder,tools,mode,image):
    source = root/"experiments/tsl9-v4160-irq-native/src/interrupt_registers.c"
    header = root/"experiments/tsl9-v4160-irq-native/src/native_io.h"
    text = source.read_text(encoding="utf-8-sig")
    htext = header.read_text(encoding="utf-8-sig")
    controls = [
        ("A2_write",source,text,"    return ir_init_return(result,0u,",'    __asm__ volatile("li a2, 1");\n    return ir_init_return(result,0u,'),
        ("SP_write",source,text,"    return ir_init_return(result,0u,",'    __asm__ volatile("addi sp, sp, -16");\n    return ir_init_return(result,0u,'),
        ("wrong_final_A1",source,text,"    return ir_init_return(result,0u,","    return ir_init_return(result,1u,"),
        ("wrong_PFIC_width",header,htext,"#define IR_WRITE8(a,v) (*(volatile uint8_t *)(uintptr_t)(a)=(v))","#define IR_WRITE8(a,v) (*(volatile uint16_t *)(uintptr_t)(a)=(v))"),
        ("wrong_helper_offset",source,text,"return update32(0x18u,mask,enabled);","return update32(0x1cu,mask,enabled);")]
    reports = []
    for name,changed_path,original,before,after in controls:
        require(original.count(before) == 1,"one exact compiled control source site")
        case = folder/("negative-"+name)
        case.mkdir()
        for relative in SOURCE_PINS:
            destination = case/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes((root/relative).read_bytes())
        modified = case/changed_path.relative_to(root)
        modified.write_text(original.replace(before,after),encoding="utf-8")
        obj,ir,linked,assembly,commands = compile_and_link(case,case,tools,mode)
        try:
            static_checks(obj,ir,linked,assembly,image)
        except ValueError as error:
            reports.append(dict(case=name,actual_compilation_and_link_succeeded=True,rejected=True,reason=str(error),
                                changed_source=str(changed_path.relative_to(root)),source_sha256=sha(modified),object_sha256=sha(obj),LLVM_IR_sha256=sha(ir),linked_ELF_sha256=sha(linked),commands=commands))
        else:
            raise ValueError("compiled negative admitted: "+name)
    return reports


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=HERE.parents[2])
    p.add_argument("--tool-dir",type=Path)
    p.add_argument("--clang")
    p.add_argument("--linker")
    p.add_argument("--objdump")
    p.add_argument("--firmware",type=Path)
    p.add_argument("--language",choices=("c","cpp","both"),default="both")
    a = p.parse_args()
    root = a.project_root.resolve()
    require({name:sha(root/name) for name in SOURCE_PINS} == SOURCE_PINS,"frozen native core and public header pins")
    require(sha(HERE/"elf32.py") == PARSER_SHA,"exact tiny local ELF parser")
    firmware = resolve_firmware(root,a.firmware)
    image = firmware.read_bytes()
    require(len(image) == 76800 and hashlib.sha256(image).hexdigest() == IMAGE_SHA,"exact offline original BIN input")
    directory = a.tool_dir or (NDK if os.name == "nt" and NDK.is_dir() else None)
    tools = {key:resolve_tool(getattr(a,key),directory,name) for key,name in (("clang","clang"),("linker","ld.lld"),("objdump","llvm-objdump"))}
    tool_pins = {key:sha(path) for key,path in tools.items()}
    script_pins = {name:sha(HERE/name) for name in ("verify_native.py","gates.py","elf32.py")}
    results = []
    for mode in (("c","cpp") if a.language == "both" else (a.language,)):
        folder = HERE/"build"/("native-"+uuid.uuid4().hex+"-"+mode)
        folder.mkdir(parents=True)
        obj,ir,linked,assembly,commands = compile_and_link(root,folder,tools,mode)
        checks = static_checks(obj,ir,linked,assembly,image)
        transcripts = transcript_controls(assembly,linked,image)
        negatives = compiled_controls(root,folder,tools,mode,image)
        report = dict(schema="TSL9-IRQ-five-native-components-static-proof-v1",passed=True,mode=mode,
                      source_sha256=SOURCE_PINS,script_sha256=script_pins,firmware_input=dict(path=str(firmware),sha256=IMAGE_SHA,bytes=len(image)),
                      tools={key:dict(path=str(path),sha256=tool_pins[key]) for key,path in tools.items()},flags=flags(mode),commands=commands,
                      placement_script_sha256=sha(folder/"placements.ld"),LLVM_IR_sha256=sha(ir),checks=checks,
                      transcript_controls=transcripts,actual_compiled_controls=negatives,
                      helper_original_placement_and_120byte_identity=True,
                      all_allocated_bytes_function_ownership_passed=checks["linked"]["all_allocated_bytes_function_owned"],
                      main_original_extent_check=dict(passed=checks["machine"][ENTRY]["bytes"]<=144,actual_bytes=checks["machine"][ENTRY]["bytes"],original_bytes=144,original_start=0x9a42,original_end_exclusive=0x9ad2),
                      main_scratch_VA=SCRATCH,scratch_storage_suitability_proved=False,original_full_image_integration_proved=False,
                      full_original_ABI_proved=False,interrupt_or_pointwise_semantics_proved=False,firmware_BIN_produced=False,
                      target_execution=False,ISA_emulation=False,network=False,hardware=False,OTA_ready=False)
        require({name:sha(root/name) for name in SOURCE_PINS} == SOURCE_PINS and {key:sha(path) for key,path in tools.items()} == tool_pins and {name:sha(HERE/name) for name in script_pins} == script_pins,"all source/script/tool inputs unchanged")
        receipt = folder/"verification.json"
        receipt.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        results.append(dict(mode=mode,receipt=str(receipt),sha256=sha(receipt),functions={name:dict(bytes=f["bytes"],instructions=f["instruction_rows"]) for name,f in checks["machine"].items()},helpers_original_identity=True,main_original_extent_fits=report["main_original_extent_check"]["passed"],compiled_negative_controls=len(negatives),transcript_controls=len(transcripts)))
    print(json.dumps(dict(passed=True,results=results,original_full_image_integration_proved=False,OTA_ready=False)))


if __name__ == "__main__":
    main()
