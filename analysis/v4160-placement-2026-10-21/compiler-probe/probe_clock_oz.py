"""Compile only the frozen clock register model at -Oz, with pinned static gates."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import uuid

HERE = Path(__file__).resolve().parent
DEPENDENCY = Path("apk-analysis/tsl9-v4160-clock-abi-2026-10-21/compiler-review")
VERIFIER = "4095d8dfa936b81b7380da627570afa10b50d08789eba8f5aa15859991ae9885"
PARSER = "00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141"
SOURCES = {"clock_fields.c": "416e0990c9ed3a142953af97ea6496bf269311f003dfec1046ab32308afd8701", "clock_io.h": "fd2d1bb3c780daf698c93db536ca5f2229e20553dc5543646c0667bab839e36f", "clock_query.c": "dcaa19f44760e16e022e73aa86fbcc3b0638c6ca1410a1fb03087366fa8eebc8", "clock_registers.h": "c52596a6f9943912122d845e61ed5ea4298d2a205f3bdd614de96ef2e3b17552"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", type=Path, default=HERE.parents[2])
    p.add_argument("--tool-dir", type=Path, required=True)
    p.add_argument("--language", choices=("c", "cpp", "both"), default="both")
    a = p.parse_args()
    root = a.project_root.resolve()
    dep = root / DEPENDENCY
    if sha(dep / "verify_compiler.py") != VERIFIER or sha(dep / "elf32.py") != PARSER:
        raise ValueError("immutable clock verifier dependency changed")
    spec = importlib.util.spec_from_file_location("pinned_clock_native", dep / "verify_compiler.py")
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    parser, _ = v.elf_parser(root)
    source = root / "experiments/tsl9-v4160-clock-registers/src"
    v.require({name: sha(source / name) for name in SOURCES} == SOURCES, "frozen clock four-source pins")
    tools = {key: v.executable(None, a.tool_dir, name) for key, name in (("clang", "clang"), ("linker", "ld.lld"), ("objdump", "llvm-objdump"))}
    tool_pins = {name: sha(path) for name, path in tools.items()}
    original_run = v.run
    def oz_run(argv, folder, label):
        return original_run(["-Oz" if arg == "-Os" else arg for arg in argv], folder, label)
    # Only optimization changes; original compile_unit reservations remain exact.
    v.run = oz_run
    results = []
    for mode in (("c", "cpp") if a.language == "both" else (a.language,)):
        folder = HERE / "build" / ("clock-oz-" + uuid.uuid4().hex + "-" + mode)
        folder.mkdir(parents=True)
        commands, objects = [], []
        for unit in ("clock_query", "clock_fields"):
            record, obj = v.compile_unit(tools, source, folder, unit, mode)
            v.require("-Oz" in record["argv"] and "-Os" not in record["argv"], "actual Oz command")
            commands.append(record)
            objects.append(obj)
            record, _ = v.run([*record["argv"][:-4], "-S", "-emit-llvm", source / (unit + ".c"), "-o", folder / (unit + ".ll")], folder, "llvm-ir-" + unit)
            commands.append(record)
        linked = folder / "COMPONENT-ONLY-NOT-FIRMWARE.elf"
        record, _ = v.run([tools["linker"], "--no-relax", "--no-undefined", "--entry=" + v.QUERY, "-Ttext=0x1000", *objects, "-o", linked], folder, "link")
        commands.append(record)
        record, disassembly = v.run([tools["objdump"], "--disassemble", linked], folder, "disassembly")
        commands.append(record)
        checked = v.machine_gate(disassembly, linked, parser)
        receipt = dict(schema="TSL9-clock-register-bounded-Oz-static-probe-v1", passed=True, mode=mode,
                       source_sha256=SOURCES, runner_sha256=sha(Path(__file__)), immutable_dependencies={"verify_compiler.py": VERIFIER, "elf32.py": PARSER},
                       tools={name: dict(path=str(path), sha256=tool_pins[name]) for name, path in tools.items()}, commands=commands,
                       objects={path.name: sha(path) for path in objects}, LLVM_IR={unit: sha(folder / (unit + ".ll")) for unit in ("clock_query", "clock_fields")},
                       linked_component_sha256=sha(linked), functions=checked,
                       transcript_controls=v.transcript_controls(disassembly, linked, parser), actual_compiled_controls=v.compiled_controls(source, folder, tools, mode, parser),
                       original_fixed_placement_proved=False, full_original_ABI_proved=False, pointwise_register_semantics_proved=False,
                       firmware_executed=False, ISA_emulation=False, network=False, hardware=False, OTA_ready=False)
        v.require({name: sha(source / name) for name in SOURCES} == SOURCES, "clock source pins unchanged")
        v.require({name: sha(path) for name, path in tools.items()} == tool_pins, "LLVM tools unchanged")
        path = folder / "verification.json"
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        results.append(dict(mode=mode, receipt=str(path), sha256=sha(path), functions={name: {key: value for key, value in details.items() if key not in ("rows", "direct_CFG_edges")} for name, details in checked.items()}))
    print(json.dumps(dict(passed=True, results=results)))


if __name__ == "__main__":
    main()
