"""Strict local HEX -> captured-segment -> startup-request coverage evidence.

No target copy/state model or instruction execution. Absent bytes never acquire
values. Uses the saved content-pinned Intel HEX reader, with explicit guards
that remain active under Python -O; emits no BIN/HEX or executable mapping.
"""
import argparse
import importlib.util
import json
from hashlib import sha256,sha1
from pathlib import Path
import check_v4160_fallback_initialization_static as init

ROOT,LIB=init.ROOT,init.LIB
CANDIDATES=ROOT/'analysis/wch-resident-candidate-2026-10-21'
OUT=Path(__file__).with_name('v4160-sparse-boot-coverage.json')
PARSER_SHA='727ec4a519e751f72180381ab9129d58e351affd0bc467a99889f1f14e77e5df'
PARSER_BLOB='680d42832cd6640f34b5a5806375c3b838c8abaf'
DETAILS=(
 ('original-dec2023',526184,'11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5',
  '13202d1678c9766117d787d98b4de55ed61fc571',11973,11968,191244,0x6eb2c,
  '7416a8d7c1d595a759e14b05918b732a9168c6003af658359d8c3f452840b450',11963,11971),
 ('original',527568,'5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23',
  '0b484ccaf6466ab984190ffea14448f1d5443054',12005,12000,191744,0x6ed20,
  'bc3a261829e7c230061200abb66ef5b3e8e9308e4f93b550d4ebf31db8f9a936',11995,12003))
check=init.check


def blob(raw):return sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def parser():
    p=CANDIDATES/'carrier/intel_hex.py';raw=p.read_bytes()
    check(len(raw)==8416 and sha256(raw).hexdigest()==PARSER_SHA and blob(raw)==PARSER_BLOB,'saved HEX parser identity')
    check((CANDIDATES/'carrier-dec2023/intel_hex.py').read_bytes()==raw,'both saved HEX parsers equal')
    spec=importlib.util.spec_from_file_location('tsl9_saved_strict_hex',p)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def intervals(addresses):
    rows=[]
    for a in sorted(addresses):
        if not rows or a!=rows[-1][1]:rows.append([a,a+1])
        else:rows[-1][1]=a+1
    return [[hex(a),hex(b)] for a,b in rows]


def coverage(memory,start,count):
    check(type(start) is int and type(count) is int and count>=0 and 0<=start<=0xffffffff and start+count<=0x100000000,
          'coverage uint32 interval')
    missing=[a for a in range(start,start+count) if a not in memory]
    return {'start':hex(start),'end_exclusive':hex(start+count),'requested_bytes':count,
        'captured_bytes':count-len(missing),'missing_bytes':len(missing),'missing_ranges':intervals(missing),
        'first_missing':hex(missing[0]) if missing else None,'fully_captured':not missing}


def words(memory,start,count):
    check(start%4==0 and count%4==0,'coverage word alignment')
    masks=[sum(1<<i for i in range(4) if p+i in memory) for p in range(start,start+count,4)]
    prefix=next((i for i,m in enumerate(masks) if m!=15),len(masks))
    return {'requested_words':len(masks),'complete_words':masks.count(15),'leading_complete_words':prefix,
        'per_word_capture_masks':masks,'first_incomplete_word':hex(start+4*prefix) if prefix<len(masks) else None}


def captured(memory,start,count):
    check(all(p in memory for p in range(start,start+count)),'requested bytes not fully captured')
    return bytes(memory[p] for p in range(start,start+count))


def inspect(raw,reader):
    p=reader.parse(raw)
    cursor=0
    for row in p['records']:
        check(row['source_byte_offset']==cursor and row['checksum_valid'],'HEX source record accounting')
        n=row['source_record_ASCII_bytes'];line=raw[cursor:cursor+n]
        check(sha256(line).hexdigest()==row['line_sha256'],'HEX raw record provenance')
        ending=row['source_line_ending_bytes']
        check(raw[cursor+n:cursor+n+ending] in (b'',b'\n',b'\r\n'),'HEX record newline accounting')
        cursor+=n+ending
    check(cursor==len(raw),'HEX complete source accounting')
    memory={};prev_end=None
    for start,data in p['segments']:
        check(data and (prev_end is None or start>prev_end),'HEX segments strictly separated')
        for i,b in enumerate(data):
            check(start+i not in memory,'HEX duplicate captured address');memory[start+i]=b
        prev_end=start+len(data)
    check(sum(r['data_bytes'] for r in p['records'] if r['type']==0)==len(memory),'HEX data bytes equal sparse addresses')
    return p,memory


def derive(app,carriers,header,hex_sources,reader,sidecars=True):
    parents=init.derive(app,carriers,header);profiles=[]
    for data,parent,desc,raw,source_meta in zip(carriers,parents['profiles'],init.binding.PROFILES,hex_sources,DETAILS):
        original,n,digest,git_blob,records,data_records,data_bytes,tail_end,tail_sha,line_first,line_last=source_meta
        check(len(raw)==n and sha256(raw).hexdigest()==digest and blob(raw)==git_blob,'whole HEX identity '+parent['label'])
        p,memory=inspect(raw,reader)
        check(len(p['records'])==records and p['type_counts']=={'2':3,'0':data_records,'3':1,'1':1} and
              len(memory)==data_bytes and len(p['segments'])==17,'whole HEX layout '+parent['label'])
        check(len(p['starts'])==1 and p['starts'][0]['entry_address']==LIB,'whole HEX start address')
        check(p['segments'][0]==(LIB,data),'main carrier equals first sparse segment')
        segment_rows=[]
        for start,b in p['segments']:
            name='REFERENCE-CANDIDATE-ONLY-%08X-%08X.bin'%(start,start+len(b))
            if sidecars:check((CANDIDATES/desc[1]/name).read_bytes()==b,'existing sidecar equals parsed HEX '+name)
            segment_rows.append({'start':hex(start),'end_exclusive':hex(start+len(b)),'bytes':len(b),
                'sha256':sha256(b).hexdigest(),'sidecar':desc[1]+'/'+name,'sidecar_compared':sidecars})
        mapping=init.binding.profile(data,parent['label']);first={k:int(v,16) for k,v in mapping['first_copy'].items()}
        first_count=first['inclusive_last']-first['destination']+4
        seed=coverage(memory,int(mapping['seed_source'],16),48)
        initial=coverage(memory,first['source'],first_count)
        check(seed['fully_captured'] and initial['fully_captured'],'seed and first copy completely captured')
        req=parent['second_copy_request'];start=int(req['source'],16);count=req['bytes'];dest=int(req['destination'],16)
        second=coverage(memory,start,count);second['word_coverage']=words(memory,start,count)
        check(second['missing_ranges']==[[hex(tail_end),hex(tail_end+4)]] and second['missing_bytes']==4 and
              start+count==tail_end+4,'second copy exactly one final absent word')
        prefix=captured(memory,start,count-4)
        check(sha256(prefix).hexdigest()==tail_sha and p['segments'][-1]==(start,prefix),'captured tail segment identity')
        source_records=[r for r in p['records'] if r['type']==0 and r['absolute_start']<start+count and r['absolute_end_exclusive']>start]
        check([r['line'] for r in source_records]==list(range(line_first,line_last+1)),'tail record line provenance')
        gap=coverage(memory,LIB+len(data),start-(LIB+len(data)))
        check((gap['requested_bytes'],gap['captured_bytes'],gap['missing_bytes'])==(62,30,32),'between-segments sparse gap distinction')
        missing_destination=dest+(tail_end-start)
        check(missing_destination==int(parent['zero']['start'],16) and parent['second_zero_destination_overlap_bytes']==4,
              'absent source word maps to first zero destination word')
        profiles.append({'label':parent['label'],'source':{'path':original+'/wchble_rom.hex','bytes':n,
                'sha256':digest,'git_blob_sha1':git_blob,'records':records,'type_counts':p['type_counts'],
                'captured_data_bytes':len(memory),'segment_count':len(p['segments']),'start_records':p['starts']},
            'segments':segment_rows,'seed_request':seed,'first_copy_request':initial,'second_copy_request':second,
            'captured_second_prefix_sha256':tail_sha,'second_source_data_records':source_records,
            'interval_from_main_end_to_second_source':gap,
            'missing_source_destination_range':[hex(missing_destination),hex(missing_destination+4)],
            'following_zero_start':parent['zero']['start'],
            'following_zero_proves_prior_read_valid':False,'missing_bytes_have_values':False,
            'target_copy_or_state_simulated':False,'full_boot_proved':False,'installed_binding_proved':False})
    return {'schema':'TSL9-sparse-boot-coverage-v1','scope':'Whole local HEX parsing, sidecar byte equality and source coverage only',
        'parser':{'path':'carrier/intel_hex.py','bytes':8416,'sha256':PARSER_SHA,'git_blob_sha1':PARSER_BLOB,
            'alternate_saved_parser_equal':True,'explicit_source_accounting_guard_active_under_O':True},
        'profiles':profiles,'source_padding_or_repaired_image_created':False,'ISA_provider_MMIO_executed':False,
        'installed_binding_proved':False,'physical_read_fault_prediction':False}


def rec(kind,address=0,data=b''):
    b=bytes([len(data)])+address.to_bytes(2,'big')+bytes([kind])+data
    return b':'+(b+bytes([-sum(b)&255])).hex().upper().encode()


def tests(reader,raw_sources):
    def src(*rows):return b'\n'.join(rows)+b'\n'
    eof=rec(1)
    positives=(
      (src(rec(2,data=b'\x40\x00'),rec(0,0x10,b'ab'),eof),{0x40010:97,0x40011:98}),
      (src(rec(4,data=b'\0\x04'),rec(0,0x10,b'ab'),eof),{0x40010:97,0x40011:98}),
      (src(rec(0,5,b'b'),rec(0,1,b'a'),eof),{1:97,5:98}))
    for raw,expected in positives:check(inspect(raw,reader)[1]==expected,'HEX positive address semantics')
    valid=rec(0,0,b'a')
    bad_checksum=valid[:-2]+('%02X'%(int(valid[-2:],16)^1)).encode()
    negatives=(
      (src(bad_checksum,eof),'checksum mismatch'),(src(b':02'+valid[3:],eof),'byte count mismatch'),
      (src(rec(6),eof),'unsupported record type'),(src(eof,valid),'record after EOF'),
      (src(valid),'missing EOF'),(src(valid,valid,eof),'overlapping address'),
      (src(valid,rec(0,0,b'b'),eof),'overlapping address'),
      (src(rec(2,data=b'a'),eof),'malformed extended address'),
      (src(rec(0,0xffff,b'ab'),eof),'data crosses 16-bit offset boundary'),
      (src(rec(3,data=b'\0'*4),rec(5,data=b'\0\0\0\1'),eof),'conflicting start records'))
    for raw,reason in negatives:
        try:inspect(raw,reader)
        except reader.HexError as error:check(reason in str(error),'unexpected HEX negative guard')
        else:raise RuntimeError('HEX negative accepted')
    for raw in raw_sources:
        lines=raw.splitlines(keepends=True);i=max(j for j,line in enumerate(lines) if line[7:9]==b'00')
        line=lines[i];end=2 if line.endswith(b'\r\n') else 1 if line.endswith(b'\n') else 0
        text=line[:-end] if end else line
        changed=text[:-2]+('%02X'%(int(text[-2:],16)^1)).encode()+(line[-end:] if end else b'')
        lines[i]=changed
        try:inspect(b''.join(lines),reader)
        except reader.HexError as error:check('checksum mismatch' in str(error),'actual HEX checksum mutation guard')
        else:raise RuntimeError('actual HEX checksum mutation accepted')
    for mask in range(16):
        mem={0x1000+i:0 for i in range(4) if mask>>i&1};c=coverage(mem,0x1000,4);w=words(mem,0x1000,4)
        check(c['captured_bytes']==mask.bit_count() and c['fully_captured']==(mask==15) and
              w['per_word_capture_masks']==[mask],'four-byte sparse mask algebra')
        if mask!=15:
            try:captured(mem,0x1000,4)
            except RuntimeError as error:check(str(error)=='requested bytes not fully captured','missing byte read guard')
            else:raise RuntimeError('absent byte gained value')
    for raw,meta in zip(raw_sources,init.DETAILS):
        _,memory=inspect(raw,reader);start=meta[6];count=meta[8]-meta[7]+4
        for i in range(4):
            changed=memory.copy();del changed[start+i]
            check(coverage(changed,start,count)['missing_bytes']==5 and
                  words(changed,start,count)['leading_complete_words']==0,'captured-byte deletion changes coverage')
    print('PASS: 3 address semantics; 10 HEX grammar negatives; 2 actual checksum mutations; 16 sparse masks; 8 captured-byte deletions')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true',help='Create new ledger exclusively');opt=p.parse_args()
    app,header=init.binding.APP.read_bytes(),init.core.outer.HEADER.read_bytes()
    check(len(app)==76800 and sha256(app).hexdigest()==init.binding.APP_HASH,'APP identity')
    check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK header identity')
    carriers=[]
    for label,folder,tail,n,digest in init.binding.PROFILES:
        raw=(CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
        check(len(raw)==n and sha256(raw).hexdigest()==digest,'candidate identity '+label);carriers.append(raw)
    hex_sources=[(CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in DETAILS]
    reader=parser();ledger=derive(app,carriers,header,hex_sources,reader);tests(reader,hex_sources)
    output=(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n').encode()
    if opt.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'sparse coverage ledger exact replay')
    print('PASS: 23978 HEX records; 34 source-matched sidecars; both second copies lack exactly the final 4-byte word')
    print('PASS: ledger exact replay; full boot/physical read/installed identity UNPROVED; NO ISA/copy-state/provider/MMIO execution')


if __name__=='__main__':main()
