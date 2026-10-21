"""Bound the readable source changes and provider-call identities, without evaluation."""
from pathlib import Path
import re
import frontier as F

CORE={'flash_native.c':'94bbb25ff93325152240c03d2fe01fbc5c7215417ffd3d98b2a61ecde21a7393','flash_native.h':'b26fe2050e88708e7d18257841f5682ac49fcd4b402aac42ffc5aaae649dd7bd','native_io.h':'579916278d4967cef1af0d04b68b403a515f3d56977613015639a0c9c916c08c','host_io.c':'01bb5096a99afdc6e774733121417994a250f40c3f0a6924ddd5b5db57861857','host_io.h':'41e0e2509a3e49a5f99fee0e703df44180f8a344a3c28bb782459f66dd27292a'}
RUNNER='832035fea10ca77b3f48631f368b2d7e7a9c4cfb3d3509a5585a63718bd79be8'
def calls(text):
    pattern=r'FN_(?:READ|WRITE|POLL_STEP|POLL_TRUE|CHECK_FLOW|WORD_DONE|RET_STATUS|RET_UNLOCK|RET_ERASE|RET_PROGRAM|FRAME_BEGIN|FRAME_RELOAD|FRAME_END|CSR_CLEAR|CSR_SET|CALL_UNLOCK|CALL_STATUS|CALL_ERASE|CALL_PROGRAM|CALL_LOCK)\('
    result=[]
    for m in re.finditer(pattern,text):
        depth=1;end=m.end()
        while depth and end<len(text):
            if text[end]=='(':depth+=1
            elif text[end]==')':depth-=1
            end+=1
        F.need(not depth,'Balanced provider expression');result.append(re.sub(r'\s+','',text[m.start():end]))
    return result
def inspect(root):
    old=root/'experiments/tsl9-v4160-flash-entry-order/src';new=root/'experiments/tsl9-v4160-flash-register-prefix/src'
    for name,pin in {'flash_native.c':'c2f85fd50a7def5ff4baf200415e9faa3f2a253dea51c6bc54ae6a139fef960b','native_io.h':'e0d58fdf1ae5ebc1f497a023443a4e6432f5cd75d987c691a2dcf68b3e64af7e'}.items():F.need(F.sha(old/name)==pin,'Immutable entry-order comparison source '+name)
    for name,pin in CORE.items():F.need(F.sha(new/name)==pin,'Frozen register-prefix source '+name)
    runner=F.case(root,'v4160-flash-register-prefix-2026-10-22')/'implementation/verify_native.py';F.need(F.sha(runner)==RUNNER,'Final frozen native CLI')
    for name in ('flash_native.h','host_io.c','host_io.h'):F.need((old/name).read_bytes()==(new/name).read_bytes(),'Unchanged host data/backend '+name)
    a=(old/'flash_native.c').read_text(encoding='utf-8');b=(new/'flash_native.c').read_text(encoding='utf-8')
    normalized=b.replace('FN_SOURCE_ADDRESS(source,offset)','FN_ADD(source,FN_K(offset))').replace('FN_DEST_ADDRESS(destination,offset)','FN_ADD(destination,FN_K(offset))')
    F.need(calls(a)==calls(normalized),'Exact ordered provider/poll/call/normal-return expressions under address identity')
    for name in ('status','lock','quarter'):
        pattern=r'fn_word tsl9_flash_'+name+r'_[\s\S]*?\n}\n#endif';left=re.search(pattern,a)[0];right=re.search(pattern,b)[0];F.need(left==right,'Unchanged readable function '+name)
    before=(old/'native_io.h').read_text(encoding='utf-8').split('#else',1)[0];after=(new/'native_io.h').read_text(encoding='utf-8').split('#else',1)[0]
    additions=['#define FN_REG3(v) (v)','#define FN_REG4(v) (v)','#define FN_REG5(v) (v)','#define FN_KEY1_HIGH() FN_K(0x45670000u)','#define FN_KEY2_HIGH() FN_K(0xcdef9000u)','#define FN_SOURCE_ADDRESS(source,offset) FN_ADD((source),FN_K(offset))','#define FN_DEST_ADDRESS(destination,offset) FN_ADD((destination),FN_K(offset))']
    for line in additions:F.need(after.count(line+'\n')==1,'Exact HOST identity/value/address primitive');after=after.replace(line+'\n','')
    F.need(before==after,'Every preexisting HOST macro byte remains unchanged')
    F.need(((0x45670000+0x123)&0xffffffff)==0x45670123 and ((0xcdef9000+0xfffff9ab)&0xffffffff)==0xcdef89ab,'Fully-known constant key decompositions modulo2^32')
    return {'frozen_source_sha256':CORE,'native_runner_sha256':RUNNER,'unchanged_source_functions':['status','lock','quarter'],'host_backend_and_public_header_unchanged':True,'preexisting_HOST_macros_unchanged':True,'new_HOST_primitives':'three identities, two fully-known key constants and two existing fn_add address aliases','provider_expression_count':len(calls(a)),'provider_expressions_unchanged_after_address_alias_normalization':True,'fully_known_key_constants_match':True,'full_source_semantic_equivalence_proved':False,'old_native_machine_bytes_reused_as_current_proof':False,'target_execution':False}
