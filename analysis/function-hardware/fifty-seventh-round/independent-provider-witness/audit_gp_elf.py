"""Finite RV32IMAC integer-destination audit on retained R56 ELF, no execution."""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent
OLD=BASE/"fifty-fifth-round/independent-service-events-contract"
sys.path.insert(0,str(OLD))
from elf_service_events import parse,sha


def decode16(w):
    q,f=w&3,w>>13
    rd=w>>7&31
    if q==0:
        if f==0:return ((8+(w>>2&7)),"C.ADDI4SPN",True) if w&0x1fe0 else (None,"reserved-zero-C.ADDI4SPN",False)
        if f==2:return 8+(w>>2&7),"C.LW",True
        if f==6:return None,"C.SW",True
        return None,"unknown-quadrant0",False
    if q==1:
        if f==0:return rd,"C.ADDI/NOP",True
        if f==1:return 1,"C.JAL-RV32",True
        if f==2:return rd,"C.LI",True
        if f==3:
            if rd==2:return 2,"C.ADDI16SP",bool(w&0x107c)
            return rd,"C.LUI",rd not in (0,2) and bool(w&0x107c)
        if f==4:
            part=w>>10&3
            if part in (0,1):return 8+rd%8,"C.SRLI/SRAI",not bool(w&0x1000)
            if part==2:return 8+rd%8,"C.ANDI",True
            return 8+rd%8,"C.SUB/XOR/OR/AND",not bool(w&0x1000)
        if f==5:return None,"C.J",True
        if f in (6,7):return None,"C.BEQZ/BNEZ",True
    if q==2:
        if f==0:return rd,"C.SLLI",not bool(w&0x1000)
        if f==2:return rd,"C.LWSP",rd!=0
        if f==4:
            rs2=w>>2&31;high=w>>12&1
            if not high and not rs2:return None,"C.JR",rd!=0
            if not high:return rd,"C.MV",True
            if not rs2 and rd==0:return None,"C.EBREAK",True
            if not rs2:return 1,"C.JALR",True
            return rd,"C.ADD",True
        if f==6:return None,"C.SWSP",True
    return None,"unknown-compressed",False


def decode32(w):
    op=w&127;rd=w>>7&31;f=w>>12&7;f7=w>>25
    if op in (0x17,0x37,0x6f):return rd,{0x17:"AUIPC",0x37:"LUI",0x6f:"JAL"}[op],True
    if op==0x67:return rd,"JALR",f==0
    if op==3:return rd,"LOAD",f in (0,1,2,4,5)
    if op==0x23:return None,"STORE",f in (0,1,2)
    if op==0x63:return None,"BRANCH",f in (0,1,4,5,6,7)
    if op==0x13:
        valid=(f not in (1,5)) or (f==1 and f7==0) or (f==5 and f7 in (0,32))
        return rd,"OP-IMM",valid
    if op==0x33:
        return rd,"OP/M",f7 in (0,1) or (f7==32 and f in (0,5))
    if op==0x73:
        if f in (1,2,3,5,6,7):return rd,"CSR",True
        known={0x00000073:"ECALL",0x00100073:"EBREAK",0x30200073:"MRET",0x10500073:"WFI"}
        return None,known.get(w,"unknown-SYSTEM"),w in known
    if op==0x0f:return None,"FENCE",f in (0,1) and rd==0
    if op==0x2f:
        return rd,"AMO.W",f==2 and w>>27 in (0,1,2,3,4,8,12,16,20,24,28)
    return None,f"unknown-opcode-{op:02x}",False


def audit(e):
    fn=[(n,q) for n,q in e["symbols"].items() if q["section"] and q["type"]==2 and q["bytes"]]
    writers=[];unknown=[];gaps=[];counts=collections.Counter();total=0;codebytes=0
    for index,s in enumerate(e["sections"]):
        if s[1]!=1 or not s[2]&4 or not s[5]:continue
        code=e["data"][s[4]:s[4]+s[5]];offset=0;codebytes+=len(code)
        while offset<len(code):
            if offset+2>len(code):unknown.append({"section":e["names"][index],"offset":offset,"reason":"trailing-byte"});break
            h=int.from_bytes(code[offset:offset+2],"little")
            width=2 if h&3!=3 else 4
            if width==4 and h&31==31:
                unknown.append({"section":e["names"][index],"offset":offset,"reason":"long-encoding-unsupported"});break
            if offset+width>len(code):unknown.append({"section":e["names"][index],"offset":offset,"reason":"truncated-instruction"});break
            w=int.from_bytes(code[offset:offset+width],"little")
            rd,kind,known=decode16(w) if width==2 else decode32(w)
            owners=[{"symbol":n,"function_offset":offset-q["value"]} for n,q in fn if q["section"]==index and q["value"]<=offset<q["value"]+q["bytes"]]
            row={"section":e["names"][index],"offset":offset,"width":width,"encoding":code[offset:offset+width].hex(),"class":kind,"owners":owners}
            if not owners:gaps.append(row)
            if not known:unknown.append(row)
            if rd==3: writers.append({**row,"known_integer_destination_GP":known})
            counts[kind]+=1;total+=1;offset+=width
    return {"gp_destination_instructions":writers,"unknown_decodings":unknown,"executable_bytes_without_FUNC_owner":gaps,
            "instruction_classes":dict(counts),"instructions_scanned":total,"executable_bytes":codebytes,
            "decoder_scope":"RV32IMAC integer destination classification, including CSR read destination; no value execution"}


def main():
    inputs=[Path(__file__),OLD/"elf_service_events.py"];results=[]
    for mode in ("c","cpp"):
        receipt=BASE/"fifty-sixth-round"/("platform-"+mode+".json")
        j=json.loads(receipt.read_text());obj=Path(j["object"])
        assert sha(obj)==j["object_sha256"]
        inputs.extend([receipt,obj]);e=parse(obj);r=audit(e)
        names={o["symbol"] for w in r["gp_destination_instructions"] for o in w["owners"]}
        results.append({"mode":mode,"object":str(obj),"sha256":sha(obj),**r,
                        "known_GP_writer_symbols":sorted(names),
                        "known_writers_within_expected_allowlist":names<={"tsl9_reset_entry","tsl9_context_restore_irq"},
                        "all_executable_encodings_classified_under_RV32IMAC":not r["unknown_decodings"] and not r["executable_bytes_without_FUNC_owner"],
                        "resident_ROM_unported_or_physical_GP_retention_proved":False})
    guards={str(p):sha(p) for p in inputs}
    print(json.dumps({"schema":"r57-independent-GP-ELF-finite-decode-v1","pass":True,"guards":guards,"results":results,
                      "source_scan_used_as_full_machine_proof":False,"original_binary_opened":False,"target_executed":False,
                      "target_compiled":False,"emulation":False,"network":False,"hardware":False},separators=(",",":")))


if __name__=="__main__":main()
