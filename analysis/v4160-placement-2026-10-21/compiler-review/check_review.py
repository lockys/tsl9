"""Read-only check: selected failed native profiles and separate available IR."""
import argparse
import hashlib
import json
from pathlib import Path
from ir_checks import gate, transcript_controls, require
from verify_native import SOURCE_PINS, flags

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", type=Path, default=HERE.parents[2])
    p.add_argument("--require-local-builds", action="store_true")
    a = p.parse_args()
    root = a.project_root.resolve()
    seal = json.loads((HERE / "final-audit.json").read_text(encoding="utf-8"))
    for name, pin in seal["members"].items():
        require(sha(HERE / name) == pin, "sealed member changed: " + name)
    for name, pin in SOURCE_PINS.items():
        require(sha(root / "experiments/tsl9-v4160-interrupt-registers/src" / name) == pin, "current original model changed")
    index = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    require(len(index["results"]) == 8, "four bounded profiles, C11/C++17 each")
    replayed, unavailable = [], []
    for item in index["results"]:
        metadata = HERE / item["metadata"]
        require(sha(metadata) == item["sha256"], "selected byte-identical receipt")
        r = json.loads(metadata.read_text(encoding="utf-8"))
        require(not r["native_compilation_succeeded"], "no native success misstatement")
        native_flags = flags(r["mode"])
        if item["kind"] in ("A1_allocation", "combined_return_A1"):
            native_flags.remove("-ffixed-x11")
        require(r["flags"] == native_flags, "only exact authorized optimizer/register profile")
        folder = HERE / item["artifact_dir"]
        if not folder.is_dir():
            unavailable.append(item["artifact_dir"])
            continue
        require(sha(folder / "verification.json") == item["sha256"], "historical local receipt pin")
        require(not (folder / "interrupt_registers.o").exists() and not any(folder.glob("*.elf")), "no native object/ELF emitted")
        compile_commands = [c for c in r["commands"] if "-c" in c["argv"]]
        require(len(compile_commands) == 1 and compile_commands[0]["exit"] != 0, "actual failed native compile")
        error = (folder / "compile.log").read_text(encoding="utf-8")
        require(error.count("Stack pointer required, but has been reserved.") == 5, "exact actual five-function allocation blocker")
        for c in r["commands"]:
            label = c.get("label")
            require(label is not None and sha(folder / (label + ".log")) == c["log_sha256"], "actual command log pin")
        ir = folder / "interrupt_registers.ll"
        require(sha(ir) == r["LLVM_IR_sha256"], "actual optimized IR pin")
        if item["kind"] == "original":
            require(gate(ir) == r["IR_only_checks"] and transcript_controls(ir) == r["IR_transcript_controls"], "original IR-only proof and six transcript controls replay")
        if item["kind"] == "A1_allocation":
            gate(ir)
        if item["kind"] in ("return_commit_source", "combined_return_A1"):
            for name, pin in r["diagnostic_source_sha256"].items():
                require(sha(folder.parent / name) == pin, "actual disposable diagnostic source pin")
        replayed.append(item["metadata"])
    require(not a.require_local_builds or not unavailable, "required historical local failed-profile archives unavailable")
    print(json.dumps(dict(passed=True, seal_sha256=sha(HERE / "final-audit.json"), metadata_receipts=8, local_failed_profiles_replayed=replayed,
                          unavailable_local_archives=unavailable, native_verification_passed=False, actual_native_function_sizes=None,
                          fresh_compilation_performed=False, target_execution=False, ISA_emulation=False)))


if __name__ == "__main__":
    main()
