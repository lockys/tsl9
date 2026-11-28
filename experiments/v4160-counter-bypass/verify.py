"""Compiled post-copy bypass semantics versus continuous original instructions."""
import argparse,ctypes,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from oracle import Counter,need
from audit import derive
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
IMAGE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
TOOLS_SHA={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
RAM=bytes((i*37+11)&255 for i in range(65536))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def corpus():
    for cached in (0,1,255):
        for current in (0,1,255):
            for flag in (0,1):
                for field in (1960,1961,2050,2139,2140):
                    for mode in (0,1,2,3,255):
                        for index in (0,1,2,3,4,91,92,255):
                            yield dict(cached=cached,current=current,flag=flag,field=field,mode=mode,index=index)
def fixture(c,image):
    ram=bytearray(RAM);gp=0x20004000;sp=0x2000d000
    def put(a,w,v):ram[a-0x20000000:a-0x20000000+w]=v.to_bytes(w,'little')
    put(gp+170,1,c['cached']);put(gp+175,1,c['flag']);put(gp+176,1,c['index'])
    put(0x2000beea,1,c['current']);put(0x2000bed5,1,c['mode'])
    put(sp+8,4,0xe00000a5|((c['field']>>8)<<8)|((c['field']&255)<<16))
    r=[(j*0x1020304+0x112233)&0xffffffff for j in range(32)]
    r[0]=0;r[2]=sp;r[3]=gp
    return [(0x20000000,bytes(ram)),(0x1ab48,image[0x1ab48-0x8000:0x1ab50-0x8000])],r
def build(tools,folder,text,mode,opt,name):
    unit=folder/(name+'.c');unit.write_text(text+'\n'+(HERE/'wrapper.c').read_text().replace('#include "model.c"',''),encoding='utf-8')
    obj,dll=folder/(name+'.obj'),folder/(name+'.dll')
    args=[tools['clang'],'--target=x86_64-pc-windows-msvc','-ffreestanding','-fno-builtin','-fno-stack-protector',opt,'-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-c',unit,'-o',obj]
    if mode=='cpp':args+=['-fno-exceptions','-fno-rtti']
    for command in (args,[tools['ld.lld'],'-flavor','link','/dll','/noentry','/nodefaultlib','/out:'+str(dll),obj]):
        p=subprocess.run([str(x) for x in command],capture_output=True,text=True,timeout=30)
        need(p.returncode==0,'build: '+p.stderr[:1000])
    return dll
def exercise(dll,engine,image,cases,mutant=False):
    import _ctypes
    bytep=ctypes.POINTER(ctypes.c_ubyte);wordp=ctypes.POINTER(ctypes.c_uint32)
    lib=ctypes.CDLL(str(dll));fn=lib.counter_run
    fn.argtypes=[bytep,bytep,wordp,wordp,ctypes.c_uint32,wordp];fn.restype=None
    events=(ctypes.c_uint32*1024)();outcomes={}
    try:
        for i,c in enumerate(cases):
            regions,r=fixture(c,image);memory,expected,trace,pc,calls,window=engine.run(regions,r)
            buffers=[(ctypes.c_ubyte*len(data)).from_buffer_copy(data) for _,data in regions]
            regs=(ctypes.c_uint32*32)(*r);out=(ctypes.c_uint32*5)()
            fn(*buffers,regs,events,256,out);need(out[3]==0,'valid fixture host diagnostic')
            state=all(bytes(b)==bytes(data) for b,(_,data) in zip(buffers,memory)) and list(regs)==expected and out[0]==pc and out[1]==calls and out[4]==window
            trace_equal=ctypes.string_at(ctypes.addressof(events),out[2]*16)==trace
            if mutant:
                if not state:return dict(case=i,fixture=c,state_mismatch=True,trace_equal=trace_equal)
                continue
            need(state and trace_equal,'counter differential '+str(c))
            key=hex(pc)+':window'+str(window);outcomes[key]=outcomes.get(key,0)+1
        need(not mutant,'mutant has no state witness')
        return dict(cases=len(cases),outcomes=outcomes,all_32_registers_two_regions_trace_equal=True)
    finally:del fn;_ctypes.FreeLibrary(lib._handle)
def worker(tool_dir):
    need(os.name=='nt' and ctypes.sizeof(ctypes.c_void_p)==8,'Windows x64')
    tools={n:tool_dir/(n+'.exe') for n in TOOLS_SHA}
    for n,p in tools.items():need(sha(p)==TOOLS_SHA[n],'tool identity '+n)
    need(IMAGE.stat().st_size==76800 and sha(IMAGE)==IMAGE_SHA,'original image identity')
    image=IMAGE.read_bytes();engine=Counter(image);cases=list(corpus());model=(HERE/'model.c').read_text()
    inputs={n:sha(HERE/n) for n in ('model.c','wrapper.c','oracle.py','verify.py','audit.py')}
    mutants={
        'invented_index_mask':model.replace('r[15]=load(m,r[3]+176,1);r[14]=r[15]<<1;','r[15]=load(m,r[3]+176,1)&3u;r[14]=r[15]<<1;'),
        'lookup_index_incremented':model.replace('r[15]=load(m,r[3]+176,1);r[14]=r[15]<<1;','r[15]=(load(m,r[3]+176,1)+1)&3u;r[14]=r[15]<<1;'),
        'status_compares_only_truth':model.replace('if(r[15]!=r[10])','if((r[15]!=0)!=(r[10]!=0))'),
        'geometry_upper_off_by_one':model.replace('if(r[14]<r[15])','if(r[14]+1<r[15])'),
        'getter_reuses_cached_status':model.replace('load(m,0x2000beea,1)','load(m,r[3]+170,1)'),
        'table_bias_off_by_one':model.replace('r[14]=2050','r[14]=2051'),
        'masked_store_only_wraps_byte':model.replace('(r[15]+1)&3u','(r[15]+1)&255u')}
    profiles={}
    with tempfile.TemporaryDirectory(prefix='tsl9-counter-host-') as d:
        folder=Path(d)
        for mode in ('c','cpp'):
            for opt in ('-O0','-O2'):
                name=mode+opt.replace('-','_');profiles[name]=exercise(build(tools,folder,model,mode,opt,name),engine,image,cases)
        rejected={name:exercise(build(tools,folder,text,'c','-O2',name),engine,image,cases,True) for name,text in mutants.items()}
    for n,h in inputs.items():need(sha(HERE/n)==h,'source unchanged')
    return dict(passed=True,cases_per_profile=len(cases),profiles=profiles,compiled_mutants_rejected=rejected,
        decoded_origin_audit=derive(image),decoder_bytes=sum(n for _,n in engine.code.values()),decoder_instructions=len(engine.code),
        original_image_sha256=IMAGE_SHA,inputs_sha256=inputs,tools_sha256=TOOLS_SHA,actual_host_C_executed=True,
        original_post_copy_and_getter_instructions_interpreted=True,unselected_table_values_modeled=0,
        normal_entry_or_global_index_invariant_proved=False,hardware_executed=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
    if a.worker:print(json.dumps(worker(a.tool_dir)))
    else:
        r=subprocess.run([sys.executable]+(['-O'] if sys.flags.optimize else [])+['-B',str(Path(__file__).resolve()),'--worker','--tool-dir',str(a.tool_dir.resolve())],capture_output=True,text=True,timeout=120)
        need(r.returncode==0,'bounded worker: '+r.stderr[-2200:]);print(r.stdout.strip())
