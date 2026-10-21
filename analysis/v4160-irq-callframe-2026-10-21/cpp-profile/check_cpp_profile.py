"""Read-only closure for the single no-exceptions C++ metadata profile."""
import argparse
import json
from pathlib import Path
from verify_cpp_profile import HERE, PINS, SEAL_SHA, load_dependencies, compare_baseline, normalized, sha, require


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=HERE.parents[2])
    p.add_argument("--firmware",type=Path)
    p.add_argument("--require-local-builds",action="store_true")
    a = p.parse_args()
    root = a.project_root.resolve()
    seal = json.loads((HERE/"final-audit.json").read_text(encoding="utf-8"))
    for name,pin in seal["members"].items():
        require(sha(HERE/name) == pin,"sealed new profile member changed: "+name)
    native,ELF,baseline = load_dependencies(root)
    require({name:sha(root/name) for name in native.SOURCE_PINS} == native.SOURCE_PINS,"current frozen native/public sources unchanged")
    index = json.loads((HERE/"results.json").read_text(encoding="utf-8"))
    require(len(index["results"]) == 1,"exactly one new C++ profile result")
    item = index["results"][0]
    metadata = HERE/item["metadata"]
    require(sha(metadata) == item["sha256"],"byte-identical actual selected receipt")
    report = json.loads(metadata.read_text(encoding="utf-8"))
    require(report["passed"] and report["flags"] == native.flags("cpp")+["-fno-exceptions"] and report["baseline_flags"] == baseline["flags"],"exactly one added flag, no changed optimizer/allocator")
    require(report["source_sha256"] == native.SOURCE_PINS and report["runner_sha256"] == sha(HERE/"verify_cpp_profile.py") and report["immutable_dependency_members"] == PINS and report["immutable_dependency_seal_sha256"] == SEAL_SHA,"actual source/new runner/immutable prior checker pins")
    require(not report["main_original_extent_fits"] and not report["original_full_image_integration_proved"] and not report["OTA_ready"],"main180>144 and full integration gates remain false")
    folder = HERE/item["artifact_dir"]
    replayed = False
    if folder.is_dir():
        require(sha(folder/"verification.json") == item["sha256"],"actual local receipt pin")
        require(sha(folder/"irq.ll") == report["LLVM_IR_sha256"] and sha(folder/"placements.ld") == report["placement_script_sha256"],"actual IR/linker source pins")
        for command in report["commands"]:
            require(command["exit"] == 0 and sha(folder/(command["label"]+".log")) == command["log_sha256"],"actual compile/IR/link/disassembly log pin")
            if command["label"] in ("compile","llvm-ir"):
                argv = command["argv"]
                require(argv[1:1+len(report["flags"])] == report["flags"],"actual one-flag compiler command")
        firmware = native.resolve_firmware(root,a.firmware)
        image = firmware.read_bytes()
        checks = native.static_checks(folder/"irq.o",folder/"irq.ll",folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf",(folder/"disassembly.log").read_text(encoding="utf-8"),image)
        require(normalized(checks) == report["checks"],"same actual native/IR proof replay")
        require(normalized(compare_baseline(checks,folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf",ELF,baseline)) == report["baseline_comparison"],"all five exact baseline function bytes/proof results replay")
        require(".eh_frame" not in ELF(folder/"irq.o").byname and ".eh_frame" not in ELF(folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf").byname,"actual EH frame section absent from both object and linked ELF")
        require(normalized(native.transcript_controls((folder/"disassembly.log").read_text(encoding="utf-8"),folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf",image)) == report["transcript_controls"],"same30 actual transcript controls replay")
        replayed = True
    require(not a.require_local_builds or replayed,"required historical local artifact archive missing")
    print(json.dumps(dict(passed=True,seal_sha256=sha(HERE/"final-audit.json"),metadata_receipts=1,local_artifacts_replayed=replayed,
                          fresh_compilation=False,all5_function_bytes_identical_to_baseline=True,extra_readonly_metadata_removed=True,
                          actual_allocated_bytes=300,main_original_extent_fits=False,original_full_image_integration=False,target_execution=False,ISA_emulation=False,OTA_ready=False)))


if __name__ == "__main__":
    main()
