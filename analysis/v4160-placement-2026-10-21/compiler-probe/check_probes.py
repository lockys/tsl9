"""Read-only check of selected -Oz metadata and available local static artifacts."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", type=Path, default=HERE.parents[2])
    p.add_argument("--require-local-builds", action="store_true")
    a = p.parse_args()
    root = a.project_root.resolve()
    seal = json.loads((HERE / "final-audit.json").read_text(encoding="utf-8"))
    for name, pin in seal["members"].items():
        require(sha(HERE / name) == pin, "sealed member changed: " + name)
    index = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    native = module(HERE / "probe_oz.py", "oz_source_pins")
    clock = module(HERE / "probe_clock_oz.py", "clock_oz_source_pins")
    thunk = module(HERE / "probe_thunks.py", "thunk_static_decode")
    for directory, pins in ((root / native.DEPENDENCY, native.PINS), (root / clock.DEPENDENCY, {"verify_compiler.py": clock.VERIFIER, "elf32.py": clock.PARSER})):
        for name, pin in pins.items():
            require(sha(directory / name) == pin, "immutable static gate dependency changed")
    for name, pin in native.SOURCE_PINS.items():
        require(sha(root / "experiments/tsl9-v4160-reset-memory/src" / name) == pin, "current reset source changed")
    for name, pin in clock.SOURCES.items():
        require(sha(root / "experiments/tsl9-v4160-clock-registers/src" / name) == pin, "current clock source changed")
    reset_gate = module(root / native.DEPENDENCY / "verify_native.py", "oz_reset_static_gates")
    clock_gate = module(root / clock.DEPENDENCY / "verify_compiler.py", "oz_clock_static_gates")
    parser, _ = clock_gate.elf_parser(root)
    checked, missing = [], []
    for item in index["results"]:
        receipt = HERE / item["metadata"]
        require(sha(receipt) == item["sha256"], "byte-identical selected receipt")
        r = json.loads(receipt.read_text(encoding="utf-8"))
        require(r["passed"], "selected static result passed")
        folder = HERE / item["artifact_dir"]
        if not folder.is_dir():
            missing.append(item["artifact_dir"])
            continue
        require(sha(folder / "verification.json") == item["sha256"], "original local receipt equals selected metadata")
        if item["kind"] == "reset":
            require(r["flags"].count("-Oz") == 1 and "-Os" not in r["flags"], "only requested alternative optimization")
            linked = folder / ("ADDRESS-WITNESS-ONLY.elf" if r["fragment"] else "COMPONENT-ONLY-NOT-FIRMWARE.elf")
            text = (folder / "disassembly.log").read_text(encoding="utf-8")
            require(reset_gate.elf_gate(folder / "reset_memory.o", r["fragment"]) == r["object"], "actual reset object replay")
            require(reset_gate.elf_gate(linked, r["fragment"], True) == r["linked_component"], "actual reset linked ELF replay")
            require(sha(folder / "reset_memory.ll") == r["LLVM_IR_sha256"] and reset_gate.ir_gate(folder / "reset_memory.ll") == r["LLVM_IR"], "actual reset IR replay")
            require(reset_gate.machine_gate(text, linked, r["fragment"]) == r["machine"], "full actual reset bytes/RD/loop CFG replay")
            require(reset_gate.transcript_controls(text, linked, r["fragment"]) == r["transcript_controls"], "reset transcript controls replay")
            for control in r["actual_compiled_controls"]:
                case = folder / ("negative-" + control["case"])
                target = case / "COMPILED-NEGATIVE-NOT-FIRMWARE.elf"
                require(sha(case / "reset_memory.c") == control["source_sha256"] and sha(case / "reset_memory.o") == control["object_sha256"] and sha(case / "reset_memory.ll") == control["LLVM_IR_sha256"] and sha(target) == control["linked_sha256"], "actual compiled reset control pins")
                try:
                    reset_gate.ir_gate(case / "reset_memory.ll")
                    reset_gate.machine_gate((case / "disassembly.log").read_text(encoding="utf-8"), target, r["fragment"])
                except ValueError:
                    pass
                else:
                    raise ValueError("actual compiled reset control admitted")
        elif item["kind"] == "clock":
            require(all("-Oz" in c["argv"] and "-Os" not in c["argv"] for c in r["commands"] if "-c" in c["argv"]), "actual clock Oz commands")
            linked = folder / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
            require(sha(linked) == r["linked_component_sha256"], "actual clock ELF pin")
            for name, pin in r["objects"].items():
                require(sha(folder / name) == pin, "actual clock object pin")
            for name, pin in r["LLVM_IR"].items():
                require(sha(folder / (name + ".ll")) == pin, "actual clock IR artifact pin")
            text = (folder / "disassembly.log").read_text(encoding="utf-8")
            require(clock_gate.machine_gate(text, linked, parser) == r["functions"], "actual clock full bytes/RD/CFG/output-pattern replay")
            require(clock_gate.transcript_controls(text, linked, parser) == r["transcript_controls"], "clock transcript controls replay")
            for control in r["actual_compiled_controls"]:
                case = folder / ("negative-" + control["case"])
                target = case / "COMPILED-NEGATIVE-NOT-FIRMWARE.elf"
                require(sha(target) == control["linked_component_sha256"] and sha(case / control["changed_source"]) == control["source_sha256"], "actual compiled clock control pins")
                try:
                    clock_gate.machine_gate((case / "disassembly.log").read_text(encoding="utf-8"), target, parser)
                except ValueError:
                    pass
                else:
                    raise ValueError("actual compiled clock control admitted")
        else:
            require(item["kind"] == "thunk", "known result kind")
            for witness in r["witnesses"]:
                case = folder / witness["case"]
                target = case / "NUMERIC-WIDTH-WITNESS-ONLY.elf"
                require(sha(case / "thunk.s") == witness["source_sha256"] and sha(case / "thunk.o") == witness["object_sha256"] and sha(target) == witness["ELF_sha256"], "actual synthetic thunk artifact pins")
                elf = parser(target)
                symbol = next(s for s in elf.symbols if s["name"] == "probe_entry")
                raw = elf.function_bytes(symbol)
                require(raw.hex() == witness["raw_bytes"] and thunk.jump(raw, symbol["value"]) == witness["decoded"], "actual jump-width/raw-immediate replay")
        checked.append(item["metadata"])
    require(len(index["results"]) == 7, "four reset + two clock + one thunk selected receipts")
    require(not a.require_local_builds or not missing, "requested local historical artifact archives unavailable")
    print(json.dumps(dict(passed=True, seal_sha256=sha(HERE / "final-audit.json"), metadata_receipts=7, local_artifacts_replayed=checked, unavailable_local_archives=missing, fresh_compilation_performed=False, original_fixed_placement_proved=False, RV32_executed=False)))


if __name__ == "__main__":
    main()
