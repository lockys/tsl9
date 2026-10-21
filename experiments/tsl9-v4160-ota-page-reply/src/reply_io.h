#ifndef TSL9_OTA_REPLY_IO_H
#define TSL9_OTA_REPLY_IO_H
#if defined(OP_HOST_TEST)
#include "host_io.h"
#else
#define OP_INLINE static __attribute__((always_inline)) inline
#define OP_ENTRY(connection,command,index) ((void)0)
#define OP_FIXED(reg,value) __extension__ ({register uint32_t v __asm__(reg)=(value);__asm__ volatile("" : "+r"(v) : : "memory");v;})
#define OP_OBSERVE(reg) __extension__ ({register uint32_t v __asm__(reg);__asm__ volatile("" : "=r"(v) : : "memory");v;})
#define OP_SET_S0(v) ((void)OP_FIXED("s0",(v)))
#define OP_SET_S1(v) ((void)OP_FIXED("s1",(v)))
#define OP_SET_S2(v) ((void)OP_FIXED("s2",(v)))
#define OP_SET_S3(v) ((void)OP_FIXED("s3",(v)))
#define OP_SET_S4(v) ((void)OP_FIXED("s4",(v)))
#define OP_LIVE_S0(v) ((v)=OP_OBSERVE("s0"))
#define OP_LIVE_S1(v) ((v)=OP_OBSERVE("s1"))
#define OP_LIVE_S2(v) ((v)=OP_OBSERVE("s2"))
#define OP_LIVE_S3(v) ((v)=OP_OBSERVE("s3"))
#define OP_LIVE_S4(v) ((v)=OP_OBSERVE("s4"))
#define OP_FRAME_HEAD() ((void)0)
#define OP_FRAME_REST() ((void)0)
#define OP_RESTORE_NULL() ((void)0)
#define OP_RESTORE_S0() ((void)0)
#define OP_RESTORE_TAIL() ((void)0)
#define OP_SLOT(site,address,value) ((void)(site),(value)=OP_FIXED("a5",*(volatile uint32_t *)(uintptr_t)(address)))
#define OP_FREE_SLOT(site,address,value) ((void)(site),(value)=OP_FIXED("t1",*(volatile uint32_t *)(uintptr_t)(address)))
#define OP_WRITE8(site,address,value) ((void)(site),*(volatile uint8_t *)(uintptr_t)(address)=(uint8_t)(value))
#define OP_OTHER_CALLER_CLOBBERS "a3","a4","a6","a7","t0","t1","t2","t3","t4","t5","t6"
#define OP_ALLOC_SIZE0() OP_FIXED("a0",1026u)
#define OP_HEADER_HIGH5(value) OP_FIXED("a5",(value)>>8)
#define OP_SOURCE_HIGH1() OP_FIXED("a1",0x20000u)
#define OP_SOURCE_LOW1(value) OP_FIXED("a1",OP_FIXED("a1",(value))+4u)
#define OP_SOURCE_ADD1(value,index) OP_FIXED("a1",(uint32_t)((value)+(index)))
#define OP_COPY_SIZE2() OP_FIXED("a2",1024u)
#define OP_SOURCE_SHIFT1(value) OP_FIXED("a1",(value)<<10)
#define OP_BUFFER_ADVANCE0(value) OP_FIXED("a0",OP_FIXED("a0",(value))+2u)
#define OP_ARG0(value) OP_FIXED("a0",(value))
#define OP_ARG1(value) OP_FIXED("a1",(value))
#define OP_ARG2(value) OP_FIXED("a2",(value))
#define OP_TX_SIZE3() OP_FIXED("a3",1026u)
OP_INLINE uint32_t op_native_call3(uint32_t target,uint32_t x0,uint32_t x1,uint32_t x2) {
 register uint32_t a0 __asm__("a0")=x0,a1 __asm__("a1")=x1,a2 __asm__("a2")=x2,a5 __asm__("a5")=target;
 __asm__ volatile("jalr ra, %3, 0" : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a5) : : "ra",OP_OTHER_CALLER_CLOBBERS,"memory");return a0;
}
#define OP_ALLOC(target,n,cmd,index,out) ((out)=op_native_call3((target),(n),(cmd),(index)))
#define OP_COPY(target,dst,src,n) ((void)op_native_call3((target),(dst),(src),(n)))
typedef struct op_native_tx_residue {uint32_t a1,a2;} op_native_tx_residue;
OP_INLINE op_native_tx_residue op_native_tx(uint32_t x0,uint32_t x1,uint32_t x2,uint32_t x3) {
 register uint32_t a0 __asm__("a0")=x0,a1 __asm__("a1")=x1,a2 __asm__("a2")=x2,a3 __asm__("a3")=x3;
 __asm__ volatile("jal ra, __tsl9v4160_call_8a56" : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3) : : "ra","a4","a5","a6","a7","t0","t1","t2","t3","t4","t5","t6","memory");
 op_native_tx_residue out={a1,a2};return out;
}
#define OP_TX(ctx,cmd,buf,n,r1,r2) do {op_native_tx_residue out=op_native_tx((ctx),(cmd),(buf),(n));(r1)=out.a1;(r2)=out.a2;}while(0)
#define OP_RETURN_NULL(value) return (value)
#define OP_TAIL_RELEASE(target,buf,r1,r2) do { \
 register uint32_t t1 __asm__("t1")=(target),a0 __asm__("a0")=(buf); \
 __asm__ volatile("" : "+r"(t1),"+r"(a0) : : "memory"); \
 __attribute__((musttail)) return ((uint32_t (*)(uint32_t,uint32_t,uint32_t))(uintptr_t)t1)(a0,(r1),(r2)); \
}while(0)
#endif
#endif
