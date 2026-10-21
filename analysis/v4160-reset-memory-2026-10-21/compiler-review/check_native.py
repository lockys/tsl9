"""Read-only sealed reset-memory metadata and optional retained artifact replay."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def contained(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), "contained evidence path")
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", type=Path, default=HERE.parents[2])
    p.add_argument("--require-local-builds", action="store_true")
    args = p.parse_args()
    root = args.project_root.resolve()
    seal = json.loads((HERE / "final-audit.json").read_text(encoding="utf-8"))
    require(seal["passed"] and not seal["original_fixed_placement_proved"] and not seal["OTA_ready"], "explicit structural evidence class")
    for member in seal["members"]:
        path = contained(HERE, member["path"])
        require(path.stat().st_size == member["bytes"] and sha(path) == member["sha256"], "sealed bytes/hash: " + member["path"])
    index = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    model = root / "experiments/tsl9-v4160-reset-memory/src"
    for name, digest in index["source_sha256"].items():
        require(sha(contained(model, name)) == digest, "current reset C/H source identity")
    spec = importlib.util.spec_from_file_location("reset_memory_static_replay", HERE / "verify_native.py")
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    metadata_checked, artifacts_replayed, host_replayed, missing = [], [], [], []
    for build in index["results"]:
        metadata = contained(HERE, build["metadata"])
        require(sha(metadata) == build["sha256"], "byte-identical selected native receipt metadata")
        r = json.loads(metadata.read_text(encoding="utf-8"))
        require(r["passed"] and r["mode"] == build["mode"] and r["fragment"] == build["fragment"] and r["source_sha256"] == index["source_sha256"], "actual native configuration/source metadata")
        require(sha(HERE / "verify_native.py") == r["source_script_sha256"] and sha(HERE / "elf32.py") == r["ELF_parser_sha256"], "current verifier/parser identity")
        require(r["machine"]["helper_bytes"] == (80 if build["fragment"] else 78) and r["machine"]["instruction_rows"] == 24, "honest native code size")
        require(r["LLVM_IR"]["GP_observation_sites"] == 3 and r["machine"]["physical_GP_operand_reads"] == 4 and len(r["machine"]["loop_components"]) == 2, "separate IR/live-native GP and loop facts")
        require(not r["original_slot_check"]["passed"] and r["original_slot_check"]["continuation_overlaps_candidate_if_original_placement"], "original placement gap remains explicit")
        if build["fragment"]:
            require(r["object"]["undefined_symbols"] == [v.CONTINUATION] and r["object"]["continuation_relocations"] == [dict(offset=76, type=17, addend=0)], "actual four-byte JAL continuation obligation")
            require(r["strict_missing_continuation_rejected"] and not r["continuation_body_supplied"] and not r["numeric_witness_is_implementation"], "strict rejected provider and numeric-only witness")
        metadata_checked.append(dict(mode=build["mode"], fragment=build["fragment"]))
        folder = contained(HERE, build["artifact_dir"])
        if not (folder / "verification.json").is_file():
            missing.append(build["artifact_dir"])
            continue
        require(sha(folder / "verification.json") == build["sha256"], "actual historical native receipt matches shipped metadata")
        obj, ir = folder / "reset_memory.o", folder / "reset_memory.ll"
        linked = folder / ("ADDRESS-WITNESS-ONLY.elf" if build["fragment"] else "COMPONENT-ONLY-NOT-FIRMWARE.elf")
        require(sha(obj) == r["object"]["sha256"] and sha(ir) == r["LLVM_IR_sha256"] and sha(linked) == r["linked_component"]["sha256"], "actual native object/IR/ELF bytes")
        require(v.elf_gate(obj, build["fragment"]) == r["object"] and v.elf_gate(linked, build["fragment"], True) == r["linked_component"] and v.ir_gate(ir) == r["LLVM_IR"], "actual ELF/IR structural gates replay")
        text = (folder / "disassembly.log").read_bytes().decode("utf-8", errors="replace")
        require(v.machine_gate(text, linked, build["fragment"]) == r["machine"], "actual full native raw/RD/loop CFG replay")
        require(v.transcript_controls(text, linked, build["fragment"]) == r["transcript_controls"] and len(r["transcript_controls"]) == 6, "six transcript controls replay")
        require(len(r["actual_compiled_controls"]) == 3, "three actual compiled native controls")
        for control in r["actual_compiled_controls"]:
            case = folder / ("negative-" + control["case"])
            elf = case / "COMPILED-NEGATIVE-NOT-FIRMWARE.elf"
            require(control["actual_compilation_and_link_succeeded"] and control["rejected"], "native control actually compiled/linked/rejected")
            require(sha(case / "reset_memory.c") == control["source_sha256"] and sha(case / "reset_memory.o") == control["object_sha256"] and sha(case / "reset_memory.ll") == control["LLVM_IR_sha256"] and sha(elf) == control["linked_sha256"], "actual compiled control artifact bytes")
            try:
                v.ir_gate(case / "reset_memory.ll")
                v.machine_gate((case / "disassembly.log").read_bytes().decode("utf-8", errors="replace"), elf, build["fragment"])
            except ValueError as error:
                require(str(error) == control["reason"], "specific compiled control rejection")
            else:
                raise ValueError("compiled native control admitted")
        artifacts_replayed.append(dict(mode=build["mode"], fragment=build["fragment"]))
    for build in index["parent_host_builds"]:
        path = contained(root, build["receipt"])
        if not path.is_file():
            missing.append(build["receipt"])
            continue
        require(sha(path) == build["sha256"], "actual parent host/source receipt")
        r = json.loads(path.read_text(encoding="utf-8"))
        require(r["passed"] and r["tests"] == dict(passed=True, groups=5, cases=338, checks=133601), "parent host5groups338cases133601checks")
        require(r["source_proof_checked"] and r["original_source"]["source_bytes"] == 62 and r["original_source"]["instructions"] == 17 and r["original_source"]["raw_mutations_rejected"] == 17, "source62bytes17instructions17rawcontrols")
        host_replayed.append(build["mode"])
    require(not args.require_local_builds or not missing, "required historical local build artifacts missing")
    print(json.dumps(dict(passed=True, sealed_members=len(seal["members"]), native_metadata_checked=metadata_checked,
                          historical_native_archives_replayed=artifacts_replayed, parent_host_receipts_replayed=host_replayed,
                          missing_historical_artifacts=missing, new_compilation_performed=False,
                          original_fixed_placement_proved=False, continuation_provider_proved=False,
                          firmware_executed=False, ISA_emulation=False, network=False, hardware=False, OTA_ready=False)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print("Reset memory proof replay failed: " + str(error), file=sys.stderr)
        sys.exit(1)
