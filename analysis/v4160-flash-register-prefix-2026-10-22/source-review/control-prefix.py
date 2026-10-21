#!/usr/bin/env python3
"""Finite original-order regressions and SSA/width controls; data only."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import frontier as F

HERE=Path(__file__).resolve().parent
def run(root,firmware,folder,output):
    decode,proof,original,unused=F.source(root,firmware);component=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf';bodies=F.component_bodies(root,component);reference=F.read(HERE/'baseline.json');prior={x['entry']:bytes.fromhex(x['current_hex']) for x in reference['functions']}
    for entry,size in F.RANGES:
        if entry!=0x9c0a:F.need(bodies[entry]==original[entry-0x8000:entry-0x8000+size],'Controls require actual exact-original leaf baseline')
    F.need(not output.exists(),'Create-only independent control directory');output.mkdir(parents=True);E=F.elf(root,component);changes=[]
    def body(entry):return bytearray(bodies[entry])
    changes.append(('unlock_previous_materialization',0x18e98,prior[0x18e98]))
    raw=body(0x18e98);raw[16:22]=raw[18:22]+raw[16:18];changes.append(('unlock_key2_low_hoisted_before_first_store',0x18e98,raw))
    raw=body(0x18ec4);raw[6:14]=raw[10:14]+raw[6:10];changes.append(('erase_alignment_before_mask',0x18ec4,raw))
    changes.append(('erase_previous_RMW_and_poll_registers',0x18ec4,prior[0x18ec4]))
    raw=body(0x18ec4);raw[28:34]=prior[0x18ec4][28:34];changes.append(('erase_busy_poll_A3_instead_of_A4',0x18ec4,raw))
    raw=body(0x18ef2);raw[:16]=prior[0x18ef2][:16];changes.append(('program_previous_initial_scratch_and_boundary',0x18ef2,raw))
    raw=body(0x18ef2);raw[4:6]=bytes.fromhex('104b');changes.append(('program_CTRL_read_A2_instead_of_A5',0x18ef2,raw))
    raw=body(0x18ef2);raw[6:12]=raw[8:12]+raw[6:8];changes.append(('program_alignment_before_mode_mask',0x18ef2,raw))
    raw=body(0x18ef2);raw[68:78]=prior[0x18ef2][68:78];changes.append(('program_previous_commit_scratch_registers',0x18ef2,raw))
    raw=body(0x18ef2);raw[82:88]=prior[0x18ef2][82:88];changes.append(('program_final_busy_poll_A3_instead_of_A4',0x18ef2,raw))
    raw=body(0x18ef2);raw[40:44]=prior[0x18ef2][40:44];changes.append(('program_commutative_source_ADD_encoding',0x18ef2,raw))
    raw=body(0x18ec4);raw[18:20]=bytes.fromhex('cccb');changes.append(('erase_wrong_destination_store_GPR',0x18ec4,raw))
    rows=[]
    for name,entry,raw in changes:
        section=next(s for s in E.sections if s['flags']&2 and s['address']==entry);mutant=bytearray(E.raw);mutant[section['offset']:section['offset']+section['size']]=raw;path=output/(name+'.elf');path.write_bytes(mutant);actual=F.component_bodies(root,path)[entry]
        comparison=F.compare(original[entry-0x8000:entry-0x8000+len(raw)],actual,entry,decode);F.need(not comparison['exact_original_bytes'],'Actual exact-original byte regression rejected')
        if name!='program_commutative_source_ADD_encoding':F.need(not comparison['same_decoded_instruction_frontiers_modulo_commutative_sources'],'Actual physical register/order frontier regression rejected')
        else:F.need(comparison['same_decoded_instruction_frontiers_modulo_commutative_sources'],'Commutative encoding control must not be mislabeled a GPR-frontier difference')
        rows.append({'case':name,'sha256':F.sha(path),'bytes':path.stat().st_size,'exact_byte_gate_rejected':True,'frontier_gate_rejected':not comparison['same_decoded_instruction_frontiers_modulo_commutative_sources']})
    spec=importlib.util.spec_from_file_location('prefix_control_IR',HERE/'ir-review.py');ir=importlib.util.module_from_spec(spec);spec.loader.exec_module(ir)
    originals={n:(folder/(n+'.ll')).read_text(encoding='utf-8') for n in ('unlock','erase','program')}
    for n,t in originals.items():ir.inspect(n,t)
    program=originals['program'];erase=originals['erase'];unlock=originals['unlock']
    bridge=re.search(r'"=\{x15\},\{x15\},~\{memory\}"\(i32 %\d+\)',program)[0]
    poststore=re.search(r'store volatile i32.*?\n\s*%\d+ = (?:tail )?call i32 asm sideeffect "", ("=\{x14\},\{x14\},~\{memory\}"\(i32 %\d+\))',unlock,re.S)[1]
    controls=[('program_volatile_removed','program',program.replace('load volatile i32','load i32',1)),('program_load_width16','program',program.replace('load volatile i32','load volatile i16',1)),('program_initial_bridge_A2','program',program.replace(bridge,bridge.replace('x15','x12'),1)),('erase_wrong_mode_mask','erase',erase.replace('(i32 131072)','(i32 65536)',1)),('unlock_poststore_bridge_wrong_register','unlock',unlock.replace(poststore,poststore.replace('x14','x13'),1)),('program_source_address_wrong_base','program',program.replace('"={x13},{x11},{x15},~{memory}"','"={x13},{x10},{x15},~{memory}"',1)),('program_address_sub_instead_of_add','program',program.replace('"add $0, $1, $2"','"sub $0, $1, $2"',1))]
    for name,which,text in controls:
        F.need(text!=originals[which],'Changed actual IR control');path=output/(name+'.ll');path.write_bytes(text.encode('utf-8'))
        try:ir.inspect(which,text)
        except ValueError as error:reason=str(error)
        else:raise ValueError('Accepted IR control '+name)
        rows.append({'case':name,'sha256':F.sha(path),'bytes':path.stat().st_size,'rejected':True,'reason':reason})
    result={'schema':'ID2966-independent-prefix-file-controls-v1','passed':True,'ELF_byte_controls':len(changes),'frontier_controls_rejected':len(changes)-1,'byte_only_commutative_controls':1,'IR_controls_rejected':len(controls),'actual_component_sha256':F.sha(component),'actual_IR_sha256':{n:F.sha(folder/(n+'.ll')) for n in originals},'rows':rows,'target_execution':False,'emulation':False,'network':False,'hardware':False}
    (output/'verification.json').write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'));return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--candidate-folder',type=Path,required=True);p.add_argument('--output-directory',type=Path,required=True);a=p.parse_args();out=a.output_directory.resolve();out.relative_to(HERE);r=run(a.project_root.resolve(),a.firmware.resolve(),a.candidate_folder.resolve(),out);print(json.dumps({'passed':True,'actual_ELF_controls':r['ELF_byte_controls'],'actual_IR_controls':r['IR_controls_rejected'],'report':str(out/'verification.json')}))
if __name__=='__main__':main()
