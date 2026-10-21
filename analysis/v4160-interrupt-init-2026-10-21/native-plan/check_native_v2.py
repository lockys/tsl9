"""Read-only full-coverage v2 seal/archive replay; never runs a compiler/target."""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def normalized(value):
    return json.loads(json.dumps(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=HERE.parents[2])
    parser.add_argument("--require-local-builds", action="store_true")
    args = parser.parse_args()
    old = module("irq_native_old_checker", "check_native.py")
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        old.main()
    inherited = json.loads(capture.getvalue())
    require, sha, contained = old.require, old.sha, old.contained
    seal = json.loads((HERE / "final-audit-v2.json").read_text(encoding="utf-8"))
    require(seal["passed"] and sha(HERE / "final-audit.json") == seal["immutable_v1_seal_sha256"], "unchanged complete v1 seal")
    for member in seal["members"]:
        path = contained(HERE, member["path"])
        require(path.stat().st_size == member["bytes"] and sha(path) == member["sha256"], "v2 sealed member bytes/hash: " + member["path"])
    summary = json.loads((HERE / "results-v2.json").read_text(encoding="utf-8"))
    verifier = module("irq_native_v2_replay", "verify_native_v2.py")
    replayed, missing = [], []
    for build in summary["verified_builds"]:
        receipt_path = contained(HERE, build["receipt"])
        if not receipt_path.is_file():
            missing.append(build["receipt"])
            continue
        require(sha(receipt_path) == build["receipt_sha256"], "v2 actual native receipt identity")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        require(receipt["passed"] and receipt["schema"] == "TSL9-readable-interrupt-init-native-verification-v2" and receipt["mode"] == build["mode"], "actual v2 passed mode/schema")
        folder = receipt_path.parent
        obj, ir, elf = folder / "interrupt_init.o", folder / "interrupt_init.ll", folder / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
        require(sha(obj) == receipt["object"]["sha256"] and sha(elf) == receipt["linked_component"]["sha256"] and sha(ir) == receipt["LLVM_IR_sha256"], "actual v2 compiled object/ELF/IR identity")
        require(verifier.base.elf_gate(obj, False) == receipt["object"] and verifier.base.elf_gate(elf, True) == receipt["linked_component"], "v2 ELF archive gate replay")
        require(verifier.base.ir_gate(ir) == receipt["LLVM_IR"], "v2 IR archive gate replay")
        disassembly = (folder / "component-disassembly.log").read_text(encoding="utf-8")
        require(normalized(verifier.machine_gate(disassembly, elf)) == receipt["machine_static_proof"], "complete ELF-bound raw machine coverage and semantic proof replay")
        require(receipt["full_ELF_disassembly_coverage_proved"], "actual full symbol machine proof")
        for name, digest in receipt["script_inputs_sha256"].items():
            require(sha(contained(HERE, name)) == digest, "actual v2 script input identity")
        require(len(receipt["compiled_negative_controls"]) == 4, "v2 four compiled source controls")
        for negative in receipt["compiled_negative_controls"]:
            case = folder / ("negative-" + negative["case"])
            require(negative["actual_compilation_succeeded"] and negative["rejected"], "v2 compiled source control status")
            require(sha(case / "interrupt_init.c") == negative["source_sha256"] and sha(case / "mutant.o") == negative["object_sha256"] and sha(case / "mutant.ll") == negative["LLVM_IR_sha256"], "actual v2 compiled source mutation artifacts")
            try:
                verifier.base.ir_gate(case / "mutant.ll")
            except ValueError as error:
                require(str(error) == negative["reason"], "specific v2 compiled source rejection")
            else:
                raise ValueError("v2 compiled source mutation admitted")
        replayed.append(build["mode"])
    require(not args.require_local_builds or not missing, "required v2 native archive is missing")
    print(json.dumps(dict(passed=True, version=2, sealed_new_members=len(seal["members"]), inherited_v1=inherited,
                          native_v2_archives_replayed=replayed, missing_local_v2_receipts=missing,
                          new_compilation_performed=False, firmware_executed=False, ISA_emulation=False,
                          hardware=False, network=False, OTA_ready=False)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print("Native evidence v2 check failed: " + str(error), file=sys.stderr)
        sys.exit(1)
