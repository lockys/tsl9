"""Exactly one C++ profile: add -fno-exceptions, compile/static checks only."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

HERE = Path(__file__).resolve().parent
DEPENDENCY = Path("apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review")
SEAL_SHA = "13772c1bfe0c3faf0fe37cf4cbdd8fe4be40ca6f6913ef132c64a3c0677f9c04"
PINS = {"verify_native.py":"58e726bf5590eeb318c7123a75fd00c5b406b58e36c545c65962a1ac80a369ac",
        "gates.py":"c51f2242a3f3356ce77c09c12757cda0ed13b6830ac255cbfbd4fcdfd36341e5",
        "elf32.py":"00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141",
        "receipts/cpp.json":"1134805ce608d4a588c70ea5417c2c684887b262110c490a2531ed20c012b7e3"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition,message):
    if not condition:
        raise ValueError(message)


def normalized(value):
    return json.loads(json.dumps(value))


def load_dependencies(root):
    dep = root/DEPENDENCY
    require(sha(dep/"final-audit.json") == SEAL_SHA,"immutable five-function native baseline seal")
    for name,pin in PINS.items():
        require(sha(dep/name) == pin,"immutable baseline dependency: "+name)
    sys.path.insert(0,str(dep))
    spec = importlib.util.spec_from_file_location("immutable_irq_native_profile",dep/"verify_native.py")
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    require(all(Path(sys.modules[name].__file__).resolve() == (dep/(name+".py")).resolve() for name in ("gates","elf32")),"actual loaded pinned dependency paths")
    baseline = json.loads((dep/"receipts/cpp.json").read_text(encoding="utf-8"))
    return native,sys.modules["elf32"].ELF,baseline


def compare_baseline(checks,linked,ELF,baseline):
    elf = ELF(linked)
    comparisons = {}
    for name,old in baseline["checks"]["machine"].items():
        old_bytes = b"".join(bytes.fromhex(row["bytes"]) for row in old["rows"])
        require(len(old_bytes) == old["bytes"] and hashlib.sha256(old_bytes).hexdigest() == old["code_sha256"],"sealed baseline raw-row byte identity")
        symbols = [s for s in elf.symbols if s["index"] and s["name"] == name and s["info"]&15 == 2]
        require(len(symbols) == 1,"one actual new function")
        actual = elf.function_bytes(symbols[0])
        same = actual == old_bytes
        require(same,"new profile changed actual function bytes: "+name)
        comparisons[name] = dict(bytes=len(actual),instructions=old["instruction_rows"],code_sha256=hashlib.sha256(actual).hexdigest(),
                                 identical_to_sealed_CPP_baseline=True,address=symbols[0]["value"])
    equality = {key:normalized(checks[key]) == baseline["checks"][key] for key in ("machine","initializer_static_def_use","LLVM_IR")}
    require(all(equality.values()),"same native/SSA structural and normal-output proof results")
    return dict(functions=comparisons,proof_result_equality=equality,all_five_functions_identical=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=HERE.parents[2])
    p.add_argument("--tool-dir",type=Path)
    p.add_argument("--clang")
    p.add_argument("--linker")
    p.add_argument("--objdump")
    p.add_argument("--firmware",type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    native,ELF,baseline = load_dependencies(root)
    require({name:sha(root/name) for name in native.SOURCE_PINS} == native.SOURCE_PINS,"frozen existing native core/public header")
    firmware = native.resolve_firmware(root,a.firmware)
    image = firmware.read_bytes()
    require(len(image) == 76800 and hashlib.sha256(image).hexdigest() == native.IMAGE_SHA,"exact offline original image")
    directory = a.tool_dir or (native.NDK if os.name == "nt" and native.NDK.is_dir() else None)
    tools = {key:native.resolve_tool(getattr(a,key),directory,name) for key,name in (("clang","clang"),("linker","ld.lld"),("objdump","llvm-objdump"))}
    tool_pins = {name:sha(path) for name,path in tools.items()}
    old_flags = native.flags("cpp")
    profile_flags = [*old_flags,"-fno-exceptions"]
    require(profile_flags[:-1] == baseline["flags"] and profile_flags.count("-fno-exceptions") == 1 and "-fno-rtti" not in profile_flags,"exact one-flag change from sealed CPP profile")
    def only_cpp(mode):
        require(mode == "cpp","only requested C++17 profile")
        return list(profile_flags)
    native.flags = only_cpp
    folder = HERE/"build"/("no-exceptions-"+uuid.uuid4().hex+"-cpp")
    folder.mkdir(parents=True)
    obj,ir,linked,text,commands = native.compile_and_link(root,folder,tools,"cpp")
    checks = native.static_checks(obj,ir,linked,text,image)
    comparison = compare_baseline(checks,linked,ELF,baseline)
    require(not checks["object"]["extra_readonly_allocations"] and not checks["linked"]["extra_readonly_allocations"],"actual object and linked extra read-only metadata removed")
    require(checks["object"]["total_allocated_bytes"] == checks["linked"]["total_allocated_bytes"] == 300 and checks["linked"]["all_allocated_bytes_function_owned"],"all actual300 allocated bytes owned by the five functions")
    transcripts = native.transcript_controls(text,linked,image)
    report = dict(schema="TSL9-IRQ-CPP-no-exceptions-single-profile-v1",passed=True,
                  flags=profile_flags,baseline_flags=old_flags,only_added_flag="-fno-exceptions",source_sha256=native.SOURCE_PINS,
                  runner_sha256=sha(Path(__file__)),immutable_dependency_seal_sha256=SEAL_SHA,immutable_dependency_members=PINS,
                  tools={name:dict(path=str(path),sha256=tool_pins[name]) for name,path in tools.items()},commands=commands,
                  firmware_input=dict(path=str(firmware),sha256=native.IMAGE_SHA,bytes=len(image)),LLVM_IR_sha256=sha(ir),placement_script_sha256=sha(folder/"placements.ld"),
                  checks=checks,baseline_comparison=comparison,transcript_controls=transcripts,
                  allocation_comparison={kind:dict(baseline_total=baseline["checks"][kind]["total_allocated_bytes"],actual_total=checks[kind]["total_allocated_bytes"],
                                                  baseline_extra_readonly=baseline["checks"][kind]["extra_readonly_allocations"],actual_extra_readonly=checks[kind]["extra_readonly_allocations"]) for kind in ("object","linked")},
                  helper_original120byte_identity=True,main_original_extent_fits=False,main_bytes=180,original_main_bytes=144,
                  all_allocated_function_ownership_passed=True,original_full_image_integration_proved=False,original_ABI_proved=False,
                  target_execution=False,ISA_emulation=False,firmware_BIN_produced=False,network=False,hardware=False,OTA_ready=False)
    require({name:sha(root/name) for name in native.SOURCE_PINS} == native.SOURCE_PINS and {name:sha(path) for name,path in tools.items()} == tool_pins,"source and tools unchanged")
    require(all(sha(root/DEPENDENCY/name) == pin for name,pin in PINS.items()) and sha(root/DEPENDENCY/"final-audit.json") == SEAL_SHA,"old sealed dependencies unchanged")
    receipt = folder/"verification.json"
    receipt.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(passed=True,receipt=str(receipt),sha256=sha(receipt),all5_function_bytes_identical=True,
                         object_allocated_bytes=300,linked_allocated_bytes=300,extra_readonly_removed=True,main_original_extent_fits=False,OTA_ready=False)))


if __name__ == "__main__":
    main()
