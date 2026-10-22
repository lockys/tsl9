#ifndef TSL9_CALLBACK_IO_H
#define TSL9_CALLBACK_IO_H
#include "callback.h"
#ifdef CB_HOST
#define CB_STATE(h) ((h)->values)
#define CB_GP(h) ((h)->values.gp)
#define CB_ARGS(h) ((h)->args)
#define CB_STOP(h) ((h)->flow!=CB_CONTINUE)
uint32_t cb_host_read(cb_host *,uint32_t site,uint32_t address,uint32_t width);
void cb_host_write(cb_host *,uint32_t site,uint32_t address,uint32_t width,uint32_t value);
void cb_host_call(cb_host *,uint32_t site,uint32_t target,uint32_t target_register,uint32_t mask);
void cb_host_frame_enter(cb_host *);
void cb_host_frame_leave(cb_host *);
#define CB_READ(h,pc,a,w,out) do{(out)=cb_host_read(h,pc,a,w);if(CB_STOP(h))return;}while(0)
#define CB_WRITE(h,pc,a,w,v) do{cb_host_write(h,pc,a,w,v);if(CB_STOP(h))return;}while(0)
#define CB_CALL(h,pc,t,r,m) do{cb_host_call(h,pc,t,r,m);if(CB_STOP(h))return;}while(0)
#else
typedef struct cb_native { cb_values values;uint32_t args[8]; } cb_native;
#define CB_STATE(h) ((h)->values)
#define CB_ARGS(h) ((h)->args)
#define CB_STOP(h) 0
static inline uint32_t cb_native_read(uint32_t address,uint32_t width){if(width==8)return *(volatile uint8_t *)(uintptr_t)address;if(width==16)return *(volatile uint16_t *)(uintptr_t)address;return *(volatile uint32_t *)(uintptr_t)address;}
static inline void cb_native_write(uint32_t address,uint32_t width,uint32_t value){if(width==8)*(volatile uint8_t *)(uintptr_t)address=(uint8_t)value;else if(width==16)*(volatile uint16_t *)(uintptr_t)address=(uint16_t)value;else *(volatile uint32_t *)(uintptr_t)address=value;}
static __attribute__((always_inline)) inline void cb_native_call(cb_native *h,uint32_t target,uint32_t target_register){
    register uint32_t a0 __asm__("a0")=h->args[0],a1 __asm__("a1")=h->args[1],a2 __asm__("a2")=h->args[2],a3 __asm__("a3")=h->args[3],a4 __asm__("a4")=h->args[4],a5 __asm__("a5")=h->args[5],a6 __asm__("a6")=h->args[6],a7 __asm__("a7")=h->args[7];
    if(target_register==6){a6=target;__asm__ volatile("jalr ra,a6,0":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5),"+r"(a6),"+r"(a7)::"ra","t0","t1","t2","t3","t4","t5","t6","memory");}
    else{a5=target;__asm__ volatile("jalr ra,a5,0":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5),"+r"(a6),"+r"(a7)::"ra","t0","t1","t2","t3","t4","t5","t6","memory");}
    h->args[0]=a0;h->args[1]=a1;h->args[2]=a2;h->args[3]=a3;h->args[4]=a4;h->args[5]=a5;h->args[6]=a6;h->args[7]=a7;
    /* Conventional callee preservation only: native C does not prove the
     * source's physical live S/SP state when an unknown resident violates ABI. */
}
static inline uint32_t cb_native_gp(void){register uint32_t value __asm__("gp");__asm__ volatile("":"=r"(value)::"memory");return value;}
#define CB_GP(h) ((void)(h),cb_native_gp())
#define CB_READ(h,pc,a,w,out) do{(void)(pc);(out)=cb_native_read(a,w);}while(0)
#define CB_WRITE(h,pc,a,w,v) do{(void)(pc);cb_native_write(a,w,v);}while(0)
#define CB_CALL(h,pc,t,r,m) do{(void)(pc);(void)(m);cb_native_call(h,t,r);}while(0)
#endif
#endif
