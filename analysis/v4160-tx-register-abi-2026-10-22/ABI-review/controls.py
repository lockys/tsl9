#!/usr/bin/env python3
"""Malformed actual-object controls for the new frame pass; no target execution."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct
import sys

sys.dont_write_bytecode=True


class BytesInput:
    def __init__(self,raw):
        self.raw=raw

    def read_bytes(self):
        return self.raw


def need(value,message):
    if not value:
        raise ValueError(message)


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def inspect(root,tool,input_object):
    tool_pin=H(tool.read_bytes());policy_pin=H(tool.with_name('policy.json').read_bytes())
    module=runpy.run_path(str(tool))
    module['policy_gate'](tool.with_name('policy.json'))
    context=module['context'](root)
    e=context['ELF'](input_object)
    facts=module['inspect'](e,context['decode'])
    owner=facts['owner'];comment=e.byname['.comment']
    shoff=struct.unpack_from('<I',e.raw,32)[0]
    table=next(s for s in e.sections if s['type']==2)
    entries=e.symbol_tables[table['index']]
    function_index=next(i for i,s in enumerate(entries) if s['info']&15==2)
    anchor_index=next(i for i,s in enumerate(entries) if s['index']==owner['index'] and
                      s['name'].startswith('.L') and s['value']>12)
    reltable=next(s for s in e.sections if s['type']==4)
    loc={}
    for offset in range(reltable['offset'],reltable['offset']+reltable['size'],12):
        info=struct.unpack_from('<I',e.raw,offset+4)[0]
        loc[info&255]=offset
    mut=[]
    def edit(name,fn):
        raw=bytearray(e.raw);fn(raw);mut.append((name,bytes(raw)))
    def xorword(raw,at,width,mask):
        raw[at:at+width]=(int.from_bytes(raw[at:at+width],'little')^mask).to_bytes(width,'little')
    edit('aliased_comment_storage',lambda b:struct.pack_into('<II',b,shoff+comment['index']*40+16,
                                                            owner['offset']+2,10))
    edit('function_visibility_changed',lambda b:b.__setitem__(table['offset']+function_index*16+13,2))
    edit('function_binding_changed',lambda b:b.__setitem__(table['offset']+function_index*16+12,18))
    edit('duplicate_selected_section_name',lambda b:struct.pack_into('<I',b,shoff+comment['index']*40,
                                                                   owner['name_offset']))
    edit('wrong_save_GPR',lambda b:xorword(b,owner['offset']+2,2,4))
    edit('wrong_save_slot',lambda b:xorword(b,owner['offset']+2,2,128))
    first_load=next(r for r in facts['tail'] if r['op']=='lw' and r['rs1']==2)
    edit('wrong_restore_slot',lambda b:xorword(b,owner['offset']+first_load['offset'],2,16))
    zero=next(r for r in facts['tail'] if r['op']=='sh' and r['rs2']==0)
    edit('wrong_descriptor_width',lambda b:xorword(b,owner['offset']+zero['offset'],4,3<<12))
    edit('interior_symbol_anchor',lambda b:struct.pack_into('<I',b,table['offset']+anchor_index*16+4,214))
    edit('interior_relocation_site',lambda b:struct.pack_into('<I',b,loc[23],214))
    anchor_value=next(r for r in e.relocations if r['type']==24)['symbol']['value']
    edit('interior_relocation_target',lambda b:struct.pack_into('<i',b,loc[24]+8,214-anchor_value))
    exitbranch=next(r for r in facts['rows'] if r['offset']==178)
    need(exitbranch['op']=='bgeu' and exitbranch['target']==208,'Actual encoded loop exit contract')
    edit('encoded_interior_branch_target',lambda b:xorword(b,owner['offset']+178,4,1<<25))
    call=next(r for r in facts['rows'] if r['op']=='jalr' and r['rd']==1)
    edit('opaque_call_return_at_window_start',lambda b:b.__setitem__(slice(owner['offset']+206,
                                                                        owner['offset']+208),
                                                                  bytes.fromhex(call['raw_hex'])))
    results=[]
    for name,raw in mut:
        try:
            changed=context['ELF'](BytesInput(raw))
            module['transform'](changed,context['decode'])
        except ValueError as error:
            results.append(dict(name=name,actual_compiler_ELF_bytes_mutated=True,rejected=True,
                                reason=str(error),mutated_input_sha256=H(raw)))
        else:
            raise ValueError('Malformed actual object admitted: '+name)
    scheduled,_=module['transform'](e,context['decode'])
    try:
        module['transform'](context['ELF'](BytesInput(scheduled)),context['decode'])
    except ValueError as error:
        results.append(dict(name='double_application',actual_scheduled_object_bytes_used=True,
                            rejected=True,reason=str(error)))
    else:
        raise ValueError('Already scheduled object admitted')
    need(H(tool.read_bytes())==tool_pin and H(tool.with_name('policy.json').read_bytes())==policy_pin and
         H(input_object.read_bytes())==H(e.raw),'Tool, policy and actual input remain unchanged during control run')
    return dict(schema='TSL9-TX-independent-frame-guard-controls-v1',
                actual_input_sha256=H(e.raw),tool_sha256=tool_pin,
                policy_sha256=policy_pin,
                controls=results,total_rejected=len(results),
                accepted_firmware_generated=False,target_execution=False,ISA_emulation=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--tool',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    result=inspect(args.project_root.resolve(),args.tool.resolve(),args.input.resolve())
    need(not args.receipt.exists(),'Create-only malformed-object control receipt')
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(all_controls_rejected=True,total_rejected=result['total_rejected'],
                         target_execution=False,ISA_emulation=False)))


if __name__=='__main__':
    main()
