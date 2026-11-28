"""Compiled RX payload semantics and exhaustive decode-derived counter bounds."""
import argparse,ctypes,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from oracle import Payload,need
from layout import derive
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
IMAGE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
TOOLS_SHA={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
RAM=bytes((j*37+11)&255 for j in range(65536));RX=0x2000b9d8
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def corpus():
    for field,counts in [('normal',(0,1,2,3,1038,1039,1040,65534,65535)),
        ('count',(0,2,1038)),('length',(0,2,1038)),('state',(0,2,1038)),('sum',(1,3,1039))]:
        for count in counts:
            for length in (0,1,2,1039,1040,1041,65535):
                for byte in (0,1,127,255):
                    for old_sum in (0,255):
                        for source in ('GP_sum','payload','count','length','state'):
                            yield dict(field=field,count=count,length=length,byte=byte,old_sum=old_sum,source=source)
def fixture(c):
    ram=bytearray(RAM);d=RX+c['count']
    gp=0x20004000 if c['field']=='normal' else d-{'count':138,'length':142,'state':156,'sum':165}[c['field']]
    def put(a,w,v):
        i=a-0x20000000;need(0<=i and i+w<=len(ram),'mapped fixture')
        ram[i:i+w]=v.to_bytes(w,'little')
    put(gp+138,2,c['count']);put(gp+142,2,c['length']);put(gp+156,1,5);put(gp+165,1,c['old_sum'])
    r=[(j*0x1020304+0x112233)&0xffffffff for j in range(32)]
    r[0]=0;r[2]=0x2000d020;r[3]=gp;r[15]=c['byte']
    # A rejected count does not form/dereference a payload destination. Keep
    # the synthetic checksum pointer mapped even for deliberate bad mutants.
    r[9]={'GP_sum':gp+165,'payload':RX+c['count']%1040,'count':gp+138,'length':gp+142,'state':gp+156}[c['source']]
    return [(0x20000000,bytes(ram))],r
def build(tools,folder,text,mode,opt,name):
    unit=folder/(name+'.c');unit.write_text(text+'\n'+(HERE/'wrapper.c').read_text().replace('#include "model.c"',''),encoding='utf-8')
    obj,dll=folder/(name+'.obj'),folder/(name+'.dll')
    args=[tools['clang'],'--target=x86_64-pc-windows-msvc','-ffreestanding','-fno-builtin','-fno-stack-protector',opt,'-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-c',unit,'-o',obj]
    if mode=='cpp':args+=['-fno-exceptions','-fno-rtti']
    for command in (args,[tools['ld.lld'],'-flavor','link','/dll','/noentry','/nodefaultlib','/out:'+str(dll),obj]):
        p=subprocess.run([str(x) for x in command],capture_output=True,text=True,timeout=30)
        need(p.returncode==0,'build: '+p.stderr[:1000])
    return dll
def exercise(dll,engine,cases,mutant=False):
    import _ctypes
    bytep=ctypes.POINTER(ctypes.c_ubyte);wordp=ctypes.POINTER(ctypes.c_uint32)
    lib=ctypes.CDLL(str(dll));fn=lib.rx_run;fn.argtypes=[bytep,wordp,wordp,ctypes.c_uint32,wordp];fn.restype=None
    events=(ctypes.c_uint32*256)();accepted=0
    try:
        for i,c in enumerate(cases):
            regions,r=fixture(c);memory,expected,trace,pc=engine.run(regions,r)
            ram=(ctypes.c_ubyte*65536).from_buffer_copy(regions[0][1]);regs=(ctypes.c_uint32*32)(*r);out=(ctypes.c_uint32*3)()
            fn(ram,regs,events,64,out);need(out[2]==0,'host diagnostic on valid input')
            state=bytes(ram)==bytes(memory[0][1]) and list(regs)==expected and out[0]==pc
            trace_equal=ctypes.string_at(ctypes.addressof(events),out[1]*16)==trace
            if mutant:
                if not state:return dict(case=i,fixture=c,state_mismatch=True,trace_equal=trace_equal)
                continue
            need(state and trace_equal,'payload differential '+str(c))
            accepted+=c['count']<=1039
        need(not mutant,'mutant has no state witness')
        return dict(cases=len(cases),payload_cases=accepted,rejected_cases=len(cases)-accepted,all_32_registers_full_RAM_trace_equal=True)
    finally:del fn;_ctypes.FreeLibrary(lib._handle)
def worker(tool_dir):
    need(os.name=='nt' and ctypes.sizeof(ctypes.c_void_p)==8,'Windows x64')
    tools={n:tool_dir/(n+'.exe') for n in TOOLS_SHA}
    for n,p in tools.items():need(sha(p)==TOOLS_SHA[n],'tool identity '+n)
    need(IMAGE.stat().st_size==76800 and sha(IMAGE)==IMAGE_SHA,'original image identity')
    image=IMAGE.read_bytes();engine=Payload(image);cases=list(corpus());model=(HERE/'model.c').read_text()
    inputs={n:sha(HERE/n) for n in ('model.c','wrapper.c','oracle.py','verify.py','layout.py')}
    mutants={
        'guard_allows_1040':model.replace('r[14]=1039','r[14]=1040'),
        'payload_uses_new_count':model.replace('r[13]+=r[12]','r[13]+=r[14]'),
        'cached_expected_length':model.replace('r[13]=load(m,r[3]+142,2);','r[13]=cached_length;').replace('    r[12]=load','    uint32_t cached_length=load(m,r[3]+142,2);\n    r[12]=load'),
        'cached_checksum_byte':model.replace('r[14]=load(m,r[9],1);','r[14]=cached_sum;').replace('    r[12]=load','    uint32_t cached_sum=load(m,r[9],1);\n    r[12]=load'),
        'state_six_only_on_equality':model.replace('if(r[14]>=r[13])','if(r[14]==r[13])'),
        'checksum_ignores_live_S1':model.replace('load(m,r[9],1)','load(m,r[3]+165,1)'),
        'checksum_register_truncated':model.replace('r[15]+=r[14]','r[15]=(r[15]+r[14])&255u')}
    profiles={}
    with tempfile.TemporaryDirectory(prefix='tsl9-rx-payload-host-') as d:
        folder=Path(d)
        for mode in ('c','cpp'):
            for opt in ('-O0','-O2'):
                name=mode+opt.replace('-','_');profiles[name]=exercise(build(tools,folder,model,mode,opt,name),engine,cases)
        rejected={name:exercise(build(tools,folder,text,'c','-O2',name),engine,cases,True) for name,text in mutants.items()}
    for n,h in inputs.items():need(sha(HERE/n)==h,'source unchanged')
    return dict(passed=True,cases_per_profile=len(cases),profiles=profiles,compiled_mutants_rejected=rejected,
        decoded_counter_and_RAM_audit=derive(image),decoder_bytes=sum(n for _,n in engine.code.values()),decoder_instructions=len(engine.code),
        original_image_sha256=IMAGE_SHA,inputs_sha256=inputs,tools_sha256=TOOLS_SHA,actual_host_C_executed=True,
        original_payload_instructions_interpreted=True,whole_callback_executed=False,hardware_executed=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
    if a.worker:print(json.dumps(worker(a.tool_dir)))
    else:
        r=subprocess.run([sys.executable]+(['-O'] if sys.flags.optimize else [])+['-B',str(Path(__file__).resolve()),'--worker','--tool-dir',str(a.tool_dir.resolve())],capture_output=True,text=True,timeout=120)
        need(r.returncode==0,'bounded worker: '+r.stderr[-2200:]);print(r.stdout.strip())
