"""Compile entry C/C++, compare bounded original ISA with scripted returns."""
import argparse,ctypes,hashlib,json,os,struct,subprocess,sys,tempfile
from pathlib import Path
from oracle import Entry,need
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
IMAGE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
TOOLS_SHA={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
           'ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def action(result=0,registers=None,writes=None,target=0x12345678):
    return dict(target=target,result=result,registers=registers or {},writes=writes or [])
def fixture(n=7,handle=0x1234,first=True,second=True,actions=None,name='matrix',sp=0x2000d020):
    ram=bytearray((j*37+11)&255 for j in range(65536));low=bytearray((j*13+17)&255 for j in range(512))
    def write(a,w,v):
        data,base=(ram,0x20000000) if a>=0x20000000 else (low,0x40000)
        data[a-base:a-base+w]=(v&((1<<(8*w))-1)).to_bytes(w,'little')
    r=[(j*0x1020304+0x112233)&0xffffffff for j in range(32)]
    r[0]=0;r[1]=0x12345678;r[2]=sp;r[3]=0x20004000
    r[10]=handle;r[11]=0xa7;r[12]=0x20008000;r[13]=n
    write(r[3]+150,2,handle if first else (handle+1));write(r[3]+154,2,handle if second else (handle+1))
    write(0x4013c,4,0x12345679)  # JALR clears bit zero.
    write(0x20004100+154,2,0x789a)
    return dict(name=name,regions=[(0x20000000,bytes(ram)),(0x40000,bytes(low))],registers=r,
                actions=actions if actions is not None else [action(),action()])
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
    lib=ctypes.CDLL(str(dll));fn=lib.entry_run
    fn.argtypes=[bytep,bytep,wordp,ctypes.POINTER(Action),ctypes.c_uint32,wordp,ctypes.c_uint32,wordp];fn.restype=None
    outcomes={};events=(ctypes.c_uint32*4096)()
    try:
        for i,c in enumerate(cases):
            expected,regs,trace,pc,calls=engine.run(c['regions'],c['registers'],c['actions'])
            bufs=[(ctypes.c_ubyte*len(data)).from_buffer_copy(data) for _,data in c['regions']]
            r=(ctypes.c_uint32*32)(*c['registers']);out=(ctypes.c_uint32*4)();acts=(Action*2)()
            for j,a in enumerate(c['actions']):
                acts[j].target=a['target'];acts[j].result=a['result'];acts[j].write_count=len(a['writes'])
                for k,v in a['registers'].items():acts[j].mask|=1<<k;acts[j].registers[k]=v
                for k,w in enumerate(a['writes']):acts[j].writes[k]=Write(*w)
            fn(*bufs,r,acts,len(c['actions']),events,1024,out)
            need(out[3]==0,'valid fixture host fault '+c['name'])
            state=all(bytes(b)==data for b,(_,data) in zip(bufs,expected)) and list(r)==regs and out[0]==pc and out[1]==calls
            equal_trace=ctypes.string_at(ctypes.addressof(events),out[2]*16)==trace
            if mutation:
                if not state:return dict(case=i,name=c['name'],state_mismatch=True,trace_equal=equal_trace)
                continue
            need(state and equal_trace,'entry differential: '+str(i)+' '+c['name'])
            key=hex(pc)+':'+str(calls)+'calls';outcomes[key]=outcomes.get(key,0)+1
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
    engine=Entry(IMAGE.read_bytes());cases=list(corpus());model=(HERE/'model.c').read_text();profiles={}
    # Mutants are separate host compilations. Each must alter final state/boundary.
    gp=model.replace('    r[15]=1039;','    uint32_t entry_gp=r[3];\n    r[15]=1039;').replace('load(m,r[3]+154,2)','load(m,entry_gp+154,2)')
    slot=model.replace('    r[15]=1039;','    uint32_t saved_target=0;\n    r[15]=1039;')
    needle='r[15]=0x40000;r[15]=load(m,r[15]+316,4);'
    need(slot.count(needle)==2,'two provider loads')
    slot=slot.replace(needle,needle+'saved_target=r[15];',1)
    at=slot.rindex(needle);slot=slot[:at]+slot[at:].replace(needle,'r[15]=0x40000;r[15]=*calls?saved_target:load(m,r[15]+316,4);',1)
    inherited=model.replace('    r[15]=1039;','    uint32_t entry_a2=r[12],entry_a3=r[13];\n    r[15]=1039;').replace('r[11]=r[3]+128;r[10]=r[18];','r[11]=r[3]+128;r[10]=r[18];r[12]=entry_a2;r[13]=entry_a3;')
    sp=model.replace('    r[15]=1039;','    uint32_t entry_sp=r[2];\n    r[15]=1039;').replace('    r[1]=load(m,r[2]+28,4);','    r[2]=entry_sp-32;\n    r[1]=load(m,r[2]+28,4);')
    mutants={'stale_GP':gp,'stale_provider_slot':slot,'truncated_result':model.replace('if(r[10]==r[15])','if((r[10]&65535)==r[15])'),'reset_second_call_A2_A3':inherited,'restore_entry_SP':sp}
    with tempfile.TemporaryDirectory(prefix='tsl9-entry-host-') as d:
        folder=Path(d)
        for mode in ('c','cpp'):
            for opt in ('-O0','-O2'):
                name=mode+opt.replace('-','_');profiles[name]=exercise(build(tools,folder,model,mode,opt,name),engine,cases)
        rejected={}
        # Slot mutation may select a different target: it is checked as a script
        # mismatch, so exercise only matching targets for other mutations first.
        for name,text in mutants.items():
            dll=build(tools,folder,text,'c','-O2',name)
            if name=='stale_provider_slot':
                c=next(c for c in cases if c['name']=='fresh_provider_slot')
                # Compare state before second provider execution separately below.
                rejected[name]=slot_mutation(dll,engine,c)
            else:
                try:rejected[name]=exercise(dll,engine,cases,True)
                except ValueError as error:raise ValueError(name+': '+str(error)) from error
    for n,h in inputs.items():need(sha(HERE/n)==h,'inputs unchanged')
    return dict(passed=True,cases_per_profile=len(cases),profiles=profiles,compiled_mutations_rejected=rejected,
        inputs_sha256=inputs,tools_sha256=TOOLS_SHA,original_image_sha256=IMAGE_SHA,
        actual_host_C_executed=True,original_instructions_interpreted=True,real_provider_executed=False,
        provider_ABI_or_reachability_proved=False,firmware_build_changed=False)

def slot_mutation(dll,engine,c):
    # A stale call target must fail the explicit target constraint before any
    # second return is applied. This is a target mismatch witness, not C ABI proof.
    import _ctypes
    lib=ctypes.CDLL(str(dll));fn=lib.entry_run
    bytep=ctypes.POINTER(ctypes.c_ubyte);wordp=ctypes.POINTER(ctypes.c_uint32)
    fn.argtypes=[bytep,bytep,wordp,ctypes.POINTER(Action),ctypes.c_uint32,wordp,ctypes.c_uint32,wordp];fn.restype=None
    try:
        engine.run(c['regions'],c['registers'],c['actions'])
        buffers=[(ctypes.c_ubyte*len(b)).from_buffer_copy(b) for _,b in c['regions']]
        r=(ctypes.c_uint32*32)(*c['registers']);actions=(Action*2)();events=(ctypes.c_uint32*4096)();out=(ctypes.c_uint32*4)()
        actions[0].target=0x12345678;actions[0].result=0;actions[0].write_count=1;actions[0].writes[0]=Write(0x4013c,4,0x2468ace1)
        actions[1].target=0x2468ace0;actions[1].result=1
        fn(*buffers,r,actions,2,events,1024,out)
        trace=ctypes.string_at(ctypes.addressof(events),out[2]*16)
        headers=[struct.unpack_from('<4I',trace,j) for j in range(0,len(trace),16) if struct.unpack_from('<I',trace,j)[0]==3]
        need(out[3]==4 and out[1]==2 and len(headers)==2 and headers[1][1]==0x12345678,'stale slot must violate second target')
        return dict(name=c['name'],second_target_mismatch=True,observed_second_target=hex(headers[1][1]),
                    required_second_target='0x2468ace0',synthetic_fault=4)
    finally:del fn;_ctypes.FreeLibrary(lib._handle)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
    if a.worker:print(json.dumps(worker(a.tool_dir)))
    else:
        command=[sys.executable]+(['-O'] if sys.flags.optimize else [])+['-B',str(Path(__file__).resolve()),'--worker','--tool-dir',str(a.tool_dir.resolve())]
        r=subprocess.run(command,capture_output=True,text=True,timeout=120)
        need(r.returncode==0,'bounded worker: '+r.stderr[-2200:]);print(r.stdout.strip())
