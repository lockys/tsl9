"""Read-only sealed native-clock proof/archive replay; no target execution."""
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
    require(path.is_relative_to(base.resolve()), "contained evidence path")
    return path


def normalized(value):
    return json.loads(json.dumps(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=HERE.parents[2])
    parser.add_argument("--require-local-builds", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()
    seal = json.loads((HERE / "final-audit.json").read_text(encoding="utf-8"))
    require(seal["passed"] and not seal["native_branch_semantics_proved"] and not seal["OTA_ready"], "sealed static structural evidence class")
    for member in seal["members"]:
        path = contained(HERE, member["path"])
        require(path.stat().st_size == member["bytes"] and sha(path) == member["sha256"], "sealed member bytes/hash: " + member["path"])
    summary = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    for path, digest in summary["source_sha256"].items():
        require(sha(contained(root, path)) == digest, "actual C/H source identity")
    spec = importlib.util.spec_from_file_location("native_clock_proof_replay", HERE / "verify_native.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    replayed, missing, host_replayed = [], [], []
    for build in summary["native_builds"]:
        path = contained(HERE, build["receipt"])
        if not path.is_file():
            missing.append(build["receipt"])
            continue
        require(sha(path) == build["receipt_sha256"], "actual native receipt identity")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        require(receipt["passed"] and receipt["mode"] == build["mode"] and not receipt["native_branch_semantics_proved"], "actual native structural receipt")
        folder = path.parent
        obj, ir, elf = folder / "native_clock.o", folder / "native_clock.ll", folder / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
        require(sha(obj) == receipt["object"]["sha256"] and sha(elf) == receipt["linked_component"]["sha256"] and sha(ir) == receipt["LLVM_IR_sha256"], "actual compiled native artifact identities")
        require(verifier.elf_gate(obj, False) == receipt["object"] and verifier.elf_gate(elf, True) == receipt["linked_component"], "native object/linked ELF gates replay")
        require(verifier.ir_gate(ir) == receipt["LLVM_IR"], "actual native IR primitive/offset properties replay")
        text = (folder / "component-disassembly.log").read_text(encoding="utf-8")
        require(normalized(verifier.machine_gate(text, elf)) == receipt["machine_static_coverage"], "full ELF-bound machine coverage/GP/width/CFG replay")
        require(normalized(verifier.transcript_controls(text, elf)) == receipt["actual_transcript_controls"] and len(receipt["actual_transcript_controls"]) == 12, "twelve actual transcript negative controls replay")
        require(len(receipt["actual_compiled_source_controls"]) == 5, "five actual compiled source controls")
        for negative in receipt["actual_compiled_source_controls"]:
            case = folder / ("negative-" + negative["case"])
            require(negative["actual_compilation_succeeded"] and negative["rejected"], "actual compiled mutant rejected")
            require(sha(case / "native_clock.c") == negative["source_sha256"] and sha(case / "mutant.o") == negative["object_sha256"] and sha(case / "mutant.ll") == negative["LLVM_IR_sha256"], "actual compiled mutant artifact identities")
            try:
                verifier.ir_gate(case / "mutant.ll")
            except ValueError as error:
                require(str(error) == negative["reason"], "specific compiled mutant rejection reason")
            else:
                raise ValueError("native source mutant unexpectedly admitted")
        for name, digest in receipt["script_inputs_sha256"].items():
            require(sha(contained(HERE, name)) == digest, "actual verifier source inputs unchanged")
        replayed.append(build["mode"])
    for build in summary["parent_host_builds"]:
        path = contained(root, build["receipt"])
        if not path.is_file():
            missing.append(build["receipt"])
            continue
        require(sha(path) == build["receipt_sha256"], "parent actual host/source receipt identity")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        require(receipt["passed"] and receipt["mode"] == build["mode"] and receipt["tests"] == dict(passed=True, groups=6, checks=269618), "parent hosted6groups269618checks")
        source = receipt["original_source"]
        require(receipt["source_proof_checked"] and source["passed"] and source["target_bytes"] == 214 and source["target_instructions"] == 69 and source["raw_operand_mutation_rejections"] == 50, "source214bytes69instructions50rawcontrols")
        host_replayed.append(build["mode"])
    require(not args.require_local_builds or not missing, "required retained local build receipts are missing")
    print(json.dumps(dict(passed=True, sealed_members=len(seal["members"]), current_C_H_checked=True,
                          native_archives_replayed=replayed, parent_host_receipts_replayed=host_replayed,
                          missing_local_build_receipts=missing, new_compilation_performed=False,
                          native_branch_semantics_proved=False, firmware_executed=False, ISA_emulation=False,
                          network=False, hardware=False, OTA_ready=False)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print("Native clock evidence check failed: " + str(error), file=sys.stderr)
        sys.exit(1)
