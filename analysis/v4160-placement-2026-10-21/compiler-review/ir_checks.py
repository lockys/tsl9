"""Bounded LLVM IR source-to-register commitments, no machine execution."""
import re

ENTRY = "tsl9_rebuild_interrupt_registers_9a42"
HELPERS = {"tsl9_rebuild_rcc_registers_19124": 0x40021018, "tsl9_rebuild_rcc_registers_19142": 0x4002101c,
           "tsl9_rebuild_rcc_registers_19160": 0x4002100c, "tsl9_rebuild_rcc_registers_1917e": 0x40021010}
BASE = 0x40021000
MASKS = [0x02020006, 0x101d, 0x02020006, 0x02020006, 0x101d, 0x101d]
ADDRESSES = [0x4002101c, 0x40021018, 0x40021010, 0x40021010, 0x4002100c, 0x4002100c]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def body(text, name):
    found = re.search(r"^define\b[^\n]*@" + name + r"\([^\n]*\).*?\n\}", text, re.M | re.S)
    require(found is not None, "actual function LLVM IR: " + name)
    return found.group()


def address(line):
    found = re.search(r"inttoptr \(i32 (-?\d+) to ptr\)", line)
    require(found is not None, "constant explicit volatile address")
    return int(found.group(1)) & 0xffffffff


def normalize(value):
    return int(value) & 0xffffffff if re.fullmatch(r"-?\d+", value) else value


def commit(line):
    found = re.search(r'asm sideeffect "", "([^"\n]+)"\((.*?)\)', line)
    require(found is not None and found.group(1) == "{x10},{x11},{x14},{x15},~{memory}", "exact fixed A0/A1/A4/A5 input-only commitment")
    values = re.findall(r"i32 (%[-\w.]+|-?\d+)", found.group(2))
    require(len(values) == 4, "four explicit register values")
    return [normalize(value) for value in values]


def gate(path):
    text = path.read_text(encoding="utf-8")
    require('target triple = "riscv32-unknown-unknown-elf"' in text, "actual RV32 ELF IR")
    init = body(text, ENTRY)
    effects, commitments = [], []
    for line in init.splitlines():
        if 'asm sideeffect ""' in line:
            commitments.append(dict(after_effect=len(effects), registers=commit(line)))
        elif "asm sideeffect" in line:
            csr = re.search(r'"(csrc|csrs) 0x800, \$0".*\(i32 136\)', line)
            require(csr is not None and "~{memory}" in line, "CSR800 mask136 and memory clobber")
            effects.append(dict(kind=csr.group(1), csr=0x800, mask=136))
        elif "load volatile" in line:
            load = re.search(r"(%[-\w.]+) = load volatile i(\d+)", line)
            require(load is not None, "volatile read width")
            effects.append(dict(kind="read", width=int(load.group(2)), address=address(line), result=load.group(1)))
        elif "store volatile" in line:
            store = re.search(r"store volatile i(\d+) ([^,]+),", line)
            require(store is not None, "volatile write width")
            effects.append(dict(kind="write", width=int(store.group(1)), address=address(line), value=normalize(store.group(2))))
        if re.search(r"\b(?:call|invoke)\b", line):
            require("asm sideeffect" in line, "no initializer hidden helper or library calls")
    expected = [dict(kind="csrc", csr=0x800, mask=136)]
    for target in ADDRESSES:
        expected.extend([dict(kind="read", width=32, address=target), dict(kind="write", width=32, address=target)])
    for target, width, value in [(0xe000e42d, 8, 0), (0xe000e104, 32, 0x2000), (0xe000e424, 8, 0x20), (0xe000e104, 32, 0x10), (0xe000e427, 8, 0x30), (0xe000e104, 32, 0x80)]:
        expected.append(dict(kind="write", width=width, address=target, value=value))
    expected.append(dict(kind="csrs", csr=0x800, mask=136))
    require(len(effects) == len(expected) == 20, "exact initializer20effects")
    for actual, wanted in zip(effects, expected):
        require(all(actual.get(key) == value for key, value in wanted.items()), "initializer effect order/address/width/value")
    wanted_commitments = []
    for i, mask in enumerate(MASKS):
        read, write = effects[1 + 2*i], effects[2 + 2*i]
        enabled = i in (0, 1, 2, 4)
        op, operand = ("or", mask) if enabled else ("and", (~mask) & 0xffffffff)
        expression = re.search(r"^\s*" + re.escape(write["value"]) + r" = " + op + r" i32 " + re.escape(read["result"]) + r", (-?\d+)\s*$", init, re.M)
        require(expression is not None and normalize(expression.group(1)) == operand, "fresh read RMW exact mask")
        wanted_commitments.append(dict(after_effect=3 + 2*i, registers=[write["value"], int(enabled), BASE if enabled else read["result"], read["result"] if enabled else BASE]))
    final = effects[12]["value"]
    wanted_commitments.append(dict(after_effect=20, registers=[final, 0, 128, 0xe000e000]))
    require(commitments == wanted_commitments, "seven exact ordered full-register commitments")
    require(re.search(r"\bret i32 " + re.escape(final) + r"\s*$", init, re.M) is not None, "return actual final fresh RMW")
    require(not re.search(r"\b(?:br|switch|invoke)\b", init), "initializer straight-line IR")
    helper_facts = {}
    for name, target in HELPERS.items():
        h = body(text, name)
        volatile = [line for line in h.splitlines() if "volatile" in line]
        require(len(volatile) == 2 and "load volatile i32" in volatile[0] and "store volatile i32" in volatile[1] and all(address(line) == target for line in volatile), "helper one fresh32bitRMW at exact address")
        args = re.search(r"@" + name + r"\(i32[^%]*(%[-\w.]+), i32[^%]*(%[-\w.]+)\)", h)
        require(args is not None, "two32bit helper arguments")
        mask, enabled = args.groups()
        loaded = re.search(r"(%[-\w.]+) = load volatile i32", volatile[0]).group(1)
        predicate = re.search(r"(%[-\w.]+) = icmp eq i32 " + re.escape(enabled) + r", 0", h)
        or_value = re.search(r"(%[-\w.]+) = or i32 " + re.escape(loaded) + r", " + re.escape(mask), h)
        complement = re.search(r"(%[-\w.]+) = xor i32 " + re.escape(mask) + r", -1", h)
        require(predicate is not None and or_value is not None and complement is not None, "full enabled-zero predicate/OR/complement")
        and_value = re.search(r"(%[-\w.]+) = and i32 " + re.escape(loaded) + r", " + re.escape(complement.group(1)), h)
        require(and_value is not None, "AND_NOT of fresh read")
        selected = re.search(r"(%[-\w.]+) = select i1 " + re.escape(predicate.group(1)) + r", i32 " + re.escape(and_value.group(1)) + r", i32 " + re.escape(or_value.group(1)), h)
        require(selected is not None and "store volatile i32 " + selected.group(1) + "," in volatile[1], "store same fullflag-selected RMW")
        commits = [commit(line) for line in h.splitlines() if 'asm sideeffect ""' in line]
        require(commits == [[or_value.group(1), enabled, BASE, loaded], [and_value.group(1), 0, loaded, BASE]], "helper true and false exact A0/A1/A4/A5 commitments")
        require(re.search(r"ret i32 " + re.escape(selected.group(1)) + r"\s*$", h, re.M) is not None, "helper returns selected stored result")
        require(not any(re.search(r"\b(?:call|invoke)\b", line) and "asm sideeffect" not in line for line in h.splitlines()), "no helper hidden calls")
        helper_facts[name] = dict(address=target, volatile_effects=2, commits=commits, exact_nonzero_A1_value_retained=True, returned_value=selected.group(1))
    return dict(passed=True, initializer_effects=effects, initializer_commitments=commitments, helpers=helper_facts,
                native_machine_allocation_proved=False, native_instructions_inspected=False, RV32_executed=False)


def transcript_controls(path):
    text = path.read_text(encoding="utf-8")
    init = body(text, ENTRY)
    commits = [line for line in init.splitlines(keepends=True) if 'asm sideeffect ""' in line]
    require(len(commits) == 7, "actual initializer commitment control sites")
    final_return = re.search(r"^  ret i32 (%[-\w.]+)$", init, re.M)
    require(final_return is not None, "actual final return control site")
    variants = {
        "wrong_CSR_mask": text.replace('"r,~{memory}"(i32 136)', '"r,~{memory}"(i32 137)', 1),
        "wrong_PFIC_width": text.replace("store volatile i8 0,", "store volatile i16 0,", 1),
        "wrong_register_constraint": text.replace("{x10},{x11},{x14},{x15},~{memory}", "{x10},{x12},{x14},{x15},~{memory}", 1),
        "wrong_fresh_RMW_mask": text.replace("or i32 %1, 33685510", "or i32 %1, 33685511", 1),
        "missing_commitment": text.replace(commits[0], "", 1),
        "wrong_final_return": text.replace(init, init.replace(final_return.group(), "  ret i32 0"), 1),
    }
    class TextOnly:
        def __init__(self, content):
            self.content = content
        def read_text(self, **unused):
            return self.content
    controls = []
    for name, changed in variants.items():
        require(changed != text, "actual IR mutation: " + name)
        try:
            gate(TextOnly(changed))
        except ValueError as error:
            controls.append(dict(case=name, rejected=True, reason=str(error)))
        else:
            raise ValueError("modified IR admitted: " + name)
    return controls
