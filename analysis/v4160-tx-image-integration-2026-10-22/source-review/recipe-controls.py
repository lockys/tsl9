"""Focused mutations of actual command/dependency records; no compiler execution."""
import copy

def inspect(R,P,root,firmware,folder,r):
    c=P.context(R,root,firmware);tools={k:__import__('pathlib').Path(v['path']).resolve() for k,v in r['tools'].items()};expected=P.recipes(R,root,folder,r['mode'],tools,c);rows=[]
    def rejects(name,operation):
        try:operation()
        except ValueError:rows.append(name);return
        raise ValueError('Accepted independent provenance control: '+name)
    for name in ('chronology','TX source substitution','ASM preprocessor','TX scheduling bypass','missing bytecode guard','wrong language','original BIN codegen'):
        commands=copy.deepcopy(r['commands']);by={x['label']:x for x in commands}
        if name=='chronology':commands[59],commands[60]=commands[60],commands[59]
        elif name=='TX source substitution':a=by['tx-valid_body-object']['argv'];a[a.index('-c')+1]=str(root/'experiments/tsl9-v4160-tx-register-abi/src/tx_native.c')
        elif name=='ASM preprocessor':a=by['tx-entry-object']['argv'];a[a.index('-x')+1]='assembler-with-cpp'
        elif name=='TX scheduling bypass':a=by['merge-typed']['argv'];a[a.index(str(folder/'tx-valid_body-ordered.o'))]=str(folder/'tx-valid_body.o')
        elif name=='missing bytecode guard':by['explicit-tx-frame-ordering']['argv'].remove('-B')
        elif name=='wrong language':a=by['tx-valid_body-IR']['argv'];a[a.index('-x')+1]='c++' if r['mode']=='c' else 'c'
        else:by['merge-source-integrated']['argv'].insert(-2,str(firmware))
        rejects(name,lambda:P.command_gate(R,commands,expected))
    unit=next(u for u in c['units'](r['mode']) if u['label']=='reply');adapter=folder/'reply-adapter.h';text=(folder/'reply.d').read_text();primary=unit['source'];parser=c['P'].dependency
    rejects('dependency wrong target',lambda:parser(text,'other.o',primary,adapter))
    rejects('dependency wrong primary',lambda:parser(text,'reply.o',root/'experiments/tsl9-v4160-tx-register-abi/adapter/valid_body.c',adapter))
    rejects('dependency missing own forced adapter',lambda:parser(text,'reply.o',primary,folder/'main-adapter.h'))
    for name in ('omitted actual IR artifact pin','outer generation log pin','preflight query argv','missing direct ASM stability pin'):
        altered=copy.deepcopy(r)
        if name=='omitted actual IR artifact pin':del altered['artifacts'][next(n for n in altered['artifacts'] if n.endswith('.ll'))]
        elif name=='outer generation log pin':altered['generation_invocation']['sha256']='0'*64
        elif name=='preflight query argv':altered['preflight_query']['argv'].append('-unexpected')
        else:del altered['input_stability_pins'][str(root/'experiments/tsl9-v4160-tx-image-integration/adapter/entry.S')]
        rejects(name,lambda:P.inspect(R,root,firmware,folder,altered))
    return dict(passed=True,focused_recipe_dependency_controls=len(rows),controls=rows,execution=False)
