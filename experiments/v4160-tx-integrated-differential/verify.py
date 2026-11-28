"""Compile composed TX C/C++ against one continuous bounded ISA run."""
import argparse,ctypes,hashlib,json,os,struct,subprocess,sys,tempfile
from pathlib import Path
from oracle import Whole,need
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
IMAGE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
TOOLS_SHA={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
           'ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
SIZE=196608
CAPACITY=2*65535+256
RAM_PATTERN=bytes((j*37+11)&255 for j in range(SIZE))
LOW_PATTERN=bytes((j*13+17)&255 for j in range(512))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def action(result=0,registers=None,writes=None,target=0x12345678):
    return dict(target=target,result=result,registers=registers or {},writes=writes or [])
def fixture(n=7,handle=0x1234,first=True,second=True,actions=None,name='matrix',sp=0x2000d020):
    initial_writes=[]
    def write(a,w,v):initial_writes.append((a,w,v&((1<<(8*w))-1)))
    r=[(j*0x1020304+0x112233)&0xffffffff for j in range(32)]
    r[0]=0;r[1]=0x12345678;r[2]=sp;r[3]=0x20004000
    r[10]=handle;r[11]=0xa7;r[12]=0x20008000;r[13]=n
    write(r[3]+150,2,handle if first else (handle+1));write(r[3]+154,2,handle if second else (handle+1))
    write(0x4013c,4,0x12345679)  # JALR clears bit zero.
    write(0x20004100+154,2,0x789a)
    return dict(name=name,initial_writes=initial_writes,registers=r,
                actions=actions if actions is not None else [action(),action()])
def materialize(c):
    ram=bytearray(RAM_PATTERN);low=bytearray(LOW_PATTERN)
    for a,w,v in c['initial_writes']:
        data,base=(ram,0x20000000) if a>=0x20000000 else (low,0x40000)
        i=a-base;need(0<=i and i+w<=len(data),'fixture write mapped')
        data[i:i+w]=v.to_bytes(w,'little')
    return [(0x20000000,bytes(ram)),(0x40000,bytes(low))]
def corpus():
    for n in (0,1039,1040,65536,0xffffffff):
        for handle in (0,1,0xfffe,0xffff,0x10001):
            for first in (False,True):
                for second in (False,True):
                    for ret1 in (0,1,2,0xffffffff):
                        for ret2 in (0,1,2,0xffffffff):
                            yield fixture(n,handle,first,second,[action(ret1),action(ret2)])
    yield fixture(actions=[action(0,{3:0x20004100,18:0x789a,12:0xcafebabe,13:0xfacefeed}),action(1)],name='live_GP_S2_and_inherited_A2_A3')
    yield fixture(actions=[action(0,{3:0x20004100}),action(1)],name='GP_redirect_rejects_second')
    yield fixture(actions=[action(0,writes=[(0x4013c,4,0x2468ace1)]),action(1,target=0x2468ace0)],name='fresh_provider_slot')
    yield fixture(actions=[action(0x10001),action(0x10001)],name='full_width_results')
    yield fixture(actions=[action(1,{8:0xffffffff,9:0x20009000,19:0xabcdef12})],name='post_provider_unchecked_length')
    yield fixture(actions=[action(0,{2:0x2000d040},[(0x2000d05c,4,0x87654321)]),action(0)],name='live_SP_restore')
    yield fixture(actions=[action(0,writes=[(0x2000409a,2,0xabcd)]),action(1)],name='fresh_second_handle')
    yield fixture(actions=[action(0),action(0,writes=[(0x2000d01c,4,0x31415926)])],name='saved_RA_write')
    yield fixture(actions=[action(0,{j:(0x2000d000 if j==2 else 0x20004100 if j==3 else 0x76540000+j) for j in range(1,32) if j!=10}),action()],name='arbitrary_register_changes')
    yield fixture(sp=0x200040a0,name='saved_frame_aliases_handles')

    yield fixture(actions=[action(1,{8:3,9:0x20020000,19:0x55,3:0x20004100,2:0x2000d040},
        [(0x40050,4,0x87654321),(0x20020000,1,0xaa),(0x2000d05c,4,0xdeadbeef),(0x20004194,1,0x5a)])],name='composed_live_state')
    for bank in (0,1):
        for n in (0,1,4,31,255):
            slot=0x2000b18c+1062*bank;d=slot+6
            for delta in (None,-1,0,4,5,16):
                source=0x20020000 if delta is None else d+delta
                for stack in ('separate','checksum_RA','metadata_S0','tail_S0'):
                    # Chosen final frame pointers are injected by the accepted
                    # opaque return, after the entry frame saves have occurred.
                    sp={'separate':0x2000d000,'checksum_RA':((slot+11+n)&~3)-28,
                        'metadata_S0':((slot+2)&~3)-24,'tail_S0':0x40038}[stack]
                    for selector in ('normal','metadata','tail','saved_RA'):
                        address={'normal':0x20004094+4*bank,'metadata':slot+2,'tail':0x40050,'saved_RA':sp+28}[selector]
                        changes={8:n,9:source,19:0xabcdef12,2:sp,3:address-148-4*bank}
                        a=action(1,changes,[(0x40050,4,0x13579bdf)])
                        yield fixture(n=min(n,1039),first=(bank==0),actions=[a],name='alias_'+stack+'_'+selector)
        for n in (1039,1040,1050,1051,1052,65529,65530,65535):
            yield fixture(n=7,first=(bank==0),actions=[action(1,{8:n,9:0x20020000})],name='long_'+str(n))

class Write(ctypes.Structure):_fields_=[('address',ctypes.c_uint32),('width',ctypes.c_uint32),('value',ctypes.c_uint32)]
class Action(ctypes.Structure):_fields_=[('target',ctypes.c_uint32),('result',ctypes.c_uint32),('mask',ctypes.c_uint32),('registers',ctypes.c_uint32*32),('write_count',ctypes.c_uint32),('writes',Write*4)]
def build(tools,folder,text,mode,opt,name):
    unit=folder/(name+'.c');unit.write_text(text+'\n'+(HERE/'wrapper.c').read_text().replace('#include "model.c"',''),encoding='utf-8')
    obj,dll=folder/(name+'.obj'),folder/(name+'.dll')
    args=[tools['clang'],'--target=x86_64-pc-windows-msvc','-ffreestanding','-fno-builtin','-fno-stack-protector',opt,'-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17','-c',unit,'-o',obj]
    if mode=='cpp':args+=['-fno-exceptions','-fno-rtti']
    for command in (args,[tools['ld.lld'],'-flavor','link','/dll','/noentry','/nodefaultlib','/out:'+str(dll),obj]):
        p=subprocess.run([str(x) for x in command],capture_output=True,text=True,timeout=30)
        need(p.returncode==0,'compile/link: '+p.stderr[:1200])
    return dll
def exercise(dll,engine,cases,mutation=False):
    import _ctypes
    bytep=ctypes.POINTER(ctypes.c_ubyte);wordp=ctypes.POINTER(ctypes.c_uint32)
    lib=ctypes.CDLL(str(dll));fn=lib.whole_run
    fn.argtypes=[bytep,bytep,wordp,ctypes.POINTER(Action),ctypes.c_uint32,wordp,ctypes.c_uint32,wordp];fn.restype=None
    outcomes={};events=(ctypes.c_uint32*(4*CAPACITY))()
    try:
        for i,c in enumerate(cases):
            regions=materialize(c)
            expected,regs,trace,pc,calls,domain=engine.run(regions,c['registers'],c['actions'])
            bufs=[(ctypes.c_ubyte*len(data)).from_buffer_copy(data) for _,data in regions]
            r=(ctypes.c_uint32*32)(*c['registers']);out=(ctypes.c_uint32*5)();acts=(Action*2)()
            for j,a in enumerate(c['actions']):
                acts[j].target=a['target'];acts[j].result=a['result'];acts[j].write_count=len(a['writes'])
                for k,v in a['registers'].items():acts[j].mask|=1<<k;acts[j].registers[k]=v
                for k,w in enumerate(a['writes']):acts[j].writes[k]=Write(*w)
            fn(*bufs,r,acts,len(c['actions']),events,CAPACITY,out)
            need(out[3]==0,'valid fixture host fault '+c['name'])
            state=all(bytes(b)==data for b,(_,data) in zip(bufs,expected)) and list(r)==regs and out[0]==pc and out[1]==calls and out[4]==domain
            equal_trace=ctypes.string_at(ctypes.addressof(events),out[2]*16)==trace
            if mutation:
                if not state:return dict(case=i,name=c['name'],state_mismatch=True,trace_equal=equal_trace)
                continue
            need(state and equal_trace,'composed differential: '+str(i)+' '+c['name'])
            key=hex(pc)+':'+str(calls)+'calls:domain'+str(domain);outcomes[key]=outcomes.get(key,0)+1
        need(not mutation,'mutation has no state witness')
        return dict(cases=len(cases),outcomes=outcomes,all_registers_memory_trace_equal=True)
    finally:
        del fn;_ctypes.FreeLibrary(lib._handle)
def worker(tool_dir):
    need(os.name=='nt' and ctypes.sizeof(ctypes.c_void_p)==8,'Windows x64 required')
    tools={n:tool_dir/(n+'.exe') for n in TOOLS_SHA}
    for n,p in tools.items():need(sha(p)==TOOLS_SHA[n],'pinned tool '+n)
    need(IMAGE.stat().st_size==76800 and sha(IMAGE)==IMAGE_SHA,'original image identity')
    inputs={n:sha(HERE/n) for n in ('model.c','wrapper.c','oracle.py','verify.py')}
    engine=Whole(IMAGE.read_bytes());cases=list(corpus());model=(HERE/'model.c').read_text();profiles={}
    mutants={}
    for name,original,reg in [('stale_length','r[13]',8),('stale_source','r[12]',9),('stale_command','r[11]',19),('stale_GP','r[3]',3),('stale_SP','r[2]-32',2)]:
        text=model.replace('    uint32_t pc=tx_entry(', '    uint32_t stale='+original+';\n    uint32_t pc=tx_entry(')
        text=text.replace('    tx_complete(m,r);','    r['+str(reg)+']=stale;\n    tx_complete(m,r);')
        mutants[name]=text
    mutants['checksum_offset']=model.replace('add32(add32(d,length),5)','add32(add32(d,length),4)')
    with tempfile.TemporaryDirectory(prefix='tsl9-whole-host-') as d:
        folder=Path(d)
        for mode in ('c','cpp'):
            for opt in ('-O0','-O2'):
                name=mode+opt.replace('-','_');profiles[name]=exercise(build(tools,folder,model,mode,opt,name),engine,cases)
        rejected={}
        for name,text in mutants.items():
            dll=build(tools,folder,text,'c','-O2',name)
            try:rejected[name]=exercise(dll,engine,cases,True)
            except ValueError as error:raise ValueError(name+': '+str(error)) from error
    for n,h in inputs.items():need(sha(HERE/n)==h,'inputs unchanged')
    return dict(passed=True,cases_per_profile=len(cases),profiles=profiles,compiled_mutations_rejected=rejected,
        inputs_sha256=inputs,tools_sha256=TOOLS_SHA,original_image_sha256=IMAGE_SHA,
        actual_host_C_executed=True,continuous_original_ISA_run=True,seam_state_recorded=True,original_instructions_interpreted=True,real_provider_executed=False,
        provider_ABI_or_reachability_proved=False,post_provider_length_above_65535_is_domain_stop=True,firmware_build_changed=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
    if a.worker:print(json.dumps(worker(a.tool_dir)))
    else:
        command=[sys.executable]+(['-O'] if sys.flags.optimize else [])+['-B',str(Path(__file__).resolve()),'--worker','--tool-dir',str(a.tool_dir.resolve())]
        r=subprocess.run(command,capture_output=True,text=True,timeout=120)
        need(r.returncode==0,'bounded worker: '+r.stderr[-2200:]);print(r.stdout.strip())
