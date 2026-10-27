"""Join actual indirect sites to conditional callback provenance; no target execution."""
import argparse, hashlib, json, re, runpy, sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, label):
    if not ok:
        raise ValueError(label)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    return json.loads(Path(path).read_bytes())

def lib(path):
    return runpy.run_path(str(ROOT / path), run_name='callback_ledger_static_library')

def canonical(value):
    return json.loads(json.dumps(value))

def verify(llvm):
    E = load(HERE / 'evidence-v1.json')
    for field in ['reference_inputs', 'whole_reader_inputs', 'checker_inputs']:
        need(all(sha(ROOT / p) == h for p, h in E[field].items()), 'Pinned ' + field)
    for key, hkey in [('SDK_firmware', 'SDK_firmware_sha256'), ('APP_firmware', 'APP_sha256'),
                      ('primary_header', 'primary_header_sha256'), ('SDK_native_object', 'SDK_native_object_sha256')]:
        need(sha(ROOT / E[key]) == E[hkey], 'Pinned ' + key)
    sdk = (ROOT / E['SDK_firmware']).read_bytes()
    app = (ROOT / E['APP_firmware']).read_bytes()
    V = lib('experiments/tsl9-original-RF-tx-path/audit-v1.py')
    B = lib('experiments/tsl9-original-startup/build-v1.py')
    O = lib(E['whole_reader_study'] + '/verify-ownership-v3.py')
    parent = load(ROOT / E['prior_receipt'])
    P = lib(E['prior_study'] + '/audit-v1.py')
    need(parent['passed'] and parent['checker_sha256'] == sha(ROOT / E['prior_study'] / 'audit-v1.py'), 'Exact retained complete prior receipt')
    # Recheck actual current artifacts and their source/native contracts. The older
    # recursive audit chain is pinned, not claimed to have been rerun here.
    N, native = P['native'](llvm)
    need(native == parent['native_results'] and P['contract'](N, O) == parent['contract'], 'Fresh prior native and complete-body contract')
    compositions = {}
    for mode in ['c', 'cpp']:
        inp = [ROOT / E['whole_reader_study'] / 'build/composition-v1' / mode / 'candidate.o',
               ROOT / E['prior_study'] / 'build/native-v1' / mode / 'unit.o']
        obj = ROOT / E['prior_study'] / 'build/composition-v1' / mode / 'candidate.o'
        compositions[mode] = P['composition'](obj, inp, N, O)
        need(compositions[mode] == parent['composition'][mode], 'Fresh whole composition and independent readers')
    need(compositions['c'] == compositions['cpp'], 'C/C++ native composition equality')
    inventory = lib(E['prior_study'] + '/indirect-inventory-v1.py')['inventory'](compositions['c']['object_sha256'])
    route = lib(E['prior_study'] + '/provenance-v1.py')['provenance']()
    need(inventory == parent['indirect_inventory'] == load(ROOT / E['inventory']), 'Fresh complete indirect inventory')
    need(route == parent['provenance'] == load(ROOT / E['prior_study'] / 'provenance-v1.json'), 'Fresh scheduled table provenance')
    cb = lib('experiments/tsl9-original-callback-provenance/verify-v1.py')
    cbdir = ROOT / 'experiments/tsl9-original-callback-provenance'
    cbproof = cb['static_contract'](load(cbdir / 'spec-v1.json'), load(cbdir / 'evidence-v1.json'))
    need(canonical(cbproof) == load(ROOT / E['APP_callback_provenance'])['contract'], 'Fresh original APP callback/configuration/clock contract')
    binding = load(ROOT / E['APP_binding_proof'])
    need(binding['passed'] and binding['primary_callback_ABI']['passed'] and not binding['staCB_value_at_heap_call_proved'], 'Retain typed callback ABI and earlier heap uncertainty')
    need(binding['conditional_provider_binding']['tsCB_target'] == 0x197f0 and binding['conditional_provider_binding']['rcCB_target'] == 0x197b8, 'Existing explicit original callback targets')
    A=lib('experiments/tsl9-original-APP-library-binding/verify-v1.py')
    original_refs=load(ROOT/E['APP_binding_evidence'])['APP']['references']
    callbacks=[f for f in original_refs if f['start'] in [0x197b8,0x197f0]]
    need(len(callbacks)==2,'Both complete sample/calibration callback references')
    EL=lib(E['whole_reader_study']+'/elf_reader-v7.py')['ELF']
    Other=lib('analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py')['ELF']
    for mode,path in E['APP_native_diagnostic_paths'].items():
        need(sha(ROOT/path)==E['APP_native_diagnostic_sha256'],'Unchanged nonloadable APP diagnostic')
        e,other=EL(ROOT/path),Other(ROOT/path)
        need(e.header[0]==other.kind==2 and not any(h[0]==1 for h in e.program_headers),'Native APP witness has no loadable segment')
        for f in callbacks:
            raw=app[f['start']-0x8000:f['end']-0x8000]
            need(raw==b''.join(bytes.fromhex(o['bytes'])for o in f['operations']) and sha_bytes(raw)==f['original_sha256'],'Complete original APP callback bytes')
            x,owners_a=A['native_bytes'](e,f['start'],f['end'],True)
            y,owners_b=A['native_bytes'](other,f['start'],f['end'],True)
            need(x==y==raw and owners_a==owners_b,'Two readers verify both callback native witnesses')
    byte_map = O['inspect'](ROOT / E['SDK_native_object'])['_byte_map']
    op, graphs, owners, functions = {}, {}, {}, []
    for scope in E['SDK_scopes']:
        need(sha(ROOT / scope['path']) == scope['sha256'], 'Exact complete SDK evidence scope')
        selected = [f for f in load(ROOT / scope['path'])['selected_functions'] if f['start'] in scope['entries']]
        need(len(selected) == len(scope['entries']), 'All selected complete functions exist')
        for f in selected:
            raw = b''.join(bytes.fromhex(o['bytes']) for o in f['operations'])
            need(raw == sdk[f['source_start'] - 0x40000:f['source_end'] - 0x40000] and sha_bytes(raw) == f['original_sha256'], 'Every complete original SDK byte')
            need(all(pc in byte_map for pc in range(f['start'], f['end'])), 'Every selected SDK byte has a current native owner')
            frame = max([int(m[1]) for o in f['operations'] if (m := re.fullmatch(r'addi sp, sp, -(\d+)', o['opcode']))] or [0])
            ext = {d[1] for o in f['operations'] if (d := B['decode_control'](bytes.fromhex(o['bytes']), o['addr']))}
            oo, g, row = V['whole_cfg'](f, B, ext, frame)
            need(not set(oo) & set(op), 'No duplicate selected whole function')
            op.update(oo); graphs[f['start']] = g; functions.append(row)
            owners.update({p: f['start'] for p in oo})
        need(all(site in op for site in scope['sites']), 'All requested original indirect sites exist')
    need(len(functions) == 14 and sum(q['instructions'] for q in functions) == 1629, 'Fourteen complete SDK scopes / 1629 instructions')
    def exact(mapping):
        for pc,expected in mapping.items():
            need(op[pc]['opcode']==expected, f'Exact callback operand at {pc:#x}: expected {expected}; found {op[pc]["opcode"]}')
    def dominates(site, pcs):
        root = owners[site]; g = graphs[root]
        need(all(site not in V['reachable'](g, root, skip=p) for p in pcs), 'Pointer setup/load dominates actual call')
    def pointer_path(site, load_pc, register, setup):
        dominates(site, setup + [load_pc])
        root = owners[site]; g = graphs[root]; rev = {p: [] for p in g}
        for p, ns in g.items():
            for n in ns: rev[n].append(p)
        path = sorted(V['reachable'](g, load_pc, skip=site) & V['reachable'](rev, site))
        # Explicitly allow ordinary stores/branches and calls preserving the
        # selected saved register. Do not infer callee ABI compliance from CFG.
        for pc in path:
            if pc == load_pc: continue
            o = op[pc]; text = o['opcode']
            if o['type'] in ['call', 'ucall']:
                need(register.startswith('s'), 'Live callback pointer across call requires saved register')
            elif o['type'] not in ['store', 'cjmp', 'jmp']:
                operands = text.partition(' ')[2]
                need(operands.split(',')[0] != register, 'Loaded callback register is not explicitly overwritten')
        return dict(load_PC=load_pc, setup_PCs=setup, register=register, path_PCs=path,
                    local_dominance_proved=True, no_explicit_pointer_register_overwrite=True,
                    intervening_calls_require_private_saved_register_contract=any(op[p]['type'] in ['call', 'ucall'] for p in path))
    rows = []
    common = ['matching installed ROM is required but not proved', 'valid disjoint memory and stack',
              'original private ABI and normal callee returns', 'no asynchronous overwrite or reentrant binding replacement']
    def add(site, family, target=None, slot=None, conditions=None, outcome='conditional-target', witnesses=None):
        rows.append(dict(PC=site, function=owners[site], family=family, outcome=outcome,
                         target_original_PC=target, pointer_slot=slot, original_instruction=op[site]['opcode'],
                         conditions=common + (conditions or []), witnesses=witnesses or {}, live_binding_proved=False))
    clock = [(0x4346c,0x4345a,0x4345e,'a5',0x200031e0), (0x43d7a,0x43d66,0x43d6a,'a5',0x20003234),
             (0x437ca,0x43758,0x4375c,'s7',0x200031e0), (0x5f6d6,0x5f6a8,0x5f6ce,'a5',0x20003234),
             (0x5f708,0x5f6f8,0x5f6fc,'a5',0x200031e0), (0x648be,0x648b4,0x648b8,'a5',0x200031e0),
             (0x65ec2,0x65eb6,0x65eba,'a5',0x200031e0)]
    for site, base, load_pc, reg, slot in clock:
        base_reg = {'s7':'a5'}.get(reg, reg)
        if site == 0x43d7a: base_reg = 's2'
        if site == 0x5f6d6: base_reg = 's8'
        exact({base:'lui ' + base_reg + ', 0x20003', load_pc:f'lw {reg}, {slot-0x20003000}({base_reg})', site:'jalr ' + reg})
        add(site,'raw-clock',0x191c6,slot,['accepted original nonnull 16-byte clock configuration copied; both clock slots stable',
             'MMIO termination/coherence/frequency and physical meaning remain unproved'], witnesses=pointer_path(site,load_pc,reg,[base]))
    exact({0x43fd2:'lui a0, 0x44',0x43fd6:'addi a0, a0, -670',0x43fda:'jal 0x43b0a',
           0x43b0c:'lui a5, 0x20003',0x43b12:'sw a0, 560(a5)',0x43b16:'jalr a0',0x43b1e:'sw a0, 436(a5)',
           0x43520:'lui a5, 0x20003',0x43524:'lw a5, 560(a5)',0x43536:'beqz a5, 0x43540',0x43538:'jalr a5'})
    need((0x44000-670)==0x43d62, 'Provider literal arithmetic')
    dominates(0x43fda,[0x43fd2,0x43fd6]); dominates(0x43b16,[0x43b12])
    incoming_path=V['reachable'](graphs[0x43b0a],0x43b0a,skip=0x43b16)
    need(all(op[p]['type']=='store' or op[p]['opcode'].partition(' ')[2].split(',')[0]!='a0'
             for p in incoming_path),'Registration helper retains incoming A0 until callback invocation')
    add(0x43b16,'provider',0x43d62,0x20003230,['only the TimerInit caller context 0x43FDA passing A0=0x43D62',
        'registration helper other caller contexts are not resolved'],witnesses=dict(caller=0x43fda,literal_PCs=[0x43fd2,0x43fd6],store_PC=0x43b12))
    add(0x43538,'provider',0x43d62,0x20003230,['after the above provider registration and no later slot overwrite',
        'provider subsequently loads raw-clock separately at 0x43D7A'],witnesses=pointer_path(0x43538,0x43524,'a5',[0x43520]))
    samples = [(0x43d38,0x43d34,'a5',[0x43cc4,0x43cec],0x197f0,44),
               (0x43ef6,0x43ee4,'a4',[0x43edc,0x43ee0],0x197f0,44),
               (0x43f30,0x43f2a,'a5',[0x43ef2],0x197b8,48),
               (0x43f60,0x43f52,'a5',[0x43f4a,0x43f4e],0x197b8,48)]
    exact({0x43d34:'lw a5, 44(a5)',0x43d36:'beqz a5, 0x43d42',0x43d38:'jalr a5',
           0x43edc:'lui a5, 0x20003',0x43ee0:'addi a4, a5, 492',0x43ee4:'lw a4, 44(a4)',0x43ef6:'jalr a4',
           0x43ef2:'addi s2, a5, 492',0x43f2a:'lw a5, 48(s2)',0x43f30:'jalr a5',
           0x43f4a:'lui s0, 0x20003',0x43f4e:'addi a5, s0, 492',0x43f52:'lw a5, 48(a5)',
           0x43f5c:'beqz a5, 0x43f64',0x43f60:'jalr a5',0x43f64:'beqz a1, 0x43fe6',0x43f66:'lw a5, 0(a1)'})
    need(0x43f60 < 0x43f64 < 0x43f66, 'Calibration invocation precedes clock pointer validation')
    for site,load_pc,reg,setup,target,offset in samples:
        conditions=['original 64-byte BLE configuration copy to 0x200031EC with original tsCB/rcCB fields; stable until invocation',
                    'callback return/physical ADC or calibration effects are not fully closed']
        if site==0x43f60: conditions.append('does not require accepted clock configuration: calibration call is earlier than clock validation')
        add(site,'sample' if offset==44 else 'calibration',target,0x200031ec+offset,conditions,witnesses=pointer_path(site,load_pc,reg,setup))
    status = [(0x434aa,0x434a4,0x434ac),(0x43842,0x4383c,0x43764),
              (0x200000a0,0x20000098,0x2000005a),(0x59e14,0x59e0c,0x59e22),(0x59e20,0x59e0c,0x59e22)]
    exact({0x4349c:'lui a5, 0x20003',0x434a0:'lw a5, 544(a5)',0x434a4:'beqz a5, 0x434ac',
           0x43834:'lui a5, 0x20003',0x43838:'lw a5, 544(a5)',0x4383c:'beqz a5, 0x43764',
           0x20000090:'lui a4, 0x20003',0x20000094:'lw a4, 544(a4)',0x20000098:'beqz a4, 0x2000005a',
           0x59e00:'lui s2, 0x20003',0x59e04:'addi s2, s2, 492',0x59e08:'lw a5, 52(s2)',
           0x59e0c:'beqz a5, 0x59e22',0x59e16:'lw a5, 52(s2)',0x59e14:'jalr a5',0x59e20:'jalr a5'})
    for site,guard,zero in status:
        g=graphs[owners[site]]
        dominates(site,[guard]); need(g[guard][0]==zero and site not in V['reachable'](g,zero), 'Known zero branch skips this activation callback')
        add(site,'status-zero',slot=0x20003220,outcome='conditional-skipped',conditions=[
            'post-known-BLE-copy zero staCB field remains zero at first guard',
            'earlier pre-copy heap-call value is not proved',
            '0x59E20 is skipped by the FIRST 0x59E0C guard; no added second null guard'],
            witnesses=dict(guard_PC=guard,zero_branch=zero,zero_branch_cannot_reach_call=True))
    need(route['conditional_original_PC_provenance_proved'] and route['ID31_and47_not_covered_by_callback_route_proof'], 'Retain bounded scheduled table route')
    add(0x43390,'scheduled-record',0x56cdc,0x2000322c,[
        'only original producer record and selected table entry under prior provenance conditions',
        'i=16*t+k, t in {1,2}, k in [0,14], single event A1=1<<k',
        'bit15 message path and IDs31/47 excluded from route proof, not declared unusable',
        'initialization-before-dispatch and actual timer delivery unproved'],witnesses=dict(provenance=E['prior_study']+'/provenance-v1.json'))
    sites=inventory['register_transfer_sites_requiring_separate_binding_analysis'];all_sites={s['PC']for s in sites}
    joined={r['PC']for r in rows};need(len(rows)==len(joined)==19 and joined<=all_sites and len(all_sites)==51,'Exactly nineteen distinct joins from actual fifty-one sites')
    rest=[dict(PC=s['PC'],outcome='not-joined-in-this-ledger',prior_proofs_not_overridden=True)for s in sites if s['PC']not in joined]
    need(len(rest)==32,'Thirty-two other sites are not missing-function count')
    ledger=dict(schema='TSL9-conditional-callback-binding-ledger-v1',passed=True,rows=sorted(rows,key=lambda r:r['PC']),
        other_sites=rest,counts=dict(actual_register_sites=51,conditionally_joined=19,conditional_target=14,conditional_skipped=5,not_joined_here=32),
        families=dict(raw_clock=7,provider=2,sample=2,calibration=2,status_zero=5,scheduled_record=1),
        no_universal_or_live_binding_claim=True,prior_conditional_proofs_not_overridden=True,missing_function_count_not_inferred=True)
    result=dict(schema='TSL9-callback-binding-ledger-verification-v1',passed=True,checker_sha256=sha(__file__),
        evidence_sha256=sha(HERE/'evidence-v1.json'),ledger=ledger,SDK_whole_functions=functions,
        SDK_reference_CODE_bytes=sum(f['bytes']for f in functions),SDK_reference_instructions=1629,
        original_APP_callback_contract_freshly_checked=True,prior_current_native_and_composition_freshly_checked=True,
        older_recursive_chain_rerun=False,older_receipts_pinned=True,composition=compositions['c'],
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,
        new_target_CODE_bytes=0,new_target_DATA_bytes=0,new_target_compilation=False,
        inherited_startup_source_gap_bytes=4,staCB_value_at_earlier_heap_call_proved=False,
        actual_global_binding_before_any_dispatch_proved=False,physical_compatibility_proved=False,
        runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
    return result

def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',type=Path,required=True)
    p.add_argument('--write-receipts',action='store_true')
    a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve())
        if a.write_receipts:
            for name,value in [('ledger-v1.json',v['ledger']),('verification-v1.json',v)]:
                dest=HERE/name;need(not dest.exists(),'Create-only verification receipt')
                dest.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,**v['ledger']['counts'],SDK_reference_instructions=1629,new_BIN=False,firmware_ready=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:
            message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)))
        raise SystemExit(1)
