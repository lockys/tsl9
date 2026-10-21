"""Read-only closure for the original-extent callframe native components."""
import argparse
import json
from pathlib import Path
from verify_callframe import HERE,SOURCE_PINS,load_context,original_image,profile_flags,static_checks,transcript_controls,normal,sha,require,linker_source


def logs(folder,commands):
    for command in commands:
        require(command["exit"]==0 and sha(folder/(command["label"]+".log"))==command["log_sha256"],"actual successful compiler/linker/disassembly log pin")


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--project-root",type=Path,default=HERE.parents[2]);p.add_argument("--firmware",type=Path);p.add_argument("--require-local-builds",action="store_true");a=p.parse_args();root=a.project_root.resolve()
    seal=json.loads((HERE/"final-audit.json").read_text(encoding="utf-8"))
    for name,pin in seal["members"].items():require(sha(HERE/name)==pin,"sealed member changed: "+name)
    require({n:sha(root/n) for n in SOURCE_PINS}==SOURCE_PINS,"current frozen callframe/public/native IO source pins")
    ctx=load_context(root);index=json.loads((HERE/"results.json").read_text(encoding="utf-8"));require(len(index["results"])==2,"actual C/C++ selected receipts")
    replayed=[];missing=[];image=None
    for item in index["results"]:
        path=HERE/item["metadata"];require(sha(path)==item["sha256"],"selected receipt byte identity")
        r=json.loads(path.read_text(encoding="utf-8"));require(r["passed"] and r["source_sha256"]==SOURCE_PINS and r["runner_sha256"]==sha(HERE/"verify_callframe.py") and r["dependencies"]==ctx["dependency_pins"],"actual source/runner/dependency pins")
        require(r["main_flags"]==profile_flags(ctx,r["mode"],True) and r["helper_flags"]==profile_flags(ctx,r["mode"],False),"same explicit main/helper native profiles")
        require(r["whole_component_original_extents_fit"] and not r["exact_original_main_bytes"] and not r["original_pointwise_equivalence_proved"] and not r["asynchronous_equivalence_proved"] and not r["original_full_image_integration_proved"] and not r["OTA_ready"],"scoped extent fit does not promote changed save order/full image/hardware gates")
        folder=HERE/item["artifact_dir"]
        if not folder.is_dir():missing.append(item["artifact_dir"]);continue
        if image is None:_,image=original_image(root,ctx,a.firmware)
        require(sha(folder/"verification.json")==item["sha256"],"actual local receipt pin")
        for name,pin in r["artifacts"].items():require(sha(folder/name)==pin,"actual native artifact pin")
        require((folder/"placements.ld").read_text(encoding="utf-8")==linker_source(),"actual original-extent linker policy")
        logs(folder,r["commands"])
        require(normal(static_checks(folder,ctx,image))==r["checks"],"all ELF264bytes94instructions/frame/body/JAL/fresh reload/IR structural facts replay")
        require(normal(transcript_controls(folder,ctx,image))==r["transcript_controls"] and len(r["transcript_controls"])==30,"all30 transcript controls replay")
        require(len(r["actual_compiled_controls"])==6,"six actual compiled source controls")
        for control in r["actual_compiled_controls"]:
            case=folder/("negative-"+control["case"]);changed=control["changed_source"]
            require(changed in SOURCE_PINS and sha(case/changed)==control["source_sha256"],"actual changed source-control pin")
            for relative,pin in SOURCE_PINS.items():
                if relative!=changed:require(sha(case/relative)==pin,"all other negative-control source inputs unchanged")
            for name,pin in control["artifacts"].items():require(sha(case/name)==pin,"actual compiled negative artifact pin")
            logs(case,control["commands"])
            try:static_checks(case,ctx,image)
            except ValueError as error:require(str(error)==control["reason"],"same actual native control rejection")
            else:raise ValueError("compiled negative admitted in readback")
        replayed.append(item["metadata"])
    require(not a.require_local_builds or not missing,"required historical local archives missing")
    print(json.dumps(dict(passed=True,seal_sha256=sha(HERE/"final-audit.json"),metadata_receipts=2,local_artifacts_replayed=replayed,missing_local_archives=missing,
                          fresh_compilation=False,allocated_bytes=264,instructions=94,whole_component_original_extents_fit=True,save_order_identical=False,
                          original_pointwise_equivalence_proved=False,asynchronous_equivalence_proved=False,full_original_image_integration=False,target_execution=False,ISA_emulation=False,OTA_ready=False)))


if __name__=="__main__":main()
