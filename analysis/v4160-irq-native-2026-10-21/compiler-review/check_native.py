"""Read-only native component closure; metadata validation is not compilation."""
import argparse
import json
from pathlib import Path
from elf32 import require
from gates import IMAGE_SHA, ENTRY
from verify_native import SOURCE_PINS, sha, static_checks, transcript_controls, flags, resolve_firmware

HERE = Path(__file__).resolve().parent


def normalized(value):
    return json.loads(json.dumps(value))


def command_logs(folder,commands):
    for command in commands:
        require(command["exit"] == 0 and sha(folder/(command["label"]+".log")) == command["log_sha256"],"actual successful command log pin")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root",type=Path,default=HERE.parents[2])
    p.add_argument("--firmware",type=Path)
    p.add_argument("--require-local-builds",action="store_true")
    a = p.parse_args()
    root = a.project_root.resolve()
    seal = json.loads((HERE/"final-audit.json").read_text(encoding="utf-8"))
    for name,pin in seal["members"].items():
        require(sha(HERE/name) == pin,"sealed member changed: "+name)
    for name,pin in SOURCE_PINS.items():
        require(sha(root/name) == pin,"current frozen native/public source changed")
    index = json.loads((HERE/"results.json").read_text(encoding="utf-8"))
    require(len(index["results"]) == 2,"actual C11/C++17 selected receipts")
    image_path = resolve_firmware(root,a.firmware,required=False)
    image = image_path.read_bytes() if image_path is not None else None
    if image is not None:
        require(len(image) == 76800 and __import__("hashlib").sha256(image).hexdigest() == IMAGE_SHA,"exact offline original input")
    replayed,missing = [],[]
    for item in index["results"]:
        metadata = HERE/item["metadata"]
        require(sha(metadata) == item["sha256"],"selected receipt exactly matches actual original bytes")
        report = json.loads(metadata.read_text(encoding="utf-8"))
        require(report["passed"] and report["flags"] == flags(report["mode"]),"exact single native profile")
        require(report["source_sha256"] == SOURCE_PINS and all(sha(HERE/name) == pin for name,pin in report["script_sha256"].items()),"same final source/script pins")
        require(not report["main_original_extent_check"]["passed"] and not report["original_full_image_integration_proved"] and not report["OTA_ready"],"main180byte original144byte gap and integration gates remain false")
        require(report["all_allocated_bytes_function_ownership_passed"] == (report["mode"] == "c"),"C++ extra allocated metadata is a separate false ownership gate")
        folder = HERE/item["artifact_dir"]
        if not folder.is_dir():
            missing.append(item["artifact_dir"])
            continue
        require(image is not None,"local static replay needs original BIN or --firmware override")
        require(sha(folder/"verification.json") == item["sha256"],"actual original local receipt pin")
        require(sha(folder/"irq.ll") == report["LLVM_IR_sha256"] and sha(folder/"placements.ld") == report["placement_script_sha256"],"actual IR/linker source pins")
        command_logs(folder,report["commands"])
        text = (folder/"disassembly.log").read_text(encoding="utf-8")
        checked = static_checks(folder/"irq.o",folder/"irq.ll",folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf",text,image)
        require(normalized(checked) == report["checks"],"actual ELF/full byte/RD/CFG/helper120byte identity/main effect+output/IR replay")
        require(normalized(transcript_controls(text,folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf",image)) == report["transcript_controls"],"all30 transcript controls replay")
        require(len(report["actual_compiled_controls"]) == 5,"five actual compiled source controls")
        for control in report["actual_compiled_controls"]:
            case = folder/("negative-"+control["case"])
            changed = control["changed_source"].replace("\\","/")
            require(changed in SOURCE_PINS and sha(case/changed) == control["source_sha256"],"actual changed control source pin")
            for relative,pin in SOURCE_PINS.items():
                if relative != changed:
                    require(sha(case/relative) == pin,"other control source inputs unchanged")
            require(sha(case/"irq.o") == control["object_sha256"] and sha(case/"irq.ll") == control["LLVM_IR_sha256"] and sha(case/"COMPONENT-ONLY-NOT-FIRMWARE.elf") == control["linked_ELF_sha256"],"actual compiled control artifact pins")
            command_logs(case,control["commands"])
            try:
                static_checks(case/"irq.o",case/"irq.ll",case/"COMPONENT-ONLY-NOT-FIRMWARE.elf",(case/"disassembly.log").read_text(encoding="utf-8"),image)
            except ValueError as error:
                require(str(error) == control["reason"],"same actual source control rejection")
            else:
                raise ValueError("compiled control admitted during replay")
        replayed.append(item["metadata"])
    require(not a.require_local_builds or not missing,"required selected local build archives missing")
    print(json.dumps(dict(passed=True,seal_sha256=sha(HERE/"final-audit.json"),metadata_receipts=2,local_artifacts_replayed=replayed,missing_local_archives=missing,
                          fresh_compilation=False,helpers_original_120byte_identity=True,main_original_extent_fits=False,
                          CPP_all_allocated_bytes_function_owned=False,full_image_integration=False,target_execution=False,ISA_emulation=False,OTA_ready=False)))


if __name__ == "__main__":
    main()
