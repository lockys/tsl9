"""Host C/continuous ISA differential for APP plus two reference providers."""
import argparse,ctypes,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from oracle import Whole,need
from profiles import ROOT,PROFILES
from layout import derive
HERE=Path(__file__).resolve().parent
IMAGE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
TOOLS_SHA={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
RAM=bytes((i*37+11)&255 for i in range(65536))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def corpus():
    for n in (0,31,1039,1040):
        for lane in ('first','second','both','sentinel','none','wide'):
            for table in ('empty','missing','zero','one','two','ff','duplicate','late'):
                for task in (0,1,255):
                    for tasks in (0,1,255):
                        yield dict(n=n,lane=lane,table=table,task=task,tasks=tasks,name='matrix')
    for name in ('max_count','forward_alias','frame_alias','event_control_alias','event_tail_slot_alias'):
        yield dict(n=4,lane='first',table='one',task=0,tasks=1,name=name)
def fixture(case,rom,cfg):
    ram=bytearray(RAM);low=bytearray(rom[:512]);control=bytearray(b'\x78\x56\x34\x12')
    def write(a,w,v):
        if a>=0x4002420c:data,base=control,0x4002420c
        elif a>=0x20000000:data,base=ram,0x20000000
        else:data,base=low,0x40000
        i=a-base;need(0<=i and i+w<=len(data),'mapped fixture write')
        data[i:i+w]=(v&((1<<(8*w))-1)).to_bytes(w,'little')
    r=[(j*0x1020304+0x112233)&0xffffffff for j in range(32)]
    r[0]=0;r[1]=0x12345678;r[2]=0x2000d020;r[3]=0x20004000
    r[10]=0xfffe if case['lane']=='sentinel' else 0x10001 if case['lane']=='wide' else 0x1234
    r[11]=0xa7;r[12]=0x20008000;r[13]=case['n']
    tables={'empty':[],'missing':[(0x4321,1),(0x9876,1)],'zero':[(0x1234,0)],'one':[(0x1234,1)],
            'two':[(0x1234,2)],'ff':[(0x1234,255)],'duplicate':[(0x1234,1),(0x1234,0)],
            'late':[(0x4321,0),(0x5678,1),(0x9876,255),(0x1234,1)]}
    records=tables[case['table']]
    if case['name']=='max_count':records=[(0x5678,0)]*254+[(0x1234,1)]
    write(cfg[2],1,len(records))
    for j,(h,v) in enumerate(records):write(r[3]+128+4*j,2,h);write(r[3]+130+4*j,1,v)
    write(r[3]+150,2,r[10] if case['lane'] in ('first','both','sentinel','wide') else 0x4321)
    write(r[3]+154,2,r[10] if case['lane'] in ('second','both','sentinel','wide') else 0x4321)
    write(r[3]+148,1,case['task']);write(r[3]+152,1,case['task'])
    write(cfg[4],1,case['tasks']);write(cfg[5],4,0x20006000)
    for task in (0,1,255):write(0x20006000+2*task,2,0xa5a4)
    if case['name']=='forward_alias':r[12]=0x2000b196
    if case['name']=='frame_alias':r[2]=0x2000b198
    if case['name']=='event_control_alias':write(cfg[5],4,0x4002420c)
    if case['name']=='event_tail_slot_alias':write(cfg[5],4,0x40050)
    return [(0x20000000,bytes(ram)),(0x40000,bytes(low)),(0x4002420c,bytes(control))],r
def build(tools,folder,text,mode,opt,name):
    unit=folder/(name+'.c');unit.write_text(text+'\n'+(HERE/'wrapper.c').read_text().replace('#include "model.c"',''),encoding='utf-8')
    obj,dll=folder/(name+'.obj'),folder/(name+'.dll')
    args=[tools['clang'],'--target=x86_64-pc-windows-msvc','-ffreestanding','-fno-builtin','-fno-stack-protector',opt,'-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-c',unit,'-o',obj]
    if mode=='cpp':args+=['-fno-exceptions','-fno-rtti']
    for command in (args,[tools['ld.lld'],'-flavor','link','/dll','/noentry','/nodefaultlib','/out:'+str(dll),obj]):
        r=subprocess.run([str(x) for x in command],capture_output=True,text=True,timeout=30)
        need(r.returncode==0,'build failed: '+r.stderr[:1000])
    return dll
def exercise(dll,image,residents,cases,mutant=False):
    import _ctypes
    bytep=ctypes.POINTER(ctypes.c_ubyte);wordp=ctypes.POINTER(ctypes.c_uint32)
    lib=ctypes.CDLL(str(dll));fn=lib.reference_run
    fn.argtypes=[bytep,bytep,bytep,wordp,wordp,wordp,ctypes.c_uint32,wordp];fn.restype=None
    profiles={};events=(ctypes.c_uint32*16384)()
    try:
        for label,rom in residents.items():
            cfg=PROFILES[label]['cfg'];engine=Whole(image,rom,cfg);outcomes={}
            for i,c in enumerate(cases):
                regions,initial=fixture(c,rom,cfg)
                memory,r,trace,pc,calls=engine.run(regions,initial)
                buffers=[(ctypes.c_ubyte*len(b)).from_buffer_copy(b) for _,b in regions]
                regs=(ctypes.c_uint32*32)(*initial);configuration=(ctypes.c_uint32*6)(*cfg);out=(ctypes.c_uint32*4)()
                fn(*buffers,regs,configuration,events,4096,out)
                need(out[3]==0,'host diagnostic '+str(out[3])+' '+c['name'])
                equal=all(bytes(b)==data for b,(_,data) in zip(buffers,memory)) and list(regs)==r and out[0]==pc and out[1]==calls
                trace_equal=ctypes.string_at(ctypes.addressof(events),out[2]*16)==trace
                if mutant:
                    if not equal:return dict(reference=label,case=i,fixture=c,state_mismatch=True,trace_equal=trace_equal)
                    continue
                need(equal and trace_equal,'reference differential '+label+' '+str(i)+' '+str(c))
                key=hex(pc)+':'+str(calls)+'queries';outcomes[key]=outcomes.get(key,0)+1
            profiles[label]=dict(cases=len(cases),outcomes=outcomes,all_32_registers_three_regions_trace_equal=True)
        need(not mutant,'compiled mutant accepted')
        return profiles
    finally:del fn;_ctypes.FreeLibrary(lib._handle)
def load_inputs():
    need(IMAGE.stat().st_size==76800 and sha(IMAGE)==IMAGE_SHA,'APP identity')
    residents={}
    for label,v in PROFILES.items():
        p=ROOT/v['path'];need(p.stat().st_size==v['size'] and sha(p)==v['sha256'],'reference identity '+label)
        raw=p.read_bytes();cfg=v['cfg']
        need(int.from_bytes(raw[0x13c:0x140],'little')==cfg[0] and int.from_bytes(raw[0x50:0x54],'little')==cfg[3],'reference slots')
        need(raw[cfg[0]-0x40000+10:cfg[0]-0x40000+12]==bytes.fromhex('2821'),'conditional Xwchc CCC port')
        need(raw[cfg[3]-0x40000+42:cfg[3]-0x40000+48]==bytes.fromhex('1a21d98d0ea1'),'conditional Xwchc event ports')
        residents[label]=raw
    return IMAGE.read_bytes(),residents
def worker(tool_dir):
    need(os.name=='nt' and ctypes.sizeof(ctypes.c_void_p)==8,'Windows x64')
    tools={n:tool_dir/(n+'.exe') for n in TOOLS_SHA}
    for n,p in tools.items():need(sha(p)==TOOLS_SHA[n],'tool identity '+n)
    inputs={n:sha(HERE/n) for n in ('model.c','wrapper.c','oracle.py','verify.py','profiles.py','layout.py')}
    image,residents=load_inputs();cases=list(corpus());model=(HERE/'model.c').read_text();profiles={}
    mutants={
        'CCC_value_offset':model.replace('load(m,r[10]+2,1)','load(m,r[10]+3,1)'),
        'CCC_requires_last_row':model.replace('if(r[12]==r[10]) break;','if(r[12]==r[10] && r[15]+1==r[13]) break;'),
        'event_replaces_mask':model.replace('r[11]|=r[14]','r[11]=r[14]'),
        'event_accepts_id_equal_count':model.replace('if(r[14]<=r[10])','if(r[14]<r[10])'),
        'control_not_restored':model.replace('store(m,r[15]+524,4,r[13])','store(m,r[15]+524,4,0)')}
    with tempfile.TemporaryDirectory(prefix='tsl9-reference-host-') as d:
        folder=Path(d)
        for mode in ('c','cpp'):
            for opt in ('-O0','-O2'):
                name=mode+opt.replace('-','_');profiles[name]=exercise(build(tools,folder,model,mode,opt,name),image,residents,cases)
        rejected={name:exercise(build(tools,folder,text,'c','-O2',name),image,residents,cases,True) for name,text in mutants.items()}
    for n,h in inputs.items():need(sha(HERE/n)==h,'source unchanged')
    return dict(passed=True,cases_per_reference_per_profile=len(cases),profiles=profiles,compiled_mutants_rejected=rejected,nominal_RAM_contract=derive(image),
        inputs_sha256=inputs,tools_sha256=TOOLS_SHA,reference_images={k:dict(sha256=v['sha256'],bytes=v['size'],cfg=[hex(x) for x in v['cfg']]) for k,v in PROFILES.items()},
        actual_host_C_executed=True,APP_and_reference_instructions_interpreted=True,scripted_provider_returns=False,
        conditional_Xwchc=True,synthetic_control_word=True,installed_resident_identity_proved=False,hardware_executed=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
    if a.worker:print(json.dumps(worker(a.tool_dir)))
    else:
        r=subprocess.run([sys.executable]+(['-O'] if sys.flags.optimize else [])+['-B',str(Path(__file__).resolve()),'--worker','--tool-dir',str(a.tool_dir.resolve())],capture_output=True,text=True,timeout=120)
        need(r.returncode==0,'bounded worker: '+r.stderr[-2200:]);print(r.stdout.strip())
