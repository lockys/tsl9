"""Select unchanged SPI-helper C bodies; three exact clock bodies already exist in the parent."""
from pathlib import Path
import hashlib
import json
import re
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'src/native/receive/spi_filter_helpers.c'
EXPECTED='0636bd841598403d7d76fd2e7068c71bc359cc668f3bec760081d4bddff35553'
OMIT=['tsl9_channel_external_81b0','tsl9_channel_clock_frame_81b6','tsl9_channel_clock_scale_81bc']
def definition_end(text,at):
    depth=1
    while depth:
        if at>=len(text):raise ValueError('Complete C definition')
        if text.startswith('//',at):
            end=text.find('\n',at);at=len(text)if end<0 else end;continue
        if text.startswith('/*',at):
            end=text.find('*/',at+2)
            if end<0:raise ValueError('Complete C comment')
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
    return at
def derive():
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('Pinned complete curated source')
    text=raw.decode('utf-8');spans=[]
    for name in OMIT:
        matches=list(re.finditer(r'(?m)^(?:REGION|FRAME) void '+name+r'\(void\)\s*\{',text))
        if len(matches)!=1:raise ValueError('One complete actual function definition')
        m=matches[0];end=definition_end(text,m.end())
        spans.append(dict(name=name,start=m.start(),end=end,sha256=hashlib.sha256(text[m.start():end].encode()).hexdigest()))
    result=text
    for span in sorted(spans,key=lambda x:x['start'],reverse=True):result=result[:span['start']]+result[span['end']:]
    result='/* Derived from curated spi_filter_helpers.c. Only the three clock\\n * definitions already owned by the parent are omitted. Other C text and\\n * symbolic references are unchanged. */\n'.replace('\\n','\n')+result
    return dict(source=result,parent_source=SOURCE.relative_to(ROOT).as_posix(),parent_sha256=EXPECTED,
                omitted_definitions=spans,only_three_complete_definitions_omitted=True,executable_original_bytes_copied=False)
if __name__=='__main__':print(json.dumps(derive(),ensure_ascii=True))
