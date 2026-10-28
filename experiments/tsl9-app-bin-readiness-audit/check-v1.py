"""Inspect actual retained APP/SDK artifacts;exit2 means inspected but not firmware-ready."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]

def need(ok,label):
 if not ok:raise ValueError(label)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):return json.loads(Path(p).read_bytes())

def lib(p):return runpy.run_path(str(R/p),run_name='actual_app_bin_evidence_library')

def runs(values):
 out=[]
 for a in sorted(values):
  if not out or a!=out[-1]['end']:out.append(dict(start=a,end=a+1,bytes=1))
  else:out[-1]['end']=a+1;out[-1]['bytes']+=1
 return out

def audit(llvm):
 K=read(HERE/'inputs-v1.json')
 for p,h in K['pins'].items():
  need(not Path(p).is_absolute()and'..'not in Path(p).parts and'command_dispatch_windows'not in p,'Only bounded allowed evidence paths')
  need(sha(R/p)==h,'Frozen actual input changed: '+p)
 for name,h in K['tools'].items():need(sha(llvm/name)==h,'Pinned native tool identity')
 A=lib(K['formal_audit']);formal=A['audit'](llvm)
 need(A['canonical'](formal)==read(R/K['formal_receipt']),'Fresh retained formal native/source proof equals receipt')
 need(formal['source_C_H_files']==162 and formal['original_coordinate_bytes_equal']==73478 and formal['coverage_percent']==95.67 and formal['other_unselected_bytes']==194,'Actual formal APP baseline')
 L=lib(K['layout_builder']);E=L['E'];components={mode:E(R/K['APP_component']/mode/K['APP_object'])for mode in ['c','cpp']};component=components['c'];plan=L['derive'](component)
 need(sha(R/K['APP_component']/'c'/K['APP_object'])==sha(R/K['APP_component']/'cpp'/K['APP_object']),'Actual formal C/C++ objects identical')
 expected={
  'tsl9_boot_resident_40000':('resident_ROM_ABI_dependency',0x40000),
  'tsl9_incoming_external_14056':('currently_excluded_APP_CODE',0x14056),
  'tsl9_input_state_decoders_static_data_1ab48':('undefined_DATA_provider_use_contract',0x1ab48),
  'tsl9_record_field_transitions_static_data_1a078':('undefined_DATA_provider_use_contract',0x1a078),
  'tsl9_registered_callbacks_static_data_1a638':('undefined_DATA_provider_use_contract',0x1a638),
  'tsl9_settings_default_data_1a69c':('currently_excluded_APP_default_DATA',0x1a69c)}
 undef=sorted(s['name']for s in component.symbols if s['name']and s['section']==0)
 need(set(undef)==set(expected)and len(plan['imports'])==6,'Actual six project provider imports,not assumed standard compiler libraries')
 owned={p for o in plan['owners']for p in range(o['original_PC'],o['original_PC']+o['bytes'])};domain=set(range(0x8000,0x1ac00));excluded=set(range(0x14056,0x14c8a))|set(range(0x1a69c,0x1a6a0));missing=domain-owned
 need(owned<=domain and not owned&excluded and len(owned)==73478 and len(missing)==3322 and len(missing&excluded)==3128,'Exact native APP coverage without excluded source material')
 other=runs(missing-excluded);need(sum(x['bytes']for x in other)==194 and len(other)==34,'Actual unselected address metadata only;no gap filling or payload inspection')
 providers=[]
 for name,(kind,pc)in expected.items():
  owners=[dict(name=o['name'],start=o['original_PC'],bytes=o['bytes'],offset=pc-o['original_PC'])for o in plan['owners']if o['info']==17 and o['original_PC']<=pc<o['original_PC']+o['bytes']]
  providers.append(dict(name=name,original_reference=pc,classification=kind,undefined_in_actual_APP_object=True,positive_DATA_backing_at_reference=owners,full_provider_definition_proved=False,must_not_fake_with_alias_or_stub=True))
 diagnostics={mode:E(R/K['APP_layout']/mode/'NONLOADABLE-ORIGINAL-LAYOUT.elf')for mode in ['c','cpp']};diag=diagnostics['c']
 need(sha(R/K['APP_layout']/'c/NONLOADABLE-ORIGINAL-LAYOUT.elf')==sha(R/K['APP_layout']/'cpp/NONLOADABLE-ORIGINAL-LAYOUT.elf'),'Actual C/C++ original-coordinate diagnostics identical')
 load_count=sum(p[0]==1 for p in diag.program_headers);need((diag.header[0],diag.header[1],diag.header[3],load_count)==(2,243,0,0)and diag.program_headers and all(p[0]==0 for p in diag.program_headers),'Actual diagnostic ET_EXEC,entry0,PT_NULL only')
 refs=[s for s in diag.symbols if s['name'].startswith('__rea_original_reference_')]
 need(len(refs)==6 and all((s['section'],s['info'],s['other'],s['size'])==(0xfff1,0,2,0)for s in refs),'Only hidden NOTYPE ABS reference constants;no function/provider implementation')
 need({s['value']for s in refs}=={pc for _,pc in expected.values()},'Exact original reference coordinates')
 sdk=read(R/K['SDK_receipt']);need(sdk['passed']and not sdk['SDK_linked_into_APP']and not sdk['physical_compatibility_proved'],'SDK reference remains separate from APP and physical proof')
 O=lib(K['SDK_owner_reader']);sdkowners=O['inspect'](R/K['SDK_component']/'c/candidate.o')
 need(sha(R/K['SDK_component']/'c/candidate.o')==sha(R/K['SDK_component']/'cpp/candidate.o')==sdk['SDK_composition']['c']['object_sha256'],'Actual retained C/C++ SDK object identity')
 need((sdkowners['CODE_bytes'],len(sdkowners['named_UND']))==(54780,18)and sdkowners['duplicate_original_CODE_bytes']==0,'Actual SDK ownership and remaining ordinary imports')
 prefix=read(R/K['startup_prefix_receipt']);trap=read(R/K['trap_summary']);ram=read(R/K['RAM_summary'])
 need(prefix['passed']and prefix['inherited_startup_source_gap_bytes']==4 and not prefix['complete_startup_proved'],'Archived SDK source gap remains explicit')
 need(not trap['installed_ROM_identity_proved']and not trap['physical_Xwchc_profile_proved']and not trap['physical_trap_route_proved'],'Inspected trap evidence does not prove the installed physical profile')
 need(not ram['physical_RAM_capacity_proved']and not ram['whole_program_stack_or_IRQ_bound_proved']and not ram['heap_or_APP_global_ownership_proved'],'Inspected RAM evidence does not prove device capacity or ownership')
 gates=[
  dict(id='curated_APP_source_evidence',status='proved',evidence=K['formal_receipt'],detail='Fresh actual162-source/original-coordinate evidence retained;this is not full-image or physical proof'),
  dict(id='APP_source_byte_completeness',status='not_ready',evidence=K['APP_component'],detail='3322 APP bytes remain unselected:3128 currently excluded and194 other;no padding or copied vendor gap bytes supplied'),
  dict(id='APP_source_provider_definitions',status='not_ready',evidence=K['APP_component'],detail='Six project providers remain undefined;existing DATA backing and hidden ABS references do not define their complete use contracts'),
  dict(id='loadable_rebuilt_APP_artifact',status='not_ready',evidence=K['APP_layout'],detail='Measured artifact has entry0 and zero PT_LOAD;it is intentionally diagnostic,not a firmware BIN'),
  dict(id='installed_resident_ROM_ABI',status='not_proven',evidence=K['SDK_receipt'],detail='Archived candidate CODE at40000 is not installed-ROM identity or ABI proof;resident code need not be copied into APP merely to reduce an import count'),
  dict(id='startup_and_interrupt_binding',status='not_proven',evidence=K['trap_summary'],detail='Original8034->8038 conservative boundary and physical trap/ISA binding remain unresolved'),
  dict(id='device_RAM_stack_and_global_ownership',status='not_proven',evidence=K['RAM_summary'],detail='Physical RAM capacity,whole-program stack/IRQ bounds and heap/APP-global ownership remain unproved'),
  dict(id='Flash_OTA_layout_and_rebuilt_device_behavior',status='not_proven',evidence=K['formal_receipt'],detail='No loadable rebuilt image or artifact-matched physical boot/function evidence;transport completion alone would not prove these')]
 ready=all(g['status']=='proved'for g in gates);need(not ready,'Inspected real artifacts must not be labeled flash-ready')
 return dict(schema='TSL9-actual-APP-BIN-readiness-v1',evidence_audit_passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),gates=gates,firmware_ready=ready,expected_not_ready_exit_code=2,APP_source_C_H_files=162,APP_CODE_bytes=69412,APP_DATA_bytes=4066,APP_selected_original_coordinate_bytes=73478,APP_domain=[0x8000,0x1ac00],APP_domain_bytes=76800,APP_static_byte_coverage_percent=95.67,coverage_is_not_function_completion=True,APP_source_undefined_symbols=providers,standard_compiler_runtime_symbols_in_actual_UND=[],legacy_compiler_UND_field_is_project_provider_count=True,APP_missing_bytes=3322,APP_excluded_missing_bytes=3128,APP_other_unselected_bytes=194,APP_other_unselected_ranges=other,missing_payload_not_selected_or_output=True,missing_payload_individual_hashes_not_output=True,APP_diagnostic=dict(ELF_type=diag.header[0],machine=diag.header[1],entry=diag.header[3],PT_LOAD_count=load_count,program_header_types=[p[0]for p in diag.program_headers],hidden_reference_only_ABS_constants=6,ABS_FUNC_providers=0),resident_reference=dict(SDK_CODE_bytes=54780,SDK_DATA_bytes=412,ordinary_UND=len(sdkowners['named_UND']),entry40000_original_coordinate_byte_owned=0x40000 in sdkowners['_byte_map'],installed_ROM_identity_proved=False,linked_into_APP=False,not_added_to_APP_coverage=True,archived_startup_missing_source_range=[0x6eb2c,0x6eb30],archived_startup_missing_source_bytes=4,that_source_gap_is_not_APP_four_missing_bytes=True),required_next_work=['Resolve the actual APP provider obligations under the current selection/privacy scope;do not substitute standard compiler libraries','Classify the194 other unselected bytes only when they close a runtime/layout requirement;do not raise coverage by arbitrary padding','Establish installed resident-ROM ABI/startup/IRQ/RAM/Flash mapping;do not assume rebuilding the whole archived ROM is required inside APP','Produce a genuinely loadable artifact only after required bytes/providers/layout and allowed scope are resolved','Keep OTA transport,artifact identity,boot and functional verification separate;use actual device evidence before any flash-ready claim'],source_or_native_artifact_changed=False,new_APP_CODE_or_DATA_bytes=0,new_SDK_CODE_or_DATA_bytes=0,new_BIN=False,full_firmware_rebuilt=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
 try:
  v=audit(a.tool_dir.resolve());dest=HERE/'report-v1.json'
  if a.write_receipt:
   need(not dest.exists(),'Create-only actual readiness receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
  else:need(dest.exists()and v==read(dest),'Fresh actual audit equals retained readiness receipt')
  print(json.dumps(dict(evidence_audit_passed=True,firmware_ready=v['firmware_ready'],APP_source_undefined_symbols=len(v['APP_source_undefined_symbols']),APP_other_unselected_bytes=v['APP_other_unselected_bytes'],entry=v['APP_diagnostic']['entry'],PT_LOAD_count=v['APP_diagnostic']['PT_LOAD_count'],SDK_ordinary_UND=v['resident_reference']['ordinary_UND'],not_ready_gate_ids=[g['id']for g in v['gates']if g['status']!='proved'],new_BIN=False,exit_code=0 if v['firmware_ready']else 2)))
  raise SystemExit(0 if v['firmware_ready']else 2)
 except Exception as e:
  message=str(e)
  for p,t in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
  print(json.dumps(dict(evidence_audit_passed=False,error_type=type(e).__name__,reason=message)));raise SystemExit(1)
