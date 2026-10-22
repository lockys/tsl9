#include "clock_registers.h"
#include "clock_io.h"

void tsl9_rebuild_clock_fields_registers_1973c(void)
{
    const uint32_t frequency=CA_READ32(CA_GP()+108u);
    const uint32_t quotient=CA_DIVIDE_8M(frequency)&255u;
    CA_WRITE8(CA_GP()+382u,(uint8_t)quotient);
    {
        const uint32_t factor=CA_FIELD_FACTOR();
        const uint32_t product=quotient*factor;
        CA_WRITE16(CA_GP()+380u,(uint16_t)product);
        CA_FIELD_OUTPUTS(factor,product);
    }
}
