"""Offline full large consumer/caller/counter/threshold and mapped RAM leaf.

Literal operands/data, conditional CFG, finite-index and integer certificates.
No target ISA, register/RAM machine, provider/copy/allocator/MMIO execution.
"""
import argparse
import json
from collections import deque
from hashlib import sha256
from pathlib import Path
import check_v4160_callback_dispatch_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.common
outer=previous.outer
OUT=Path(__file__).with_name('v4160-large-consumer-service-static.json')
PARTS=('consumer','caller','counter','threshold','RAMservice')
STARTS=((0x69a22,0x678cc,0x56184,0x534f6,0x2000263a),(0x69b3a,0x67a0a,0x562c4,0x535a4,0x20002686))
SOURCES=((0x69a22,0x678cc,0x56184,0x534f6,0x428aa),(0x69b3a,0x67a0a,0x562c4,0x535a4,0x42936))
SIZES=(1214,46,24,54,128)
COUNTS=(400,20,10,18,50)
HASHES=(('cef469881f199b7e7a74c2c511d84fe1a84cfc266991b5b75b1462c8c79e8ee5','3114bb35a8dae70056012d68cb7dc391ddae63ba018bc8150f9e286ab8072229','0311b2f9036ae52e5ae7987159729331ff6d402f5f1a4e0ae0abf65a55db4e8b','17f264d6cf1df9d539db350a8c91ad63a6c161013ccdda65d0ba263a13cdca78','4efd5ae35f1b66d703f286535b1bff98aeb9903039a8b9482c91b33bc545fa70'),
 ('a96c47409c8ad57a229a2630da23566a2dce5e8c18164c5b76013b155e745a59','f40dd5314469d835909d0c57d0b8d605b05e1cb870c1eab41f7da4372ce55ba7','62baf9404f4384c03b6d8fd6dea5645725e37f0732f691446f87b80ae72bae9b','5b347e105034a3bf888e3643da8f774df6a86ca54a4aadbfe932ff47aac483b9','4ab0f722dbd5ead3d31591931b1a141e119dc30de2cabbfb6e97f38293a7591d'))
TABLES=(0x6e4f4,0x6e6e4)
TABLE=bytes.fromhex('070b0d1113171d1f25292b2f353b3d4347494f535961ff00')
TABLE_HASH='0d71c11a608a03201226e75ab803f12dee8997dc7ccd80e177ccc8c3d9e96d76'
FIELDS={**previous.FIELDS,'srai':('rd','rs1','imm'),'blt':('rs1','rs2','target'),'load_signed':('rd','rs1','imm','width')}
BRANCHES=previous.BRANCHES|{'bge','blt'}

LITERALS=(
{
'consumer':'''
000 addi 2 2 -80
002 store 2 25 36 4
004 store 2 26 32 4
006 store 2 27 28 4
008 store 2 12 9 1
00a mv 27 10
00c mv 26 11
00e mv 25 12
010 mv 11 13
012 li 12 6
014 addi 10 2 10
018 store 2 8 72 4
01a store 2 9 68 4
01c store 2 19 60 4
01e store 2 20 56 4
020 store 2 21 52 4
022 store 2 22 48 4
024 store 2 23 44 4
026 store 2 24 40 4
028 mv 23 15
02a lui 8 536883200
02e store 2 1 76 4
030 store 2 18 64 4
032 mv 24 13
034 mv 9 14
036 mv 22 16
038 mv 21 17
03a load 20 2 80 4
03c load 19 2 84 4
03e auipc 1 536440832
042 jalr 1 1 -1838
046 addi 15 8 952
04a load 15 15 128 4
04e addi 8 8 952
052 beqz 15 126
054 load 15 15 28 4
056 slli 14 15 17
05a bge 14 0 126
05e li 10 12
060 load 1 2 76 4
062 load 8 2 72 4
064 load 9 2 68 4
066 load 18 2 64 4
068 load 19 2 60 4
06a load 20 2 56 4
06c load 21 2 52 4
06e load 22 2 48 4
070 load 23 2 44 4
072 load 24 2 40 4
074 load 25 2 36 4
076 load 26 2 32 4
078 load 27 2 28 4
07a addi 2 2 80
07c jr 1
07e load 15 8 152 4
082 beqz 15 94
084 jal 1 352644
088 lui 15 536883200
08c load 15 15 513 1
090 srli 15 15 2
092 beq 10 15 94
096 andi 15 9 -8
09a li 10 17
09c bnez 15 96
09e andi 15 9 5
0a2 bnez 15 168
0a4 li 10 18
0a6 jump 96
0a8 load 15 8 128 4
0ac beqz 15 188
0ae load 14 15 28 4
0b0 slli 13 14 17
0b4 blt 13 0 94
0b8 load 15 15 11 1
0ba bnez 15 94
0bc load 18 8 148 4
0c0 bne 18 0 1148
0c4 load 15 8 152 4
0c8 call_indirect 1 15
0ca mv 18 10
0cc beqz 10 94
0ce li 14 3
0d0 bltu 14 26 164
0d4 store 18 27 13 1
0d8 store 18 26 101 1
0dc li 12 6
0de li 11 0
0e0 mv 10 24
0e2 auipc 1 536440832
0e6 jalr 1 1 -1608
0ea bne 10 0 1160
0ee li 14 1
0f0 store 18 14 108 1
0f4 store 18 25 109 1
0f8 li 12 6
0fa mv 11 24
0fc addi 10 18 110
100 auipc 1 536440832
104 jalr 1 1 -2032
108 store 18 0 56 1
10c andi 24 9 1
110 li 26 0
112 beq 24 0 554
116 load 13 23 0 2
11a li 14 4
11c bgeu 13 14 290
120 li 13 4
122 store 18 13 52 2
126 load 14 22 0 2
12a slli 12 13 16
12e srli 12 12 16
130 bgeu 12 14 310
134 mv 14 13
136 slli 13 14 16
13a srli 13 13 16
13c li 12 4
13e bgeu 13 12 324
142 li 14 4
144 slli 13 14 16
148 store 18 14 54 2
14c srli 13 13 16
14e addi 14 0 85
152 mul 14 13 14
156 addi 11 18 80
15a srai 14 14 8
15c store 18 14 50 2
160 li 14 1
162 store 18 14 56 1
166 load 14 21 0 2
16a store 18 14 14 2
16e load 10 20 0 2
172 add 14 14 10
174 srai 14 14 1
176 store 18 14 80 2
17a store 18 10 20 2
17e jal 1 341238
182 load 13 18 80 2
186 lui 14 4096
188 addi 14 14 -896
18c bgeu 14 13 402
190 mv 13 14
192 slli 14 13 16
196 srli 14 14 16
198 li 12 6
19a bgeu 14 12 416
19e li 13 6
1a0 store 18 13 80 2
1a4 slli 10 13 16
1a8 load 13 19 0 2
1ac addi 14 0 499
1b0 srli 10 10 16
1b2 bgeu 14 13 442
1b6 addi 13 0 499
1ba slli 11 13 16
1be srli 11 11 16
1c0 addi 14 11 1
1c4 mul 14 14 10
1c8 load 15 2 88 4
1ca store 18 13 26 2
1ce load 13 15 0 2
1d0 srai 14 14 2
1d2 bge 14 13 472
1d6 mv 14 13
1d8 load 15 2 92 4
1da slli 14 14 16
1dc srli 14 14 16
1de store 18 14 32 2
1e2 load 13 15 0 2
1e4 load 15 2 96 4
1e6 lui 12 4096
1e8 store 18 13 38 2
1ec load 13 15 0 2
1ee addi 12 12 -896
1f2 store 18 13 44 2
1f6 mv 13 14
1f8 bgeu 12 14 510
1fc mv 13 12
1fe slli 12 13 16
202 srli 12 12 16
204 li 14 10
206 bgeu 12 14 524
20a li 13 10
20c slli 14 13 16
210 srli 14 14 16
212 slli 14 14 2
214 div 14 14 10
218 store 18 13 32 2
21c addi 14 14 -1
21e bge 11 14 548
222 mv 14 11
224 store 18 14 26 2
228 li 26 1
22a andi 25 9 2
22e beq 25 0 788
232 slli 27 26 1
236 add 14 21 27
23a load 14 14 0 2
23c add 13 20 27
240 addi 11 18 82
244 store 18 14 16 2
248 load 10 13 0 2
24a add 14 14 10
24c srai 14 14 1
24e store 18 14 82 2
252 store 18 10 22 2
256 jal 1 341238
25a load 13 18 82 2
25e lui 14 4096
260 addi 14 14 -896
264 bgeu 14 13 618
268 mv 13 14
26a slli 14 13 16
26e srli 14 14 16
270 li 12 6
272 bgeu 14 12 632
276 li 13 6
278 store 18 13 82 2
27c add 14 19 27
280 load 14 14 0 2
282 slli 10 13 16
286 addi 13 0 499
28a srli 10 10 16
28c bgeu 13 14 660
290 addi 14 0 499
294 slli 11 14 16
298 srli 11 11 16
29a store 18 14 28 2
29e addi 14 11 1
2a2 mul 14 14 10
2a6 load 15 2 88 4
2a8 add 13 15 27
2ac load 13 13 0 2
2ae srai 14 14 2
2b0 bge 14 13 694
2b4 mv 14 13
2b6 load 15 2 92 4
2b8 slli 14 14 16
2ba srli 14 14 16
2bc add 13 15 27
2c0 store 18 14 34 2
2c4 load 13 13 0 2
2c6 load 15 2 96 4
2c8 lui 12 4096
2ca store 18 13 40 2
2ce add 27 27 15
2d0 load 13 27 0 2
2d4 addi 12 12 -896
2d8 store 18 13 46 2
2dc mv 13 14
2de bgeu 12 14 740
2e2 mv 13 12
2e4 slli 14 13 16
2e8 srli 14 14 16
2ea li 12 10
2ec bgeu 14 12 754
2f0 li 13 10
2f2 slli 14 13 16
2f6 srli 14 14 16
2f8 slli 14 14 2
2fa div 14 14 10
2fe store 18 13 34 2
302 addi 14 14 -1
304 bge 11 14 778
308 mv 14 11
30a addi 26 26 1
30c store 18 14 28 2
310 andi 26 26 255
314 andi 9 9 4
316 beq 9 0 1166
31a slli 9 26 1
31e add 23 23 9
320 load 13 23 0 2
324 li 14 4
326 bgeu 13 14 812
32a li 13 4
32c store 18 13 70 2
330 add 22 22 9
332 load 14 22 0 2
336 slli 12 13 16
33a srli 12 12 16
33c bgeu 12 14 834
340 mv 14 13
342 slli 13 14 16
346 srli 13 13 16
348 li 12 4
34a bgeu 13 12 848
34e li 14 4
350 slli 13 14 16
354 store 18 14 72 2
358 srli 13 13 16
35a addi 14 0 85
35e mul 14 13 14
362 add 21 21 9
364 add 20 20 9
366 addi 11 18 84
36a srai 14 14 8
36c store 18 14 74 2
370 load 14 18 56 1
374 ori 14 14 2
378 store 18 14 56 1
37c load 14 21 0 2
380 store 18 14 18 2
384 load 10 20 0 2
388 add 14 14 10
38a srai 14 14 1
38c store 18 14 84 2
390 store 18 10 24 2
394 jal 1 341238
398 load 13 18 84 2
39c lui 14 4096
39e addi 14 14 -896
3a2 bgeu 14 13 936
3a6 mv 13 14
3a8 slli 14 13 16
3ac srli 14 14 16
3ae li 12 6
3b0 bgeu 14 12 950
3b4 li 13 6
3b6 store 18 13 84 2
3ba add 19 19 9
3bc slli 10 13 16
3c0 load 13 19 0 2
3c4 addi 14 0 499
3c8 srli 10 10 16
3ca bgeu 14 13 978
3ce addi 13 0 499
3d2 slli 11 13 16
3d6 srli 11 11 16
3d8 addi 14 11 1
3dc mul 14 14 10
3e0 load 15 2 88 4
3e2 store 18 13 30 2
3e6 add 15 15 9
3e8 load 13 15 0 2
3ea srai 14 14 2
3ec bge 14 13 1010
3f0 mv 14 13
3f2 load 15 2 92 4
3f4 slli 14 14 16
3f6 srli 14 14 16
3f8 add 13 15 9
3fc store 18 14 36 2
400 load 13 13 0 2
402 load 15 2 96 4
404 lui 12 4096
406 store 18 13 42 2
40a add 9 9 15
40c load 13 9 0 2
40e addi 12 12 -896
412 store 18 13 48 2
416 mv 13 14
418 bgeu 12 14 1054
41c mv 13 12
41e slli 12 13 16
422 srli 12 12 16
424 li 14 10
426 bgeu 12 14 1068
42a li 13 10
42c slli 14 13 16
430 srli 14 14 16
432 slli 14 14 2
434 div 14 14 10
438 store 18 13 36 2
43c addi 14 14 -1
43e bge 11 14 1092
442 mv 14 11
444 store 18 14 30 2
448 bne 25 0 1128
44c beq 24 0 1192
450 load 14 18 80 2
454 store 18 14 82 2
458 load 14 18 26 2
45c store 18 14 28 2
460 load 14 18 32 2
464 store 18 14 34 2
468 load 14 8 224 4
46c load 15 18 136 4
470 ori 14 14 512
474 store 8 14 224 4
478 call_indirect 1 15
47a jump 96
47c load 13 18 7 1
480 li 14 1
482 bne 13 14 206
486 jump 94
488 store 18 0 108 1
48c jump 264
48e load 14 18 80 2
492 store 18 14 84 2
496 load 14 18 26 2
49a store 18 14 30 2
49e load 14 18 32 2
4a2 store 18 14 36 2
4a6 jump 1096
4a8 load 14 18 84 2
4ac store 18 14 82 2
4b0 load 14 18 30 2
4b4 store 18 14 28 2
4b8 load 14 18 36 2
4bc jump 1124
''',
'caller':'''
000 addi 2 2 -48
002 load 6 2 64 4
004 store 2 1 44 4
006 store 2 6 16 4
008 load 6 2 60 4
00a store 2 6 12 4
00c load 6 2 56 4
00e store 2 6 8 4
010 load 6 2 52 4
012 store 2 6 4 4
014 load 6 2 48 4
016 store 2 6 0 4
018 jal 1 432674
01c lui 11 8192
01e addi 11 11 67
022 jal 1 435984
026 load 1 2 44 4
028 li 10 0
02a addi 2 2 48
02c jr 1
''',
'counter':'''
000 lui 15 536883200
004 load 15 15 1108 4
008 li 10 0
00a bnez 15 14
00c jr 1
00e load 14 15 11 1
010 bnez 14 20
012 addi 10 10 1
014 load 15 15 0 4
016 jump 10
''',
'threshold':'''
000 lui 13 450560
004 li 15 0
006 addi 13 13 1268
00a addi 16 0 255
00e add 14 13 15
012 load 12 14 0 1
014 slli 14 12 16
018 srli 14 14 16
01a bltu 10 14 34
01e bne 12 16 36
022 jr 1
024 load 12 11 0 2
026 bltu 14 12 46
02a store 11 14 0 2
02c jr 1
02e addi 15 15 1
030 andi 15 15 255
034 jump 14
''',
'RAMservice':'''
000 lui 16 536883200
004 load 14 16 1288 4
008 load 15 14 56 4
00a srli 15 15 5
00c andi 15 15 1
00e bnez 15 124
010 beqz 12 24
012 load 15 14 48 4
014 srli 15 15 15
016 store 12 15 0 1
018 beqz 13 70
01a load 15 16 1288 4
01e load 14 15 48 4
020 slli 14 14 17
022 srli 15 14 22
026 bge 14 0 50
02a ori 15 15 -1024
02e slli 15 15 16
030 srli 15 15 16
032 load_signed 14 13 0 2
036 slli 15 15 16
038 srai 15 15 16
03a beqz 14 68
03c add 15 15 14
03e li 14 2
040 div 15 15 14
044 store 13 15 0 2
046 beqz 11 102
048 load 15 10 1 1
04a beqz 15 102
04c add 10 10 15
04e load 15 10 9 1
050 li 14 1
052 li 10 6
054 andi 13 15 111
058 bne 13 14 126
05c slli 15 15 24
05e srai 15 15 24
060 li 10 14
062 blt 15 0 126
066 load 15 16 1288 4
06a lui 14 536883200
06e li 10 0
070 load 15 15 56 4
072 srli 15 15 27
074 andi 15 15 3
076 store 14 15 1311 1
07a jr 1
07c li 10 1
07e jr 1
'''
},
{
'consumer':'''
000 addi 2 2 -80
002 store 2 25 36 4
004 store 2 26 32 4
006 store 2 27 28 4
008 store 2 12 9 1
00a mv 27 10
00c mv 26 11
00e mv 25 12
010 mv 11 13
012 li 12 6
014 addi 10 2 10
018 store 2 8 72 4
01a store 2 9 68 4
01c store 2 19 60 4
01e store 2 20 56 4
020 store 2 21 52 4
022 store 2 22 48 4
024 store 2 23 44 4
026 store 2 24 40 4
028 mv 23 15
02a lui 8 536883200
02e store 2 1 76 4
030 store 2 18 64 4
032 mv 24 13
034 mv 9 14
036 mv 22 16
038 mv 21 17
03a load 20 2 80 4
03c load 19 2 84 4
03e auipc 1 536436736
042 jalr 1 1 1978
046 addi 15 8 1032
04a load 15 15 128 4
04e addi 8 8 1032
052 beqz 15 126
054 load 15 15 28 4
056 slli 14 15 17
05a bge 14 0 126
05e li 10 12
060 load 1 2 76 4
062 load 8 2 72 4
064 load 9 2 68 4
066 load 18 2 64 4
068 load 19 2 60 4
06a load 20 2 56 4
06c load 21 2 52 4
06e load 22 2 48 4
070 load 23 2 44 4
072 load 24 2 40 4
074 load 25 2 36 4
076 load 26 2 32 4
078 load 27 2 28 4
07a addi 2 2 80
07c jr 1
07e load 15 8 152 4
082 beqz 15 94
084 jal 1 352964
088 lui 15 536883200
08c load 15 15 593 1
090 srli 15 15 2
092 beq 10 15 94
096 andi 15 9 -8
09a li 10 17
09c bnez 15 96
09e andi 15 9 5
0a2 bnez 15 168
0a4 li 10 18
0a6 jump 96
0a8 load 15 8 128 4
0ac beqz 15 188
0ae load 14 15 28 4
0b0 slli 13 14 17
0b4 blt 13 0 94
0b8 load 15 15 11 1
0ba bnez 15 94
0bc load 18 8 148 4
0c0 bne 18 0 1148
0c4 load 15 8 152 4
0c8 call_indirect 1 15
0ca mv 18 10
0cc beqz 10 94
0ce li 14 3
0d0 bltu 14 26 164
0d4 store 18 27 13 1
0d8 store 18 26 101 1
0dc li 12 6
0de li 11 0
0e0 mv 10 24
0e2 auipc 1 536440832
0e6 jalr 1 1 -1888
0ea bne 10 0 1160
0ee li 14 1
0f0 store 18 14 108 1
0f4 store 18 25 109 1
0f8 li 12 6
0fa mv 11 24
0fc addi 10 18 110
100 auipc 1 536436736
104 jalr 1 1 1784
108 store 18 0 56 1
10c andi 24 9 1
110 li 26 0
112 beq 24 0 554
116 load 13 23 0 2
11a li 14 4
11c bgeu 13 14 290
120 li 13 4
122 store 18 13 52 2
126 load 14 22 0 2
12a slli 12 13 16
12e srli 12 12 16
130 bgeu 12 14 310
134 mv 14 13
136 slli 13 14 16
13a srli 13 13 16
13c li 12 4
13e bgeu 13 12 324
142 li 14 4
144 slli 13 14 16
148 store 18 14 54 2
14c srli 13 13 16
14e addi 14 0 85
152 mul 14 13 14
156 addi 11 18 80
15a srai 14 14 8
15c store 18 14 50 2
160 li 14 1
162 store 18 14 56 1
166 load 14 21 0 2
16a store 18 14 14 2
16e load 10 20 0 2
172 add 14 14 10
174 srai 14 14 1
176 store 18 14 80 2
17a store 18 10 20 2
17e jal 1 341412
182 load 13 18 80 2
186 lui 14 4096
188 addi 14 14 -896
18c bgeu 14 13 402
190 mv 13 14
192 slli 14 13 16
196 srli 14 14 16
198 li 12 6
19a bgeu 14 12 416
19e li 13 6
1a0 store 18 13 80 2
1a4 slli 10 13 16
1a8 load 13 19 0 2
1ac addi 14 0 499
1b0 srli 10 10 16
1b2 bgeu 14 13 442
1b6 addi 13 0 499
1ba slli 11 13 16
1be srli 11 11 16
1c0 addi 14 11 1
1c4 mul 14 14 10
1c8 load 15 2 88 4
1ca store 18 13 26 2
1ce load 13 15 0 2
1d0 srai 14 14 2
1d2 bge 14 13 472
1d6 mv 14 13
1d8 load 15 2 92 4
1da slli 14 14 16
1dc srli 14 14 16
1de store 18 14 32 2
1e2 load 13 15 0 2
1e4 load 15 2 96 4
1e6 lui 12 4096
1e8 store 18 13 38 2
1ec load 13 15 0 2
1ee addi 12 12 -896
1f2 store 18 13 44 2
1f6 mv 13 14
1f8 bgeu 12 14 510
1fc mv 13 12
1fe slli 12 13 16
202 srli 12 12 16
204 li 14 10
206 bgeu 12 14 524
20a li 13 10
20c slli 14 13 16
210 srli 14 14 16
212 slli 14 14 2
214 div 14 14 10
218 store 18 13 32 2
21c addi 14 14 -1
21e bge 11 14 548
222 mv 14 11
224 store 18 14 26 2
228 li 26 1
22a andi 25 9 2
22e beq 25 0 788
232 slli 27 26 1
236 add 14 21 27
23a load 14 14 0 2
23c add 13 20 27
240 addi 11 18 82
244 store 18 14 16 2
248 load 10 13 0 2
24a add 14 14 10
24c srai 14 14 1
24e store 18 14 82 2
252 store 18 10 22 2
256 jal 1 341412
25a load 13 18 82 2
25e lui 14 4096
260 addi 14 14 -896
264 bgeu 14 13 618
268 mv 13 14
26a slli 14 13 16
26e srli 14 14 16
270 li 12 6
272 bgeu 14 12 632
276 li 13 6
278 store 18 13 82 2
27c add 14 19 27
280 load 14 14 0 2
282 slli 10 13 16
286 addi 13 0 499
28a srli 10 10 16
28c bgeu 13 14 660
290 addi 14 0 499
294 slli 11 14 16
298 srli 11 11 16
29a store 18 14 28 2
29e addi 14 11 1
2a2 mul 14 14 10
2a6 load 15 2 88 4
2a8 add 13 15 27
2ac load 13 13 0 2
2ae srai 14 14 2
2b0 bge 14 13 694
2b4 mv 14 13
2b6 load 15 2 92 4
2b8 slli 14 14 16
2ba srli 14 14 16
2bc add 13 15 27
2c0 store 18 14 34 2
2c4 load 13 13 0 2
2c6 load 15 2 96 4
2c8 lui 12 4096
2ca store 18 13 40 2
2ce add 27 27 15
2d0 load 13 27 0 2
2d4 addi 12 12 -896
2d8 store 18 13 46 2
2dc mv 13 14
2de bgeu 12 14 740
2e2 mv 13 12
2e4 slli 14 13 16
2e8 srli 14 14 16
2ea li 12 10
2ec bgeu 14 12 754
2f0 li 13 10
2f2 slli 14 13 16
2f6 srli 14 14 16
2f8 slli 14 14 2
2fa div 14 14 10
2fe store 18 13 34 2
302 addi 14 14 -1
304 bge 11 14 778
308 mv 14 11
30a addi 26 26 1
30c store 18 14 28 2
310 andi 26 26 255
314 andi 9 9 4
316 beq 9 0 1166
31a slli 9 26 1
31e add 23 23 9
320 load 13 23 0 2
324 li 14 4
326 bgeu 13 14 812
32a li 13 4
32c store 18 13 70 2
330 add 22 22 9
332 load 14 22 0 2
336 slli 12 13 16
33a srli 12 12 16
33c bgeu 12 14 834
340 mv 14 13
342 slli 13 14 16
346 srli 13 13 16
348 li 12 4
34a bgeu 13 12 848
34e li 14 4
350 slli 13 14 16
354 store 18 14 72 2
358 srli 13 13 16
35a addi 14 0 85
35e mul 14 13 14
362 add 21 21 9
364 add 20 20 9
366 addi 11 18 84
36a srai 14 14 8
36c store 18 14 74 2
370 load 14 18 56 1
374 ori 14 14 2
378 store 18 14 56 1
37c load 14 21 0 2
380 store 18 14 18 2
384 load 10 20 0 2
388 add 14 14 10
38a srai 14 14 1
38c store 18 14 84 2
390 store 18 10 24 2
394 jal 1 341412
398 load 13 18 84 2
39c lui 14 4096
39e addi 14 14 -896
3a2 bgeu 14 13 936
3a6 mv 13 14
3a8 slli 14 13 16
3ac srli 14 14 16
3ae li 12 6
3b0 bgeu 14 12 950
3b4 li 13 6
3b6 store 18 13 84 2
3ba add 19 19 9
3bc slli 10 13 16
3c0 load 13 19 0 2
3c4 addi 14 0 499
3c8 srli 10 10 16
3ca bgeu 14 13 978
3ce addi 13 0 499
3d2 slli 11 13 16
3d6 srli 11 11 16
3d8 addi 14 11 1
3dc mul 14 14 10
3e0 load 15 2 88 4
3e2 store 18 13 30 2
3e6 add 15 15 9
3e8 load 13 15 0 2
3ea srai 14 14 2
3ec bge 14 13 1010
3f0 mv 14 13
3f2 load 15 2 92 4
3f4 slli 14 14 16
3f6 srli 14 14 16
3f8 add 13 15 9
3fc store 18 14 36 2
400 load 13 13 0 2
402 load 15 2 96 4
404 lui 12 4096
406 store 18 13 42 2
40a add 9 9 15
40c load 13 9 0 2
40e addi 12 12 -896
412 store 18 13 48 2
416 mv 13 14
418 bgeu 12 14 1054
41c mv 13 12
41e slli 12 13 16
422 srli 12 12 16
424 li 14 10
426 bgeu 12 14 1068
42a li 13 10
42c slli 14 13 16
430 srli 14 14 16
432 slli 14 14 2
434 div 14 14 10
438 store 18 13 36 2
43c addi 14 14 -1
43e bge 11 14 1092
442 mv 14 11
444 store 18 14 30 2
448 bne 25 0 1128
44c beq 24 0 1192
450 load 14 18 80 2
454 store 18 14 82 2
458 load 14 18 26 2
45c store 18 14 28 2
460 load 14 18 32 2
464 store 18 14 34 2
468 load 14 8 224 4
46c load 15 18 136 4
470 ori 14 14 512
474 store 8 14 224 4
478 call_indirect 1 15
47a jump 96
47c load 13 18 7 1
480 li 14 1
482 bne 13 14 206
486 jump 94
488 store 18 0 108 1
48c jump 264
48e load 14 18 80 2
492 store 18 14 84 2
496 load 14 18 26 2
49a store 18 14 30 2
49e load 14 18 32 2
4a2 store 18 14 36 2
4a6 jump 1096
4a8 load 14 18 84 2
4ac store 18 14 82 2
4b0 load 14 18 30 2
4b4 store 18 14 28 2
4b8 load 14 18 36 2
4bc jump 1124
''',
'caller':'''
000 addi 2 2 -48
002 load 6 2 64 4
004 store 2 1 44 4
006 store 2 6 16 4
008 load 6 2 60 4
00a store 2 6 12 4
00c load 6 2 56 4
00e store 2 6 8 4
010 load 6 2 52 4
012 store 2 6 4 4
014 load 6 2 48 4
016 store 2 6 0 4
018 jal 1 432954
01c lui 11 8192
01e addi 11 11 67
022 jal 1 436468
026 load 1 2 44 4
028 li 10 0
02a addi 2 2 48
02c jr 1
''',
'counter':'''
000 lui 15 536883200
004 load 15 15 1188 4
008 li 10 0
00a bnez 15 14
00c jr 1
00e load 14 15 11 1
010 bnez 14 20
012 addi 10 10 1
014 load 15 15 0 4
016 jump 10
''',
'threshold':'''
000 lui 13 450560
004 li 15 0
006 addi 13 13 1764
00a addi 16 0 255
00e add 14 13 15
012 load 12 14 0 1
014 slli 14 12 16
018 srli 14 14 16
01a bltu 10 14 34
01e bne 12 16 36
022 jr 1
024 load 12 11 0 2
026 bltu 14 12 46
02a store 11 14 0 2
02c jr 1
02e addi 15 15 1
030 andi 15 15 255
034 jump 14
''',
'RAMservice':'''
000 lui 16 536883200
004 load 14 16 1368 4
008 load 15 14 56 4
00a srli 15 15 5
00c andi 15 15 1
00e bnez 15 124
010 beqz 12 24
012 load 15 14 48 4
014 srli 15 15 15
016 store 12 15 0 1
018 beqz 13 70
01a load 15 16 1368 4
01e load 14 15 48 4
020 slli 14 14 17
022 srli 15 14 22
026 bge 14 0 50
02a ori 15 15 -1024
02e slli 15 15 16
030 srli 15 15 16
032 load_signed 14 13 0 2
036 slli 15 15 16
038 srai 15 15 16
03a beqz 14 68
03c add 15 15 14
03e li 14 2
040 div 15 15 14
044 store 13 15 0 2
046 beqz 11 102
048 load 15 10 1 1
04a beqz 15 102
04c add 10 10 15
04e load 15 10 9 1
050 li 14 1
052 li 10 6
054 andi 13 15 111
058 bne 13 14 126
05c slli 15 15 24
05e srai 15 15 24
060 li 10 14
062 blt 15 0 126
066 load 15 16 1368 4
06a lui 14 536883200
06e li 10 0
070 load 15 15 56 4
072 srli 15 15 27
074 andi 15 15 3
076 store 14 15 1391 1
07a jr 1
07c li 10 1
07e jr 1
'''
}
)


def specs(part,index):
    pc=STARTS[index][PARTS.index(part)];out={}
    for line in LITERALS[index][part].splitlines():
        if not line:continue
        a,op,*args=line.split();vals=[int(v,0) for v in args];check(len(vals)==len(FIELDS[op]),'large literalfields')
        d=dict(zip(FIELDS[op],vals));d['op']=op
        if op=='load_signed':d['op']='load';d['signed']=True
        if op in BRANCHES|{'jump'}:d['target']+=pc
        out[pc+int(a,16)]=d
    return out


def threshold_table(raw,index):
    check(len(raw)==24,'large tablelength')
    for k,b in enumerate(raw):check(b==TABLE[k],'large tablebyte '+str(k))
    check(sha256(raw).hexdigest()==TABLE_HASH,'large threshold tablehash')
    check(raw.index(255)==22 and all(b!=255 for b in raw[:22]),'large firstsentinel22')
    check(all(((k+1)&255)==k+1 for k in range(22)),'large indexnoWrap before sentinel')
    return {'start':TABLES[index],'bytes':24,'sha256':TABLE_HASH,'values':list(raw),'first_ff_index':22,'max_threshold_reads':23,
      'proof':'index0,oneincrementandmask255perbackedge; no wrap before22;thresholdFF exitsbeforeinputwordread. Stabletable/validaccess/ordinaryregistersemantics required',
      'possible_input_word_reads_max':22,'possible_SH_count_max':1,'physical_input_or_table_validity_proved':False}


def body(raw,part,index):
    k=PARTS.index(part);pc=STARTS[index][k];n=decode(raw,pc);s=specs(part,index);check(set(n)==set(s),'large '+part+' boundaries')
    for p,f in s.items():init.g(n,p,'large '+part+' operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[k],COUNTS[k],HASHES[index][k]),'large '+part+' identity')
    edges={};calls=[];rets=[]
    for p,v in n.items():
        op=v['op'];q=[p+v['size']]
        if op=='jr':check(v['rs1']==1,'large RAreturn');q=[];rets.append(p)
        elif op in BRANCHES:q.append(v['target'])
        elif op=='jump':q=[v['target']]
        elif op in ('jal','jalr','call_indirect'):
            check(v['rd']==1,'large RAcalllink')
            if op=='jal':t=hex(v['target'])
            elif op=='call_indirect':t='freshU32[B152]' if p==pc+0xc8 else 'freshU32[N136]'
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==v['rs1'],'large PCpair');t=hex((p-4+a['imm']+v['imm'])&0xfffffffe)
            calls.append({'pc':p,'target':t})
        check(all(x in n for x in q),'large closed '+part+' CFG');edges[p]=q
    cycles=[g for g in common.sccs(edges) if len(g)>1 or g[0] in edges[g[0]]]
    check((not cycles)==(part not in ('counter','threshold')),'large cycleclassification '+part)
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(edges[p])
    check(seen==set(n),'large allnodesreachable '+part)
    stores=[{'pc':p,'base':v['rs1'],'offset':v['imm'],'source':v['rs2'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    check((len(stores),len(calls))==((67,9),(6,2),(0,0),(1,0),(3,0))[k],'large stores/callscensus '+part)
    if part in ('counter','threshold','RAMservice'):check(not any(v.get('rd') in (2,8,9,*range(18,28)) for v in n.values()),'large leaf preservesS/SP')
    if part=='RAMservice':
        check(n[pc+0x32].get('signed') is True and n[pc+0x32]['width']==2,'large RAM signedLH contract')
        check({v['rd'] for v in n.values() if 'rd' in v}=={10,13,14,15,16},'large RAM exactGPRdefinitions')
    return {'start':pc,'end_exclusive':pc+SIZES[k],'source':SOURCES[index][k],'bytes':SIZES[k],'sha256':sha256(raw).hexdigest(),'instructions':list(n.values()),
      'local_CFG':edges,'cyclic_SCCs':cycles,'calls':calls,'stores':stores,'returns':rets,'complete_local_body':True,'local_CFG_acyclic':not cycles,'actual_finite_callchain_proved':False}


def certificates(b,part):
    pc=b['start'];e=b['local_CFG'];ends=set(b['returns'])
    def path(a,z):
        q=deque([(a,[a])]);seen=set()
        while q:
            p,s=q.popleft()
            if p==z:return s
            if p in seen:continue
            seen.add(p);q.extend((v,s+[v]) for v in e[p])
        return None
    def suffix(p):
        choices=[s for z in sorted(ends) if (s:=path(p,z)) is not None];check(bool(choices),'large selectedexitpath');return min(choices,key=len)
    witnesses=[]
    for p,qs in e.items():
        for q in qs:
            s=path(pc,p)+[q]+suffix(q)[1:];check(all(z in e[a] for a,z in zip(s,s[1:])),'large validedgewalk');witnesses.append([v-pc for v in s])
    offsets={'consumer':[0x42,0x84,0xc8,0xd0,0xe6,0x104,0x17e,0x214,0x256,0x2fa,0x394,0x434,0x478,0x47c],
      'caller':[0x18,0x22],'counter':[0xe,0x12],'threshold':[0x12,0x24,0x2a,0x2e],'RAMservice':[0x16,0x32,0x40,0x48,0x4e,0x76,0x7c]}[part]
    selected={hex(o):[v-pc for v in path(pc,pc+o)+suffix(pc+o)[1:]] for o in offsets}
    callback_walks={}
    if part=='RAMservice':
        for name,choices in (('initial_bit5_set',{0xe:0x7c}),('initial_bit5_clear_A2_nonnull_A3_A1_zero',{0xe:0x10,0x10:0x12,0x18:0x46,0x46:0x66})):
            p=pc;seq=[]
            while True:
                check(p not in seq,'large RAM selectedpath acyclic');seq.append(p);qs=e[p]
                if not qs:break
                p=pc+choices[p-pc] if p-pc in choices else qs[0];check(p in qs,'large RAM selectededge')
            os=[p-pc for p in seq];check(not({0x32,0x48,0x4e}&set(os)),'large selectedcallback bypassesLH/packetreads')
            callback_walks[name]=os
    return {'selected_syntactic_walks':selected,'all_edge_witness_count':len(witnesses),'all_edge_witness_sha256':sha256(json.dumps(witnesses,separators=(',',':')).encode()).hexdigest(),
      'RAM_current_callback_walks':callback_walks,
      'scope':'encodedCFGwalks only, notinputfeasibility/calleecompletion/physicalprogress proof'}


def division_contract(b):
    pc=b['start'];n={v['pc']:v for v in b['instructions']};e=b['local_CFG'];facts=[]
    pred={p:set() for p in e}
    for p,qs in e.items():
        for q in qs:pred[q].add(p)
    dom={p:({pc} if p==pc else set(e)) for p in e};changed=True
    while changed:
        changed=False
        for p in e:
            if p==pc:continue
            value={p}|set.intersection(*(dom[q] for q in pred[p]))
            if value!=dom[p]:dom[p]=value;changed=True
    for cap,low,entry,last,div in ((0x182,0x198,0x1a4,0x1b0,0x214),(0x25a,0x270,0x282,0x28a,0x2fa),(0x398,0x3ae,0x3bc,0x3c8,0x434)):
        check({pc+cap,pc+low,pc+entry,pc+last}<dom[pc+div],'large divisorclamps/defs dominateDIV')
        check(n[pc+cap]['op']=='load' and n[pc+cap]['width']==2 and n[pc+low]['imm']==6,'large divisorclamp anchors')
        check(n[pc+entry]['op']=='slli' and n[pc+entry]['rd']==10 and n[pc+last]['op']=='srli' and n[pc+last]['rd']==10,'large divisorzeroextension anchors')
        check(n[pc+div]['op']=='div' and n[pc+div]['rs2']==10,'large signedDIV usesclampedA0')
        check([p-pc for p,v in n.items() if entry<=p-pc<=div and v.get('rd')==10]==[entry,last],'large nootherA0definitions beforeDIV')
        check(not any(entry<=v['pc']-pc<=div for v in b['calls']),'large no calleeclobber betweendivisordef andDIV')
        facts.append({'DIV_offset':div,'A0_definition_offsets':[entry,last],'positive_divisor_range':[6,3200],'numerator_range':[40,12800]})
    return {'sites':facts,'DIV_zero_excluded_locally_underordinary_semantics':True,'signed_quotient_range':[0,2133],'after_minus1_and_min_with_K_range':[-1,499],
      'halfword_negative_case':'-1 storesas65535; positive divisor doesnot imply positive correctedhalfword','actual_inputvector_reachability_or_physical_units_proved':False}


def domains():
    accepted=[x for x in range(8) if x&5];check(accepted==[1,3,4,5,6,7],'large flagslowdomain')
    for h in range(65536):check(6<=min(3200,max(6,h))<=3200,'large positivedivisor clampdomain')
    check(12800//6==2133 and 40//3200==0,'large quotientextremes')
    witness=(3200*82)//4;check(witness==65600 and witness&65535==64 and (4*64)//3200-1==-1,'large truncation/minusone integerwitness')
    statuses={0:[],6:[],14:[]}
    for x in range(256):statuses[6 if x&111!=1 else 14 if x&128 else 0].append(x)
    check(statuses[0]==[1,17] and statuses[14]==[129,145] and len(statuses[6])==252,'large RAM genericpacket bytedomain')
    for v in range(-512,512):
        for old in (-32768,-3,-1,0,1,3,32767):
            total=v+old;q=(-(abs(total)//2) if total<0 else total//2) if old else v
            check(-16640<=q<=16639,'large signedLH smoothing domain')
    return {'accepted_flags':accepted,'flags0or2_status':18,'flags_highbits_nonzero_status':17,'flag_gate_preceded_by_copy':True,
      'positive_divisor_U16_cases':65536,'quotient_range':[0,2133],'postcorrection_range':[-1,499],'pure_integer_witness':{'D':3200,'K':81,'pretruncate':65600,'low16':64,'corrected':-1,'SH_low16':65535},
      'witness_actual_ingress_reachability_proved':False,'RAM_packet_status0_bytes':statuses[0],'RAM_packet_status14_bytes':statuses[14],'RAM_packet_status6_count':252,
      'RAM_signed10_domain':[-512,511],'RAM_signed16_old_domain':[-32768,32767],'RAM_sum_range':[-33280,33278],'RAM_halfword_reply_range':[-16640,16639],'RAM_selected_signed_cases':7168,
      'RAM_generic_status_domain':[0,1,6,14],'callback_A1_A3_zero_status_domain':[0,1]}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        bodies={part:body(init.binding.take(data,SOURCES[i][k],SIZES[k]),part,i) for k,part in enumerate(PARTS)};certs={part:certificates(b,part) for part,b in bodies.items()};tab=threshold_table(init.binding.take(data,TABLES[i],24),i)
        pc=STARTS[i][0];b=bodies['consumer'];n={v['pc']:v for v in b['instructions']};B=0x200033b8+80*i;F=0x200031ec+80*i
        expected=['0x20000332',hex(STARTS[i][2]),'freshU32[B152]','0x200004bc','0x20000332',hex(STARTS[i][3]),hex(STARTS[i][3]),hex(STARTS[i][3]),'freshU32[N136]']
        check([v['target'] for v in b['calls']]==expected,'large fullconsumer exactcallee targets')
        check(bodies['caller']['calls'][0]['target']==hex(pc) and bodies['caller']['calls'][1]['target']==hex(0x6a710+484*i),'large caller/fullbody exactjoin')
        mapping=init.binding.profile(data,pr['label']);m=mapping['first_copy'];ram=STARTS[i][4];source=int(m['source'],16)+ram-int(m['destination'],16)
        check(source==SOURCES[i][4] and int(m['destination'],16)<=ram and ram+128<=int(mapping['first_copy_end_exclusive'],16),'large RAMservice fullsource mapping')
        servicecalls=[v for v in pr['body']['calls'] if v['target']==hex(ram)];check(len(servicecalls)==3,'large priorcallback threeRAMcalls joinfullbody')
        ctor=outer.body(init.binding.take(data,outer.STARTS[i][1],154),'outer148',i);ctn={v['pc']:v for v in ctor['instructions']};ctp=int(ctor['start'],16)
        check(ctn[ctp+44]['imm']+0x20003000==B+148 and ctn[ctp+92]['imm']==136,'large constructorobject/callback offsets join')
        profiles.append({'label':pr['label'],'B':B,'F':F,'bodies':bodies,'CFG_certificates':certs,'threshold_table':tab,'division_certificates':division_contract(b),
          'reused_constructor':{k:ctor[k] for k in ('start','bytes','sha256')},
          'entry_contract':{'frame_bytes':80,'saved':'RA andall12 Sregisters','first_request':'unconditionalRAM20000332(SP10,entryA3,6) beforestatus/flag rejection',
            'first_global_gate':'freshB128nonnull ->word28 bit14set returns12','constructor_initial_guard':'freshB152==0 returns12',
            'counter_gate':'counterreply == independentlyfreshU8[F21]>>2 returns12; equalityonly, not>= limit',
            'flags':'fullentryA4 accepts exactly1,3,4,5,6,7; highbitsreturns17;0/2returns18',
            'second_outer_gate':'freshB128again; word28bit14set orbyte11nonzero returns12; no mergingseparatereads',
            'constructor':'freshB148nonzero skipsconstructor andtestsN7==1 ->12; elsefreshreloadB152 andcallwithoutfreshnullguard; A0locally17',
            'constructor_null':'returns12','tag':'unsignedentryA1>3 returns18 AFTER possibleallocation/publication; not an early no-effectguard',
            'minimum_fixed_extents':{'N':140,'B':228,'old_outer':32},'actualbindings/nonalias/lifetimes_proved':False},
          'initial_copy_sequence':{'firststores':['N13=low8entryA0','N101=entryA1 low8 after<=3gate'],
            'predicate_request':['RAM200004bc','entryA3',0,6],'nonzero':'N108=0; skipsecondcopy','zero':'N108=1,N109=low8entryA2;RAM20000332(N110,entryA3,6)',
            'predicate_limit':'zero reply doesnotprove source nonnull/full6readable; reference/bodybinding/effects stillnotclosedhere',
            'both':'N56=0 beforeselectednumericblocks','copy/borrowedsource/preservation_proved':False},
          'numeric_contract':{'input_vectors':'pointer-valuedentryA5/A6/A7 andfiveincomingstackwords; U16loads includeindexedoffsets0,2,4 underacceptedflags/liveSregpreservation',
            'selected_lanes':'flagsbits0/1/2 selectencodedblocks; earlierselectedlanes affecthalfwordindex','physicaltiming_or_complete_data_domain_proved':False,
            'threshold_calls':'threecalls mayupdate N80/N82/N84 throughA1; tablebound23reads separatefromcounterchainreturn',
            'clamps_and_DIV':'localdivisor6..3200,numerator40..12800; truncationbeforelaterclampscanproducepost-DIV -1 storedffff. Integercertificate isnot ingressreachability'},
          'final_callback':{'source':'freshU32[N136]','local_null_guard':False,'before':'freshB224 OR512 store; A0 inherited, notlocallysettoN','after':'jumpstraighttoframe-restoring RET; preserve actualcalleeA0, no fixedsuccess0',
            'conditional_constructor_value':hex(0x57b7c+320*i),'actualcallbackidentity/lifetime_proved':False},
          'caller_contract':{'frame_bytes':48,'saved':['RA'],'first_request':'forwardentryA0..A7;copyfiveincomingstackwords intooutgoingwords0..16; callconsumer',
            'second_request':{'target':hex(0x6a710+484*i),'A0':'consumerreply','A1':0x2043},'local_return':'explicit0 aftersecondcallee returns; doesnotprovesuccess','async_completion/pointerretention_proved':False},
          'counter_contract':{'head_slot':B+156,'count':'initialA0=0;incrementwordby1 whenfreshU8[node11]==0; nextU32[node0]','minimum_node_extent':12,
            'calls_stores_frame':False,'S/SP/RA_preserved_locally':True,'bound/acyclicity/lifetime/overflowexclusion_proved':False},
          'threshold_contract':{'args':'entryA0 unsignedbound, entryA1 halfwordpointer','A0_unchanged':True,'no_calls/frame/Sregwrites':True,
            'periteration':'readthresholdbyte;threshold>A0 orFF ->RET;elsefreshU16[A1];threshold>=word ->SHthreshold andRET;elsestepindex',
            'bound':'<=23thresholdloads/<=22freshwordloads/<=1SH withoriginalretainedtablebytes, validaccess andordinaryindexsemantics; no fullcallchaintermination claim'},
          'RAM_source_mapping':{'first_copy':m,'first_copy_end_exclusive':mapping['first_copy_end_exclusive'],'RAM_entry':ram,'source':source,'fullbytes':128,'actualstartup_or_installedRAM_proved':False},
          'RAMservice_contract':{'frame/calls/loops':False,'GPR_writes':[10,13,14,15,16],'preserved_locally':'A1,A2,A7,SP,RA,allSregisters; pointedcontents stillmayaliaswrites',
            'Rslot':0x20003508+80*i,'C11_address':0x2000351f+80*i,'initial':'captureR0,readR0word56bit5; ifsetreturn1 beforedatastores',
            'A2_nonnull':'byte[A2]=low8(U32[R0+48]>>15), bits15..22; no sourcepointerglobalreload forR0',
            'A3_nonnull':'freshR1/W48;signextend10bits5..14;SIGNED LH old[A3]; old0 ->storevalue; else signedDIV(value+old,2) trunc0 ->SH. SignedTrue explicitlyguarded',
            'A1_nonzero':'packetP=entryA0; k=U8[P1];k0skipscheck;elsex=U8[P+k+9];(x&6f)!=1 returns6, elsexnegative returns14;elsecontinue',
            'final':'freshR2/W56;C11=bits27..28;return0. R0/R1/R2 andseparatewordreads notmerged',
            'return_sideeffects':'status1 nodatastores;6/14 canfollowoptionalA2/A3stores;0 includesC11store; numericcodesnotprotocolmeaning',
            'minimum_extents':{'R':60,'optionalA2':1,'optionalA3':2,'C':12,'genericpacketmaximumrawk_extent':265},
            'current_callback':'A1=0,A3=0,A2=capturedN20pointer ->no packetA0dereference/noLHpath; returns0or1 undernormalvalidaccess; N20writeonlybit5clear/validnonnullA2',
            'provider/MMIO/actualretention_proved':False},
          'target_execution_or_emulation':False})
    return {'schema':'TSL9-large-consumer-service-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'scope':'2*(1214B400i consumer+46B20i caller+24B10i counter+54B18i helper+128B50i RAMservice)+2*24Btable;2980newbytes/996instructionguards/48tablebyteguards',
      'boundary':'static fullbody/graph/request/bounded-helper contracts; actualprovider/object/framepreservation, counterchainreturn andcallercompletion unproved',
      'remaining':['callbackN13657b7c/57cbc body/effects','RAM200004bc predicate source/bodybinding','lookup/counterhead/nodewriters andcallback/notificationroots/B120bindings','physicalsideeffects/inputreachability/retention/asynccompletion'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=bytesguard=walks=edges=signedness=0
    for i,data in enumerate(carriers):
        for k,part in enumerate(PARTS):
            pc=STARTS[i][k];raw=init.binding.take(data,SOURCES[i][k],SIZES[k]);b=body(raw,part,i);c=certificates(b,part);walks+=len(c['selected_syntactic_walks']);edges+=c['all_edge_witness_count']
            for p,v in decode(raw,pc).items():
                at=p-pc;z=v['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
                try:body(buf,part,i)
                except RuntimeError as ex:check(str(ex).startswith('large '+part+' operand '),'large specifiedmutation '+str(ex))
                else:raise RuntimeError('large mutationescaped')
                mutations+=1
            if part=='RAMservice':
                buf=bytearray(raw);buf[0x32:0x36]=(int.from_bytes(buf[0x32:0x36],'little')^(1<<14)).to_bytes(4,'little')
                try:body(buf,part,i)
                except RuntimeError as ex:check(str(ex)=='large RAMservice operand 0x32','large LHsignednessguard')
                else:raise RuntimeError('large LHtoLHU escaped')
                signedness+=1
        tab=init.binding.take(data,TABLES[i],24);threshold_table(tab,i)
        for k in range(24):
            buf=bytearray(tab);buf[k]^=1
            try:threshold_table(buf,i)
            except RuntimeError as ex:check(str(ex)=='large tablebyte '+str(k),'large specifiedtablebyteguard')
            else:raise RuntimeError('large tablemutationescaped')
            bytesguard+=1
    check((mutations,bytesguard,signedness)==(996,48,2),'large mutationcensus');domains()
    print('PASS:996 instruction +48 tablebyte +2 LHsignedness mutations rejected;2980 new originalbytes;'+str(walks)+' selectedCFG walks;'+str(edges)+' edge witnesses;23-read helper bound/flags/division/signed-byte domains')


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');o=p.parse_args();image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
    check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
    carriers=[]
    for label,folder,tail,z,digest in init.binding.PROFILES:
        data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes();check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
    raw_hex=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,raw_hex,sparse.parser());ledger=derive(image,carriers,header,coverage)
    ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);output=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    if o.write:
        with OUT.open('xb') as f:f.write(output)
    else:check(OUT.read_bytes()==output,'large exactledger replay')
    print('PASS:fullconsumer/caller/counter/helper-sentinel/constructor joins;callback->mapped RAMservice including signedLH;exact ledger')
    print('PASS:NO target execution/emulation;actualbindings/objects/counterreturn/calleecompletion/retention UNPROVED')


if __name__=='__main__':main()
