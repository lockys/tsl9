"""Conditional same-node projection, not two observed invocations or a full CPU.
Uses the sibling's instruction-tested prefix; re-enters it with inherited fields.
Distinct source/destination, accessible RAM, successful helper return, no interference.
"""
from pathlib import Path
import runpy
pre=runpy.run_path(str(Path(__file__).with_name('check_v131_queue_flag_clear.py')))
rom=pre['rom']; prefix=pre['run']
def ck(x):
    if not x:raise ValueError('queue two-round mismatch')
def window(a,h):ck(rom[a-0x40000:a-0x40000+len(bytes.fromhex(h))]==bytes.fromhex(h))
window(0x40d7a,'5c4389075cc34cb8032504112e864c430905eff07f81') # first partial: source += 2, amount=cap
window(0x40dc0,'93e717005ca46dbf') # continuation partial skips source += 2
window(0x40d90,'832784115038d443da27b296118fd4c3daa789473cbc') # reread head; bump cursor, reduce length, state=2
window(0x40e04,'54b8a3040700032504114c430905eff00ff9') # continuation final: amount=remaining, flag=0
window(0x40e16,'832784115038d443da27b296118fd4c3daa78d47c1b7') # same arithmetic, then state=3
window(0x40dea,'3cbc')
window(0x405c4,'b386f50003c80600b306f500850723800601e317f6fec5b7') # byte-by-byte forward copy

def step(node,cap):
    pc,f=prefix(node['left'],cap,node['flag'],2)
    if pc==0x40d68:node['cursor']+=2
    ck(pc in (0x40d68,0x40dc0,0x40e06)); final=pc==0x40e06
    node['flag']=f;amount=node['left'] if final else cap
    start=node['cursor'];chunk=bytes(node['mem'][start+i] for i in range(amount))
    node['cursor']+=amount;node['left']-=amount;node['state']=3 if final else 2
    return chunk
payload=bytes(range(0x50,0x5c));cases=eligible=0
for first in range(12): # first round always partial, including zero capacity
    for second in range(256):
        node=dict(left=12,flag=0x81,cursor=100,mem=dict(enumerate(payload,102)))
        chunk=step(node,first)
        ck((chunk,node['cursor'],node['left'],node['flag'],node['state'])==(payload[:first],102+first,12-first,1,2))
        chunk+=step(node,second);total=min(12,first+second);done=first+second>=12
        ck((chunk,node['cursor'],node['left'],node['flag'],node['state'])==(payload[:total],102+total,12-total,0 if done else 1,3 if done else 2))
        ck((node['state']!=0 and not node['flag']&1)==done);eligible+=done;cases+=1
print(f'PASS: {cases} conditional two-round pairs; {eligible} meet both local pop gates; {cases-eligible} remain partial')
