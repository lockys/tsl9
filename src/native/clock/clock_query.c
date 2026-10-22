#include "clock_registers.h"
#include "clock_io.h"

/* Reconstruct both memory effects and normal-return register residues.
 * A2 is assigned only on the original external-PLL branch. It is never
 * captured at entry and restored from a potentially stale snapshot. */
void tsl9_rebuild_clock_query_registers_18834(void)
{
    const uint32_t rcc=UINT32_C(0x40021004);
    const uint32_t selector=CA_READ32(rcc)&12u;
    uint32_t frequency,residue_a3;
    if(selector==4u) {
        frequency=UINT32_C(32000000);residue_a3=4u;
    } else if(selector==8u) {
        const uint32_t multiplier_sample=CA_READ32(rcc);
        const uint32_t source_sample=CA_READ32(rcc);
        uint32_t multiplier=((multiplier_sample>>18)&15u)+2u;
        uint32_t base;
        residue_a3=17u;
        if(multiplier==17u)multiplier=18u;
        if((source_sample&UINT32_C(0x10000))==0u) {
            const uint32_t control=CA_READ32(UINT32_C(0x40023800));
            base=(control&16u)!=0u?UINT32_C(8000000):UINT32_C(4000000);
        } else {
            const uint32_t external_sample=CA_READ32(rcc);
            const uint32_t external_mask=CA_EXTERNAL_MASK();
            residue_a3=UINT32_C(0x40021000);
            if((external_sample&external_mask)==external_mask) {
                base=UINT32_C(16000000);
            } else {
                const uint32_t fallback_sample=CA_READ32(rcc);
                residue_a3=fallback_sample<<14;
                base=(residue_a3&UINT32_C(0x80000000))!=0u
                    ?UINT32_C(4000000):UINT32_C(8000000);
            }
        }
        frequency=multiplier*base;
    } else {
        frequency=UINT32_C(8000000);residue_a3=8u;
    }
    CA_WRITE32(CA_GP()+108u,frequency);
    {
        const uint32_t prescaler_sample=CA_READ32(rcc);
        const uint8_t shift=CA_READ8(CA_GP()+64u+((prescaler_sample>>4)&15u));
        const uint32_t live_frequency=CA_READ32(CA_GP()+108u);
        const uint32_t result=live_frequency>>(shift&31u);
        CA_WRITE32(CA_GP()+108u,result);
        CA_QUERY_OUTPUTS(residue_a3,(uint32_t)shift,result);
    }
}
