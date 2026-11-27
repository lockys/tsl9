"""Offline full callback bodies, computed-switch tables and conditional CFG.

No target ISA, register/RAM machine, callback/copy/provider/polling, MMIO,
CSR or device is executed or emulated. Literal/graph/integer checks only.
"""
import argparse
import json
from collections import deque
from hashlib import sha256
from pathlib import Path
import check_v4160_constructor_consumer_tail_static as previous

init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
common=previous.previous
outer=previous.outer
OUT=Path(__file__).with_name('v4160-callback-dispatch-static.json')
STARTS=(0x55480,0x5555e)
SIZES=(1064,1154)
COUNTS=(356,387)
HASHES=('b93ed58469d0daa81a37bf7c4dae6da58332aa99c416b3646edf3b42933aa3e9','e34792dfa1d0d595eb589d2413519dbf5d148474c717e2a73ccc6915a1681eb4')
TABLES=(0x6e50c,0x6e6fc)
TABLE_HASHES=('4db72a1fbd28fb640c3b33f09ecffea1494b00cc9f47910e2028a6e9cdc1ceb5','c9ed822df352b45d12df25148cd044feaeabc84f32b728b4646a35ae212f5fec')
TABLE_WORDS=((0x55552,0x5557e,0x55688,0x554d8,0x55720,0x55800,0x5579c,0x5583c,0x5587c,0x554ea,0x5563a,0x555e4,0x557e8),
 (0x55630,0x5565c,0x5576e,0x555b6,0x55800,0x558e0,0x5587c,0x5591c,0x559b4,0x555c8,0x55720,0x556ca,0x558c8))
FIELDS={**common.FIELDS,'bltu':('rs1','rs2','target'),'bgeu':('rs1','rs2','target'),'call_indirect':('rd','rs1')}
BRANCHES={'beq','bne','bltu','bgeu','beqz','bnez'}

LITERALS=(
'''
000 addi 2 2 -48
002 store 2 9 36 4
004 lui 9 536883200
008 addi 15 9 952
00c store 2 8 40 4
00e load 8 15 100 4
010 store 2 18 32 4
012 store 2 20 24 4
014 store 2 21 20 4
016 lui 20 450560
01a lui 18 536883200
01e lui 21 536883200
022 store 2 19 28 4
024 store 2 22 16 4
026 store 2 1 44 4
028 addi 9 9 952
02c addi 20 20 1292
030 addi 18 18 1300
034 lui 19 536883200
038 addi 21 21 492
03c addi 22 8 20
040 load 15 8 11 1
042 li 14 12
044 addi 15 15 110
048 andi 15 15 255
04c bltu 14 15 436
050 slli 15 15 2
052 add 15 15 20
054 load 15 15 0 4
056 jr 15
058 li 14 4
05a load 15 9 124 1
05e bne 14 15 90
062 mv 10 8
064 jal 1 344866
068 jump 64
06a li 12 0
06c addi 11 0 37
070 li 10 0
072 jal 1 408660
076 addi 12 0 37
07a li 11 0
07c li 10 1
07e auipc 1 536530944
082 jalr 1 1 444
086 load 15 18 3 1
08a andi 15 15 1
08c beqz 15 180
08e load 10 8 80 4
090 li 13 0
092 mv 12 22
094 li 11 0
096 store 18 0 3 1
09a auipc 1 536530944
09e jalr 1 1 288
0a2 bnez 10 170
0a4 mv 10 8
0a6 jal 1 349060
0aa load 14 8 11 1
0ac addi 15 0 147
0b0 beq 14 15 64
0b4 jal 1 409176
0b8 mv 10 8
0ba jal 1 343522
0be load 1 2 44 4
0c0 load 8 2 40 4
0c2 load 9 2 36 4
0c4 load 18 2 32 4
0c6 load 19 2 28 4
0c8 load 20 2 24 4
0ca load 21 2 20 4
0cc load 22 2 16 4
0ce addi 2 2 48
0d0 jr 1
0d2 load 15 18 2 1
0d6 andi 15 15 1
0d8 beqz 15 244
0da load 15 8 16 1
0dc store 18 0 2 1
0e0 li 14 1
0e2 bgeu 14 15 236
0e6 li 14 6
0e8 bne 15 14 180
0ec addi 15 0 -101
0f0 store 8 15 11 1
0f2 jump 64
0f4 load 15 19 1340 4
0f8 load 15 15 100 4
0fa bnez 15 64
0fc jump 180
0fe load 15 18 2 1
102 andi 15 15 1
104 beq 15 0 1008
108 store 18 0 2 1
10c jal 1 409176
110 mv 10 8
112 jal 1 343448
116 lui 9 536883200
11a load 15 9 -84 4
11e beqz 15 334
120 load 15 15 4 4
122 beqz 15 334
124 li 15 2
126 store 2 15 4 1
128 load 15 8 69 1
12c addi 10 2 6
130 li 12 6
132 store 2 15 5 1
134 load 15 8 20 1
136 addi 11 8 70
13a store 2 15 12 1
13c auipc 1 536522752
140 jalr 1 1 -650
144 load 15 9 -84 4
148 addi 10 2 4
14a load 15 15 4 4
14c call_indirect 1 15
14e load 15 8 103 1
152 beqz 15 190
154 load 11 8 69 1
158 load 10 8 8 1
15a addi 12 8 70
15e jal 1 436176
162 jump 190
164 load 15 8 107 1
168 load 10 8 99 1
16c li 12 0
16e addi 11 0 37
172 or 10 10 15
174 jal 1 408660
178 li 12 0
17a li 11 0
17c li 10 1
17e auipc 1 536530944
182 jalr 1 1 188
186 load 15 18 3 1
18a andi 15 15 1
18c beqz 15 436
18e load 10 8 80 4
190 li 13 0
192 mv 12 22
194 li 11 0
196 store 18 0 3 1
19a auipc 1 536530944
19e jalr 1 1 32
1a2 bnez 10 426
1a4 mv 10 8
1a6 jal 1 344166
1aa load 14 8 11 1
1ac addi 15 0 154
1b0 beq 14 15 64
1b4 jal 1 409176
1b8 jump 592
1ba load 15 8 107 1
1be load 10 8 99 1
1c2 li 12 0
1c4 addi 11 0 37
1c8 or 10 10 15
1ca jal 1 408660
1ce li 12 0
1d0 li 11 0
1d2 li 10 1
1d4 auipc 1 536530944
1d8 jalr 1 1 102
1dc load 15 18 3 1
1e0 andi 15 15 1
1e2 beqz 15 436
1e4 load 10 8 80 4
1e6 li 13 0
1e8 mv 12 22
1ea li 11 0
1ec store 18 0 3 1
1f0 auipc 1 536530944
1f4 jalr 1 1 -54
1f8 bnez 10 512
1fa mv 10 8
1fc jal 1 343576
200 load 14 8 11 1
202 addi 15 0 153
206 jump 432
208 load 15 18 2 1
20c andi 15 15 1
20e beq 15 0 1008
212 store 18 0 2 1
216 jal 1 409176
21a load 15 9 124 1
21e li 14 2
220 beq 14 15 558
224 load 15 9 124 1
228 li 14 3
22a bne 14 15 600
22e load 13 19 1340 4
232 load 14 8 116 2
236 load 15 13 96 4
238 addi 14 14 300
23c srli 15 15 1
23e bgeu 15 14 600
242 addi 15 0 -107
246 store 8 15 11 1
248 load 15 13 96 4
24a srli 15 15 1
24c bne 15 0 64
250 mv 10 8
252 jal 1 343448
256 jump 190
258 load 14 8 25 1
25a load 15 8 26 1
25c beqz 14 662
25e load 13 8 10 1
260 beq 14 13 1058
264 beq 13 15 624
268 store 8 14 10 1
26a mv 10 8
26c jal 1 347144
270 load 15 18 7 1
274 andi 15 15 255
278 bne 15 0 64
27c load 15 9 124 1
280 li 14 2
282 beq 14 15 656
286 load 15 9 124 1
28a li 14 3
28c bne 14 15 592
290 addi 15 0 -107
294 jump 240
296 beqz 15 624
298 load 14 8 10 1
29a bnez 14 624
29c store 8 15 10 1
29e jump 618
2a0 load 15 18 2 1
2a4 andi 15 15 1
2a6 beq 15 0 1008
2aa store 18 0 2 1
2ae load 15 9 124 1
2b2 andi 15 15 16
2b4 beqz 15 728
2b6 jal 1 409176
2ba load 15 9 124 1
2be andi 15 15 32
2c2 beqz 15 698
2c4 load 15 9 124 1
2c8 mv 10 8
2ca andi 15 15 207
2ce store 9 15 124 1
2d2 jal 1 344468
2d6 jump 64
2d8 load 15 9 125 1
2dc andi 15 15 1
2de beqz 15 746
2e0 jal 1 409176
2e4 addi 15 0 -98
2e8 jump 240
2ea load 15 9 124 1
2ee li 14 5
2f0 andi 15 15 15
2f2 bne 15 14 778
2f6 jal 1 352668
2fa load 15 21 21 1
2fe andi 15 15 3
300 bgeu 10 15 436
304 addi 15 0 -99
308 jump 240
30a load 15 9 124 1
30e li 14 6
310 andi 15 15 15
312 bne 15 14 436
316 addi 15 0 -100
31a jump 240
31c load 15 18 2 1
320 andi 15 15 1
322 beq 15 0 64
326 store 18 0 2 1
32a load 15 9 124 1
32e andi 15 15 16
330 beqz 15 834
332 jal 1 409176
336 load 15 9 124 1
33a andi 15 15 32
33e beqz 15 822
340 jump 708
342 load 15 9 125 1
346 andi 15 15 1
348 bnez 15 736
34a load 15 9 124 1
34e li 14 5
350 andi 15 15 15
352 beq 15 14 772
356 load 15 9 124 1
35a li 14 6
35c andi 15 15 15
35e beq 15 14 790
362 jal 1 409176
366 jump 190
368 li 15 3
36a store 8 15 124 1
36e load 15 9 120 4
370 mv 10 8
372 call_indirect 1 15
374 load 14 8 11 1
376 addi 15 0 151
37a beq 14 15 64
37e jump 190
380 load 15 18 3 1
384 andi 15 15 1
386 beqz 15 944
388 jal 1 409176
38c lui 15 536883200
390 load 14 15 1288 4
394 load 15 14 100 4
396 andi 15 15 -5
398 store 14 15 100 4
39a store 18 0 10 1
39e lui 14 1073881088
3a2 load 15 14 72 1
3a6 andi 15 15 253
3aa store 14 15 72 1
3ae jump 592
3b0 load 15 19 1340 4
3b4 load 15 15 100 4
3b6 bne 15 0 64
3ba jump 904
3bc load 15 18 2 1
3c0 andi 15 15 1
3c2 beqz 15 1008
3c4 store 18 0 2 1
3c8 load 15 9 124 1
3cc andi 15 15 16
3ce beq 15 0 272
3d2 load 15 9 124 1
3d6 andi 15 15 32
3da beqz 15 978
3dc mv 10 8
3de jal 1 344468
3e2 load 15 9 124 1
3e6 andi 15 15 207
3ea store 9 15 124 1
3ee jump 268
3f0 load 15 19 1340 4
3f4 load 15 15 100 4
3f6 bne 15 0 64
3fa jump 436
3fc lui 15 536883200
400 addi 15 15 1300
404 load 14 15 2 1
406 andi 14 14 1
408 beq 14 0 436
40c store 15 0 2 1
410 jal 1 409176
414 mv 10 8
416 jal 1 342694
41a mv 10 8
41c jal 1 348976
420 jump 190
422 beq 15 0 624
426 jump 668
''',
'''
000 addi 2 2 -48
002 store 2 9 36 4
004 lui 9 536883200
008 addi 15 9 1032
00c store 2 8 40 4
00e load 8 15 100 4
010 store 2 18 32 4
012 store 2 20 24 4
014 store 2 21 20 4
016 lui 20 450560
01a lui 18 536883200
01e lui 21 536883200
022 store 2 19 28 4
024 store 2 22 16 4
026 store 2 1 44 4
028 addi 9 9 1032
02c addi 20 20 1788
030 addi 18 18 1380
034 lui 19 536883200
038 addi 21 21 572
03c addi 22 8 20
040 load 15 8 11 1
042 li 14 12
044 addi 15 15 110
048 andi 15 15 255
04c bltu 14 15 444
050 slli 15 15 2
052 add 15 15 20
054 load 15 15 0 4
056 jr 15
058 li 14 4
05a load 15 9 124 1
05e bne 14 15 90
062 mv 10 8
064 jal 1 345068
068 jump 64
06a li 12 0
06c addi 11 0 37
070 li 10 0
072 jal 1 408894
076 addi 12 0 37
07a li 11 0
07c li 10 1
07e auipc 1 536530944
082 jalr 1 1 298
086 load 15 18 3 1
08a andi 15 15 1
08c beqz 15 180
08e load 10 8 80 4
090 li 13 0
092 mv 12 22
094 li 11 0
096 store 18 0 3 1
09a auipc 1 536530944
09e jalr 1 1 142
0a2 bnez 10 170
0a4 mv 10 8
0a6 jal 1 349262
0aa load 14 8 11 1
0ac addi 15 0 147
0b0 beq 14 15 64
0b4 jal 1 409410
0b8 mv 10 8
0ba jal 1 343700
0be load 1 2 44 4
0c0 load 8 2 40 4
0c2 load 9 2 36 4
0c4 load 18 2 32 4
0c6 load 19 2 28 4
0c8 load 20 2 24 4
0ca load 21 2 20 4
0cc load 22 2 16 4
0ce addi 2 2 48
0d0 jr 1
0d2 load 15 18 2 1
0d6 andi 15 15 1
0d8 beqz 15 244
0da load 15 8 16 1
0dc store 18 0 2 1
0e0 li 14 1
0e2 bgeu 14 15 236
0e6 li 14 6
0e8 bne 15 14 180
0ec addi 15 0 -101
0f0 store 8 15 11 1
0f2 jump 64
0f4 load 15 19 1420 4
0f8 load 15 15 100 4
0fa bnez 15 64
0fc jump 180
0fe load 15 18 2 1
102 andi 15 15 1
104 beq 15 0 1098
108 store 18 0 2 1
10c lui 9 536883200
110 jal 1 409410
114 load 15 9 -4 4
118 beqz 15 328
11a load 15 15 4 4
11c beqz 15 328
11e li 15 2
120 store 2 15 4 1
122 load 15 8 69 1
126 addi 10 2 6
12a li 12 6
12c store 2 15 5 1
12e load 15 8 20 1
130 addi 11 8 70
134 store 2 15 12 1
136 auipc 1 536522752
13a jalr 1 1 -866
13e load 15 9 -4 4
142 addi 10 2 4
144 load 15 15 4 4
146 call_indirect 1 15
148 load 15 8 103 1
14c beqz 15 356
14e load 11 8 69 1
152 load 10 8 8 1
154 addi 12 8 70
158 jal 1 436660
15c load 15 8 103 1
160 andi 15 15 2
162 bnez 15 184
164 mv 10 8
166 jal 1 343626
16a jump 190
16c load 15 8 107 1
170 load 10 8 99 1
174 li 12 0
176 addi 11 0 37
17a or 10 10 15
17c jal 1 408894
180 li 12 0
182 li 11 0
184 li 10 1
186 auipc 1 536530944
18a jalr 1 1 34
18e load 15 18 3 1
192 andi 15 15 1
194 beqz 15 444
196 load 10 8 80 4
198 li 13 0
19a mv 12 22
19c li 11 0
19e store 18 0 3 1
1a2 auipc 1 536530944
1a6 jalr 1 1 -122
1aa bnez 10 434
1ac mv 10 8
1ae jal 1 344368
1b2 load 14 8 11 1
1b4 addi 15 0 154
1b8 beq 14 15 64
1bc jal 1 409410
1c0 jump 356
1c2 load 15 8 107 1
1c6 load 10 8 99 1
1ca li 12 0
1cc addi 11 0 37
1d0 or 10 10 15
1d2 jal 1 408894
1d6 li 12 0
1d8 li 11 0
1da li 10 1
1dc auipc 1 536530944
1e0 jalr 1 1 -52
1e4 load 15 18 3 1
1e8 andi 15 15 1
1ea beqz 15 444
1ec load 10 8 80 4
1ee li 13 0
1f0 mv 12 22
1f2 li 11 0
1f4 store 18 0 3 1
1f8 auipc 1 536530944
1fc jalr 1 1 -208
200 bnez 10 520
202 mv 10 8
204 jal 1 343754
208 load 14 8 11 1
20a addi 15 0 153
20e jump 440
210 load 15 18 2 1
214 andi 15 15 1
216 beq 15 0 1098
21a store 18 0 2 1
21e jal 1 409410
222 load 15 9 124 1
226 li 14 2
228 beq 14 15 566
22c load 15 9 124 1
230 li 14 3
232 bne 14 15 602
236 load 13 19 1420 4
23a load 14 8 116 2
23e load 15 13 96 4
240 addi 14 14 300
244 srli 15 15 1
246 bgeu 15 14 602
24a addi 15 0 -107
24e store 8 15 11 1
250 load 15 13 96 4
252 srli 15 15 1
254 bne 15 0 64
258 jump 356
25a load 14 8 25 1
25c load 15 8 26 1
25e beqz 14 664
260 load 13 8 10 1
262 beq 14 13 1148
266 beq 13 15 626
26a store 8 14 10 1
26c mv 10 8
26e jal 1 347346
272 load 15 18 7 1
276 andi 15 15 255
27a bne 15 0 64
27e load 15 9 124 1
282 li 14 2
284 beq 14 15 658
288 load 15 9 124 1
28c li 14 3
28e bne 14 15 356
292 addi 15 0 -107
296 jump 240
298 beqz 15 626
29a load 14 8 10 1
29c bnez 14 626
29e store 8 15 10 1
2a0 jump 620
2a2 load 15 18 2 1
2a6 andi 15 15 1
2a8 beq 15 0 1098
2ac store 18 0 2 1
2b0 load 15 9 124 1
2b4 andi 15 15 16
2b6 beqz 15 730
2b8 jal 1 409410
2bc load 15 9 124 1
2c0 andi 15 15 32
2c4 beqz 15 700
2c6 load 15 9 124 1
2ca mv 10 8
2cc andi 15 15 207
2d0 store 9 15 124 1
2d4 jal 1 344670
2d8 jump 64
2da load 15 9 125 1
2de andi 15 15 1
2e0 beqz 15 748
2e2 jal 1 409410
2e6 addi 15 0 -98
2ea jump 240
2ec load 15 9 124 1
2f0 li 14 5
2f2 andi 15 15 15
2f4 bne 15 14 780
2f8 jal 1 352988
2fc load 15 21 21 1
300 andi 15 15 3
302 bgeu 10 15 444
306 addi 15 0 -99
30a jump 240
30c load 15 9 124 1
310 li 14 6
312 andi 15 15 15
314 bne 15 14 444
318 addi 15 0 -100
31c jump 240
31e load 15 18 2 1
322 andi 15 15 1
324 beq 15 0 64
328 store 18 0 2 1
32c load 15 9 124 1
330 andi 15 15 16
332 beqz 15 836
334 jal 1 409410
338 load 15 9 124 1
33c andi 15 15 32
340 beqz 15 824
342 jump 710
344 load 15 9 125 1
348 andi 15 15 1
34a bnez 15 738
34c load 15 9 124 1
350 li 14 5
352 andi 15 15 15
354 beq 15 14 774
358 load 15 9 124 1
35c li 14 6
35e andi 15 15 15
360 beq 15 14 792
364 jal 1 409410
368 jump 190
36a li 15 3
36c store 8 15 124 1
370 load 15 9 120 4
372 mv 10 8
374 call_indirect 1 15
376 load 14 8 11 1
378 addi 15 0 151
37c beq 14 15 64
380 jump 190
382 load 15 18 3 1
386 andi 15 15 1
388 beqz 15 946
38a jal 1 409410
38e lui 15 536883200
392 load 14 15 1368 4
396 load 15 14 100 4
398 andi 15 15 -5
39a store 14 15 100 4
39c store 18 0 10 1
3a0 lui 14 1073881088
3a4 load 15 14 72 1
3a8 andi 15 15 253
3ac store 14 15 72 1
3b0 jump 356
3b2 load 15 19 1420 4
3b6 load 15 15 100 4
3b8 bne 15 0 64
3bc jump 906
3be load 15 18 2 1
3c2 andi 15 15 1
3c4 beqz 15 1098
3c6 store 18 0 2 1
3ca load 15 9 124 1
3ce andi 15 15 16
3d0 beqz 15 1010
3d2 load 15 9 124 1
3d6 andi 15 15 32
3da beqz 15 978
3dc mv 10 8
3de jal 1 344670
3e2 load 15 9 124 1
3e6 andi 15 15 207
3ea store 9 15 124 1
3ee jal 1 409410
3f2 mv 10 8
3f4 jal 1 343626
3f8 lui 9 536883200
3fc load 15 9 -4 4
400 beqz 15 1072
402 load 15 15 4 4
404 beqz 15 1072
406 li 15 2
408 store 2 15 4 1
40a load 15 8 69 1
40e addi 10 2 6
412 li 12 6
414 store 2 15 5 1
416 load 15 8 20 1
418 addi 11 8 70
41c store 2 15 12 1
41e auipc 1 536522752
422 jalr 1 1 -1610
426 load 15 9 -4 4
42a addi 10 2 4
42c load 15 15 4 4
42e call_indirect 1 15
430 load 15 8 103 1
434 andi 15 15 1
436 beq 15 0 190
43a load 11 8 69 1
43e load 10 8 8 1
440 addi 12 8 70
444 jal 1 436660
448 jump 190
44a load 15 19 1420 4
44e load 15 15 100 4
450 bne 15 0 64
454 jump 444
456 lui 15 536883200
45a addi 15 15 1380
45e load 14 15 2 1
460 andi 14 14 1
462 beq 14 0 444
466 store 15 0 2 1
46a jal 1 409410
46e mv 10 8
470 jal 1 342868
474 mv 10 8
476 jal 1 349178
47a jump 190
47c beq 15 0 626
480 jump 670
'''
)


def specs(index):
    pc=STARTS[index];out={}
    for line in LITERALS[index].splitlines():
        if not line:continue
        a,op,*args=line.split();v=[int(x,0) for x in args];check(len(v)==len(FIELDS[op]),'callback literalfields')
        d=dict(zip(FIELDS[op],v));d['op']=op
        if op in BRANCHES|{'jump'}:d['target']+=pc
        out[pc+int(a,16)]=d
    check(len(out)==COUNTS[index],'callback literalcount');return out


def table(raw,index):
    check(len(raw)==52,'callback tablelength');values=[]
    for k,expected in enumerate(TABLE_WORDS[index]):
        value=int.from_bytes(raw[4*k:4*k+4],'little');check(value==expected,'callback tableword '+str(k));values.append(value)
    check(sha256(raw).hexdigest()==TABLE_HASHES[index],'callback tablehash')
    check(len(set(values))==13 and all(not(x&1) for x in values),'callback13distinct alignedtargets')
    return {'start':TABLES[index],'bytes':52,'sha256':TABLE_HASHES[index],'words':values}


def body(raw,tabraw,index):
    pc=STARTS[index];n=decode(raw,pc);s=specs(index);check(set(n)==set(s),'callback boundaries')
    for p,f in s.items():init.g(n,p,'callback operand '+hex(p-pc),**f)
    check((len(raw),len(n),sha256(raw).hexdigest())==(SIZES[index],COUNTS[index],HASHES[index]),'callback identity')
    tab=table(tabraw,index);check(all(x in n for x in tab['words']),'callback tableentries insideinstructionboundaries')
    check(n[pc+0x16]['imm']+n[pc+0x2c]['imm']==TABLES[index],'callback tablebase formation')
    check([p-pc for p,v in n.items() if v.get('rd')==20]==[0x16,0x2c,0xc8],'callback tablebase onlydefinitions plusrestore')
    edges={};calls=[];rets=[];switches=[]
    for p,v in n.items():
        op=v['op'];q=[p+v['size']]
        if op=='jr':
            if v['rs1']==1:rets.append(p);q=[]
            else:
                check(p==pc+0x56 and v['rs1']==15,'callback onlyexplicit computedtableJR');switches.append(p);q=tab['words']
        elif op in BRANCHES:q.append(v['target'])
        elif op=='jump':q=[v['target']]
        elif op in ('jal','jalr','call_indirect'):
            check(v['rd']==1,'callback calllinkRA')
            if op=='jal':target=hex(v['target'])
            elif op=='call_indirect':target='loadedA5function'
            else:
                a=n[p-4];check(a['op']=='auipc' and a['rd']==v['rs1'],'callback adjacentPCpair');target=hex((p-4+a['imm']+v['imm'])&0xfffffffe)
            calls.append({'pc':p,'target':target})
        check(all(x in n for x in q),'callback closedexpandedCFG');edges[p]=q
    check(rets==[pc+0xd0] and switches==[pc+0x56],'callback distinctRET/internalcomputedJR')
    seen=set();pending=[pc]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);pending.extend(edges[p])
    check(seen==set(n),'callback fullbodyreachable aftertables expanded')
    cycles=[g for g in common.sccs(edges) if len(g)>1 or g[0] in edges[g[0]]]
    check(len(cycles)==2 and [len(g) for g in cycles]==[243,3],'callback243node redispatchSCC and3node waitSCC')
    check(cycles[1]==[pc+0x3d2,pc+0x3d6,pc+0x3da],'callback dedicated bytewaitSCC')
    check(n[pc+0x3d2]['width']==1 and n[pc+0x3d2]['rs1']==9 and n[pc+0x3d2]['imm']==124 and n[pc+0x3d6]['imm']==32,'callback byteB124bit5 wait')
    check((len(calls),sum(v['target']=='loadedA5function' for v in calls))==((36,2),(40,3))[index],'callback exactcall census')
    stores=[{'pc':p,'base':v['rs1'],'offset':v['imm'],'source':v['rs2'],'bytes':v['width']} for p,v in n.items() if v['op']=='store']
    frame=[x for x in stores if x['base']==2]
    check((len(stores),len(frame),sum(x['bytes']==4 for x in frame))==((31,11,8),(34,14,8))[index],'callback store/frame/scratchcensus')
    check([(v['pc']-pc) for v in calls if v['target']=='0x20000332']==([0x140],[0x13a,0x422])[index],'callback extraV140copy')
    return {'start':pc,'end_exclusive':pc+SIZES[index],'bytes':SIZES[index],'sha256':HASHES[index],'instructions':list(n.values()),'switch_table':tab,
      'local_CFG':edges,'cyclic_SCCs':cycles,'calls':calls,'stores':stores,'complete_local_body':True,'actual_table_or_callee_preservation_proved':False,'finite_return_proved':False}


def certificates(b,index):
    pc=b['start'];e=b['local_CFG'];end=pc+0xd0
    def path(a,z):
        q=deque([(a,[a])]);seen=set()
        while q:
            p,s=q.popleft()
            if p==z:return s
            if p in seen:continue
            seen.add(p);q.extend((v,s+[v]) for v in e[p])
        raise RuntimeError('callback no syntactic path')
    witnesses=[]
    for p,qs in e.items():
        for q in qs:
            s=path(pc,p)+[q]+path(q,end)[1:];check(all(z in e[a] for a,z in zip(s,s[1:])),'callback edgewalk validity');witnesses.append([x-pc for x in s])
    prefix=path(pc,pc+0x56);cases={}
    for i,t in enumerate(b['switch_table']['words']):
        s=prefix+[t]+path(t,end)[1:];cases[hex(0x92+i)]={'table_index':i,'entry':t,'syntactic_entry_exit_walk':[x-pc for x in s]}
    fallback=(0x1b4,0x1bc)[index];s=path(pc,pc+0x4c)+path(pc+fallback,end);check(pc+fallback in e[pc+0x4c],'callback unsignedfallback edge')
    walks={'fallback':[x-pc for x in s]}
    for a,z,name in ((0x5e,0x5a,'wait_B124_eq4_backedge'),(0x3da,0x3d2,'wait_B124_bit5_backedge')):
        seq=path(pc,pc+a)+[pc+z]+path(pc+z,end)[1:];check(pc+z in e[pc+a],'callback specificwait backedge');walks[name]=[x-pc for x in seq]
    # Every actual indirect branch is syntactically dominated by the index bound.
    preds={p:set() for p in e}
    for p,qs in e.items():
        for q in qs:preds[q].add(p)
    dom={p:({pc} if p==pc else set(e)) for p in e};changed=True
    while changed:
        changed=False
        for p in e:
            if p==pc:continue
            d={p}|set.intersection(*(dom[q] for q in preds[p]))
            if d!=dom[p]:dom[p]=d;changed=True
    check({pc+0x40,pc+0x44,pc+0x48,pc+0x4c,pc+0x50,pc+0x52,pc+0x54}<dom[pc+0x56],'callback boundedtable index dominance')
    # Static reaching definition sites, conditional on live callee preservation.
    n={v['pc']:v for v in b['instructions']}
    def reaching(reg):
        ins={p:({-1} if p==pc else set()) for p in e};outs={p:set() for p in e};changed=True
        while changed:
            changed=False
            for p in e:
                incoming=({-1} if p==pc else set()).union(*(outs[q] for q in preds[p]))
                outgoing={p} if n[p].get('rd')==reg else incoming
                if incoming!=ins[p] or outgoing!=outs[p]:ins[p]=incoming;outs[p]=outgoing;changed=True
        return ins
    s1=reaching(9);s4=reaching(20);waitbits=(0x2ba,0x2bc)[index]
    for p in (pc+0x5a,pc+waitbits,pc+0x3d2):check(s1[p]=={pc+0x28},'callback waits useB definition notnotificationg')
    check(s4[pc+0x56]=={pc+0x2c},'callback computedJR usescapturedtablebase')
    return {'dispatch_cases':cases,'other_selected_walks':walks,'all_edge_witness_count':len(witnesses),'all_edge_witness_sha256':sha256(json.dumps(witnesses,separators=(',',':')).encode()).hexdigest(),
      'reaching_definition_sites':{'wait_S1_definition':0x28,'switch_S4_definition':0x2c,'premise':'thenlivecalleeGPR/frame preservation; encodeddefinition-sites only, no registerexecution'},
      'scope':'syntactic conditionalnormalreturn CFG walks only; no branchfeasibility/finitepoll/calleecompletion proof'}


def domains():
    selected=[];fallback=[]
    for byte in range(256):
        k=(byte+110)&255
        (selected if k<=12 else fallback).append(byte)
        if k<=12:check(byte==0x92+k,'callback exactstate-to-index relation')
    check(selected==list(range(0x92,0x9f)) and len(fallback)==243,'callback256byte indexdomain')
    return {'all_state_bytecases':256,'table_states':selected,'fallback_count':243,'N11_add110_wrap8':True,
      'table_entries':13,'table_read_offsets':[4*x for x in range(13)],'table_required_bytes':52,'actualreachable_states_or_sourcewriters_proved':False}


def derive(image,carriers,header,coverage):
    parent=previous.derive(image,carriers,header,coverage);profiles=[]
    for i,(data,pr) in enumerate(zip(carriers,parent['profiles'])):
        pc=STARTS[i];raw=init.binding.take(data,pc,SIZES[i]);tabraw=init.binding.take(data,TABLES[i],52);b=body(raw,tabraw,i);cert=certificates(b,i);B=0x200033b8+80*i;C=0x20003514+80*i
        cb=common.body(init.binding.take(data,common.STARTS[i],1220),i);cn={v['pc']:v for v in cb['instructions']};cp=cb['start']
        check(cn[cp+0x1d0]['imm']+cn[cp+0x1d4]['imm']==pc and cn[cp+0x498]['imm']+cn[cp+0x49e]['imm']==pc,'callback commonbody exactcode literals')
        check(any(v['target']==hex(cb['start']) for v in b['calls']),'callback backcall toverifiedcommonbody')
        tail=pr['bodies']['ramtail'];tailcalls=[v for v in b['calls'] if v['target']==hex(tail['start'])];check(len(tailcalls)==3,'callback three RAMtailrequests')
        clear=outer.body(init.binding.take(data,outer.STARTS[i][2],84),'clear',i);check(any(v['target']==clear['start'] for v in b['calls']),'callback fullcleartail join')
        n={v['pc']:v for v in b['instructions']};scratch_offsets=([0x126,0x132,0x13a],[0x120,0x12c,0x134,0x408,0x414,0x41c])[i]
        check(all(n[pc+x]['rs1']==2 and n[pc+x]['width']==1 for x in scratch_offsets),'callback explicit threebyte scratch stores pernotification')
        notifications=[]
        for objcheck,fncheck,copy,callback,s0,s1,s2,reload in ((0x11e,0x122,0x140,0x14c,0x126,0x132,0x13a,0x144),) if not i else ((0x118,0x11c,0x13a,0x146,0x120,0x12c,0x134,0x13e),(0x400,0x404,0x422,0x42e,0x408,0x414,0x41c,0x426)):
            check(n[pc+callback]['op']=='call_indirect' and n[pc+reload]['op']=='load','callback freshnotification pointerreload')
            notifications.append({'guard_offsets':[objcheck,fncheck],'source_global_slot':0x20002fac+80*i,'copy_offset':copy,'copy_request':['SP6','N70',6],
              'explicit_scratch':{'SP4':2,'SP5':'freshU8[N69]','SP12':'freshU8[N20]'},'callback_offset':callback,'A0':'SP4','callback_pointer_reload_offset':reload,
              'lifetime_limit':'initialobject/functionnullguards precedecopy; actualcallfreshlyreloadsbothwithoutnewnullguards; scratchSP4..12initializedonlyifcopy6completes; callbackextent/nonretention/framepreservation unknown'})
        waitbits=(0x2ba,0x2bc)[i];check(n[pc+waitbits]['op']=='load' and n[pc+waitbits]['rs1']==9 and n[pc+waitbits]['imm']==124 and n[pc+waitbits]['width']==1,'callback additional redispatchcomponent bytewait')
        profiles.append({'label':pr['label'],'B':B,'C':C,'body':b,'CFG_certificates':cert,
          'reused_commonbody':{k:cb[k] for k in ('start','bytes','sha256')},'reused_RAMtail':{k:tail[k] for k in ('start','source','bytes','sha256')},'reused_clear':{k:clear[k] for k in ('start','bytes','sha256')},
          'entry_contract':{'N':'freshU32[B100] snapshot; incomingA0 notobjectsource','N_null_guard':False,'frame_bytes':48,'saved':['RA','S0','S1','S2','S3','S4','S5','S6'],
            'minimum_fixed_N_extent':125,'required_live_preservation':'all thenliveSregisters/SP/RA/frame andN/global/tableobjects; calls/loops maymodifyexternally','callback_actual_invocation_proved':False},
          'dispatch_contract':{'byte':'freshU8[N11] eachredispatch','index':'(byte+110)&255','unsigned_bound':'<=12; otherwisefallback','JR':'internaltablejump at+56, notreturn/tail',
            'table_mutable_or_replaced_runtime_proved':False,'captured_N_reloaded_each_iteration':False,'table_pointer':'S4 heldfromprologue; calleepreservation required'},
          'RAMtail_requests':{'target':hex(tail['start']),'callsites':[v['pc']-pc for v in tailcalls],
            'A0':1,'first_A1_A2':[0,37],'remaining_A1_A2':[0,0],'limit':'all3requests selectRAMtailgenericmode1, notpriorcommonbodymode0; fulltailpolls/physicalFENCE.Ibehavior notexecuted'},
          'other_RAM_service':{'target':hex(0x2000263a+76*i),'args':['freshU32[N80]',0,'capturedN+20 pointer',0],'A2_note':'S6=N+20 pointer, not U8[N20] value','returns':'A0zero selects localcallee; nonzero skipsit; semantics/retention unproved'},
          'notifications':notifications,
          'B120_callback':{'call_offset':(0x372,0x374)[i],'word':'freshU32[B120]','local_null_guard':False,'A0':'capturedN','preceding_local_store':'N124=3','reply':'notfixedcallbackstatus; freshN11==151 mayredispatch'},
          'byte_waits':[{'offsets':[0x5a,0x5e],'read':'freshU8[B124]','exit':'equals4'},
            {'offsets':[waitbits,waitbits+4,waitbits+8],'read':'freshU8[B124]','exit':'bit5set'},
            {'offsets':[0x3d2,0x3d6,0x3da],'read':'freshU8[B124]','exit':'bit5set','independent_SCC':True}],
          'wait_and_loop_limit':'2 cyclicSCCs include multiplelocalwaits/redispatch; no localfiniteiterationbound/progress guarantee; S1 must beB onwaitpaths',
          'address_base_limit':'S1 isB generally, butreassigned20003000 innotificationbranches; do notmapallS1relativeaccessestoB',
          'pointed_effects':{'literal_byte_RMW':{'address':0x40022048,'AND_mask':253,'physical_device_identity_proved':False},'other_RMW':'freshpointedobjectfrom'+hex(0x20003508+80*i)+' word100 AND-5',
            'fixed_pointer_globals':[0x2000353c+80*i,0x20003508+80*i],'object_validity_or_MMIO_semantics_proved':False},
          'return_contract':'alllocalRETpaths restoreframe; lastA0depends callees/route, notfixedsuccess; no finitecallback/callee/pollreturn proof',
          'actual_installed_binding_proved':False,'target_execution_or_emulation':False})
    return {'schema':'TSL9-callback-dispatch-static-v1','profile':parent['profile'],'APP_sha256':sha256(image).hexdigest(),'profiles':profiles,'integer_domains':domains(),
      'scope':'2fullcallbacks1064B356i/1154B387i +2tables52B13words;2322neworiginalbytes/743instructionguards/26tablewordguards;priorcommon/RAMtail/clearproofs reused',
      'boundary':'conditionalstatic callback/table/CFG/args only; no actualregistration/scheduling/tableintegrity/provider/lifetime/finitepollreturn proof',
      'remaining':['largerB152consumer69a22/69b3a fullbody','RAMservice2000263a/20002686 source/body','notificationglobal/table/B120 writers/actualcallbackbindings','helpercontracts/frame/payloadretention/pollprogress'],
      'C_reconstruction_coverage_changed':False,'target_execution_or_emulation':False}


def tests(carriers):
    mutations=words=walks=edges=0
    for i,data in enumerate(carriers):
        pc=STARTS[i];raw=init.binding.take(data,pc,SIZES[i]);tabraw=init.binding.take(data,TABLES[i],52);b=body(raw,tabraw,i);c=certificates(b,i);walks+=len(c['dispatch_cases'])+len(c['other_selected_walks']);edges+=c['all_edge_witness_count']
        for p,v in decode(raw,pc).items():
            at=p-pc;z=v['size'];buf=bytearray(raw);buf[at:at+z]=(int.from_bytes(buf[at:at+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
            try:body(buf,tabraw,i)
            except RuntimeError as ex:check(str(ex).startswith('callback operand '),'callback specifiedmutation '+str(ex))
            else:raise RuntimeError('callback mutationescaped')
            mutations+=1
        for k in range(13):
            buf=bytearray(tabraw);buf[4*k:4*k+4]=(int.from_bytes(buf[4*k:4*k+4],'little')^2).to_bytes(4,'little')
            try:table(buf,i)
            except RuntimeError as ex:check(str(ex)=='callback tableword '+str(k),'callback table specificguard')
            else:raise RuntimeError('callback tablemutationescaped')
            words+=1
    check((mutations,words)==(743,26),'callback mutationcensus');domains()
    print('PASS:743 instruction mutations +26 tableword mutations rejected;2322 new originalbytes;'+str(walks)+' selectedCFG walks;'+str(edges)+' edge witnesses;256 dispatchbytes;exact SCCs/dominance')


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
    else:check(OUT.read_bytes()==output,'callback exactledger replay')
    print('PASS:fullswitch-table/actualversiondiffs/commonbody/RAMtail/notification-scratch joins;exact ledger')
    print('PASS:NO target execution/emulation;actualcallback/provider/tablepreservation/pollprogress/retention UNPROVED')


if __name__=='__main__':main()
