"""Bounded ELF/IR/static def-use gates; no target executor or ISA emulation."""
import hashlib
import re
from elf32 import ELF, require

ENTRY = "tsl9_rebuild_interrupt_registers_9a42"
HELPERS = {"tsl9_rebuild_rcc_registers_"+s:int(s,16) for s in ("19124","19142","19160","1917e")}
OFFSETS = dict(zip(HELPERS,(0x18,0x1c,0x0c,0x10)))
SCRATCH = 0x30000
IMAGE_SHA = "0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667"
ADDRESSES = [0x4002101c,0x40021018,0x40021010,0x40021010,0x4002100c,0x4002100c]
MASKS = [0x02020006,0x101d,0x02020006,0x02020006,0x101d,0x101d]
REGISTERS = {"zero":0,"a0":10,"a1":11,"a4":14,"a5":15}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def destination(raw):
    word = int.from_bytes(raw,"little")
    if len(raw) == 4:
        opcode = word & 127
        if opcode in (3,0x13,0x33,0x37):
            return ((word>>7)&31) or None
        if opcode in (0x23,0x63):
            return None
        if opcode == 0x73 and ((word>>7)&31) == 0 and (word>>12)&7 in (2,3):
            return None
    elif len(raw) == 2:
        q,f = word&3,word>>13
        if q == 0 and f == 2:
            return 8+((word>>2)&7)
        if q == 0 and f == 6:
            return None
        if q == 1 and f in (0,2,3):
            return ((word>>7)&31) or None
        if q == 1 and f == 4:
            return 8+((word>>7)&7)
        if q == 1 and f in (6,7):
            return None
        if q == 2 and f == 4 and (word>>2)&31:
            return ((word>>7)&31) or None
        if word == 0x8082:
            return None
    raise ValueError("unsupported raw instruction destination: "+raw.hex())


def branch_target(raw,pc):
    word = int.from_bytes(raw,"little")
    require(len(raw) == 2 and word&3 == 1 and word>>13 == 6,"actual compressed BEQZ encoding")
    offset = ((word>>12)&1)*256+((word>>10)&3)*8+((word>>5)&3)*64+((word>>3)&3)*2+((word>>2)&1)*32
    if offset&256:
        offset -= 512
    require(8+((word>>7)&7) == 11,"raw branch tests A1")
    return pc+offset


def elf_gate(path,linked):
    elf = ELF(path)
    require(elf.kind == (2 if linked else 1) and elf.flags == 1,"actual RV32 ELF, RVC and soft-float ABI")
    arch = re.search(rb"rv32[a-z0-9_]+",elf.data(elf.byname[".riscv.attributes"]))
    require(arch is not None and arch.group().startswith(b"rv32i") and all(b"_"+a in arch.group() for a in (b"m",b"a",b"c",b"zicsr")) and not any(b"_"+a in arch.group() for a in (b"f",b"d",b"v")),"RV32IMAC_Zicsr integer-only ISA attributes")
    require(not any(s["index"] == 0 and s["name"] for s in elf.symbols),"no undefined symbols or native stubs")
    globals_ = [s for s in elf.symbols if s["index"] and s["name"] and s["info"]>>4 in (1,2)]
    functions = [s for s in elf.symbols if s["index"] and s["info"]&15 == 2 and s["size"]]
    require({s["name"] for s in globals_} == {ENTRY,*HELPERS} and {s["name"] for s in functions} == {ENTRY,*HELPERS},"exact five real functions; no aliases/hidden implementation")
    require(not any(s["size"] and s["flags"]&1 for s in elf.sections),"no writable allocations or BSS")
    allocations = [s for s in elf.sections if s["size"] and s["flags"]&2]
    executable = [s for s in allocations if s["flags"]&4]
    metadata = [s for s in allocations if not s["flags"]&4]
    require(sum(s["size"] for s in executable) == sum(s["size"] for s in functions),"all executable allocated bytes owned by the five functions")
    require(all(s["name"] == ".eh_frame" and s["flags"] == 2 and s["type"] == 1 and s["size"] == (124 if linked else 120) for s in metadata),"separately recorded exact read-only/non-executable C++ EH metadata obligation")
    require(not linked or all(elf.data(s)[-4:] == b"\0\0\0\0" for s in metadata),"linked C++ EH metadata includes actual four-byte terminator")
    if linked:
        require(not elf.relocations,"linked component has no residual relocations")
        require(all(s["value"] == (SCRATCH if s["name"] == ENTRY else HELPERS[s["name"]]) for s in functions),"diagnostic main VA and exact original helper VAs")
    return dict(kind=elf.kind,architecture=arch.group().decode(),sha256=digest(path.read_bytes()),symbols={s["name"]:dict(address=s["value"],bytes=s["size"],code_sha256=digest(elf.function_bytes(s))) for s in functions},undefined_symbols=[],writable_allocations=0,relocations=len(elf.relocations),
                executable_allocated_bytes=sum(s["size"] for s in executable),executable_byte_ownership_passed=True,
                total_allocated_bytes=sum(s["size"] for s in allocations),all_allocated_bytes_function_owned=not metadata,
                extra_readonly_allocations=[dict(name=s["name"],address=s["address"],bytes=s["size"],sha256=digest(elf.data(s))) for s in metadata],
                extra_readonly_storage_integration_proved=False if metadata else None)


def machine_gate(text,path,image):
    elf = ELF(path)
    require(len(image) == 76800 and digest(image) == IMAGE_SHA,"exact original image for helper byte comparison")
    facts = {}
    allowed = {"li","lui","addi","not","or","and","lw","sw","sb","beqz","ret","csrc","csrs"}
    nonwrite = {"sw","sb","beqz","ret","csrc","csrs"}
    for name in [*HELPERS,ENTRY]:
        symbols = [s for s in elf.symbols if s["name"] == name and s["index"] and s["info"]&15 == 2]
        require(len(symbols) == 1,"one actual function symbol")
        symbol = symbols[0]
        code = elf.function_bytes(symbol)
        marker = re.search(r"^([0-9a-f]+) <"+name+r">:\s*$",text,re.M)
        require(marker is not None and int(marker.group(1),16) == symbol["value"],"ELF-bound function start")
        rows,cursor = [],0
        for line in text[marker.end():].lstrip("\r\n").splitlines():
            if not line.strip():
                break
            m = re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*",line)
            require(m is not None,"no ignored unparsed/interior instruction lines")
            pc,raw = int(m.group(1),16),bytes.fromhex(m.group(2))
            require(pc == symbol["value"]+cursor and cursor+len(raw) <= len(code) and raw == code[cursor:cursor+len(raw)],"every contiguous raw instruction byte equals actual ELF")
            require(len(raw) in (2,4) and len(raw) == (4 if raw[0]&3 == 3 else 2),"complete instruction framing")
            op,operands = m.group(3),m.group(4)
            require(op in allowed and not re.search(r"\b(?:sp|gp|tp|t[0-6]|a[236789]|s(?:[0-9]|10|11)|ra)\b",operands),"no SP/GP/T0/A2/A3/other reserved operand or hidden call")
            rd = destination(raw)
            displayed = None if op in nonwrite else REGISTERS.get(operands.split(",")[0])
            require(rd == displayed and rd in (None,10,11,14,15),"independent raw RD equals permitted displayed destination")
            require(name == ENTRY or rd != 11,"standalone helper has zero encoded A1 writes")
            rows.append(dict(address=pc,offset=cursor,bytes=raw.hex(),mnemonic=op,operands=operands,encoded_rd=rd))
            cursor += len(raw)
        require(cursor == len(code),"complete ELF function extent, including instructions after interior RET")
        graph = {r["address"]:[] for r in rows}
        for i,row in enumerate(rows):
            if row["mnemonic"] == "beqz":
                target = re.search(r", 0x([0-9a-f]+)",row["operands"])
                require(target is not None,"displayed branch target")
                target = int(target.group(1),16)
                require(target == branch_target(bytes.fromhex(row["bytes"]),row["address"]) and target in graph,"raw branch target equals displayed internal boundary")
                graph[row["address"]].append(target)
            if row["mnemonic"] != "ret":
                require(i+1<len(rows),"no implicit function escape")
                graph[row["address"]].append(rows[i+1]["address"])
        reached,pending = set(),[rows[0]["address"]]
        while pending:
            node = pending.pop()
            if node not in reached:
                reached.add(node);pending.extend(graph[node])
        require(reached == set(graph),"all instructions structurally reachable, including both helper returns")
        require(all(child>node for node,children in graph.items() for child in children),"finite acyclic direct CFG, no calls/hidden loops")
        if name in HELPERS:
            address = HELPERS[name]
            require(len(code) == 30 and code == image[address-0x8000:address-0x8000+30],"all30 helper bytes equal original BIN at exact original VA")
        else:
            require(not any(r["mnemonic"] == "beqz" for r in rows) and rows[-1]["mnemonic"] == "ret","initializer straight-line through single final RET")
        facts[name] = dict(bytes=len(code),instruction_rows=len(rows),code_sha256=digest(code),rows=rows,CFG=graph,
                           all_ELF_bytes_covered=True,every_raw_RD_checked=True,encoded_written_registers=sorted({r["encoded_rd"] for r in rows if r["encoded_rd"]}),
                           helper_original_byte_equality=name in HELPERS,helper_A1_writes=0 if name in HELPERS else None,SP_accesses=0,GP_writes=0,T0_writes=0,A2_A3_writes=0,hidden_calls=0)
    return facts


def canonical(op,left,right):
    if isinstance(left,int) and isinstance(right,int):
        return {"or":lambda:left|right,"and":lambda:left&right,"xor":lambda:left^right}[op]()&0xffffffff
    if isinstance(left,int):
        left,right = right,left
    return (op,left,right)


def expected_effects():
    expected = [dict(kind="csrc",csr=0x800,mask=136)]
    afters = []
    for i,(target,mask) in enumerate(zip(ADDRESSES,MASKS)):
        enabled = i in (0,1,2,4)
        fresh = ("fresh_read",i,target)
        after = ("or" if enabled else "and",fresh,mask if enabled else (~mask)&0xffffffff)
        expected += [dict(kind="read",width=32,address=target,identity=i),dict(kind="write",width=32,address=target,value=after)]
        afters.append(after)
    for target,width,value in [(0xe000e42d,8,0),(0xe000e104,32,0x2000),(0xe000e424,8,0x20),(0xe000e104,32,0x10),(0xe000e427,8,0x30),(0xe000e104,32,0x80)]:
        expected.append(dict(kind="write",width=width,address=target,value=value))
    expected.append(dict(kind="csrs",csr=0x800,mask=136))
    return expected,afters


def main_static_def_use(facts):
    """Straight-line definition identities only; no PC, guest memory or CSR state."""
    defs = {"zero":0}
    effects,loads = [],0
    for row in facts[ENTRY]["rows"]:
        op = row["mnemonic"]
        p = [v.strip() for v in row["operands"].split(",")]
        if op == "li":
            defs[p[0]] = int(p[1],0)&0xffffffff
        elif op == "lui":
            defs[p[0]] = (int(p[1],0)<<12)&0xffffffff
        elif op == "addi":
            require(isinstance(defs.get(p[1]),int),"constant ADDI source")
            defs[p[0]] = (defs[p[1]]+int(p[2],0))&0xffffffff
        elif op == "not":
            require(isinstance(defs.get(p[1]),int),"literal mask NOT only")
            defs[p[0]] = (~defs[p[1]])&0xffffffff
        elif op in ("or","and"):
            require(p[1] in defs and p[2] in defs,"defined RMW operands")
            defs[p[0]] = canonical(op,defs[p[1]],defs[p[2]])
        elif op in ("lw","sw","sb"):
            m = re.fullmatch(r"(-?(?:0x[0-9a-f]+|\d+))\(([a-z][a-z0-9]*)\)",p[1])
            require(m is not None and isinstance(defs.get(m.group(2)),int),"constant MMIO effective-address definition")
            target = (defs[m.group(2)]+int(m.group(1),0))&0xffffffff
            if op == "lw":
                defs[p[0]] = ("fresh_read",loads,target)
                effects.append(dict(kind="read",width=32,address=target,identity=loads));loads += 1
            else:
                require(p[0] in defs,"defined MMIO write value")
                effects.append(dict(kind="write",width=32 if op == "sw" else 8,address=target,value=defs[p[0]]))
        elif op in ("csrc","csrs"):
            word = int.from_bytes(bytes.fromhex(row["bytes"]),"little")
            require(word>>20 == 0x800 and (word>>12)&7 == (3 if op == "csrc" else 2) and (word>>7)&31 == 0 and (word>>15)&31 == REGISTERS[p[1]],"raw CSR800 discard-oldvalue encoding and source")
            require(int(p[0],0) == 0x800 and defs.get(p[1]) == 136,"actual CSR800 literal mask136")
            effects.append(dict(kind=op,csr=0x800,mask=136))
        elif op != "ret":
            raise ValueError("unsupported static initializer dataflow: "+op)
    wanted,afters = expected_effects()
    require(effects == wanted and loads == 6,"actual machine20effect order/width/address/freshness/masks")
    require([defs.get(r) for r in ("a0","a1","a4","a5")] == [afters[-1],0,128,0xe000e000],"exact final normal A0/A1/A4/A5 definitions")
    return dict(effects=effects,normal_outputs={r:defs[r] for r in ("a0","a1","a4","a5")},static_def_use_only=True,
                guest_memory_created=False,CSR_state_created=False,PC_execution=False,interrupt_semantics_proved=False)


def ir_function(text,name):
    found = re.search(r"^define\b[^\n]*@"+name+r"\([^\n]*\).*?\n\}",text,re.M|re.S)
    require(found is not None,"actual function IR: "+name)
    return found.group()


def ir_gate(path):
    """SSA identities through this finite set of transparent native primitives."""
    text = path.read_text(encoding="utf-8")
    require('target triple = "riscv32-unknown-unknown-elf"' in text and not re.search(r"\balloca\b",text),"actual RV32 IR without stack objects")
    body = ir_function(text,ENTRY)
    definitions,effects,commits = {},[],[]
    def value(token):
        token = token.strip()
        if re.fullmatch(r"-?\d+",token):
            return int(token)&0xffffffff
        require(token in definitions,"defined SSA operand: "+token)
        return definitions[token]
    def pointer(token):
        constant = re.fullmatch(r"inttoptr \(i32 (-?\d+) to ptr\)",token)
        result = int(constant.group(1))&0xffffffff if constant else value(token)
        require(isinstance(result,int),"static constant SSA effective address")
        return result
    loads,return_value = 0,None
    for line in body.splitlines()[1:-1]:
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        asm = re.match(r'(%[-\w.]+) = (?:tail )?call (?:noundef )?i32 asm sideeffect "([^"]*)", "([^"]*)"\((.*?)\)',line)
        if asm:
            result,template,constraints,arguments = asm.groups()
            args = [value(x) for x in re.findall(r"i32 (%[-\w.]+|-?\d+)",arguments)]
            require("~{memory}" in constraints,"native primitive compiler memory clobber")
            if template == "lui $0, 0x40021":
                require(constraints in ("={x14},~{memory}","={x15},~{memory}") and not args,"exact base primitive")
                definitions[result] = 0x40021000
            elif template == "li $0, $1":
                require(constraints == "={x10},i,~{memory}" and len(args) == 1 and isinstance(args[0],int),"exact immediate A0 literal primitive")
                definitions[result] = args[0]
            elif template in (r"li $0, $1\0A\09csrc 0x800, $0",r"li $0, $1\0A\09csrs 0x800, $0"):
                require(constraints == "={x14},i,~{memory}" and args == [136],"exact CSR800 A4 literal136 primitive")
                definitions[result] = 136
                effects.append(dict(kind="csrc" if "csrc" in template else "csrs",csr=0x800,mask=136))
            elif not template and constraints == "={x10},{x10},~{memory}":
                require(len(args) == 1,"A0 identity read/write primitive")
                definitions[result] = args[0]
            elif not template and constraints == "={x10},{x11},{x14},{x15},{x10},~{memory}":
                require(len(args) == 4,"exact four-register returning commitment")
                commits.append(dict(after_effect=len(effects),registers=[args[3],args[0],args[1],args[2]]))
                definitions[result] = args[3]
            else:
                raise ValueError("unsupported or altered native primitive: "+template+" / "+constraints)
            continue
        arithmetic = re.match(r"(%[-\w.]+) = (add|or|and|xor) i32 ([^,]+), ([^,]+?)(?:,|$)",line)
        if arithmetic:
            result,op,left,right = arithmetic.groups()
            left,right = value(left),value(right)
            if op == "add":
                require(isinstance(left,int) and isinstance(right,int),"constant base-plus-offset SSA")
                definitions[result] = (left+right)&0xffffffff
            else:
                definitions[result] = canonical(op,left,right)
            continue
        cast = re.match(r"(%[-\w.]+) = inttoptr i32 (%[-\w.]+) to ptr",line)
        if cast:
            definitions[cast.group(1)] = value(cast.group(2));continue
        load = re.match(r"(%[-\w.]+) = load volatile i(\d+), ptr (.+?), align",line)
        if load:
            result,width,ptr = load.groups()
            target = pointer(ptr)
            require(int(width) == 32,"fresh RCC reads exactly32bits")
            definitions[result] = ("fresh_read",loads,target)
            effects.append(dict(kind="read",width=32,address=target,identity=loads));loads += 1
            continue
        store = re.match(r"store volatile i(\d+) ([^,]+), ptr (.+?), align",line)
        if store:
            width,val,ptr = store.groups()
            effects.append(dict(kind="write",width=int(width),address=pointer(ptr),value=value(val)));continue
        returned = re.fullmatch(r"ret i32 (%[-\w.]+)",line)
        if returned:
            return_value = value(returned.group(1));continue
        raise ValueError("unaccounted initializer LLVM IR instruction: "+line)
    expected,afters = expected_effects()
    require(effects == expected and loads == 6,"IR20effect order/address/width/mask and six distinct fresh loads")
    wanted = []
    for i,after in enumerate(afters):
        enabled = i in (0,1,2,4)
        before = ("fresh_read",i,ADDRESSES[i])
        wanted.append(dict(after_effect=3+2*i,registers=[after,int(enabled),0x40021000 if enabled else before,before if enabled else 0x40021000]))
    wanted.append(dict(after_effect=20,registers=[afters[-1],0,128,0xe000e000]))
    require(commits == wanted and return_value == afters[-1],"seven exact ordered normal-register commitments and returned final fresh RMW")
    helpers = {}
    for name,offset in OFFSETS.items():
        h = ir_function(text,name)
        require("select " not in h and "icmp eq i32 %1, 0" in h,"helper full32bit A1 predicate before branch-owned work")
        require(h.count("load volatile i32") == h.count("store volatile i32") == 2 and h.count('"lui $0, 0x40021"') == 2,"two separate branch-owned fresh32bit RMW sites/bases")
        require(h.count('"={x10},{x10},~{memory}"') == 2 and h.count('"={x10},{x11},{x14},{x15},{x10},~{memory}"') == 2,"two branch masks and returning commitments")
        require(h.count("add i32") == 2 and len(re.findall(r"add i32 %[-\w.]+, "+str(offset)+r"\b",h)) == 2,"both branch-specific register offsets")
        require(not any(re.search(r"\b(?:call|invoke)\b",line) and "asm sideeffect" not in line for line in h.splitlines()),"helper no runtime calls")
        helpers[name] = dict(branch_owned_RMW_sites=2,full_A1_zero_test=True,offset=offset,structural_IR_only=True)
    return dict(effects=effects,commitments=commits,final_return=return_value,helpers=helpers,all_initializer_IR_instructions_accounted=True,static_SSA_identities_only=True,target_execution=False,ISA_emulation=False)
