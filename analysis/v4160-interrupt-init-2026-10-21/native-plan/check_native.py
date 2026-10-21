"""Read-only sealed evidence check; archive replay is explicit and optional."""
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


def contained(base, relative):
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()), "contained evidence member")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=HERE.parents[2])
    parser.add_argument("--require-local-builds", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()
    seal = json.loads((HERE / "final-audit.json").read_text(encoding="utf-8"))
    require(seal["passed"] and seal["scope"] == "native component compilation/static proof only", "explicit sealed evidence class")
    for member in seal["members"]:
        path = contained(HERE, member["path"])
        require(path.stat().st_size == member["bytes"] and sha(path) == member["sha256"], "sealed member bytes/hash: " + member["path"])
    summary = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    for name, digest in summary["source_sha256"].items():
        require(sha(contained(root, name)) == digest, "actual current C/H source identity")
    spec = importlib.util.spec_from_file_location("irq_native_proof", HERE / "verify_native.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    replayed = []
    missing = []
    for build in summary["verified_builds"]:
        receipt_path = contained(HERE, build["receipt"])
        if not receipt_path.is_file():
            missing.append(build["receipt"])
            continue
        require(sha(receipt_path) == build["receipt_sha256"], "native receipt bytes identity")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        require(receipt["passed"] and receipt["mode"] == build["mode"], "real native passed mode")
        folder = receipt_path.parent
        obj, ir, elf = folder / "interrupt_init.o", folder / "interrupt_init.ll", folder / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
        require(sha(obj) == receipt["object"]["sha256"] and sha(elf) == receipt["linked_component"]["sha256"] and sha(ir) == receipt["LLVM_IR_sha256"], "actual native object/ELF/IR hashes")
        require(verifier.elf_gate(obj, False) == receipt["object"] and verifier.elf_gate(elf, True) == receipt["linked_component"], "replayed real native ELF gates")
        require(verifier.ir_gate(ir) == receipt["LLVM_IR"], "replayed actual IR gate")
        machine = verifier.machine_gate((folder / "component-disassembly.log").read_text(encoding="utf-8"))
        # JSON converts static expression tuples to lists; normalize intentionally.
        require(json.loads(json.dumps(machine)) == receipt["machine_static_proof"], "replayed static machine def-use proof")
        require(len(receipt["compiled_negative_controls"]) == 4, "four actual compiled negative controls")
        for negative in receipt["compiled_negative_controls"]:
            case = folder / ("negative-" + negative["case"])
            require(negative["actual_compilation_succeeded"] and negative["rejected"], "compiled mutation record")
            require(sha(case / "interrupt_init.c") == negative["source_sha256"] and sha(case / "mutant.o") == negative["object_sha256"] and sha(case / "mutant.ll") == negative["LLVM_IR_sha256"], "actual compiled mutation artifact hashes")
            try:
                verifier.ir_gate(case / "mutant.ll")
            except ValueError as error:
                require(str(error) == negative["reason"], "specific compiled mutation rejection reason")
            else:
                raise ValueError("compiled mutation unexpectedly admitted")
        replayed.append(build["mode"])
    host_replayed = []
    for build in summary["parent_host_source_proof_builds"]:
        path = contained(root, build["receipt"])
        if not path.is_file():
            missing.append(build["receipt"])
            continue
        require(sha(path) == build["receipt_sha256"], "actual parent host/source receipt identity")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        require(receipt["passed"] and receipt["mode"] == build["mode"] and receipt["tests"] == dict(passed=True, groups=4, checks=6680), "parent host4groups6680checks")
        source = receipt["original_source"]
        require(receipt["source_proof_checked"] and source["passed"] and source["source_bytes"] == 264 and source["instructions"] == 94 and source["raw_negative_controls_rejected"] == 94, "parent actual source264bytes94instructions94rawnegatives")
        host_replayed.append(build["mode"])
    require(not args.require_local_builds or not missing, "required retained local build artifacts are missing")
    print(json.dumps(dict(passed=True, sealed_members=len(seal["members"]), current_C_H_checked=True,
                          native_archives_replayed=replayed, parent_host_receipts_replayed=host_replayed,
                          missing_local_build_receipts=missing, new_compilation_performed=False,
                          historical_old691_objects_replayed=False, firmware_executed=False, ISA_emulation=False,
                          hardware=False, network=False, OTA_ready=False)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print("Native evidence check failed: " + str(error), file=sys.stderr)
        sys.exit(1)
