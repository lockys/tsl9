/* Script: S=source, D=destination, A=argument, C1..3=control reads,
   V=word increment (zero for alias), I/X/F=extra busy reads. */
#define E(k,a,v) { k, (uint32_t)(a), (uint32_t)(v) },
#define B E('R',0x4002200cu,2u)
#define NONE
#define INITIAL E('R',0x4002200cu,1u) E('R',0x4002200cu,3u) E('R',0x4002200cu,2u) E('R',0x4002200cu,2u) E('R',0x4002200cu,3u)
#define INITIAL_NORMAL E('R',0x4002200cu,0u)
#define EXTRA B B
#define FINAL E('R',0x4002200cu,1u) E('R',0x4002200cu,1u)
#define COPY(n) E('R',S + 4u*(n),0xabc00000u + V*(n)) E('W',D + 4u*(n),0xabc00000u + V*(n))
#define WORD(n) COPY(n) E('R',0x4002200cu,0u)
#define TRACE E('R',0x40022010u,C1) E('W',0x40022010u,C1 | 0x10000u) I E('R',0x4002200cu,0u) \
 WORD(0) WORD(1) WORD(2) COPY(3) X E('R',0x4002200cu,0u) \
 WORD(4) WORD(5) WORD(6) WORD(7) WORD(8) WORD(9) WORD(10) WORD(11) \
 WORD(12) WORD(13) WORD(14) WORD(15) WORD(16) WORD(17) WORD(18) WORD(19) \
 WORD(20) WORD(21) WORD(22) WORD(23) WORD(24) WORD(25) WORD(26) WORD(27) \
 WORD(28) WORD(29) WORD(30) WORD(31) WORD(32) WORD(33) WORD(34) WORD(35) \
 WORD(36) WORD(37) WORD(38) WORD(39) WORD(40) WORD(41) WORD(42) WORD(43) \
 WORD(44) WORD(45) WORD(46) WORD(47) WORD(48) WORD(49) WORD(50) WORD(51) \
 WORD(52) WORD(53) WORD(54) WORD(55) WORD(56) WORD(57) WORD(58) WORD(59) \
 WORD(60) WORD(61) WORD(62) WORD(63) \
 E('R',0x40022010u,C2) E('W',0x40022010u,C2 | 0x200000u) F E('R',0x4002200cu,0u) E('R',0x40022010u,C3) E('W',0x40022010u,C3 & 0xfffeffffu)
#define S 0x20001000u
#define D 0x20000100u
#define V 1u
#define C1 0x12045678u
#define C2 0x12055678u
#define C3 0x12255678u
#define I INITIAL_NORMAL
#define X NONE
#define F NONE
static const event normal_events[] = { TRACE };
#undef S
#undef D
#define S 0xfffffff0u
#define D 0x20000200u
static const event wrap_events[] = { TRACE };
#undef S
#undef D
#undef V
#define S 0x200000fcu
#define D 0x20000100u
#define V 0u
static const event alias_events[] = { TRACE };
#undef S
#undef D
#undef V
#undef C1
#undef C2
#undef C3
#undef I
#undef X
#undef F
#define S 0x20002000u
#define D 0x20000300u
#define V 1u
#define C1 0x13579bdfu
#define C2 0x2448ace0u
#define C3 0xa5b3c4d6u
#define I INITIAL
#define X EXTRA
#define F FINAL
static const event poll_events[] = { TRACE };
#define ROW(n,a,s,d) { #n, a, s, d, n##_events, sizeof n##_events / sizeof n##_events[0] }
static const fixture fixtures[] = {
 ROW(normal,0x200001abu,0x20001000u,0x20000100u),
 ROW(wrap,0x200002ffu,0xfffffff0u,0x20000200u),
 ROW(alias,0x20000109u,0x200000fcu,0x20000100u),
 ROW(poll,0x20000355u,0x20002000u,0x20000300u),
};
