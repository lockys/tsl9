"""Actual ELF byte mutations, reparsed as data; no executable is launched."""
import struct

class Blob:
    def __init__(self,raw):self.raw=bytes(raw)
    def read_bytes(self):return self.raw

def symbol_position(e,name):
    positions=[]
    for section in e.sections:
        if section['type']!=2:continue
        for i,s in enumerate(e.symbol_tables[section['index']]):
            if s['name']==name:positions.append(section['offset']+16*i)
    if len(positions)!=1:raise ValueError('One actual ELF symbol record')
    return positions[0]

def relocation_position(e,owner,offset):
    result=[]
    for s in e.sections:
        if s['type']!=4 or e.sections[s['info']]['name']!=owner:continue
        for at in range(s['offset'],s['offset']+s['size'],12):
            if struct.unpack_from('<I',e.raw,at)[0]==offset:result.append(at)
    if len(result)!=1:raise ValueError('One actual ELF RELA record')
    return result[0]

def inspect(R,root,firmware,folder):
    root,E,decode,ref=R.metadata(root,firmware);e=E(folder/'source-integrated.o');linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');cases=[]
    def check(label,original,mutate,is_linked=False):
        raw=bytearray(original.raw);mutate(raw);bad=E(Blob(raw))
        try:R.gate(e if is_linked else bad,bad if is_linked else linked,ref,decode)
        except (ValueError,KeyError):cases.append(label);return
        raise ValueError('Static byte control accepted: '+label)
    p=symbol_position(e,R.PUBLIC)
    check('canonical fabricated FUNC280',e,lambda b:struct.pack_into('<I',b,p+8,280))
    check('canonical ABS numeric provider',e,lambda b:struct.pack_into('<H',b,p+14,65521))
    body=next(s['name'] for s in e.symbols if s['name'] in ('tsl9_tx_valid_body','_ZL18tsl9_tx_valid_bodyjjjj'));q=symbol_position(e,body)
    check('body wrongly GLOBAL',e,lambda b:b.__setitem__(q+12,18))
    p=relocation_position(e,R.OWNER,132)
    check('PCREL LO nonzero addend',e,lambda b:struct.pack_into('<i',b,p+8,2))
    p=relocation_position(e,R.OWNER,4)
    check('entry branch missing type16',e,lambda b:b.__setitem__(p+4,0))
    row=next(r for r in ref['incoming_RELA'] if r['owner'].endswith('ota_handler_9b8e'));p=relocation_position(e,row['owner'],row['offset'])
    check('outside incoming interior addend',e,lambda b:struct.pack_into('<i',b,p+8,2))
    p=e.byname[row['owner']]['offset']+row['offset']
    check('ET_REL real caller loses link',e,lambda b:b.__setitem__(p,b[p]^0x80))
    row=next(r for r in ref['incoming_machine'] if r['PC']==0x13eac);p=linked.byname[row['owner']]['offset']+row['offset']
    check('linked tail entry spuriously writes RA',linked,lambda b:b.__setitem__(p,b[p]^0x80),True)
    p=linked.byname[R.OWNER]['offset']+278
    check('typed return leaf no longer RET',linked,lambda b:b.__setitem__(p+1,b[p+1]^0x10),True)
    return dict(passed=True,actual_byte_mutations_rejected=len(cases),controls=cases,execution=False)
