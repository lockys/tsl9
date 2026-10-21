"""Focused mutations of actual recorded recipes and Make rules; no commands run."""
import copy
from pathlib import Path
import shlex
import sys
sys.dont_write_bytecode=True

def need(value,message):
    if not value:raise ValueError(message)
def rejected(name,call):
    try:call()
    except ValueError as error:return {'case':name,'rejected':True,'reason':str(error),'compiled_or_target_executed':False}
    raise ValueError('Accepted focused source/provenance countercase '+name)
def inspect(gate,root,folder,receipt,source,firmware):
    units,E,bindings=gate.profiles(root,firmware,source['manifest']);tools={name:Path(row['path']).resolve() for name,row in receipt['tools'].items()};expected=gate.expected_commands(root,folder,receipt['mode'],source['manifest'],tools,units);original=receipt['commands'];gate.commands_gate(original,expected);controls=[]
    def command(name,label,edit):
        rows=copy.deepcopy(original);row=next(row for row in rows if row['label']==label);edit(row['argv']);controls.append(rejected(name,lambda:gate.commands_gate(rows,expected)))
    rows=copy.deepcopy(original);a=next(i for i,row in enumerate(rows) if row['label']=='explicit-reply-ordering');b=next(i for i,row in enumerate(rows) if row['label']=='merge-typed');rows[a],rows[b]=rows[b],rows[a];controls.append(rejected('typed_merge_before_standalone_reply_order',lambda:gate.commands_gate(rows,expected)))
    command('typed_merge_uses_raw_reply','merge-typed',lambda args:args.__setitem__(args.index(str(folder/'reply-ordered.o')),str(folder/'reply.o')))
    command('reply_pass_uses_full_merged_object','explicit-reply-ordering',lambda args:args.__setitem__(args.index('--input')+1,str(folder/'pre-frame-integrated.o')))
    command('reply_pass_overwrites_final_partial','explicit-reply-ordering',lambda args:args.__setitem__(args.index('--output')+1,str(folder/'source-integrated.o')))
    command('frame_pass_uses_standalone_reply','explicit-frame-scheduling',lambda args:args.__setitem__(args.index('--input')+1,str(folder/'reply-ordered.o')))
    command('typed_reply_compiles_host_adapter_instead','typed-reply-object',lambda args:args.__setitem__(args.index('-c')+1,str(root/'experiments/tsl9-v4160-ota-page-reply/src/host_io.c')))
    command('typed_reply_hidden_response_file','typed-reply-IR',lambda args:args.insert(1,'@hidden-profile.rsp'))
    command('reply_omits_resource_headers_MMD','typed-reply-object',lambda args:args.__setitem__(args.index('-MD'),'-MMD'))
    command('resource_query_wrong_tool','compiler-resource-dir',lambda args:args.__setitem__(0,str(tools['linker'])))
    command('raw_reply_carrier_unfiltered','compile-ota_handler_native',lambda args:args.__setitem__(args.index('-c')+1,str(root/'experiments/tsl9-v4160-startup/src/ota_handler_native.c')))
    path=folder/'reply.d';text=path.read_text(encoding='utf-8');primary=root/'experiments/tsl9-v4160-ota-page-reply/src/page_reply.c';adapter=folder/'reply-adapter.h';paths=gate.dependency(text,'reply.o',primary,adapter)
    def rule(target,dependencies):return target+': '+' '.join(shlex.quote(path.as_posix()) for path in dependencies)+'\n'
    controls.append(rejected('dependency_wrong_own_object_target',lambda:gate.dependency(rule('main.o',paths),'reply.o',primary,adapter)))
    changed=list(paths);changed[0]=root/'experiments/tsl9-v4160-irq-callframe/src/rcc_helpers.c';controls.append(rejected('dependency_wrong_first_primary_source',lambda:gate.dependency(rule('reply.o',changed),'reply.o',primary,adapter)))
    controls.append(rejected('dependency_missing_own_adapter',lambda:gate.dependency(rule('reply.o',[path for path in paths if path!=adapter]),'reply.o',primary,adapter)))
    need(len(controls)==13 and all(row['rejected'] for row in controls),'Ten recipe and three dependency controls');return controls
