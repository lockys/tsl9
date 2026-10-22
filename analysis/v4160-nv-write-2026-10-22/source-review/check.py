"""Read-only original NV write/timer source contracts; no target execution."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PIN = 'a1d0dc4d3e8767e8dbd959235133779650f1da649c2d3f8ddbb38662addea9a7'
FW = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
RANGES = {'write_cb': (0x197be, 0x197f0), 'timer': (0x19764, 0x1979a),
          'unlock': (0x18e98, 0x18eb6), 'lock': (0x18eb6, 0x18ec4),
          'erase': (0x18ec4, 0x18ef2), 'program': (0x18ef2, 0x18f56)}

def need(value, message):
    if not value:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_bytes())

def context(root):
    root = Path(root).resolve(strict=True)
    old = next(p for p in (root/'analysis/v4160-callback-frontiers-2026-10-22/binding-review', root/'apk-analysis/tsl9-v4160-callback-frontiers-2026-10-22/binding-review') if p.is_dir())
    need(sha(old/'seal.json') == PIN, 'Pinned immutable binding seal')
    B = runpy.run_path(str(old/'check.py'))
    B['closed'](old, PIN)
    C, decode, _, folders = B['context'](root)
    return B, C, decode, folders, old

def gate(groups, original, B):
    # Equality covers every raw field, not selected masks alone. The immutable
    # source is itself re-decoded from its raw bytes in inspect().
    for k in RANGES:
        need(groups[k] == original[k], 'Complete original raw/operand contract: '+k)
    graphs = {k: B['cfg'](g) for k, g in groups.items()}
    need(sum(x['bytes'] for x in graphs.values()) == 294, '294 bounded source bytes')
    need(sum(x['rows'] for x in graphs.values()) == 115, '115 bounded source rows')
    need([x['target'] for x in graphs['write_cb']['calls']] == [0x18e98,0x18ec4,0x18ef2,0x18eb6,0x19764], 'Five direct linked calls')
    protected = (1,2,3,4,8,9,*range(18,28),5,6,7,28,29,30,31,17)
    for k in ('timer','unlock','lock','erase','program'):
        need(not graphs[k]['calls'], 'All five dependencies are bounded leaves')
        need(not any(x['rd'] in protected for x in groups[k]), 'Leaf preserves RA/SP/GP/TP/S/T/A7')
    return graphs

def descriptor(groups, graphs):
    own = {k: sorted({x['rd'] for x in g if x['rd'] not in (None,0)}) for k,g in groups.items()}
    return dict(
      source_bytes=294, source_rows=115, source_groups=graphs, explicit_written_GPRs=own,
      notation={'u32':'modulo 2^32', 'R8':'fresh zero-extended byte read', 'R32':'fresh 32-bit word read', 'W32':'ordered 32-bit word write', 'D':'entry A0', 'S':'entry A2', 'F':'u32(entry SP-32)', 'G':'entry GP'},
      write=dict(entry=0x197be,end_exclusive=0x197f0,frame_bytes=32,
        ordered_frame_accesses=[['W32',0x197c0,'F+28','entry RA'],['W32',0x197c2,'F+24','entry S0'],['W32',0x197c4,'F+12','S'],['R32',0x197d2,'F+12','source argument'],['R32',0x197e6,'F+28','exit RA'],['R32',0x197e8,'F+24','exit S0']],
        entry_A1_read=False, entry_A2_saved_before_calls=True,
        calls=[dict(PC=0x197c8,target=0x18e98,A0='D',A1='entry A1',A2='S'),dict(PC=0x197ce,target=0x18ec4,A0='D',A1='entry A1',A2='S'),dict(PC=0x197d8,target=0x18ef2,A0='D',A1='fresh R32(F+12)',A2='same fresh R32(F+12); ignored by leaf'),dict(PC=0x197dc,target=0x18eb6,A0='D & 0xFFFFFF00',A1='source',A2=256),dict(PC=0x197e2,target=0x19764,A0=1,A1='source',A2=256)],
        program_bytes=256,source_words=64,normal_result_A0=0,hardware_status_checked=False,
        no_adverse_alias_projection=dict(A1='S',A2='zext8(R8(u32(G+382)))',A3=0,A4='last fresh timer CTRL & 0xFFFFFFFE',A5=0xe000f000,A6='last source R32(u32(S+252))',SP='entry SP',RA='entry RA',S0='entry S0'),
        frame_restoration_is_conditional=True, arbitrary_entry_A1_length_used=False),
      timer=dict(entry=0x19764,end_exclusive=0x1979a,frame_bytes=0,A0_full_u32_preserved=True,A1_preserved=True,
        ordered_accesses=[
          dict(PC=0x19768,kind='R32',address=0xe000f004,result='status0'),
          dict(PC=0x1976e,kind='W32',address=0xe000f004,value='status0 & 0xFFFFFFFE'),
          dict(PC=0x19770,kind='R8',address='u32(G+382)',result='scale8'),
          dict(PC=0x19778,kind='W32',address=0xe000f010,value='u32(zext8(scale8) * entry A0)'),
          dict(PC=0x1977a,kind='W32',address=0xe000f014,value=0),
          dict(PC=0x1977c,kind='R32',address=0xe000f000,result='ctrl1'),
          dict(PC=0x19782,kind='W32',address=0xe000f000,value='ctrl1 | 0x10'),
          dict(PC=0x19784,kind='R32',address=0xe000f000,result='ctrl2'),
          dict(PC=0x1978a,kind='W32',address=0xe000f000,value='ctrl2 | 0x21'),
          dict(PC=0x1978c,kind='R32',address=0xe000f004,result='statusN',repeat='while (statusN & 1)==0',exit='first observed (statusN & 1)!=0'),
          dict(PC=0x19792,kind='R32',address=0xe000f000,result='ctrl3'),
          dict(PC=0x19796,kind='W32',address=0xe000f000,value='ctrl3 & 0xFFFFFFFE')],
        access_count='11 + poll reads',minimum_accesses_if_return=12,timeout=False,
        normal_exit=dict(A0='entry A0',A1='entry A1',A2='u32(zext8(scale8)*entry A0)',A3=0,A4='ctrl3 & 0xFFFFFFFE',A5=0xe000f000),
        timing_units_proved=False,GP_scale_initialized_here=False),
      flash=dict(base=0x40022000,unlock_write_sequence=[['base+4',0x45670123],['base+4',0xcdef89ab],['base+36',0x45670123],['base+36',0xcdef89ab]],
        unlock_exit=dict(A0='entry A0',A1='entry A1',A2='entry A2',A3=0x45670123,A4=0xcdef89ab,A5=0x40022000),
        lock_accesses=['fresh R32(base+16)','W32(base+16, read | 0x8000)'],lock_exit=dict(A0='entry A0',A1='entry A1',A2='entry A2',A3=0x8000,A4=0x40022000,A5='read | 0x8000'),
        erase_accesses=['fresh R32(base+16)','W32(base+16, read | 0x20000)','W32(base+20, entry A0 & 0xFFFFFF00)','fresh R32(base+16)','W32(base+16, read | 0x40)','fresh repeated R32(base+12) until (read & 1)==0','fresh R32(base+16)','W32(base+16, read & 0xFFFDFFFF)'],
        erase_exit=dict(A0='entry A0 & 0xFFFFFF00',A1='entry A1',A2='entry A2',A3=0xfffdffff,A4='last fresh CTRL & 0xFFFDFFFF',A5=0x40022000),
        program_accesses=['fresh R32(base+16)','W32(base+16, read | 0x10000)','fresh repeated R32(base+12) until (read & 1)==0','fresh repeated R32(base+12) until (read & 2)==0','for offset=0,4,...,252: fresh R32(u32(source+offset)); W32(u32((entry A0 & 0xFFFFFF00)+offset), read); fresh repeated R32(base+12) until (read & 2)==0','fresh R32(base+16)','W32(base+16, read | 0x200000)','fresh repeated R32(base+12) until (read & 1)==0','fresh R32(base+16)','W32(base+16, read & 0xFFFEFFFF)'],
        program_exit=dict(A0='entry A0 & 0xFFFFFF00',A1='entry A1',A2=256,A3=0xfffeffff,A4='last fresh CTRL & 0xFFFEFFFF',A5=0x40022000,A6='last fresh source word'),
        entry_program_A2_read=False,source_reads_interleaved_with_destination_writes=True,alignment_bytes=256,timeout=False,
        poll_bits_clear=[1,2],polls_status_checked_as_success=False),
      premises=['All original instruction, byte, word, return and MMIO accesses complete normally.', 'All busy polls eventually observe their required bits; no timeout is implemented.', 'No asynchronous GPR/code modification; GP byte and required pointers valid.', 'Restored caller RA/S0 and original source projection additionally require no adverse stack/source/destination/MMIO alias or intervening writes.', 'Each listed read is fresh; MMIO stability is NOT assumed.'],
      unresolved=['Installed hardware identity, Flash ownership and hardware write success.', 'Whole firmware/OTA compatibility and complete original C prototype.', 'Fault equivalence to C/native builds and caller scratch-register compatibility.', 'Timer units and physical time; source does not establish milliseconds.'],
      full_ABI_proved=False,hardware_success_proved=False,termination_proved=False)

def controls(groups, blobs, original, B, C, decode):
    cases=[('write_cb',0x197c4,'immediate'),('write_cb',0x197c8,'target'),('timer',0x19770,'immediate'),('timer',0x19774,'rs2'),('timer',0x1977a,'rs2'),('timer',0x19790,'op'),('program',0x18f16,'immediate')]
    out=[]
    keys=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
    for k,pc,field in cases:
        a=RANGES[k][0]; old=next(x for x in groups[k] if x['PC']==pc); chosen=None
        for bit in range(old['bytes']*8):
            raw=bytearray(blobs[k]);raw[pc-a+bit//8]^=1<<(bit%8)
            try: row=decode(raw[pc-a:],pc)
            except ValueError: continue
            if row[field]==old[field] or any(row[q]!=old[q] for q in keys if q!=field):continue
            chosen=raw,bit,row;break
        need(chosen is not None,'Meaningful same-shape raw mutation '+field)
        raw,bit,row=chosen;changed=dict(groups);changed[k]=C.rows(raw,a,decode)
        try: gate(changed,original,B)
        except ValueError as error:
            out.append(dict(group=k,PC=pc,field=field,bit=bit,original=old[field],mutated=row[field],raw_hex=row['raw_hex'],rejected=True,reason=str(error)));continue
        raise ValueError('Changed source contract accepted')
    return out

def inspect(root, firmware=None):
    B,C,decode,folders,old=context(root)
    if (HERE/'seal.json').exists():B['closed'](HERE,sha(HERE/'seal.json'))
    ledger=read(HERE/'ledger.json');original=read(old/'ledger.json')['groups'];groups=ledger['groups'];blobs={}
    for k,(a,z) in RANGES.items():
        raw=b''.join(bytes.fromhex(x['raw_hex']) for x in groups[k]);blobs[k]=raw
        need(len(raw)==z-a and hashlib.sha256(raw).hexdigest()==ledger['bounds'][k]['sha256'],'Source raw boundary '+k)
        need(C.rows(raw,a,decode)==groups[k],'Decoded every ledger operand '+k)
        need(C.rows(b''.join(bytes.fromhex(x['raw_hex']) for x in original[k]),a,decode)==original[k],'Decoded pinned earlier original '+k)
    graphs=gate(groups,original,B);facts=descriptor(groups,graphs)
    need(facts==read(HERE/'effects.json'),'All source formula descriptors')
    P1=runpy.run_path(str(folders['v4160-adc-config-2026-10-22/source-review']/'r2_fields.py'))['parse']
    P2=runpy.run_path(str(folders['v4160-adc-caller-2026-10-22/continuation-review']/'r2_fields.py'))['parse']
    for k,rows in read(HERE/'r2-static.json')['groups'].items():
        parsed=[]
        for x in rows:
            try: q=P1(x)
            except ValueError:q=P2(x)
            parsed.append(q)
        need(parsed==groups[k],'Independent r2 raw/operand corroboration '+k)
    result=dict(schema='TSL9-original-NV-write-source-v1',passed=True,metadata_only=firmware is None,
      actual_original_firmware_read=False,actual_original_source_bytes=0,actual_original_source_rows=0,
      source_contract=facts,raw_controls_replayed=False,source_encoding_references='Pinned previous decoder and its standard/conditional WCH source references; no encoding generated.',
      ISA_or_CPU_or_ESIL_execution=False,native_or_HOST_execution=False,compiler_or_linker=False,network=False,hardware=False,new_BIN=False)
    if firmware is not None:
        need(sha(firmware)==FW and Path(firmware).stat().st_size==76800,'Explicit actual original ID2966 firmware')
        raw=Path(firmware).read_bytes()
        for k,(a,z) in RANGES.items():need(C.rows(raw[a-0x8000:z-0x8000],a,decode)==groups[k],'Actual original source '+k)
        neg=controls(groups,blobs,original,B,C,decode)
        result.update(actual_original_firmware_read=True,actual_original_source_bytes=294,actual_original_source_rows=115,raw_controls_replayed=True,raw_controls=len(neg),controls=neg)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--firmware',type=Path)
    args=parser.parse_args()
    print(json.dumps(inspect(args.project_root,args.firmware)))
