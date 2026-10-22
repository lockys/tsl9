"""Fresh callframe component compilation and bounded raw-byte proof; no execution."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import sys
import uuid

HERE = Path(__file__).resolve().parent
ENTRY = "tsl9_rebuild_interrupt_registers_9a42"
HELPERS = {"tsl9_rebuild_rcc_registers_"+s:int(s,16) for s in ("19124","19142","19160","1917e")}
SOURCE_PINS = {
 "experiments/tsl9-v4160-irq-callframe/src/interrupt_callframe.c":"350298243ab9bf60abdc058c47721a8a8b575e13c314f6340ffbdee338e35e83",
 "experiments/tsl9-v4160-irq-callframe/src/callframe_io.h":"c8ab6f87e64e518e6dddb46d36a57633eb04af9b4e2917e99e1597973826b3c7",
 "experiments/tsl9-v4160-irq-callframe/src/rcc_helpers.c":"7fd1b2e15b6c0b100faed8e3af7c3ab79d049dc6c23f32433bfad8eee0c6b45a",
 "experiments/tsl9-v4160-irq-native/src/native_io.h":"f98eda2e291d585b086f5e65cd4d8816855e7819350f7b93dd6002bb430a3d2e",
 "experiments/tsl9-v4160-interrupt-registers/src/interrupt_registers.h":"da57cec48aa144786cd9a64c8d20aadd2bb02d9e91d43408eac6441f7ba3ae59"}
NATIVE_PINS = {"verify_native.py":"58e726bf5590eeb318c7123a75fd00c5b406b58e36c545c65962a1ac80a369ac","gates.py":"c51f2242a3f3356ce77c09c12757cda0ed13b6830ac255cbfbd4fcdfd36341e5","elf32.py":"00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141"}
NATIVE_SEAL = "273617ca292a9ee2f2962ef14d72214903068bcaaabb338148938dcf63c505a2"
PLAN_SEAL = "85843df867c68c84572efb2f4630bb199ced6c752960fee8d9128d2f4eceb934"
SOURCE_SEAL = "4d6745033aae496576b9db2fb7467396fbfda5067713cf1451a34b949b414283"
REG = {"zero":0,"ra":1,"sp":2,"s0":8,"s1":9,"a0":10,"a1":11,"a2":12,"a3":13,"a4":14,"a5":15,"s2":18}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def require(v,m):
    if not v:raise ValueError(m)
def normal(v):return json.loads(json.dumps(v))
def case(root,slug):
    for path in (root/"apk-analysis"/("tsl9-"+slug),root/"analysis"/slug):
        if path.is_dir():return path
    raise ValueError("missing source case: "+slug)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def load_context(root):
    previous=case(root,"v4160-irq-native-2026-10-21")/"compiler-review"
    require(sha(previous/"final-audit.json")==NATIVE_SEAL,"immutable native compiler baseline seal")
    for name,pin in NATIVE_PINS.items():require(sha(previous/name)==pin,"pinned prior tool/parser source")
    sys.path.insert(0,str(previous));V=module("pinned_callframe_tools",previous/"verify_native.py")
    require(all(Path(sys.modules[n].__file__).resolve()==(previous/(n+".py")).resolve() for n in ("gates","elf32")),"loaded pinned dependency paths")
    source=case(root,"v4160-interrupt-init-2026-10-21")/"source"
    require(sha(source/"final-audit.json")==SOURCE_SEAL,"original264byte94instruction seal")
    for f in json.loads((source/"final-audit.json").read_text(encoding="utf-8"))["files"]:require(sha(source/f["path"])==f["sha256"],"original source seal member")
    plan_dir=case(root,"v4160-irq-callframe-2026-10-21")/"source-plan"
    require(sha(plan_dir/"seal.json")==PLAN_SEAL,"original callframe plan seal")
    for f in json.loads((plan_dir/"seal.json").read_text(encoding="utf-8"))["files"]:require(sha(plan_dir/f["path"])==f["sha256"],"source-plan seal member")
    plan=json.loads((plan_dir/"verification.json").read_text(encoding="utf-8"))
    D=module("pinned_callframe_raw_decoder",source/"inspect-source.py")
    return dict(V=V,D=D,ELF=sys.modules["elf32"].ELF,plan=plan,
                dependency_pins=dict(native_seal=NATIVE_SEAL,native_members=NATIVE_PINS,original_source_seal=SOURCE_SEAL,source_plan_seal=PLAN_SEAL,
                                     decoder=sha(source/"inspect-source.py"),source_plan_verification=sha(plan_dir/"verification.json")))


def original_image(root,ctx,explicit=None):
    path=ctx["V"].resolve_firmware(root,explicit);data=path.read_bytes();D=ctx["D"];plan=ctx["plan"]
    require(len(data)==76800 and hashlib.sha256(data).hexdigest()==D.IMAGE_SHA,"exact offline original image")
    captured=D.capture(data);require(captured["entry_9a42"]==plan["main_rows"] and {k:v for k,v in captured.items() if k!="entry_9a42"}==plan["all_helper_rows"],"all264originalbytes94decodedinstructions match sealed plan")
    return path,data


def profile_flags(ctx,mode,main):
    flags=ctx["V"].flags(mode)+(["-fno-exceptions"] if mode=="cpp" else [])
    return [f for f in flags if not main or f not in {"-ffixed-x1","-ffixed-x2","-ffixed-x8","-ffixed-x9","-ffixed-x18"}]


def linker_source():
    return "ENTRY("+ENTRY+")\nSECTIONS {\n .irq 0x9a42 : { *(.text."+ENTRY+") }\n"+"\n".join(" .rcc_"+format(a,"x")+" "+hex(a)+" : { *(.text."+n+") }" for n,a in HELPERS.items())+"\n}\n"


def compile_link(root,folder,ctx,tools,mode):
    commands=[];source=root/"experiments/tsl9-v4160-irq-callframe/src"
    for unit,filename,main in (("main","interrupt_callframe.c",True),("helpers","rcc_helpers.c",False)):
        for extension,action in ((".o",["-c"]),(".ll",["-S","-emit-llvm"])):
            r,_=ctx["V"].run([tools["clang"],*profile_flags(ctx,mode,main),*action,source/filename,"-o",folder/(unit+extension)],folder,unit+extension);commands.append(r)
    (folder/"placements.ld").write_text(linker_source(),encoding="utf-8")
    linked=folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf"
    r,_=ctx["V"].run([tools["linker"],"--no-relax","--no-undefined","-T",folder/"placements.ld",folder/"main.o",folder/"helpers.o","-o",linked],folder,"link");commands.append(r)
    r,text=ctx["V"].run([tools["objdump"],"--disassemble",linked],folder,"disassembly");commands.append(r)
    return linked,text,commands


def elf_gate(path,ctx,kind):
    e=ctx["ELF"](path);require(e.kind==(2 if kind=="linked" else 1) and e.flags==1,"RV32 ELF/RVC softfloat kind")
    arch=re.search(rb"rv32[a-z0-9_]+",e.data(e.byname[".riscv.attributes"]))
    require(arch and all(b"_"+x in arch.group() for x in (b"m",b"a",b"c",b"zicsr")) and not any(b"_"+x in arch.group() for x in (b"f",b"d",b"v")),"RV32IMAC_Zicsr integer-only attributes")
    functions=[s for s in e.symbols if s["index"] and s["info"]&15==2 and s["size"]]
    expected={ENTRY,*HELPERS} if kind=="linked" else ({ENTRY} if kind=="main" else set(HELPERS))
    require({s["name"] for s in functions}==expected,"exact expected real functions; no hidden implementation")
    globals_={s["name"] for s in e.symbols if s["index"] and s["name"] and s["info"]>>4 in (1,2)}
    require(globals_==expected,"no extra global symbols or original aliases")
    und={s["name"] for s in e.symbols if not s["index"] and s["name"]}
    require(und==(set(HELPERS) if kind=="main" else set()),"only explicit main-object helper obligations; final link has no UND")
    allocations=[s for s in e.sections if s["size"] and s["flags"]&2]
    expected_size=264 if kind=="linked" else (144 if kind=="main" else 120)
    require(not any(s["size"] and s["flags"]&1 for s in e.sections) and ".eh_frame" not in e.byname,"no writable state or extra exception metadata")
    require(sum(s["size"] for s in allocations)==expected_size==sum(s["size"] for s in functions) and all(s["flags"]&4 for s in allocations),"every allocated byte owned by expected executable functions")
    require(all(s["size"]==(144 if s["name"]==ENTRY else 30) for s in functions),"exact144B main/four30B helpers")
    if kind=="linked":
        require(not e.relocations and struct.unpack_from("<I",e.raw,24)[0]==0x9a42,"resolved component entry and no linked relocation")
        require(all(s["value"]==(0x9a42 if s["name"]==ENTRY else HELPERS[s["name"]]) for s in functions),"all five original function VAs")
    if kind=="main":
        calls=ctx["plan"]["calls"]
        require(len(e.relocations)==6,"exact six explicit four-byte JAL relocations")
        for rel,wanted in zip(sorted(e.relocations,key=lambda x:x["offset"]),calls):
            name=next(n for n,a in HELPERS.items() if a==wanted["target"])
            require(rel["type"]==17 and rel["offset"]==wanted["site"]-0x9a42 and rel["addend"]==0 and rel["symbol"]["name"]==name,"each raw R_RISCV_JAL obligation at original call offset/target")
    if kind=="helpers":require(not e.relocations,"helper object has no unresolved relocation")
    return dict(sha256=sha(path),kind=kind,allocated_bytes=expected_size,all_allocated_byte_ownership=True,undefined_symbols=sorted(und),relocations=len(e.relocations),functions={s["name"]:dict(address=s["value"],bytes=s["size"],code_sha256=hashlib.sha256(e.function_bytes(s)).hexdigest()) for s in functions})


def display_decoded(op,operands):
    p=[x.strip() for x in operands.split(",")]
    def r(x):require(x in REG,"unexpected displayed register");return REG[x]
    if op=="li":return ["addi",r(p[0]),0,int(p[1],0)]
    if op=="lui":return ["lui",r(p[0]),(int(p[1],0)<<12)&0xffffffff]
    if op=="addi":return ["addi",r(p[0]),r(p[1]),int(p[2],0)]
    if op=="not":return ["xori",r(p[0]),r(p[1]),-1]
    if op in ("or","and"):return [op,*[r(x) for x in p]]
    if op in ("lw","sw","sb"):
        m=re.fullmatch(r"(-?(?:0x[0-9a-f]+|\d+))\((\w+)\)",p[1]);require(m is not None,"displayed direct memory operand")
        return [op,r(p[0]),r(m.group(2)),int(m.group(1),0)]
    if op=="beqz":return ["beq",r(p[0]),0,int(p[1].split()[0],0)]
    if op=="jal":return ["jal",1,int(p[0].split()[0],0)]
    if op=="ret":return ["jalr",0,1,0]
    if op in ("csrc","csrs"):return ["csrrc" if op=="csrc" else "csrrs",0,int(p[0],0),r(p[1])]
    raise ValueError("unparsed/unsupported displayed instruction: "+op)


def machine_gate(text,path,ctx,image):
    e=ctx["ELF"](path);D=ctx["D"];plan=ctx["plan"];facts={}
    originals={ENTRY:plan["main_rows"],**{n:plan["all_helper_rows"]["rcc_"+format(a,"x")] for n,a in HELPERS.items()}}
    for name in [ENTRY,*HELPERS]:
        symbols=[s for s in e.symbols if s["name"]==name and s["index"] and s["info"]&15==2];require(len(symbols)==1,"one actual function")
        s=symbols[0];code=e.function_bytes(s);m=re.search(r"^([0-9a-f]+) <"+name+r">:\s*$",text,re.M)
        require(m and int(m.group(1),16)==s["value"],"ELF-bound disassembly start")
        rows=[];cursor=0
        for line in text[m.end():].lstrip("\r\n").splitlines():
            if not line.strip():break
            row=re.fullmatch(r"\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\t(\S+)\s*(.*?)\s*",line);require(row is not None,"no skipped/unparsed interior instruction lines")
            pc=int(row.group(1),16);raw=bytes.fromhex(row.group(2))
            require(pc==s["value"]+cursor and cursor+len(raw)<=len(code) and raw==code[cursor:cursor+len(raw)],"every contiguous raw instruction byte equals actual ELF")
            require(len(raw) in (2,4) and len(raw)==(4 if raw[0]&3==3 else 2),"whole instruction framing")
            decoded=D.decode(raw,pc);require(decoded==display_decoded(row.group(3),row.group(4)),"independent full raw operand decode equals display")
            rd=decoded[1] if decoded[0] in ("addi","xori","lui","or","and","lw","jal","jalr","csrrs","csrrc") else 0
            allowed={1,2,8,9,10,11,14,15,18} if name==ENTRY else {10,14,15}
            require(not rd or rd in allowed,"only original main/helper destination registers; no A2/A3/T0 writes")
            rows.append(dict(addr=pc,size=len(raw),bytes=raw.hex(),decoded=decoded));cursor+=len(raw)
        require(cursor==len(code),"full function extent including interior RET alternatives")
        old=originals[name];require([(r["addr"],r["size"]) for r in rows]==[(r["addr"],r["size"]) for r in old],"all original instruction boundaries retained")
        if name!=ENTRY:require(rows==old,"all120 helper bytes/decoded instructions equal original at original VAs")
        else:
            require(rows[0]==old[0] and rows[5:]==old[5:] and code[10:]==image[0x9a4c-0x8000:0x9ad2-0x8000],"original firstSP adjustment and complete body from offset10 identical")
            stores=[r["decoded"] for r in rows[1:5]];wanted=[r["decoded"] for r in old[1:5]]
            require(all(r["size"]==2 and r["decoded"][0]=="sw" and r["decoded"][2]==2 for r in rows[1:5]) and Counter(map(tuple,stores))==Counter(map(tuple,wanted)),"same four C.SWSP save roles/slots, any observed order recorded separately")
        facts[name]=dict(bytes=len(code),instructions=len(rows),code_sha256=hashlib.sha256(code).hexdigest(),rows=rows,raw_operand_decode_checked=True)
    main=facts[ENTRY]["rows"];bypc={r["addr"]:r for r in main};callfacts=[]
    for c in plan["calls"]:
        r=bypc[c["site"]];require(r["size"]==4 and r["decoded"]==["jal",1,c["target"]] and c["link"]==r["addr"]+4 in bypc,"each original4B JAL PC/target/RA continuation")
        callfacts.append(c)
    for load in plan["frame"]["fresh_loads"]:require(bypc[load["site"]]["decoded"]==["lw",load["register"],2,load["offset"]],"fresh frame reload from exact live SP slot, not input snapshot")
    require(sum(f["bytes"] for f in facts.values())==264 and sum(f["instructions"] for f in facts.values())==94,"all264 allocated bytes94 actual instructions")
    original=plan["main_rows"];changed=[r["addr"] for r,o in zip(main,original) if r["bytes"]!=o["bytes"]]
    return dict(functions=facts,calls=callfacts,main_first_SP_adjustment_identical=True,main_body_offset10_identical=True,main_instruction_boundaries_identical=True,
                save_multiset_identical=True,save_order_identical=[r["decoded"] for r in main[1:5]]==[r["decoded"] for r in original[1:5]],
                actual_save_rows=main[1:5],original_save_rows=original[1:5],changed_instruction_PCs=changed,
                fresh_frame_loads=plan["frame"]["fresh_loads"],normal_output_contract=plan["normal_outputs"],whole_component_original_extents_fit=True,
                original_pointwise_equivalence_proved=False,asynchronous_equivalence_proved=False,full_original_image_integration_proved=False,
                target_execution=False,ISA_emulation=False)


def ir_gate(folder):
    main=(folder/"main.ll").read_text(encoding="utf-8");helpers=(folder/"helpers.ll").read_text(encoding="utf-8")
    require('target triple = "riscv32-unknown-unknown-elf"' in main and 'target triple = "riscv32-unknown-unknown-elf"' in helpers,"actual RV32 LLVM IR")
    calls=re.findall(r'call (?:noundef )?i32 asm sideeffect "jal ra, ([^"]+)", "([^"]+)"\((.*?)\)',main)
    targets=["tsl9_rebuild_rcc_registers_"+s for s in ("19142","19124","1917e","1917e","19160","19160")]
    constraint="={x10},{x11},{x10},~{x1},~{x14},~{x15},~{memory}"
    require(len(calls)==6 and [c[0] for c in calls]==targets and all(c[1]==constraint for c in calls),"six ordered explicit JAL boundaries, A0readwrite/A1input/RA+A4+A5+memory clobbers")
    require(not any(re.search(r"\b(?:call|invoke)\b",line) and "asm sideeffect" not in line for line in main.splitlines()),"main no compiler runtime helper calls")
    require(not re.search(r"\balloca\b|\binvoke\b|\bswitch\b|\bbr i1\b",main),"straight-line source primitive IR, frame emitted by compiler")
    stores=re.findall(r"store volatile i(\d+)",main);require(stores==["8","32","8","32","8","32"],"six ordered PFIC volatile store widths")
    require(main.count('"csrc 0x800, $0"')==main.count('"csrs 0x800, $0"')==1 and main.count('"{x18},~{memory}"')==2,"two liveS2 CSR boundaries")
    require(helpers.count("load volatile i32")==helpers.count("store volatile i32")==8,"four helpers each retain two branch-owned fresh32bit RMW sites")
    return dict(explicit_JAL_boundaries=[dict(target=c[0],constraints=c[1],IR_arguments=c[2]) for c in calls],PFIC_store_widths=[int(w) for w in stores],
                main_source_runtime_calls=0,helper_branch_owned_load_sites=8,helper_branch_owned_store_sites=8,structural_IR_checks_only=True,full_IR_semantics_proved=False)


def static_checks(folder,ctx,image):
    objects={k:elf_gate(folder/(k+".o"),ctx,k) for k in ("main","helpers")}
    linked=elf_gate(folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf",ctx,"linked")
    machine=machine_gate((folder/"disassembly.log").read_text(encoding="utf-8"),folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf",ctx,image)
    return dict(objects=objects,linked=linked,machine=machine,LLVM_IR=ir_gate(folder))


def transcript_controls(folder,ctx,image):
    text=(folder/"disassembly.log").read_text(encoding="utf-8");linked=folder/"COMPONENT-ONLY-NOT-FIRMWARE.elf";reports=[]
    for name in [ENTRY,*HELPERS]:
        marker=re.search(r"^([0-9a-f]+) <"+name+r">:\s*$",text,re.M);require(marker is not None,"actual transcript marker")
        head,tail=text[:marker.end()],text[marker.end():];lines=tail.splitlines(keepends=True);indexes=[]
        for i,line in enumerate(lines):
            if indexes and not line.strip():break
            if re.match(r"\s*[0-9a-f]+:",line):indexes.append(i)
        variants={}
        for label,index in (("missing_first",indexes[0]),("missing_middle",indexes[len(indexes)//2]),("truncated_last",indexes[-1])):
            variants[label]=head+"".join(line for i,line in enumerate(lines) if i!=index)
        changed=list(lines);changed[indexes[1]]=re.sub(r"(:\s*)[0-9a-f]{2}",r"\g<1>00",changed[indexes[1]],count=1);require(changed[indexes[1]]!=lines[indexes[1]],"actual byte control");variants["changed_raw_byte"]=head+"".join(changed)
        for label,index in (("unparsed_middle",indexes[1]),("unparsed_trailing",indexes[-1]+1)):
            changed=list(lines);changed.insert(index,"    UNPARSED-INSTRUCTION\n");variants[label]=head+"".join(changed)
        for label,changed in variants.items():
            try:machine_gate(changed,linked,ctx,image)
            except ValueError as error:reports.append(dict(function=name,case=label,rejected=True,reason=str(error),transcript_sha256=hashlib.sha256(changed.encode()).hexdigest()))
            else:raise ValueError("changed transcript admitted")
    return reports


def compiled_controls(root,folder,ctx,tools,mode,image):
    core="experiments/tsl9-v4160-irq-callframe/src/";header=core+"callframe_io.h";main=core+"interrupt_callframe.c";helpers=core+"rcc_helpers.c";io="experiments/tsl9-v4160-irq-native/src/native_io.h"
    cases=[("missing_RA_clobber",header,'"ra","a4","a5","memory"','"a4","a5","memory"',2),
           ("wrong_call_link",header,'"jal ra, "','"jal zero, "',2),
           ("wrong_call_target",main,"CF_CALL(tsl9_rebuild_rcc_registers_19142,","CF_CALL(tsl9_rebuild_rcc_registers_19124,",1),
           ("wrong_final_flag",header,'__asm__ volatile("li %0, 0"','__asm__ volatile("li %0, 1"',1),
           ("wrong_PFIC_width",io,"#define IR_WRITE8(a,v) (*(volatile uint8_t *)(uintptr_t)(a)=(v))","#define IR_WRITE8(a,v) (*(volatile uint16_t *)(uintptr_t)(a)=(v))",1),
           ("wrong_helper_offset",helpers,"return update32(0x18u,mask,enabled);","return update32(0x1cu,mask,enabled);",1)]
    reports=[]
    for name,relative,before,after,count in cases:
        case_dir=folder/("negative-"+name);case_dir.mkdir()
        for path in SOURCE_PINS:
            target=case_dir/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((root/path).read_bytes())
        altered=case_dir/relative;text=altered.read_text(encoding="utf-8-sig");require(text.count(before)==count,"exact compiled control source sites")
        altered.write_text(text.replace(before,after),encoding="utf-8")
        _,_,commands=compile_link(case_dir,case_dir,ctx,tools,mode)
        try:static_checks(case_dir,ctx,image)
        except ValueError as error:reports.append(dict(case=name,changed_source=relative,source_sha256=sha(altered),actual_compilation_and_link_succeeded=True,rejected=True,reason=str(error),
                                                       artifacts={p:sha(case_dir/p) for p in ("main.o","helpers.o","main.ll","helpers.ll","COMPONENT-ONLY-NOT-FIRMWARE.elf")},commands=commands))
        else:raise ValueError("compiled source control admitted: "+name)
    return reports


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--project-root",type=Path,default=HERE.parents[2]);p.add_argument("--tool-dir",type=Path)
    for key in ("clang","linker","objdump"):p.add_argument("--"+key)
    p.add_argument("--firmware",type=Path);p.add_argument("--language",choices=("c","cpp","both"),default="both");a=p.parse_args();root=a.project_root.resolve();ctx=load_context(root)
    require({n:sha(root/n) for n in SOURCE_PINS}==SOURCE_PINS,"frozen callframe/core/public source pins")
    firmware,image=original_image(root,ctx,a.firmware);V=ctx["V"];directory=a.tool_dir or (V.NDK if os.name=="nt" and V.NDK.is_dir() else None)
    tools={k:V.resolve_tool(getattr(a,k),directory,n) for k,n in (("clang","clang"),("linker","ld.lld"),("objdump","llvm-objdump"))};tool_pins={k:sha(v) for k,v in tools.items()};script_pin=sha(Path(__file__));results=[]
    for mode in (("c","cpp") if a.language=="both" else (a.language,)):
        folder=HERE/"build"/("callframe-"+uuid.uuid4().hex+"-"+mode);folder.mkdir(parents=True)
        _,_,commands=compile_link(root,folder,ctx,tools,mode);checks=static_checks(folder,ctx,image)
        transcripts=transcript_controls(folder,ctx,image);negatives=compiled_controls(root,folder,ctx,tools,mode,image)
        require({n:sha(root/n) for n in SOURCE_PINS}==SOURCE_PINS and {k:sha(v) for k,v in tools.items()}==tool_pins and sha(Path(__file__))==script_pin,"source/tools/runner unchanged")
        report=dict(schema="TSL9-original-placement-callframe-native-proof-v1",passed=True,mode=mode,source_sha256=SOURCE_PINS,runner_sha256=script_pin,dependencies=ctx["dependency_pins"],
                    tools={k:dict(path=str(v),sha256=tool_pins[k]) for k,v in tools.items()},main_flags=profile_flags(ctx,mode,True),helper_flags=profile_flags(ctx,mode,False),commands=commands,
                    firmware_input=dict(path=str(firmware),sha256=ctx["D"].IMAGE_SHA),artifacts={p:sha(folder/p) for p in ("main.o","helpers.o","main.ll","helpers.ll","COMPONENT-ONLY-NOT-FIRMWARE.elf","placements.ld")},
                    checks=checks,actual_compiled_controls=negatives,transcript_controls=transcripts,whole_component_original_extents_fit=True,
                    exact_original_main_bytes=False,original_pointwise_equivalence_proved=False,asynchronous_equivalence_proved=False,original_full_image_integration_proved=False,
                    physical_compatibility_proved=False,target_execution=False,ISA_emulation=False,firmware_BIN_produced=False,network=False,hardware=False,OTA_ready=False)
        receipt=folder/"verification.json";receipt.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        results.append(dict(mode=mode,receipt=str(receipt),sha256=sha(receipt),allocated_bytes=264,instructions=94,main_bytes=144,helpers_bytes=120,changed_save_instruction_PCs=checks["machine"]["changed_instruction_PCs"],actual_compiled_controls=len(negatives),transcript_controls=len(transcripts)))
    print(json.dumps(dict(passed=True,results=results,original_pointwise_equivalence_proved=False,OTA_ready=False)))


if __name__=="__main__":main()
