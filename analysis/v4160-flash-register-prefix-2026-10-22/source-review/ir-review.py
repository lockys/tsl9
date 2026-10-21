"""Read fixed-register SSA bridges and volatile widths; never evaluate IR."""
import re

def need(v,m):
    if not v:raise ValueError(m)
def inspect(name,text):
    names={'status':'18e90','unlock':'18e98','lock':'18eb6','erase':'18ec4','program':'18ef2','quarter':'9c0a'}
    expected='tsl9_flash_'+name+'_'+names[name]
    f=re.findall(r'define\b[^\n]*@'+expected+r'\([^\n]*\) [^\n]*\{\n(.*?)\n\}',text,re.S);need(len(f)==1,'One actual readable public IR function '+name);body=f[0];lines=body.splitlines()
    need('target triple = "riscv32-unknown-unknown-elf"' in text,'Actual RV32 IR target')
    memory=[x.strip() for x in lines if re.search(r'\b(?:load|store)\b',x)]
    need(all(re.search(r'\b(?:load|store) volatile i32\b',x) for x in memory),'All source memory operations remain volatile32 in '+name)
    counts={'status':(0,1),'unlock':(0,4),'lock':(1,1),'erase':(4,4),'program':(8,4),'quarter':(1,1)}
    need((sum('load volatile' in x for x in memory),sum('store volatile' in x for x in memory))==counts[name],'Distinct fresh source memory sites in '+name)
    bindings=[]
    pattern=r'\s*(%\d+) = (?:tail )?call i32 asm sideeffect "", "=\{x(\d+)\},\{x\2\},~\{memory\}"\(i32 ([^,)]+)\)'
    for i,line in enumerate(lines):
        m=re.match(pattern,line)
        if m:bindings.append({'result':m[1],'reg':int(m[2]),'input':m[3],'line':i})
    def bind(reg,value,after=-1):
        found=[r for r in bindings if r['reg']==reg and r['input']==str(value) and r['line']>after];need(len(found)==1,'Unique ordered fixed x%d SSA bridge for %s'%(reg,value));return found[0]
    def definition(pattern,after=-1):
        matches=[(i,m) for i,line in enumerate(lines) if i>after and (m:=re.match(pattern,line))];need(len(matches)==1,'Unique ordered IR expression '+pattern);return matches[0]
    if name=='unlock':
        high1=bind(13,1164378112);base=bind(15,1073881088,high1['line']);i,add1=definition(r'\s*(%\d+) = add i32 '+re.escape(high1['result'])+r', 291',base['line']);key1=bind(13,add1[1],i)
        high2=bind(14,-839938048,key1['line'])
        stores=[i for i,line in enumerate(lines) if 'store volatile i32' in line];need(len(stores)==4 and high2['line']<stores[0] and key1['result'] in lines[stores[0]],'Original key-high materialization before first key1 store')
        bridge=bind(14,high2['result'],stores[0]);i,add2=definition(r'\s*(%\d+) = add i32 '+re.escape(bridge['result'])+r', -1621',bridge['line']);key2=bind(14,add2[1],i)
        need(key2['line']<stores[1] and key2['result'] in lines[stores[1]] and key1['result'] in lines[stores[2]] and key2['result'] in lines[stores[3]],'Post-firststore key2 dependency and ordered key SSA values')
    if name in ('erase','program'):
        first_load_index,load=next((i,re.match(r'\s*(%\d+) = load volatile i32,.*',line)) for i,line in enumerate(lines) if 'load volatile i32' in line)
        observed=bind(14 if name=='erase' else 15,load[1],first_load_index);mask=bind(13,131072 if name=='erase' else 65536,observed['line']);incoming=bind(10,'%0',mask['line']);i,aligned=definition(r'\s*(%\d+) = and i32 '+re.escape(incoming['result'])+r', -256',incoming['line']);output=bind(10,aligned[1],i)
        need(first_load_index<observed['line']<mask['line']<incoming['line']<i<output['line'],'Original read/scratch/mask/A0-alignment SSA order')
        if name=='program':
            commit=bind(13,2097152,output['line']);need(any(x['reg']==15 and x['line']>commit['line'] for x in bindings),'Commit RMW uses A5 bridge')
            need(any(x['reg']==14 and x['line']>commit['line'] and x['input'].startswith('%') for x in bindings),'Final poll has A4 bridge')
            adds=re.findall(r'(%\d+) = (?:tail )?call i32 asm sideeffect "add \$0, \$1, \$2", "=\{x13\},\{x(11|10)\},\{x15\},~\{memory\}"\(i32 (%\d+), i32 (%\d+)\)',body)
            need(len(adds)==2 and [r[1] for r in adds]==['11','10'] and adds[0][2]=='%1' and adds[1][2]==output['result'] and adds[0][3]==adds[1][3],'Only two ordered original-source address ADD primitives')
            pointers=[]
            for result,reg,base,index in adds:
                unused,ptr=definition(r'\s*(%\d+) = inttoptr i32 '+re.escape(result)+r' to ptr');pointers.append(ptr[1])
            loadsite,word=definition(r'\s*(%\d+) = load volatile i32, ptr '+re.escape(pointers[0])+r',.*')
            stores=[i for i,line in enumerate(lines) if re.match(r'\s*store volatile i32 '+re.escape(word[1])+r', ptr '+re.escape(pointers[1])+r',',line)];need(len(stores)==1 and loadsite<stores[0],'Ordered source-read/destination-write use actual address primitive outputs')
    if name!='quarter':
        operations=re.findall(r'asm sideeffect "([^"]+)"',body);need(operations==(['add $0, $1, $2']*2 if name=='program' else []),'Only explicitly admitted address ADD instructions, no leaf opcode replay')
    return {'function':name,'volatile_load_sites':counts[name][0],'volatile_store_sites':counts[name][1],'fixed_identity_bridges':len(bindings),'target_execution':False,'full_IR_semantic_equivalence_proved':False}
