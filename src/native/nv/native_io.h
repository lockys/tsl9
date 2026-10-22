#ifndef TSL9_V4160_FLASH_NATIVE_IO_H
#define TSL9_V4160_FLASH_NATIVE_IO_H
#if defined(TSL9_FLASH_HOST_TEST)
#include "host_io.h"
#define FN_H h,
#define FN_K(v) fn_constant((uint32_t)(v))
#define FN_AND(a,b) fn_and((a),(b))
#define FN_OR(a,b) fn_or((a),(b))
#define FN_ADD(a,b) fn_add((a),(b))
#define FN_BASE5() FN_K(0x40022000u)
#define FN_BASE4() FN_K(0x40022000u)
#define FN_MASK3(v) FN_K(v)
#define FN_ALIGN0(v) FN_AND((v),FN_K(0xffffff00u))
#define FN_POLL5_AND(v,mask) FN_AND((v),FN_K(mask))
#define FN_COUNT() FN_K(256u)
#define FN_COUNT_VALUE(v) ((v).value)
#define FN_OFFSET_VALUE(v) ((v).value)
#define FN_READ(site,address,out) do { if(!fn_read(h,(site),(address),&(out))) return fn_failed(); } while(0)
#define FN_WRITE(site,address,value) do { if(!fn_write(h,(site),(address),(value))) return fn_failed(); } while(0)
#define FN_POLL_BEGIN unsigned fn_spins=0
#define FN_POLL_STEP(site,mask) do { if(!fn_poll_step(h,(site),(mask),&fn_spins)) return fn_failed(); } while(0)
#define FN_POLL_TRUE(site,value,mask) fn_poll_true(h,(site),(value),(mask))
#define FN_CHECK_FLOW() do { if(h->flow!=FN_RETURNED) return fn_failed(); } while(0)
#define FN_WORD_DONE() (h->words_written++)
#define FN_RET_STATUS(a0,a5) fn_commit(h,(a0),0,0,0,0,(a5),0,0x20u)
#define FN_RET_UNLOCK(a0,a3,a4,a5) fn_commit(h,(a0),0,0,&(a3),&(a4),(a5),0,0x38u)
#define FN_RET_ERASE(a0,a3,a4,a5) fn_commit(h,(a0),0,0,&(a3),&(a4),(a5),0,0x38u)
#define FN_RET_PROGRAM(a0,a1,a2,a3,a4,a5,a6) fn_commit(h,(a0),&(a1),&(a2),&(a3),&(a4),(a5),&(a6),0x7eu)
#define FN_FRAME_BEGIN(destination,source) do { if(!fn_frame_begin(h,(destination),(source))) return fn_failed(); } while(0)
#define FN_FRAME_RELOAD(source) FN_READ(0x9c30u,FN_ADD(h->regs[2],FN_K(12u)),source)
#define FN_FRAME_END(result) do { if(!fn_frame_end(h)) return fn_failed(); return (result); } while(0)
#define FN_CSR_DECLARE
#define FN_CSR_CLEAR() do { if(!fn_csr(h,FN_CSR_CLEAR_REQUEST,0x9c1au)) return fn_failed(); } while(0)
#define FN_CSR_SET() do { if(!fn_csr(h,FN_CSR_SET_REQUEST,0x9c3cu)) return fn_failed(); } while(0)
#define FN_DESTINATION(v) (v)
#define FN_CALL_UNLOCK(v) tsl9_flash_unlock_18e98(h,(v))
#define FN_CALL_STATUS(v) tsl9_flash_status_18e90(h,(v))
#define FN_CALL_ERASE(v) tsl9_flash_erase_18ec4(h,(v))
#define FN_CALL_PROGRAM(d,s) tsl9_flash_program_18ef2(h,(d),(s))
#define FN_CALL_LOCK(v) tsl9_flash_lock_18eb6(h,(v))
#else
#define FN_H
#define FN_K(v) ((uint32_t)(v))
#define FN_AND(a,b) ((a)&(b))
#define FN_OR(a,b) ((a)|(b))
#define FN_ADD(a,b) ((uint32_t)((a)+(b)))
#define FN_FIXED_VALUE(reg,value) __extension__ ({ register uint32_t fn_fixed __asm__(reg)=(uint32_t)(value);__asm__ volatile("" : "+r"(fn_fixed) : : "memory");fn_fixed; })
#define FN_BASE5() FN_FIXED_VALUE("a5",0x40022000u)
#define FN_BASE4() FN_FIXED_VALUE("a4",0x40022000u)
#define FN_MASK3(v) FN_FIXED_VALUE("a3",(v))
#define FN_ALIGN0(v) FN_FIXED_VALUE("a0",FN_AND(FN_FIXED_VALUE("a0",(v)),FN_K(0xffffff00u)))
#define FN_POLL5_AND(v,mask) FN_FIXED_VALUE("a5",FN_AND((v),FN_K(mask)))
#define FN_COUNT() FN_FIXED_VALUE("a2",256u)
#define FN_COUNT_VALUE(v) (v)
#define FN_OFFSET_VALUE(v) FN_FIXED_VALUE("a5",(v))
#define FN_READ(site,address,out) ((void)(site),(out)=*(volatile uint32_t *)(uintptr_t)(address))
#define FN_WRITE(site,address,value) ((void)(site),*(volatile uint32_t *)(uintptr_t)(address)=(value))
#define FN_POLL_BEGIN
#define FN_POLL_STEP(site,mask) ((void)(site),(void)(mask))
#define FN_POLL_TRUE(site,value,mask) ((void)(site),(void)(mask),(value)!=0u)
#define FN_CHECK_FLOW() ((void)0)
#define FN_WORD_DONE() ((void)0)
#define FN_INLINE static __attribute__((always_inline)) inline
FN_INLINE uint32_t fn_native_status(uint32_t value,uint32_t base) {
 register uint32_t a0 __asm__("a0")=value,a5 __asm__("a5")=base;
 __asm__ volatile("" : "+r"(a0) : "r"(a5) : "memory");return a0;
}
FN_INLINE uint32_t fn_native_three(uint32_t value,uint32_t x3,uint32_t x4,uint32_t x5) {
 register uint32_t a0 __asm__("a0")=value,a3 __asm__("a3")=x3,a4 __asm__("a4")=x4,a5 __asm__("a5")=x5;
 __asm__ volatile("" : "+r"(a0) : "r"(a3),"r"(a4),"r"(a5) : "memory");return a0;
}
FN_INLINE uint32_t fn_native_program(uint32_t value,uint32_t x1,uint32_t x2,uint32_t x3,uint32_t x4,uint32_t x5,uint32_t x6) {
 register uint32_t a0 __asm__("a0")=value,a1 __asm__("a1")=x1,a2 __asm__("a2")=x2,a3 __asm__("a3")=x3,a4 __asm__("a4")=x4,a5 __asm__("a5")=x5,a6 __asm__("a6")=x6;
 __asm__ volatile("" : "+r"(a0) : "r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5),"r"(a6) : "memory");return a0;
}
#define FN_RET_STATUS(a0,a5) fn_native_status((a0),(a5))
#define FN_RET_UNLOCK(a0,a3,a4,a5) fn_native_three((a0),(a3),(a4),(a5))
#define FN_RET_ERASE(a0,a3,a4,a5) fn_native_three((a0),(a3),(a4),(a5))
#define FN_RET_PROGRAM(a0,a1,a2,a3,a4,a5,a6) fn_native_program((a0),(a1),(a2),(a3),(a4),(a5),(a6))
#define FN_FRAME_BEGIN(destination,source) \
 volatile struct { uint32_t reserved[3];uint32_t source_slot;uint32_t tail; } fn_frame; \
 __asm__ volatile("" : : "m"(fn_frame) : "memory"); \
 fn_frame.source_slot=(source)
#define FN_FRAME_RELOAD(source) ((source)=fn_frame.source_slot)
#define FN_FRAME_END(result) return (result)
#define FN_CSR_DECLARE register uint32_t fn_csr __asm__("s0");__asm__ volatile("li %0,136" : "=r"(fn_csr) : : "memory")
#define FN_CSR_CLEAR() __asm__ volatile("csrc 0x800, %0" : : "r"(fn_csr) : "memory")
#define FN_CSR_SET() __asm__ volatile("csrs 0x800, %0" : : "r"(fn_csr) : "memory")
#define FN_DESTINATION(v) __extension__ ({ register uint32_t fn_d __asm__("s1")=(v);__asm__ volatile("" : : "r"(fn_d) : "memory");fn_d; })
#define FN_ONE_CALL(name,value,...) __extension__ ({ register uint32_t fn_a0 __asm__("a0")=(value); \
 __asm__ volatile("jal ra, " #name : "+r"(fn_a0) : : "ra",__VA_ARGS__,"memory");fn_a0; })
#define FN_CALL_UNLOCK(v) FN_ONE_CALL(tsl9_flash_unlock_18e98,(v),"a1","a3","a4","a5")
#define FN_CALL_STATUS(v) FN_ONE_CALL(tsl9_flash_status_18e90,(v),"a5")
#define FN_CALL_ERASE(v) FN_ONE_CALL(tsl9_flash_erase_18ec4,(v),"a1","a3","a4","a5")
#define FN_CALL_LOCK(v) FN_ONE_CALL(tsl9_flash_lock_18eb6,(v),"a3","a4","a5")
#define FN_CALL_PROGRAM(d,s) __extension__ ({ register uint32_t fn_a0 __asm__("a0")=(d),fn_a1 __asm__("a1")=(s); \
 __asm__ volatile("jal ra, tsl9_flash_program_18ef2" : "+r"(fn_a0) : "r"(fn_a1) : "ra","a2","a3","a4","a5","a6","memory");fn_a0; })
#endif
#endif
