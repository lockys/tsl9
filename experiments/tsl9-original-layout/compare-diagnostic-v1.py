"""Independently decode a nonloadable ELF32 diagnostic; compare structures and bytes, never execute it."""
import hashlib,struct
from pathlib import Path
from collections import Counter

def need(ok,label):
    if not ok:raise ValueError(label)

def audit(path,primary):
    raw=Path(path).read_bytes();need(52<=len(raw)<=64*1024*1024,'Bounded local ELF file')
    header=struct.unpack_from('<16sHHIIIIIHHHHHH',raw)
    ident=header[0];need(ident[:7]==b'\x7fELF\x01\x01\x01','ELF32 little-endian version1')
    need(header[1:5]==(2,243,1,0) and header[8]==52 and header[11]==40,'RV32 diagnostic ET_EXEC,zero entry and standard headers')
    need(0<header[12]<2048 and header[13]<header[12],'Bounded section inventory')
    def extent(offset,size):
        need(0<=offset<=len(raw) and 0<=size<=len(raw)-offset,'Every file extent within the actual file')
        return raw[offset:offset+size]
    extent(header[6],header[12]*40)
    rows=[struct.unpack_from('<10I',raw,header[6]+40*i) for i in range(header[12])]
    names=extent(rows[header[13]][4],rows[header[13]][5])
    def string(table,index):
        need(0<=index<len(table),'String-table offset');end=table.find(b'\0',index);need(end>=index,'Bounded terminated ELF string');return table[index:end].decode('utf-8')
    sections=[]
    for i,r in enumerate(rows):
        sections.append(dict(index=i,name=string(names,r[0]),type=r[1],flags=r[2],address=r[3],offset=r[4],size=r[5],link=r[6],info=r[7],align=r[8],entsize=r[9]))
        if r[1]!=8:extent(r[4],r[5])
    need(tuple(primary.header)==header[1:] and len(primary.sections)==len(sections),'Every ELF header field and section count agrees')
    for a,b in zip(primary.sections,sections):
        need(all(a[k]==v for k,v in b.items()),'Every independently decoded section field agrees')
        if b['type']!=8:need(primary.data(a)==extent(b['offset'],b['size']),'Every file-backed section byte agrees')
    need(header[9]==32 and 0<header[10]<128,'Bounded standard program header inventory')
    extent(header[5],header[10]*32);programs=[struct.unpack_from('<8I',raw,header[5]+32*i) for i in range(header[10])]
    need(all(p[0]==0 for p in programs) and programs==[tuple(p) for p in primary.program_headers],'Only matching PT_NULL entries;no loadable segment')
    symtabs=[s for s in sections if s['type']==2];need(len(symtabs)==1,'One actual symbol table');s=symtabs[0]
    need(s['entsize']==16 and s['size']%16==0 and s['link']<len(sections),'Whole ELF32 symbol records')
    strings=sections[s['link']];need(strings['type']==3,'Actual symbol name string table');strings=extent(strings['offset'],strings['size'])
    symbols=[]
    for i in range(s['size']//16):
        v=struct.unpack_from('<IIIBBH',raw,s['offset']+16*i)
        need(v[5]<len(sections) or v[5]==0xfff1,'Known symbol section or explicit ABS role')
        symbols.append(dict(index=i,name=string(strings,v[0]),value=v[1],size=v[2],info=v[3],other=v[4],section=v[5]))
    need(len(symbols)==len(primary.symbols) and all(all(a[k]==v for k,v in b.items()) for a,b in zip(primary.symbols,symbols)),'All independent symbol names,roles,values,sizes and owners agree')
    relocations=[]
    for s in sections:
        if s['type']!=4:continue
        need(s['entsize']==12 and s['size']%12==0 and s['info']<len(sections) and s['link']==symtabs[0]['index'],'Whole explicit-addend ELF32 relocations')
        owner=sections[s['info']]
        for i in range(s['size']//12):
            offset,info,addend=struct.unpack_from('<IIi',raw,s['offset']+12*i);symbol=info>>8
            need(symbol<len(symbols) and owner['address']<=offset<owner['address']+owner['size'],'Actual relocation target symbol and original-VA source position')
            relocations.append((s['info'],offset,info&255,symbol,addend))
    actual=Counter((r['section'],r['offset'],r['type'],r['symbol'],r['addend']) for r in primary.relocations)
    need(actual==Counter(relocations),'All independent relocation owners,offsets,types,symbols and addends agree')
    return dict(passed=True,ELF_type=2,entry=0,PT_LOAD_count=0,sections=len(sections),symbols=len(symbols),relocations=len(relocations),
                every_header_section_byte_symbol_and_relocation_agrees=True,ELF_sha256=hashlib.sha256(raw).hexdigest(),target_executed=False)
