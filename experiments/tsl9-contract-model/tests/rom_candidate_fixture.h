#ifndef ROM_CANDIDATE_FIXTURE_H
#define ROM_CANDIDATE_FIXTURE_H
/* Literal source bytes only; never original-code execution. Reproduced against
   twelfth-round/rom-model/source-byte-evidence.json by its read-only verifier. */
typedef struct { unsigned image;uint32_t va;unsigned n;uint8_t bytes[4];unsigned opcode,funct3,rs1,rs2; } rc_source_byte;
static const rc_source_byte rc_source_bytes[]={
{0,UINT32_C(0x20000078),4,{0x63,0x66,0xf7,0x02},99,6,14,15},
{0,UINT32_C(0x200000c6),4,{0x63,0x75,0xc8,0x02},99,7,16,12},
{0,UINT32_C(0x20000148),4,{0x63,0xeb,0xa8,0x08},99,6,17,10},
{0,UINT32_C(0x20000578),4,{0x63,0xea,0xe6,0x06},99,6,13,14},
{0,UINT32_C(0x4365a),4,{0x63,0x70,0xab,0x02},99,7,22,10},
{1,UINT32_C(0x19798),2,{0x9d,0x67},0,0,0,0},
{1,UINT32_C(0x1979a),4,{0x23,0x1a,0xf1,0x00},0,0,0,0},
{1,UINT32_C(0x19904),4,{0xb7,0x47,0xe8,0x03},0,0,0,0},
{2,UINT32_C(0x3c60),2,{0x95,0x67},0,0,0,0},
{2,UINT32_C(0x3c62),4,{0x23,0x1a,0xf1,0x00},0,0,0,0},
};
#endif
