"""Nine bounded, actual-artifact counterexamples. Mutated files stay in this review's build/."""
from pathlib import Path
import struct,uuid
import machine as M

def symbol_offset(e,name):
    found=[]
    for section in e.sections:
        if section['type']!=2:continue
        for i,s in enumerate(e.symbol_tables[section['index']]):
            if s['name']==name:found.append(section['offset']+16*i)
    M.need(len(found)==1,'Actual unique symbol storage');return found[0]
def run(root,folder,base,base_witness,native,tail,merged,linked,base_image,image):
    E=M.parser(root);out=Path(__file__).resolve().parent/'build'/('controls-'+uuid.uuid4().hex);out.mkdir(parents=True)
    result=[]
    def reject(name,e,change,check,expected):
        blob=bytearray(e.raw);change(blob);path=out/(name+'.o');path.write_bytes(blob)
        try:check(E(path))
        except ValueError as err:
            M.need(expected in str(err),'Counterexample rejected by intended semantic gate '+name+': '+str(err))
            result.append(dict(name=name,actual_mutated_file_sha256=M.sha(path),rejected=True,reason=str(err)));return
        raise ValueError('Accepted mutated source-wiring artifact '+name)
    reject('fake_native_alias_ABS',native,lambda b:struct.pack_into('<H',b,symbol_offset(native,M.OLD)+14,65521),
           lambda n:M.partial(base,n,tail,merged),'shares same actual allocated')
    weak=E(folder/'base-weakened.o')
    reject('copy_entry_not_weakened',weak,lambda b:b.__setitem__(symbol_offset(weak,M.OLD)+12,16),
           lambda w:M.weakened(base,w),'GLOBAL NOTYPE becomes WEAK')
    sec=merged.sections[M.symbol(merged,M.NEW)['index']];sh=struct.unpack_from('<I',merged.raw,32)[0]+40*sec['index']
    reject('merged_C_allocation_missing',merged,lambda b:struct.pack_into('<I',b,sh+8,sec['flags']&~2),
           lambda o:M.partial(base,native,tail,o),'Every original owner plus only realC')
    ingress=next(s for s in linked.sections if s['flags']&2 and s['address']<=0x14094<s['address']+s['size'])
    at=ingress['offset']+0x14094-ingress['address']
    reject('caller_no_RA_link',linked,lambda b:b.__setitem__(at,b[at]^128),
           lambda l:M.final(base_witness,merged,l,base_image,image),'Real caller now links')
    reject('caller_wrong_branch_target',linked,lambda b:b.__setitem__(at+3,b[at+3]^1),
           lambda l:M.final(base_witness,merged,l,base_image,image),'Real caller now links')
    r=next(r for r in native.relocations if r['type']==26);code=linked.sections[M.symbol(linked,M.NEW)['index']]
    hi=code['offset']+r['offset']
    reject('callback_HI20_wrong_provider_address',linked,lambda b:b.__setitem__(hi+2,b[hi+2]^1),
           lambda l:M.relocated_component(native,l),'Actual allocated callback HI20')
    old=next(s for s in linked.sections if s['flags']&2 and s['type']!=8 and s['address']==0x8000)
    reject('outside_original_image_byte_changed',linked,lambda b:b.__setitem__(old['offset'],b[old['offset']]^1),
           lambda l:M.final(base_witness,merged,l,base_image,image),'Only real ingress owner may differ')
    ts=next(s for s in tail.sections if s['flags']&2 and s['size']);th=struct.unpack_from('<I',tail.raw,32)[0]+40*ts['index']
    reject('page_fill_marked_executable',tail,lambda b:struct.pack_into('<I',b,th+8,ts['flags']|4),
           lambda t:M.partial(base,native,t,merged),'nonexecuting FF page fill')
    reject('partial_ROM_fake_ABS_provider',merged,lambda b:struct.pack_into('<H',b,symbol_offset(merged,M.ROM)+14,65521),
           lambda o:M.partial(base,native,tail,o),'Complete base/native RELA union')
    return result
