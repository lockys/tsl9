"""Read-only register-allocation proof and retained native artifact replay."""
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
    require(seal["passed"] and not seal["full_original_ABI_proved"] and not seal["OTA_ready"], "honest sealed proof class")
    for member in seal["members"]:
        path = contained(HERE, member["path"])
        require(path.stat().st_size == member["bytes"] and sha(path) == member["sha256"], "sealed bytes/hash: " + member["path"])
    results = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    model = root / "experiments/tsl9-v4160-clock-registers/src"
    for name, digest in results["source_sha256"].items():
        require(sha(contained(model, name)) == digest, "actual four current C/H inputs")
    spec = importlib.util.spec_from_file_location("clock_compiler_proof", HERE / "verify_compiler.py")
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    ELF, _ = v.elf_parser(root)
    native, host, missing = [], [], []
    for build in results["native_builds"]:
        path = contained(HERE, build["receipt"])
        if not path.is_file():
            missing.append(build["receipt"])
            continue
        require(sha(path) == build["receipt_sha256"], "actual native receipt identity")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        require(receipt["passed"] and receipt["mode"] == build["mode"] and receipt["source_sha256"] == results["source_sha256"], "actual native mode/source proof")
        require(sha(HERE / "verify_compiler.py") == receipt["source_script_sha256"], "same native verifier source")
        folder = path.parent
        linked = folder / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
        require(sha(linked) == receipt["linked_component_sha256"], "actual linked component bytes")
        for name, digest in receipt["objects"].items():
            require(sha(contained(folder, name)) == digest, "actual native objects")
        text = (folder / "disassembly.log").read_bytes().decode("utf-8", errors="replace")
        require(v.machine_gate(text, linked, ELF) == receipt["functions"], "full actual native raw bytes/RD/CFG/field pattern replay")
        require(v.transcript_controls(text, linked, ELF) == receipt["transcript_controls"] and len(receipt["transcript_controls"]) == 14, "fourteen transcript negative controls replay")
        require(len(receipt["actual_compiled_controls"]) == 3, "three actual compiled native controls")
        for case in receipt["actual_compiled_controls"]:
            folder_case = folder / ("negative-" + case["case"])
            elf = folder_case / "COMPILED-NEGATIVE-NOT-FIRMWARE.elf"
            require(case["actual_compilation_and_link_succeeded"] and case["rejected"], "native mutation compiled/linked/rejected")
            require(sha(elf) == case["linked_component_sha256"] and sha(folder_case / case["changed_source"]) == case["source_sha256"], "actual compiled mutation ELF/source bytes")
            for name, digest in case["object_sha256"].items():
                require(sha(contained(folder_case, name)) == digest, "actual compiled mutation object")
            text_case = (folder_case / "disassembly.log").read_bytes().decode("utf-8", errors="replace")
            require(hashlib.sha256(text_case.encode()).hexdigest() == case["disassembly_sha256"], "actual compiled mutation disassembly")
            try:
                v.machine_gate(text_case, elf, ELF)
            except ValueError as error:
                require(str(error) == case["reason"], "specific compiled native control rejection")
            else:
                raise ValueError("compiled native control unexpectedly admitted")
        native.append(build["mode"])
    for build in results["parent_host_builds"]:
        path = contained(root, build["receipt"])
        if not path.is_file():
            missing.append(build["receipt"])
            continue
        require(sha(path) == build["receipt_sha256"], "actual parent host/source receipt")
        r = json.loads(path.read_text(encoding="utf-8"))
        require(r["passed"] and r["tests"] == dict(passed=True, groups=6, checks=293845), "parent host6groups293845checks")
        require(r["original_source"]["target_bytes"] == 214 and r["original_source"]["target_instructions"] == 69 and r["original_source"]["raw_operand_mutation_rejections"] == 50, "source214bytes69instructions50controls")
        require(r["register_source"]["destination_instruction_counts"] == dict(query18834=44, derive1973c=8), "source destination-field evidence")
        host.append(build["mode"])
    require(not args.require_local_builds or not missing, "required local build artifacts are missing")
    print(json.dumps(dict(passed=True, sealed_members=len(seal["members"]), native_archives_replayed=native,
                          parent_host_receipts_replayed=host, missing_local_receipts=missing,
                          new_compilation_performed=False, full_original_ABI_proved=False,
                          original_fixed_placement_proved=False, firmware_executed=False,
                          ISA_emulation=False, network=False, hardware=False, OTA_ready=False)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print("Compiler proof replay failed: " + str(error), file=sys.stderr)
        sys.exit(1)
