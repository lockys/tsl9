#ifndef TSL9_OTA_TX_IO_H
#define TSL9_OTA_TX_IO_H
#if defined(TX_HOST_TEST)
#include "../../tsl9-v4160-ota-tx/src/host_io.h"
#define TX_EXPECT(value,expectation) (value)
#else
#define TX_EXPECT(value,expectation) __builtin_expect(!!(value),(expectation))
#define TX_INLINE static __attribute__((always_inline)) inline
#define TX_FIXED(reg,value) __extension__ ({register uint32_t v __asm__(reg)=(value);__asm__ volatile("" : "+r"(v) : : "memory");v;})
#define TX_OBSERVE(reg) __extension__ ({register uint32_t v __asm__(reg);__asm__ volatile("" : "=r"(v) : : "memory");v;})
#define TX_ENTRY(context,command,source,length) ((void)0)
#define TX_FRAME() ((void)0)
#define TX_RESTORE_FAILURE() ((void)0)
#define TX_RESTORE_HEAD() ((void)0)
#define TX_RESTORE_S0() ((void)0)
#define TX_POP_FRAME() ((void)0)
#define TX_BUDGET() ((void)0)
#define TX_GP(value) ((value)=TX_OBSERVE("gp"))
#define TX_SET_S0(v) ((void)TX_FIXED("s0",(v)))
#define TX_SET_S1(v) ((void)TX_FIXED("s1",(v)))
#define TX_SET_S2(v) ((void)TX_FIXED("s2",(v)))
#define TX_SET_S3(v) ((void)TX_FIXED("s3",(v)))
#define TX_LIVE_S0(v) ((v)=TX_OBSERVE("s0"))
#define TX_LIVE_S1(v) ((v)=TX_OBSERVE("s1"))
#define TX_LIVE_S2(v) ((v)=TX_OBSERVE("s2"))
#define TX_LIVE_S3(v) ((v)=TX_OBSERVE("s3"))
#define TX_LIMIT5() TX_FIXED("a5",1039u)
#define TX_INVALID5() TX_FIXED("a5",0xfffeu)
#define TX_ACCEPT5() TX_FIXED("a5",1u)
#define TX_ARG0(v) TX_FIXED("a0",(v))
#define TX_ARG1(v) TX_FIXED("a1",(v))
#define TX_LANE2(v) TX_FIXED("a2",(v))
#define TX_ARG4(v) TX_FIXED("a4",(v))
#define TX_ARG5(v) TX_FIXED("a5",(v))
#define TX_ARG6(v) TX_FIXED("a6",(v))
#define TX_INDEX0(v) TX_ARG0((v)&65535u)
#define TX_RECORD5(lane) TX_ARG5((lane)*TX_ARG5(1062u))
#define TX_PACKET5(offset,base) TX_ARG5(TX_ARG5((offset)+6u)+(base))
#define TX_HIGH4(v) TX_ARG4(TX_FIXED("s0",(v))>>8)
#define TX_SUM4(high,low) TX_ARG4(TX_ARG4(high)+(low))
#define TX_MASK4(v) TX_ARG4(TX_ARG4(v)&255u)
#define TX_LENGTH_S0(v) TX_FIXED("s0",TX_FIXED("s0",(v))+6u)
TX_INLINE uint32_t tx_native_magic(void) {
 register uint32_t a4 __asm__("a4");__asm__ volatile("lui %0, 0xffff8\nxori %0, %0, -171" : "=r"(a4) : : "memory");return a4;
}
#define TX_MAGIC4() tx_native_magic()
#define TX_READ16(site,address,value,reg) ((void)(site),(value)=TX_FIXED(reg,*(volatile uint16_t *)(uintptr_t)(address)))
#define TX_READ8(site,address,value,reg) ((void)(site),(value)=TX_FIXED(reg,*(volatile uint8_t *)(uintptr_t)(address)))
#define TX_WRITE16(site,address,value) ((void)(site),*(volatile uint16_t *)(uintptr_t)(address)=(uint16_t)(value))
#define TX_WRITE8(site,address,value) ((void)(site),*(volatile uint8_t *)(uintptr_t)(address)=(uint8_t)(value))
#define TX_GATE_SLOT(site,target) ((void)(site),(target)=TX_ARG5(*(volatile uint32_t *)(uintptr_t)(TX_ARG5(0x40000u)+0x13cu)))
#define TX_TAIL_SLOT(site,target) ((void)(site),(target)=TX_FIXED("t1",*(volatile uint32_t *)(uintptr_t)(TX_ARG5(0x40000u)+0x50u)))
typedef struct tx_gate_residue {uint32_t a0,a2,a3;} tx_gate_residue;
TX_INLINE tx_gate_residue tx_native_gate(uint32_t target,uint32_t x0,uint32_t x1,uint32_t raw2,uint32_t raw3) {
 register uint32_t a0 __asm__("a0")=x0,a1 __asm__("a1")=x1,a2 __asm__("a2")=raw2,a3 __asm__("a3")=raw3,a5 __asm__("a5")=target;
 __asm__ volatile("jalr ra, %4, 0" : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a5) : : "ra","a4","a6","a7","t0","t1","t2","t3","t4","t5","t6","memory");tx_gate_residue out={a0,a2,a3};return out;
}
#define TX_GATE(site,target,x0,x1,raw2,raw3,result) do {(void)(site);tx_gate_residue out=tx_native_gate((target),(x0),(x1),(raw2),(raw3));(result)=out.a0;(raw2)=out.a2;(raw3)=out.a3;}while(0)
TX_INLINE uint32_t tx_native_storage(void) {
 register uint32_t a3 __asm__("a3");
 __asm__ volatile("lla %0, __tsl9v4160_data_2000b18c" : "=r"(a3) : : "memory");return a3;
}
#define TX_STORAGE3() tx_native_storage()
#define TX_RETURN_LARGE(value) return (value)
#define TX_RETURN_FAILURE(value) return (value)
#define TX_TAIL(target,a0,a1,a2,a3) do { \
 register uint32_t t1 __asm__("t1")=(target); \
 __asm__ volatile("" : "+r"(t1) : : "memory"); \
 __attribute__((musttail)) return ((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t))(uintptr_t)t1)((a0),(a1),(a2),(a3)); \
}while(0)
#endif
#endif
