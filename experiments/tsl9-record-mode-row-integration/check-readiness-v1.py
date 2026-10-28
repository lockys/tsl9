"""Audit current source/native evidence;exit2 means verified evidence but firmware not ready."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
 if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit(llvm):
 Q=runpy.run_path(str(HERE/'audit-v1.py'),run_name='current_mode_row_readiness');v=Q['audit'](llvm);need(v==json.loads((HERE/'audit-result-v1.json').read_bytes()),'Fresh whole source/native evidence equals formal receipt');n=v['native_layout_result']
 gates=[dict(name='formal_source_and_native_evidence',status='proved'),dict(name='complete_APP_bytes',status='proved'if v['original_coordinate_bytes_equal']==76800 else'incomplete'),dict(name='all_APP_source_providers_defined',status='proved'if v['compiler_UND']==0 else'incomplete'),dict(name='loadable_firmware_artifact',status='proved'if n['PT_LOAD_count']>0 and n['entry']!=0 and n['firmware_BIN_generated']else'incomplete'),dict(name='installed_ROM_and_private_ABI',status='proved'if n['physical_MCU_ROM_RAM_IRQ_OTA_proved']and n['private_ABI_proved']else'not_proved'),dict(name='startup_and_IRQ_execution',status='proved'if n['physical_MCU_ROM_RAM_IRQ_OTA_proved']and not v['conservative_continuation_observations']else'not_proved'),dict(name='physical_RAM_ownership',status='proved'if n['physical_MCU_ROM_RAM_IRQ_OTA_proved']else'not_proved'),dict(name='Flash_OTA_and_rebuilt_device_behavior',status='proved'if v['installed_ROM_RAM_IRQ_Flash_OTA_proved']and v['full_firmware_rebuilt']else'not_proved')]
 ready=all(g['status']=='proved'for g in gates)
 return dict(schema='TSL9-current-mode-row-APP-BIN-readiness-v1',evidence_verified=True,checker_sha256=sha(__file__),audit_receipt_sha256=sha(HERE/'audit-result-v1.json'),source_C_H_files=v['source_C_H_files'],original_coordinate_bytes_equal=v['original_coordinate_bytes_equal'],coverage_percent=v['coverage_percent'],uncovered_bytes=v['uncovered_bytes'],APP_source_provider_UND=v['compiler_UND'],diagnostic_ELF_sha256=n['ELF_sha256'],diagnostic_entry=n['entry'],diagnostic_PT_LOAD_count=n['PT_LOAD_count'],gates=gates,gate_count=len(gates),proved_gates=sum(g['status']=='proved'for g in gates),firmware_ready=ready,new_BIN=n['firmware_BIN_generated'],source_or_artifact_modified=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,exit_code=0 if ready else 2)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
 try:
  v=audit(a.tool_dir.resolve());dest=HERE/'readiness-v1.json'
  if a.write_receipt:need(not dest.exists(),'Create-only actual readiness receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
  else:need(v==json.loads(dest.read_bytes()),'Fresh actual readiness equals retained receipt')
  print(json.dumps(v));raise SystemExit(v['exit_code'])
 except Exception as e:
  message=str(e)
  for path,label in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),label).replace(path.as_posix(),label)
  print(json.dumps(dict(evidence_verified=False,error_type=type(e).__name__,reason=message,exit_code=1)));raise SystemExit(1)
