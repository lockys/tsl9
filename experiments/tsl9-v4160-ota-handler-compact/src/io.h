#ifndef TSL9_V4160_OTA_HANDLER_IO_H
#define TSL9_V4160_OTA_HANDLER_IO_H
#include "ota_handler.h"
#ifdef OH_HOST
typedef oh_host oh_port;
#define OH_GP(h) ((h)->values.gp)
#define OH_STACK(h,n) ((h)->values.sp+(uint32_t)(n))
#define OH_STOP(h) ((h)->flow!=OH_CONTINUE)
uint32_t oh_host_read(oh_host *,uint32_t,uint32_t,uint32_t);
void oh_host_write(oh_host *,uint32_t,uint32_t,uint32_t,uint32_t);
void oh_host_call(oh_host *,uint32_t,oh_callee,uint32_t,uint32_t);
void oh_host_enter(oh_host *);
void oh_host_leave(oh_host *);
#define OH_READ(h,pc,address,width,out) do{(out)=oh_host_read(h,pc,address,width);if(OH_STOP(h))return;}while(0)
#define OH_WRITE(h,pc,address,width,value) do{oh_host_write(h,pc,address,width,value);if(OH_STOP(h))return;}while(0)
#define OH_CALL(h,pc,kind,target,mask) do{oh_host_call(h,pc,kind,target,mask);if(OH_STOP(h))return;}while(0)
#define OH_REQUIRE_A0(h) do{if(!(h)->return_value_known){(h)->flow=OH_UNKNOWN;return;}}while(0)
#define OH_CB_8E18() UINT32_C(0x8e18)
#define OH_CB_9EE0() UINT32_C(0x9ee0)
#define OH_CB_99E8() UINT32_C(0x99e8)
#else
/* Only the response bytes escape to the packet provider. Keep the argument
 * state in a separate object so that this exposure does not alias args[]. */
typedef struct oh_port { oh_values values;uint32_t args[8];volatile uint8_t *response; } oh_port;
#define OH_STACK(h,n) ((uint32_t)(uintptr_t)&(h)->response[(n)-12u])
#define OH_STOP(h) 0
static inline uint32_t oh_native_gp(void){register uint32_t value __asm__("gp");__asm__ volatile("":"=r"(value)::"memory");return value;}
#define OH_GP(h) ((void)(h),oh_native_gp())
static inline uint32_t oh_native_read(uint32_t address,uint32_t width){if(width==8)return *(volatile uint8_t *)(uintptr_t)address;return *(volatile uint32_t *)(uintptr_t)address;}
static inline void oh_native_write(uint32_t address,uint32_t width,uint32_t value){if(width==8)*(volatile uint8_t *)(uintptr_t)address=(uint8_t)value;else *(volatile uint32_t *)(uintptr_t)address=value;}
/* These are real unresolved source symbols, not numeric address providers.
 * A complete link must supply the actual section-backed entries. */
extern unsigned char __tsl9v4160_ota_code_8e18[];
extern unsigned char __tsl9v4160_ota_code_9ee0[];
extern unsigned char __tsl9v4160_captured_body_99e8[];
#define OH_CB_8E18() ((uint32_t)(uintptr_t)__tsl9v4160_ota_code_8e18)
#define OH_CB_9EE0() ((uint32_t)(uintptr_t)__tsl9v4160_ota_code_9ee0)
#define OH_CB_99E8() ((uint32_t)(uintptr_t)__tsl9v4160_captured_body_99e8)
static __attribute__((always_inline)) inline void oh_native_call(oh_port *h,oh_callee kind,uint32_t target){
    register uint32_t a0 __asm__("a0")=h->args[0],a1 __asm__("a1")=h->args[1],a2 __asm__("a2")=h->args[2],a3 __asm__("a3")=h->args[3],a4 __asm__("a4")=h->args[4],a5 __asm__("a5")=h->args[5],a6 __asm__("a6")=h->args[6],a7 __asm__("a7")=h->args[7];
#define OH_NATIVE_ASM(text) __asm__ volatile(text:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5),"+r"(a6),"+r"(a7)::"ra","t0","t1","t2","t3","t4","t5","t6","memory")
    switch(kind){
    case OH_UID_92F2:OH_NATIVE_ASM("jal ra,__tsl9v4160_ota_code_92f2");break;
    case OH_QUARTER_9C0A:OH_NATIVE_ASM("jal ra,__tsl9v4160_call_9c0a");break;
    case OH_SCHEDULE_9124:OH_NATIVE_ASM("jal ra,__tsl9v4160_call_9124");break;
    case OH_SMALL_REPLY_13F66:OH_NATIVE_ASM("jal ra,__tsl9v4160_ota_code_13f66");break;
    case OH_PACKET_REPLY_13E98:OH_NATIVE_ASM("jal ra,__tsl9v4160_conditional_code_13e98");break;
    case OH_PAGE_REPLY_9B8E:OH_NATIVE_ASM("jal ra,__tsl9v4160_ota_code_9b8e");break;
    case OH_COPY_SLOT_4C:a5=target;OH_NATIVE_ASM("jalr ra,a5,0");break;
    }
#undef OH_NATIVE_ASM
    h->args[0]=a0;h->args[1]=a1;h->args[2]=a2;h->args[3]=a3;h->args[4]=a4;h->args[5]=a5;h->args[6]=a6;h->args[7]=a7;
    /* Conventional C preservation only. No proof of physical live S/SP when
     * an opaque target violates that ABI; HOST mutations are separate. */
}
#define OH_READ(h,pc,address,width,out) do{(void)(h);(void)(pc);(out)=oh_native_read(address,width);}while(0)
#define OH_WRITE(h,pc,address,width,value) do{(void)(h);(void)(pc);oh_native_write(address,width,value);}while(0)
#define OH_CALL(h,pc,kind,target,mask) do{(void)(pc);(void)(mask);oh_native_call(h,kind,target);}while(0)
#define OH_REQUIRE_A0(h) ((void)(h))
#endif
#endif
