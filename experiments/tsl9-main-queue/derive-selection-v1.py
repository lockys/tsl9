"""Derive an unchanged-body C unit excluding the genuine disarm body already in the parent."""
from pathlib import Path
import hashlib
import json
import re
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'src/native/receive/record_program.c'
EXPECTED='51af3e56a2132a60a56bd4290817129608d54b3843c846fb4f56313c1a47117b'
OMIT='tsl9_program_disarm_93ee'
def derive():
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('Pinned complete curated C source')
    text=raw.decode('utf-8')
    pattern=r'(?m)^REGION void '+OMIT+r'\(void\)\s*\{'
    hits=list(re.finditer(pattern,text))
    if len(hits)!=1:raise ValueError('One complete real C definition to omit')
    start=hits[0].start();at=hits[0].end();depth=1
    while depth:
        if text.startswith('//',at):
            end=text.find('\n',at);at=len(text)if end<0 else end;continue
        if text.startswith('/*',at):
            end=text.find('*/',at+2)
            if end<0:raise ValueError('Whole C comment')
            at=end+2;continue
        if text[at]in ['"',"'"]:
            quote=text[at];at+=1
            while at<len(text):
                if text[at]=='\\':at+=2;continue
                if text[at]==quote:at+=1;break
                at+=1
            continue
        if text[at]=='{':depth+=1
        elif text[at]=='}':depth-=1
        at+=1
        if at>len(text):raise ValueError('Complete C definition extent')
    removed=text[start:at]
    header='/* Derived from the complete curated record_program.c; only the full\\n * disarm definition is omitted because the parent already owns its genuine body.\\n * All other C definitions and symbolic references are byte-for-byte retained. */\n'
    # Convert the two explanatory escaped newlines only; original C stays unchanged.
    header=header.replace('\\n','\n')
    result=header+text[:start]+text[at:]
    return dict(source=result,parent_source=SOURCE.relative_to(ROOT).as_posix(),
        parent_sha256=EXPECTED,omitted_symbol=OMIT,omitted_C_definition_sha256=hashlib.sha256(removed.encode()).hexdigest(),
        omitted_start_offset=start,omitted_end_offset=at,only_one_complete_C_definition_omitted=True,
        executable_original_bytes_copied=False)
if __name__=='__main__':print(json.dumps(derive(),ensure_ascii=True))
