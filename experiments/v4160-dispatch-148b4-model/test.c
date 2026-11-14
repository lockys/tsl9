#include "model.h"
#include <stdio.h>
#define CHECK(x) do { if (!(x)) { printf("FAIL line %d\n", __LINE__); return 1; } } while (0)
int main(void) {
    regs148b4 r = {0}; result148b4 o;
    r.a0=4; r.a2=255; r.a3=7; r.t1=9; r.t3=10; r.s0=0x1000; r.sp=0x2000;
    o=step_148b4(r,5);
    CHECK(!o.wrote && o.pc==0x148de && o.read_addr==0x1200 && o.r.a2==256 && o.r.a3==7 && o.r.t1==9 && o.r.t3==10);
    r.a0=5; r.a2=0xffffffffu; r.a3=255;
    o=step_148b4(r,5);
    CHECK(o.wrote && o.pc==0x1488e && o.read_addr==0x1000 && o.write_addr==0x222e && o.write_value==5);
    CHECK(o.r.a2==0 && o.r.a3==0 && o.r.t1==256 && o.r.t3==0x20a0);
    r.s0=0xfffffffdu; r.a2=1; r.sp=0xfffffff0u; r.a3=0xffffffffu; r.a0=0x80000000u;
    o=step_148b4(r,65535);
    CHECK(o.wrote && o.read_addr==1 && o.write_addr==0x1e && o.r.a3==0 && o.r.t1==0);
    r.a0=0; r.a2=0x1234ffffu;
    o=step_148b4(r,1);
    CHECK(!o.wrote && o.r.a2==0x12350000u);
    puts("PASS: 4 branch, wrap, unsigned and old-index cases");
    return 0;
}
