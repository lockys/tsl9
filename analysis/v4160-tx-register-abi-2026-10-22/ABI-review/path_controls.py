#!/usr/bin/env python3
"""Exercise create-only/path-alias CLI rejections without creating pass outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode=True


def H(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(root,tool,input_object,scratch):
    before=H(input_object);tool_pin=H(tool)
    one=scratch/'must-not-be-created.o';two=scratch/'must-not-be-created.json'
    if one.exists() or two.exists():
        raise ValueError('Path-control sentinels must not exist')
    tests=[('input_output_alias',input_object,two),
           ('input_receipt_alias',one,input_object),
           ('output_receipt_alias',one,one)]
    results=[]
    for name,output,receipt in tests:
        command=[sys.executable,'-B',str(tool),'--project-root',str(root),'--input',str(input_object),
                 '--output',str(output),'--receipt',str(receipt)]
        result=subprocess.run(command,capture_output=True,text=True,encoding='utf8',check=False)
        if result.returncode==0 or 'distinct existing input/create-only output and receipt' not in result.stderr:
            raise ValueError('Expected first path gate did not reject: '+name)
        if H(input_object)!=before or one.exists() or two.exists():
            raise ValueError('Rejected path control wrote an input/output')
        results.append(dict(name=name,actual_CLI_invoked=True,rejected=True,
                            input_unchanged=True,output_and_receipt_not_created=True))
    if H(tool)!=tool_pin:
        raise ValueError('Pass source changed during controls')
    return dict(schema='TSL9-TX-independent-frame-path-controls-v1',tool_sha256=tool_pin,
                input_sha256=before,controls=results,target_execution=False,ISA_emulation=False,
                firmware_generated=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--tool',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    if args.receipt.exists():
        raise ValueError('Create-only independent path receipt')
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    result=inspect(args.project_root.resolve(),args.tool.resolve(),args.input.resolve(),args.receipt.parent.resolve())
    args.receipt.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(all_path_controls_rejected=True,count=len(result['controls']),
                         input_unchanged=True,output_not_created=True)))


if __name__=='__main__':
    main()
