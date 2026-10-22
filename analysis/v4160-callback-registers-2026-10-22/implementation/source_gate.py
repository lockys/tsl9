"""Exact two-source GP refinement of sealed C; no compilation or execution."""
import hashlib,json
from pathlib import Path
OLD='experiments/tsl9-v4160-event-callback/src';NEW='experiments/tsl9-v4160-callback-registers/src'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def inspect(root):
    original=root/OLD;new=root/NEW;oldc=(original/'callback.c').read_text();oldio=(original/'io.h').read_text();need(oldc.count('s->gp')==6,'six source-live GP uses')
    constructor='__asm__ volatile("mv %0,gp":"=r"(h.values.gp)::"memory");';snapshot='    __asm__ volatile("mv %0,gp":"=r"(h->values.gp)::"memory");\n';need(oldc.count(constructor)==1 and oldio.count(snapshot)==1,'only the two native snapshot source sites')
    expectedc=oldc.replace('s->gp','CB_GP(h)').replace(constructor,'');host='#define CB_STATE(h) ((h)->values)\n';expectedio=oldio.replace(host,host+'#define CB_GP(h) ((h)->values.gp)\n',1).replace(snapshot,'');marker='#define CB_READ(h,pc,a,w,out) do{(void)(pc);';primitive='static inline uint32_t cb_native_gp(void){register uint32_t value __asm__("gp");__asm__ volatile("":"=r"(value)::"memory");return value;}\n#define CB_GP(h) ((void)(h),cb_native_gp())\n';expectedio=expectedio.replace(marker,primitive+marker)
    need((new/'callback.c').read_bytes()==expectedc.encode() and(new/'io.h').read_bytes()==expectedio.encode() and(new/'callback.h').read_bytes()==(original/'callback.h').read_bytes(),'exact source changes only, no arithmetic/control/ABI signature changes');expanded=(new/'callback.c').read_text().replace('CB_GP(h)','s->gp');need(expanded==oldc.replace(constructor,''),'HOST GP macro is precisely the prior named live field use; removed asm was native-only')
    return dict(source_refinement_passed=True,old={n:sha(original/n) for n in('callback.c','callback.h','io.h')},new={n:sha(new/n) for n in('callback.c','callback.h','io.h')},GP_use_replacements=6,removed_native_snapshot_source_sites=2,HOST_field_expansion_identity=True,HOST_suite_rerun=False,source_algorithm_changed=False,original_physical_ABI_proved=False)
