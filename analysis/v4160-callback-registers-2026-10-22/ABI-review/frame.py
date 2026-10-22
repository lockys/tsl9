"""Independent two-existing-save-word scheduling audit, never an opcode emitter."""
import hashlib
import json
from pathlib import Path
import runpy
import struct

HERE=Path(__file__).resolve().parent
PASS='f5f17633570540f838399e30d932e5eca439eae1239a9429c6b89560d4476f02'


def H(raw):return hashlib.sha256(raw).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)


def audit(root,source,output,receipt):
    tool=root/'experiments/tsl9-v4160-callback-registers/postpass/frame.py'
    need(H(tool.read_bytes())==PASS,'Frozen new function-scoped existing-word pass')
    module=runpy.run_path(str(tool));field=runpy.run_path(str(HERE/'fields.py'));ctx=field['context'](root)
    E=ctx['ELF'];before=E(source);after=E(output)
    expected,details=module['inspect'](root,source)
    need(after.raw==expected,'Only exact actual compiled save-word permutation; all other ELF bytes unchanged')
    need(before.sections==after.sections and before.symbols==after.symbols and before.relocations==after.relocations,
         'All actual section/symbol/relocation metadata identical')
    code=before.data(before.byname[details['section']]);rows=field['rows'](code,0,ctx)
    need(not any(r['target'] in (2,4) for r in rows) and
         not any(r['rd']==1 and r['op'] in ('jal','jalr') and r['PC']+r['bytes'] in (2,4) for r in rows),
         'No actual known direct control or call-return entry into the changed words')
    report=json.loads(receipt.read_bytes())
    expected_report=dict(schema='TSL9-callback-existing-save-word-order-v1',passed=True,
          input=str(source.resolve()),input_sha256=H(before.raw),output=str(output.resolve()),
          output_sha256=H(after.raw),details=details,runner_sha256=PASS,function_bytes=624,
          relative_save_order_matched=True,whole_entry_prefix_identical=False,
          original_ABI_admitted=False,padding_created=False,target_execution=False)
    need(report==expected_report,'Exact actual pass receipt, including all limits and paths')
    section=before.byname[details['section']];offset=section['offset']
    need(after.raw[:offset+2]==before.raw[:offset+2] and
         after.raw[offset+2:offset+6]==before.raw[offset+4:offset+6]+before.raw[offset+2:offset+4] and
         after.raw[offset+6:]==before.raw[offset+6:],'Independent four-byte ownership check')
    tests=[]
    class Bytes:
        def __init__(self,value):self.value=value
        def read_bytes(self):return self.value
    def reject(name,raw,gate):
        try:gate()
        except (ValueError,IndexError,KeyError,struct.error) as error:
            tests.append(dict(name=name,rejected=True,mutated_sha256=H(raw),reason=str(error)));return
        raise ValueError('Malformed existing-word schedule input admitted '+name)
    p=bytearray(before.raw);h=int.from_bytes(p[offset+2:offset+4],'little')
    p[offset+2:offset+4]=(h&~((15<<9)|(3<<7))).to_bytes(2,'little')
    reject('wrong_existing_RA_save_slot',p,lambda:module['inspect'](root,Bytes(bytes(p))))
    p=bytearray(before.raw);table=next(s for s in before.sections if s['type']==2)
    number=next(i for i,s in enumerate(before.symbol_tables[table['index']]) if
                s['index']==section['index'] and s['name'].startswith('$x'))
    struct.pack_into('<I',p,table['offset']+number*16+4,4)
    reject('actual_interior_mapping_symbol',p,lambda:module['inspect'](root,Bytes(bytes(p))))
    p=bytearray(before.raw);noncode=before.byname['.comment'];shoff=struct.unpack_from('<I',p,32)[0]
    struct.pack_into('<I',p,shoff+noncode['index']*40+4,9)
    reject('nonempty_REL_section',p,lambda:module['inspect'](root,Bytes(bytes(p))))
    p=bytearray(after.raw);p[offset+30]^=1
    reject('one_extra_nonwindow_output_byte',p,
           lambda:need(bytes(p)==expected,'All output bytes must equal exact actual two-word transform'))
    need(len(tests)==4,'Exactly four focused actual frame-pass controls')
    return dict(schema='TSL9-callback-independent-existing-save-order-v1',actual_objects_read=True,
                source_sha256=H(before.raw),output_sha256=H(after.raw),pass_sha256=PASS,
                changed_file_bytes=sum(a!=b for a,b in zip(before.raw,after.raw)),
                details=details,known_control_frontiers_into_window=[],controls=tests,
                original_relative_save_projection_matched=True,whole_original_prefix_equal=False,
                original_fifteen_RA_offsets_preserved=False,unowned_tail_bytes=8,
                original_full_ABI_admitted=False,placement_admitted=False,
                target_execution=False,ISA_emulation=False,hardware_OTA_proved=False)
