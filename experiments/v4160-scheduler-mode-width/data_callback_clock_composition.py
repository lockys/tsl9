"""Compose caller's saved clock+delay with later callback gating.

Memory is reconstructed at the boundary: no scheduler progress or callback
reachability is claimed. Shared word and data byte are explicitly assumed
unchanged between steps unless an alternate callback byte is supplied.
Provider calls return normally and do not alter the saved word or stack.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py')); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
caller=load('data_delay_caller'); callback=load('data_delay_callback'); MASK=0xffffffff


def run_case(image,byte,clock,later):
    gp=0x20000000; pointer=0x20001234; sp=0x20001000; ra=0x12345678
    args,end,ret,events=caller.run(image,byte,clock,gp,pointer,sp,ra)
    stores=[e for e in events if e[:3]==('write',0x2000bef0,4)]
    if len(stores)!=1: raise ValueError('caller store count')
    saved=stores[0][3]; delay=(0,60000,300000,600000)[byte>>6]
    if args!=(0xb254,0,delay,0) or saved!=(clock+delay)&MASK: raise ValueError('caller projection mismatch')
    kind,pc,a0,post_sp,post_ra,cb_events=callback.run(image,later,saved,gp,pointer,end,ret)
    should_call=bool((later&192) and saved)
    if (kind=='tail')!=should_call: raise ValueError('callback gate mismatch')
    if (post_sp,post_ra)!=(end,ret): raise ValueError('callback frame mismatch')
    if should_call:
        if (pc,a0)!=(0x90b0,0xb29a) or ('write',0x2000bef0,4,0) not in cb_events: raise ValueError('tail mismatch')
    elif any(e[0]=='call' or e[0]=='write' for e in cb_events): raise ValueError('early exit side effect')
    return delay,saved,should_call


def main():
    image=caller.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=caller.v.SHA: raise ValueError('firmware identity mismatch')
    count=0; zero_cancel=0; changed_suppressed=0; changed_enabled=0
    for byte in range(256):
        delay=(0,60000,300000,600000)[byte>>6]
        cancel=(-delay)&MASK
        for clock in (0,1,0xffffffff,cancel,(cancel-1)&MASK,(cancel+1)&MASK,0x12345678):
            for later in (byte,0,255,byte^0x40):
                d,saved,called=run_case(image,byte,clock,later)
                if d!=delay: raise ValueError('delay changed')
                if later==byte and byte&192 and clock==cancel:
                    if saved!=0 or called: raise ValueError('wrap cancellation failed')
                    zero_cancel+=1
                if byte&192 and saved and not (later&192):
                    if called: raise ValueError('changed byte did not suppress')
                    changed_suppressed+=1
                if not(byte&192) and saved and later&192:
                    if not called: raise ValueError('changed byte did not enable')
                    changed_enabled+=1
                count+=1
    if not all((zero_cancel,changed_suppressed,changed_enabled)): raise ValueError('missing witness class')
    for addr in (0xb2de,0xb2e4,0xb262,0xb26e):
        bad=bytearray(image); bad[addr-0x8000]^=1
        try: run_case(bad,0xff,1,0xff)
        except ValueError: pass
        else: raise ValueError(f'mutation missed {addr:#x}')
    print(f'PASS: {count} boundary reconstructions, including {zero_cancel} zero-sum clock witnesses')
    print(f'PASS: changed byte suppressed {changed_suppressed} and enabled {changed_enabled} callback checks; 4 mutants rejected')
    print('Conditional on provider return and unchanged shared word; no scheduler reachability or hardware evidence.')

if __name__=='__main__': main()
