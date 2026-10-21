#!/usr/bin/env python3
"""Two actual recipe-record mutations; no compiler or target is launched."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
G=load('language_control_context',HERE/'image-gate.py')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--output-directory',type=Path,required=True);a=p.parse_args();root=a.project_root.resolve();receipt=a.receipt.resolve();folder=receipt.parent;output=a.output_directory.resolve();output.relative_to(HERE);G.need(not output.exists(),'Create-only independent recipe controls');pins=G.read(HERE/'review-inputs.json');c=G.context(root,a.firmware.resolve(),pins['manifest_sha256']);P=load('language_control_provenance',HERE/'provenance.py');r=G.read(receipt);P.inspect(root,folder,r,c);output.mkdir(parents=True)
    mode=copy.deepcopy(r);mode['mode']='cpp' if r['mode']=='c' else 'c';standard=copy.deepcopy(r);command=next(x for x in standard['commands'] if x['label']=='typed-flash-program-IR');index=next(i for i,x in enumerate(command['argv']) if x.startswith('-std='));command['argv'][index]='-std=c++17' if r['mode']=='c' else '-std=c11';rows=[]
    for name,mutant in [('receipt_mode_contradicts_all_actual_recipes',mode),('typed_IR_standard_contradicts_recorded_language',standard)]:
        path=output/(name+'.json');path.write_bytes((json.dumps(mutant,indent=2)+'\n').encode('utf-8'))
        try:P.inspect(root,folder,G.read(path),c)
        except ValueError as error:reason=str(error);G.need('claimed C11/C++17' in reason,'Rejected by the specific source-language gate')
        else:raise ValueError('Accepted contradictory source-language record')
        rows.append({'case':name,'actual_mutated_file_sha256':G.sha(path),'rejected':True,'reason':reason})
    result={'schema':'ID2966-independent-wholeimage-language-controls-v1','passed':True,'actual_record_controls':2,'baseline_receipt_sha256':G.sha(receipt),'provenance_checker_sha256':G.sha(HERE/'provenance.py'),'rows':rows,'new_compilations':0,'target_execution':False,'ISA_emulation':False,'network':False,'hardware':False};(output/'verification.json').write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'));print(json.dumps({'passed':True,'controls':2,'report':str(output/'verification.json')}))
if __name__=='__main__':main()
