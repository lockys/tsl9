"""Offline complete record callback: byte writers, source/cursor and return boundaries.
Original operands, immutable CFGs and host bit/interval identities only.
No target execution/emulation, mutable clock/RAM/MMIO/callback/packet model.
"""
import argparse,json
from collections import deque
from pathlib import Path
from hashlib import sha256
import check_v4160_b1_b120_target_static as previous
import check_v4160_b1_completion_static as completion
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-record-callback-static.json')
STARTS=(0x5c9b4,0x5cafc)
HASHES=('11e6ea3f9ddb4289972ad86a1b556bdcbd8841744e9cc78508290ddc59e43421', 'e2b1f758aedfd0bbb8bcf8b5f9e284d8679536fc5719afa358353147c4a397af')
LITERAL="""
000 addi 2 2 -64
002 store 2 20 40 4
004 lui 20 536883200
008 addi 15 20 1300
00c load 15 15 24 4
00e store 2 21 36 4
010 store 2 1 60 4
012 lui 21 536883200
016 store 2 8 56 4
018 store 2 9 52 4
01a store 2 18 48 4
01c store 2 19 44 4
01e store 2 22 32 4
020 store 2 23 28 4
022 store 2 24 24 4
024 slli 13 15 16
028 load 14 21 1340 4
02c blt 13 0 86
030 load 15 14 108 4
032 beqz 15 62
034 lui 15 536883200
038 li 14 1
03a store 15 14 -260 1
03e load 1 2 60 4
040 load 8 2 56 4
042 load 9 2 52 4
044 load 18 2 48 4
046 load 19 2 44 4
048 load 20 2 40 4
04a load 21 2 36 4
04c load 22 2 32 4
04e load 23 2 28 4
050 load 24 2 24 4
052 addi 2 2 64
054 jr 1
056 lui 23 536883200
05a addi 15 23 952
05e load 8 15 88 4
060 addi 15 0 160
064 store 14 15 100 4
066 load 19 8 172 4
06a addi 20 20 1300
06e addi 23 23 952
072 load 24 19 9 1
076 slli 15 24 4
07a load 24 19 12 4
07e add 24 24 15
080 load 15 24 2 1
084 beqz 15 182
086 load 15 19 6 1
08a addi 13 0 1250
08e load 12 24 1 1
092 mul 15 15 13
096 addi 15 15 -40
09a beqz 12 174
09c load 13 19 7 1
0a0 mul 13 13 12
0a4 addi 12 0 125
0a8 mul 13 13 12
0ac add 15 15 13
0ae lui 13 32768
0b0 store 14 13 8 4
0b2 slli 15 15 1
0b4 store 14 15 108 4
0b6 load 15 14 0 4
0b8 andi 15 15 3
0ba beqz 15 194
0bc li 10 2
0be jal 1 409306
0c2 lui 22 536883200
0c6 load 15 22 1288 4
0ca lui 12 3342336
0ce lui 11 2181038080
0d2 load 14 15 44 4
0d4 addi 11 11 -1
0d6 andi 14 14 -4
0d8 ori 14 14 1
0dc store 15 14 44 4
0de load 14 15 0 4
0e0 andi 14 14 -385
0e4 store 15 14 0 4
0e6 load 14 15 0 4
0e8 andi 14 14 -385
0ec ori 14 14 256
0f0 store 15 14 0 4
0f2 lui 14 536883200
0f6 load 13 14 1424 4
0fa load 14 13 8 4
0fc or 14 14 12
0fe store 13 14 8 4
100 load 14 21 1340 4
104 addi 12 0 90
108 store 14 12 80 4
10a load 12 13 44 4
10c andi 12 12 -3
10e store 13 12 44 4
110 load 13 8 126 1
114 andi 12 13 127
118 load 13 15 0 4
11a andi 13 13 -128
11e or 13 13 12
120 store 15 13 0 4
122 load 13 8 104 1
126 andi 13 13 63
12a slli 12 13 25
12e load 13 15 44 4
130 and 13 13 11
132 or 13 13 12
134 store 15 13 44 4
136 load 13 8 144 4
13a load 9 8 76 4
13c store 15 13 4 4
13e load 13 8 140 4
142 store 15 13 8 4
144 load 15 8 172 4
148 load 13 15 11 1
14a li 15 1
14c bne 13 15 926
150 load 18 8 176 4
154 load 13 19 9 1
158 load 15 18 1 1
15c bne 13 15 926
160 store 14 0 108 4
164 lui 15 32768
166 store 14 15 8 4
168 store 20 0 20 4
16c load 15 14 4 4
16e ori 15 15 1
172 store 14 15 4 4
174 addi 15 0 34
178 store 8 15 17 1
17a li 14 5
17c store 9 14 0 1
17e store 9 15 1 1
180 load 15 8 53 1
184 andi 15 15 1
186 bnez 15 402
188 load 14 8 52 1
18c li 15 2
18e bne 14 15 408
192 addi 15 0 69
196 store 9 15 0 1
198 li 12 6
19a addi 11 8 54
19e addi 10 9 2
1a2 auipc 1 536489984
1a6 jalr 1 1 2012
1aa load 15 18 3 1
1ae beqz 15 440
1b0 load 15 9 0 1
1b2 ori 15 15 -128
1b6 store 9 15 0 1
1b8 li 12 6
1ba addi 11 18 4
1be addi 10 9 8
1c2 auipc 1 536489984
1c6 jalr 1 1 1980
1ca load 15 18 24 1
1ce store 9 15 14 1
1d0 load 15 18 25 1
1d4 store 9 15 15 1
1d6 load 15 18 26 1
1da store 9 15 16 1
1dc load 15 18 27 1
1e0 store 9 15 17 1
1e2 load 15 18 20 4
1e6 srli 14 15 8
1ea store 9 15 18 1
1ec srli 15 15 16
1ee store 9 14 19 1
1f0 store 9 15 20 1
1f2 load 13 8 128 1
1f6 li 14 2
1f8 li 15 3
1fa beq 13 14 512
1fe li 15 2
200 store 9 15 21 1
202 load 14 18 12 2
206 load 15 18 10 2
20a li 13 6
20c add 15 15 14
20e srli 15 15 1
210 srli 14 15 8
214 store 9 14 25 1
216 load 14 18 14 1
21a store 9 15 24 1
21c srli 15 15 3
21e store 9 14 26 1
220 load 14 18 14 2
224 addi 15 15 3
226 srli 14 14 8
228 store 9 14 27 1
22a load 14 18 16 1
22e store 9 14 28 1
230 load 14 18 17 1
234 store 9 14 29 1
236 mv 14 15
238 bgeu 13 15 574
23c li 14 6
23e slli 15 14 16
242 srli 15 15 16
244 store 9 15 22 1
246 srli 15 15 8
248 store 9 15 23 1
24a load 15 23 262 1
24e load 12 22 1288 4
252 li 10 0
254 store 9 15 30 1
256 load 15 23 263 1
25a store 9 15 31 1
25c load 15 23 264 1
260 store 9 15 32 1
264 load 15 23 265 1
268 store 9 15 33 1
26c load 15 23 266 1
270 store 9 15 34 1
274 load 15 18 28 1
278 andi 15 15 31
27a store 9 15 35 1
27e load 14 8 76 4
280 load 15 23 3 1
284 load 13 14 35 1
288 slli 15 15 5
28a or 15 15 13
28c store 14 15 35 1
290 lui 15 536883200
294 load 15 15 512 1
298 lui 13 2181038080
29c addi 13 13 -1
29e andi 15 15 63
2a2 slli 14 15 25
2a6 load 15 12 44 4
2a8 and 15 15 13
2aa or 15 15 14
2ac store 12 15 44 4
2ae load 12 8 17 1
2b0 load 11 8 128 1
2b4 store 20 0 3 1
2b8 auipc 1 536502272
2bc jalr 1 1 -1458
2c0 load 15 20 2 1
2c4 andi 15 15 1
2c6 beqz 15 830
2c8 load 13 8 128 1
2cc lui 18 536883200
2d0 load 15 18 564 4
2d4 store 20 0 2 1
2d8 addi 18 18 564
2dc li 14 1
2de load 22 18 8 2
2e2 bgeu 14 13 906
2e6 call_indirect 1 15
2e8 lui 12 999424
2ec mv 9 10
2ee addi 12 12 576
2f2 li 13 0
2f4 addi 10 0 1240
2f8 mul 10 22 10
2fc li 11 0
2fe jal 1 450330
302 add 15 10 9
306 sltu 10 15 10
30a add 10 10 11
30c mv 14 15
30e load 13 18 4 4
312 bnez 10 792
314 bltu 15 13 796
318 sub 14 15 13
31c store 8 14 36 4
31e li 12 0
320 li 11 0
322 li 10 1
324 auipc 1 536502272
328 jalr 1 1 -1566
32c jal 1 409176
330 load 15 20 3 1
334 andi 15 15 1
336 beqz 15 830
338 mv 10 8
33a jal 1 378928
33e load 15 19 9 1
342 load 14 19 4 1
346 addi 15 15 1
348 andi 15 15 255
34c store 19 15 9 1
350 bgeu 15 14 1546
354 lui 9 536883200
358 addi 15 9 564
35c load 15 15 12 1
35e addi 9 9 564
362 beq 15 0 1392
366 load 15 8 172 4
36a addi 14 0 -89
36e lui 10 536879104
372 store 15 14 10 1
374 addi 10 10 -854
378 jal 1 278226
37c lui 15 3758153728
380 lui 14 33554432
384 store 15 14 516 4
388 jump 62
38a call_indirect 1 15
38c lui 12 999424
390 mv 9 10
392 addi 12 12 576
396 li 13 0
398 addi 10 0 248
39c jump 760
39e load 15 14 4 4
3a0 andi 15 15 -2
3a2 store 14 15 4 4
3a4 li 15 7
3a6 load 23 24 8 4
3aa load 18 24 3 1
3ae store 8 15 16 1
3b0 store 9 15 0 1
3b2 li 15 1
3b4 store 9 0 3 1
3b8 store 9 15 2 1
3ba load 15 8 84 4
3bc andi 15 15 512
3c0 beqz 15 1006
3c2 li 15 4
3c4 store 9 15 3 1
3c6 load 15 8 182 1
3ca load 13 8 181 1
3ce load 14 8 76 4
3d0 slli 15 15 6
3d2 or 15 15 13
3d4 store 14 15 4 1
3d6 load 15 9 2 1
3d8 li 13 0
3da addi 15 15 1
3dc store 9 15 2 1
3de load 12 8 184 1
3e2 load 11 8 181 1
3e6 load 10 8 182 1
3ea jal 1 408938
3ee load 15 8 84 4
3f0 andi 15 15 1024
3f4 beqz 15 1064
3f6 load 14 9 3 1
3f8 load 15 8 76 4
3fa load 13 9 2 1
3fc ori 14 14 8
400 store 9 14 3 1
402 load 14 8 138 2
406 add 15 15 13
408 store 15 14 3 1
40a load 15 9 2 1
40c load 14 8 76 4
40e load 13 8 127 1
412 add 14 14 15
414 load 15 8 138 2
418 slli 13 13 4
41a srli 15 15 8
41c andi 15 15 15
41e or 15 15 13
420 store 14 15 4 1
422 load 15 9 2 1
424 addi 15 15 2
426 store 9 15 2 1
428 load 15 8 96 1
42c andi 15 15 64
430 beqz 15 1098
432 load 14 9 3 1
434 load 15 8 76 4
436 load 13 9 2 1
438 ori 14 14 64
43c store 9 14 3 1
43e load 14 8 21 1
440 add 15 15 13
442 store 15 14 3 1
444 load 15 9 2 1
446 addi 15 15 1
448 store 9 15 2 1
44a load 15 8 124 1
44e li 14 1
450 addi 15 15 -16
452 andi 15 15 255
456 bltu 14 15 1214
45a load 22 9 2 1
45e lui 11 536883200
462 li 12 5
464 addi 15 22 3
468 load 22 8 76 4
46c addi 11 11 1214
470 add 22 22 15
472 li 15 8
474 store 22 15 0 1
478 addi 15 0 40
47c store 22 15 1 1
480 addi 10 22 2
484 auipc 1 536489984
488 jalr 1 1 1274
48c load 14 8 124 1
490 li 15 16
492 bne 14 15 1372
496 load 15 8 136 2
49a addi 15 15 8
49c store 8 15 130 2
4a0 li 15 17
4a2 store 8 15 124 1
4a6 load 15 8 130 1
4aa store 22 15 7 1
4ae load 15 8 130 2
4b2 srli 15 15 8
4b4 store 22 15 8 1
4b8 load 15 9 2 1
4ba addi 15 15 9
4bc store 9 15 2 1
4be beq 23 0 1238
4c2 load 15 9 2 1
4c4 load 10 8 76 4
4c6 mv 12 18
4c8 addi 15 15 3
4ca mv 11 23
4cc add 10 10 15
4ce auipc 1 536489984
4d2 jalr 1 1 1200
4d6 load 14 9 2 1
4d8 li 10 0
4da andi 15 14 63
4de addi 15 15 1
4e0 add 18 18 15
4e2 andi 18 18 255
4e6 store 8 18 17 1
4ea store 9 14 2 1
4ec load 15 8 76 4
4ee store 15 18 1 1
4f2 addi 15 0 -105
4f6 load 14 8 76 4
4f8 store 8 15 11 1
4fa load 15 21 1340 4
4fe store 15 14 112 4
500 load 12 8 17 1
502 load 11 8 128 1
506 store 20 0 3 1
50a auipc 1 536498176
50e jalr 1 1 2044
512 jal 1 409176
516 load 15 21 1340 4
51a lui 14 8192
51c store 15 0 100 4
520 store 15 14 8 4
522 store 20 0 4 1
526 load 14 20 3 1
52a load 14 24 2 1
52e beq 14 0 830
532 load 15 15 108 4
534 beq 15 0 830
538 lui 10 536879104
53c addi 10 10 -556
540 auipc 1 536494080
544 jalr 1 1 -1898
548 load 14 21 1340 4
54c load 15 14 108 4
54e bnez 15 1356
550 li 10 0
552 auipc 1 536494080
556 jalr 1 1 -1916
55a jump 830
55c load 14 8 136 2
560 load 15 8 130 2
564 sub 15 15 14
566 li 14 2
568 blt 14 15 1190
56c li 15 18
56e jump 1186
570 lui 18 536883200
574 load 15 18 480 4
578 call_indirect 1 15
57a mv 22 10
57c load 15 18 480 4
580 call_indirect 1 15
582 beq 10 22 1404
586 load 14 19 5 1
58a load 15 19 9 1
58e load 13 9 4 4
590 mul 15 15 14
594 load 14 9 8 2
596 mul 15 15 14
59a addi 14 0 800
59e addi 15 15 400
5a2 divu 15 15 14
5a6 load 14 8 148 4
5aa add 14 14 15
5ac mv 8 14
5ae bltu 14 15 1462
5b2 bltu 14 13 1466
5b6 sub 8 14 13
5ba load 15 18 480 4
5be call_indirect 1 15
5c0 sub 15 8 10
5c4 bgeu 8 10 1484
5c8 load 10 9 4 4
5ca add 15 15 10
5cc lui 10 999424
5d0 addi 10 10 576
5d4 mulhu 11 15 10
5d8 load 12 9 8 2
5da li 13 0
5dc mul 10 15 10
5e0 jal 1 450330
5e4 mv 8 10
5e6 lui 10 380928
5ea li 15 11
5ec addi 10 10 -1612
5f0 store 20 15 7 1
5f4 auipc 1 536489984
5f8 jalr 1 1 2018
5fc load 15 21 1340 4
600 lui 14 32768
602 slli 8 8 1
604 store 15 14 8 4
606 store 15 8 108 4
608 jump 62
60a load 15 19 12 4
60e load 10 15 8 4
610 bnez 10 1582
612 load 15 8 8 1
614 addi 10 2 12
616 store 2 0 14 1
61a store 2 15 13 1
61c load 15 8 172 4
620 load 15 15 4 1
622 store 2 15 15 1
624 jal 1 339328
628 store 19 0 10 1
62c jump 62
62e auipc 1 536489984
632 jalr 1 1 302
636 load 14 19 12 4
63a load 13 19 4 1
63e li 15 0
640 blt 15 13 1610
644 load 15 14 8 4
646 bnez 15 1576
648 jump 1554
64a store 14 0 8 4
64e addi 15 15 1
650 jump 1600
"""
V140_PATCHES={8: ('addi', [15, 20, 1380]), 40: ('load', [14, 21, 1420, 4]), 58: ('store', [15, 14, -180, 1]), 90: ('addi', [15, 23, 1032]), 106: ('addi', [20, 20, 1380]), 110: ('addi', [23, 23, 1032]), 190: ('jal', [1, 409540]), 198: ('load', [15, 22, 1368, 4]), 246: ('load', [13, 14, 1504, 4]), 256: ('load', [14, 21, 1420, 4]), 422: ('jalr', [1, 1, 1684]), 454: ('jalr', [1, 1, 1652]), 590: ('load', [12, 22, 1368, 4]), 660: ('load', [15, 15, 592, 1]), 700: ('jalr', [1, 1, -1710]), 720: ('load', [15, 18, 644, 4]), 728: ('addi', [18, 18, 644]), 766: ('jal', [1, 450826]), 808: ('jalr', [1, 1, -1818]), 812: ('jal', [1, 409410]), 826: ('jal', [1, 379256]), 856: ('addi', [15, 9, 644]), 862: ('addi', [9, 9, 644]), 888: ('jal', [1, 278366]), 1002: ('jal', [1, 409172]), 1132: ('addi', [11, 11, 1294]), 1160: ('jalr', [1, 1, 946]), 1234: ('jalr', [1, 1, 872]), 1274: ('load', [15, 21, 1420, 4]), 1294: ('jalr', [1, 1, 1792]), 1298: ('jal', [1, 409410]), 1302: ('load', [15, 21, 1420, 4]), 1344: ('auipc', [1, 536489984]), 1348: ('jalr', [1, 1, 1870]), 1352: ('load', [14, 21, 1420, 4]), 1362: ('auipc', [1, 536489984]), 1366: ('jalr', [1, 1, 1852]), 1396: ('load', [15, 18, 560, 4]), 1404: ('load', [15, 18, 560, 4]), 1466: ('load', [15, 18, 560, 4]), 1504: ('jal', [1, 450826]), 1516: ('addi', [10, 10, -1284]), 1528: ('jalr', [1, 1, 1690]), 1532: ('load', [15, 21, 1420, 4]), 1572: ('jal', [1, 339496]), 1586: ('jalr', [1, 1, -26])}
TYPED=[(40, 2), (102, 2), (114, 4), (122, 2), (128, 4), (134, 4), (142, 4), (156, 4), (198, 2), (246, 2), (256, 2), (272, 4), (290, 4), (310, 2), (318, 2), (324, 2), (336, 2), (340, 4), (344, 4), (384, 4), (392, 4), (426, 4), (458, 4), (464, 4), (470, 4), (476, 4), (482, 2), (498, 4), (514, 5), (518, 5), (534, 4), (544, 5), (554, 4), (560, 4), (586, 4), (590, 2), (598, 4), (604, 4), (612, 4), (620, 4), (628, 4), (640, 4), (644, 4), (660, 4), (688, 4), (704, 4), (712, 4), (720, 2), (734, 5), (782, 2), (816, 4), (830, 4), (834, 4), (870, 2), (934, 2), (938, 4), (966, 4), (970, 4), (990, 4), (994, 4), (998, 4), (1026, 5), (1038, 4), (1044, 5), (1064, 4), (1098, 4), (1114, 4), (1128, 2), (1164, 4), (1174, 5), (1190, 4), (1198, 5), (1274, 2), (1282, 4), (1302, 2), (1318, 4), (1322, 4), (1352, 2), (1372, 5), (1376, 5), (1396, 2), (1404, 2), (1414, 4), (1418, 4), (1446, 2), (1466, 2), (1532, 2), (1546, 2), (1564, 2), (1590, 2), (1594, 4)]
QK=[(328, 'b437', 'qk.c.lbu'), (376, '1cb8', 'qk.c.sb'), (380, '98a0', 'qk.c.sb'), (382, '9cb0', 'qk.c.sb'), (406, '9ca0', 'qk.c.sb'), (432, '9c20', 'qk.c.lbu'), (438, '9ca0', 'qk.c.sb'), (462, 'fca4', 'qk.c.sb'), (468, 'fcb4', 'qk.c.sb'), (474, '9ca8', 'qk.c.sb'), (480, '9cb8', 'qk.c.sb'), (490, 'bca8', 'qk.c.sb'), (494, 'b8b8', 'qk.c.sb'), (496, 'dca8', 'qk.c.sb'), (512, 'dcb8', 'qk.c.sb'), (532, '98bc', 'qk.c.sb'), (538, '9cac', 'qk.c.sb'), (542, 'b8ac', 'qk.c.sb'), (552, 'b8bc', 'qk.c.sb'), (558, 'd8ac', 'qk.c.sb'), (564, 'd8bc', 'qk.c.sb'), (580, 'fca8', 'qk.c.sb'), (584, 'fcb8', 'qk.c.sb'), (596, 'fcac', 'qk.c.sb'), (602, 'fcbc', 'qk.c.sb'), (686, '1038', 'qk.c.lbu'), (860, 'dc27', 'qk.c.lbu'), (882, 'b8a7', 'qk.c.sb'), (942, '1ca8', 'qk.c.sb'), (944, '9ca0', 'qk.c.sb'), (952, 'bca0', 'qk.c.sb'), (964, 'bcb0', 'qk.c.sb'), (980, '5ca3', 'qk.c.sb'), (982, 'bc20', 'qk.c.lbu'), (988, 'bca0', 'qk.c.sb'), (1014, 'b830', 'qk.c.lbu'), (1018, 'b420', 'qk.c.lbu'), (1024, 'b8b0', 'qk.c.sb'), (1032, 'b8b3', 'qk.c.sb'), (1034, 'bc20', 'qk.c.lbu'), (1056, '5ca3', 'qk.c.sb'), (1058, 'bc20', 'qk.c.lbu'), (1062, 'bca0', 'qk.c.sb'), (1074, 'b830', 'qk.c.lbu'), (1078, 'b420', 'qk.c.lbu'), (1084, 'b8b0', 'qk.c.sb'), (1086, '5838', 'qk.c.lbu'), (1090, 'b8b3', 'qk.c.sb'), (1092, 'bc20', 'qk.c.lbu'), (1096, 'bca0', 'qk.c.sb'), (1208, 'bc20', 'qk.c.lbu'), (1212, 'bca0', 'qk.c.sb'), (1218, 'bc20', 'qk.c.lbu'), (1238, 'b820', 'qk.c.lbu'), (1258, 'b8a0', 'qk.c.sb'), (1272, '3cb4', 'qk.c.sb'), (1280, '1038', 'qk.c.lbu'), (1428, '9a24', 'qk.c.lhu'), (1496, '9224', 'qk.c.lhu'), (1554, '1c24', 'qk.c.lbu'), (1562, 'dc86', 'qk.c.sbsp'), (1568, 'dc23', 'qk.c.lbu'), (1570, 'dc87', 'qk.c.sbsp')]
STORE_SITES=[(2, 2, 20, 40, 4), (14, 2, 21, 36, 4), (16, 2, 1, 60, 4), (22, 2, 8, 56, 4), (24, 2, 9, 52, 4), (26, 2, 18, 48, 4), (28, 2, 19, 44, 4), (30, 2, 22, 32, 4), (32, 2, 23, 28, 4), (34, 2, 24, 24, 4), (58, 15, 14, -260, 1), (100, 14, 15, 100, 4), (176, 14, 13, 8, 4), (180, 14, 15, 108, 4), (220, 15, 14, 44, 4), (228, 15, 14, 0, 4), (240, 15, 14, 0, 4), (254, 13, 14, 8, 4), (264, 14, 12, 80, 4), (270, 13, 12, 44, 4), (288, 15, 13, 0, 4), (308, 15, 13, 44, 4), (316, 15, 13, 4, 4), (322, 15, 13, 8, 4), (352, 14, 0, 108, 4), (358, 14, 15, 8, 4), (360, 20, 0, 20, 4), (370, 14, 15, 4, 4), (376, 8, 15, 17, 1), (380, 9, 14, 0, 1), (382, 9, 15, 1, 1), (406, 9, 15, 0, 1), (438, 9, 15, 0, 1), (462, 9, 15, 14, 1), (468, 9, 15, 15, 1), (474, 9, 15, 16, 1), (480, 9, 15, 17, 1), (490, 9, 15, 18, 1), (494, 9, 14, 19, 1), (496, 9, 15, 20, 1), (512, 9, 15, 21, 1), (532, 9, 14, 25, 1), (538, 9, 15, 24, 1), (542, 9, 14, 26, 1), (552, 9, 14, 27, 1), (558, 9, 14, 28, 1), (564, 9, 14, 29, 1), (580, 9, 15, 22, 1), (584, 9, 15, 23, 1), (596, 9, 15, 30, 1), (602, 9, 15, 31, 1), (608, 9, 15, 32, 1), (616, 9, 15, 33, 1), (624, 9, 15, 34, 1), (634, 9, 15, 35, 1), (652, 14, 15, 35, 1), (684, 12, 15, 44, 4), (692, 20, 0, 3, 1), (724, 20, 0, 2, 1), (796, 8, 14, 36, 4), (844, 19, 15, 9, 1), (882, 15, 14, 10, 1), (900, 15, 14, 516, 4), (930, 14, 15, 4, 4), (942, 8, 15, 16, 1), (944, 9, 15, 0, 1), (948, 9, 0, 3, 1), (952, 9, 15, 2, 1), (964, 9, 15, 3, 1), (980, 14, 15, 4, 1), (988, 9, 15, 2, 1), (1024, 9, 14, 3, 1), (1032, 15, 14, 3, 1), (1056, 14, 15, 4, 1), (1062, 9, 15, 2, 1), (1084, 9, 14, 3, 1), (1090, 15, 14, 3, 1), (1096, 9, 15, 2, 1), (1140, 22, 15, 0, 1), (1148, 22, 15, 1, 1), (1180, 8, 15, 130, 2), (1186, 8, 15, 124, 1), (1194, 22, 15, 7, 1), (1204, 22, 15, 8, 1), (1212, 9, 15, 2, 1), (1254, 8, 18, 17, 1), (1258, 9, 14, 2, 1), (1262, 15, 18, 1, 1), (1272, 8, 15, 11, 1), (1278, 15, 14, 112, 4), (1286, 20, 0, 3, 1), (1308, 15, 0, 100, 4), (1312, 15, 14, 8, 4), (1314, 20, 0, 4, 1), (1520, 20, 15, 7, 1), (1540, 15, 14, 8, 4), (1542, 15, 8, 108, 4), (1558, 2, 0, 14, 1), (1562, 2, 15, 13, 1), (1570, 2, 15, 15, 1), (1576, 19, 0, 10, 1), (1610, 14, 0, 8, 4)]


def specs(index):
 pc=STARTS[index];out={}
 for row in LITERAL.splitlines():
  if not row:continue
  off,op,*values=row.split();o=int(off,16);values=list(map(int,values))
  if index and o in V140_PATCHES:op,values=V140_PATCHES[o]
  check(len(values)==len(FIELDS[op]),'recordCB literalfields');d=dict(zip(FIELDS[op],values));d['op']=op
  if op in BRANCHES|{'jump'}:d['target']+=pc
  out[pc+o]=d
 return out


def body(raw,index):
 pc=STARTS[index];n=decode(raw,pc);s=specs(index);check(n.keys()==s.keys(),'recordCB fullboundaries')
 for a,f in s.items():init.g(n,a,'recordCB operand '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(1618,542,HASHES[index]),'recordCB fullidentity')
 for o,f3 in TYPED:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'recordCB typedload')
 for o,h,m in QK:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'recordCB exactQK widths/stackbytes')
 e={};calls=[]
 for a,d in n.items():
  op=d['op'];q=[] if op=='jr' else [a+d['size']]
  if op in BRANCHES:q.append(d['target'])
  if op=='jump':q=[d['target']]
  if op=='jr':check(d['rs1']==1,'recordCB ordinaryRET')
  if op=='jal':check(d['rd']==1,'recordCB noexternaltaillink');calls.append(dict(offset=a-pc,target=d['target']))
  if op=='jalr':
   u=n[a-4];check(d['rd']==d['rs1']==u.get('rd')==1 and u['op']=='auipc','recordCB linkedPCpair');calls.append(dict(offset=a-pc,target=(a-4+u['imm']+d['imm'])&0xfffffffe))
  if op=='call_indirect':check(d['rd']==1 and d['rs1']==15,'recordCB loadedA5call');calls.append(dict(offset=a-pc,target='loadedA5'))
  check(op not in ('csr','ecall','mret') and all(z in n for z in q),'recordCB closedCFG');e[a]=q
 expected=[(0xbe,0x63eda+234*index),(0x1a6,0x20000332),(0x1c6,0x20000332),(0x2bc,0x200026ba+76*index),(0x2e6,'loadedA5'),(0x2fe,0x6df1a+496*index),(0x328,0x200026ba+76*index),(0x32c,0x63e58+234*index),(0x33a,0x5c830+328*index),(0x378,0x43ed2+140*index),(0x38a,'loadedA5'),(0x3ea,0x63d6a+234*index),(0x488,0x20000332),(0x4d2,0x20000332),(0x50e,0x200026ba+76*index),(0x512,0x63e58+234*index),(0x544,0x2000078a),(0x556,0x2000078a),(0x578,'loadedA5'),(0x580,'loadedA5'),(0x5be,'loadedA5'),(0x5e0,0x6df1a+496*index),(0x5f8,0x2000078a),(0x624,0x52d80+168*index),(0x632,0x20000110)]
 check(calls==[dict(offset=o,target=t) for o,t in expected],'recordCB all25calls')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n) and [a-pc for a,q in e.items() if not q]==[0x54],'recordCB allreachable/soleRET')
 groups=previous.previous.previous.dispatch.common.sccs(e);cycles=[g for g in groups if len(g)>1 or g[0] in e[g[0]]]
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];expectedstores=[tuple((*x[:3],x[3]+80*index,x[4])) if x[0]==0x3a else tuple(x) for x in STORE_SITES]
 check(stores==expectedstores and len(stores)==102 and sum(d['op']=='load' for d in n.values())==153 and len(TYPED)==91 and len(QK)==63,'recordCB all102stores/153loads/typed/QK census')
 return dict(start=pc,bytes=1618,sha256=HASHES[index],instructions=list(n.values()),CFG=e,local_CFG=e,cyclic_SCCs=cycles,calls=calls,stores=stores,returns=[pc+0x54],complete_local_body=True,actual_finite_return_proved=False)


def certificates(b):
 pc=b['start'];e=b['CFG'];n={d['pc']-pc:d for d in b['instructions']}
 def path(a,z):
  q=deque([(a,[a])]);seen=set()
  while q:
   p,s=q.popleft()
   if p==z:return s
   if p not in seen:seen.add(p);q.extend((v,s+[v]) for v in e[p])
  raise RuntimeError('recordCB no syntaxpath')
 walks=[]
 for a,qs in e.items():
  for z in qs:
   w=path(pc,a)+[z]+path(z,pc+0x54)[1:];check(all(v in e[u] for u,v in zip(w,w[1:])),'recordCB all-edge witness');walks.append([p-pc for p in w])
 cycles=[[a-pc for a in g] for g in b['cyclic_SCCs']]
 check(cycles==[[0x54c,0x54e],[0x57c,0x580,0x582],[0x640,0x64a,0x64e,0x650]] and len(walks)==577,'recordCB exact3cycles/577edges')
 # Static reaching definitions assume callees preserve then-live saved registers.
 fields=previous.previous
 nsites=[o for o,d in n.items() if d['op'] in ('load','store') and d['rs1']==8]
 nd=fields.reaching_definitions(b,8,nsites);check(all(ds==[0x5e] for ds in nd.values()),'recordCB originalN base forallexplicitN memoryaccesses')
 dstsites=[o for o,d in n.items() if d['op']=='store' and d['rs1']==9]
 dd=fields.reaching_definitions(b,9,dstsites);check(all(ds==[0x13a] for ds in dd.values()),'recordCB cachedN76 base forallexplicitS1datastores')
 indirect=fields.reaching_definitions(b,15,[0x2e6,0x38a,0x578,0x580,0x5be])
 check(indirect=={'0x2e6':[0x2d0],'0x38a':[0x2d0],'0x578':[0x574],'0x580':[0x57c],'0x5be':[0x5ba]},'recordCB contextword0 vsclockslot captures')
 stack=[d for d in b['stores'] if d[1]==2];check(len(stack)==13 and [(o,w) for o,_,_,w,_ in stack if o>=0x600]==[(0x616,14),(0x61a,13),(0x622,15)],'recordCB allframe/scratchstores')
 initialized=set().union(*(set(range(imm,imm+width)) for _,_,_,imm,width in stack));check(12 not in initialized and {13,14,15}<=initialized and max(initialized)==63,'recordCB SP12noexplicitlocalstore')
 check(n[0x614]['rd']==10 and n[0x614]['rs1']==2 and n[0x614]['imm']==12 and n[0x624]['target']==0x52d80+168*(pc==STARTS[1]),'recordCB borrowedpartialstackpayloadcall')
 check(n[0x63a]['width']==1 and n[0x63e]['imm']==0 and n[0x640]['op']=='blt' and n[0x640]['rs1']==15 and n[0x640]['rs2']==13 and n[0x64a]['rs2']==0 and n[0x64a]['rs1']==14 and n[0x64a]['imm']==8 and n[0x64e]['imm']==1,'recordCB capturedbyte rank/sameaddress zeroingloop')
 check(n[0x7a]['imm']==12 and n[0x72]['imm']==9 and n[0x76]['imm']==4 and n[0x7e]['op']=='add','recordCB stride16record operandchain')
 selected={hex(o):[a-pc for a in path(pc,pc+o)+path(pc+o,pc+0x54)[1:]] for o in (0x3a,0x5e,0x13a,0x1a6,0x1c6,0x3b0,0x488,0x4d2,0x4fe,0x54e,0x582,0x616,0x632,0x64a)}
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),selected_syntactic_walks=selected,cyclic_SCC_offsets=cycles,N_memory_definition=nd,cached_TX_store_definition=dd,indirect_source_definitions=indirect,
  local_scratch_explicit_initialized_offsets=[13,14,15],SP12_explicit_local_store=False,actual_input_feasibility_initialization_provider_preservation_or_progress_proved=False)


def domains():
 for i in range(256):check(16*i+16<=4096,'recordCB byteindex stride16 geometry')
 for count in range(256):check(count<=255 and count+1<=256,'recordCB capturedbytecount finite sameaddressloop rank')
 for length in range(256):
  for header in range(256):
   out=(length+(header&63)+1)&255;check(out==(length+(header%64)+1)%256,'recordCB byte lengthpublicationwrap')
 # Offset/length arithmetic for a single captured pointer, not memory simulation.
 fixed={(0,1),(1,1),(2,6),(8,6),*((o,1) for o in range(14,36))};covered=set().union(*(set(range(o,o+z)) for o,z in fixed))
 check(covered==set(range(36)),'recordCB matchingrecord union ofdirectstores/copy6 requests covers36bytes')
 max_timer=255*1250-40+255*255*125;check(max_timer==8446835,'recordCB selectedrecord scalarmaximum')
 check((2*(-40))&0xffffffff==0xffffffb0,'recordCB timer signedminimum canwrap no positivityguard')
 for old in range(65536):check((old+8)&65535==(old+8)%65536,'recordCB localN130 publicationmod16')
 return dict(index_byte_cases=256,sameaddress_zeroing_count_cases=256,header_length_scalar_cases=65536,N130_increment_cases=65536,
  matching_record_required_destination_extent=36,matching_N176_source_extent=29,selected_table_entry_extent=12,selected_indexed_table_extent_up_to=4096,
  generic_payload_source_length='capturedU8[selectedrecord+3] in0..255,sourcecapturedU32[record+8];actualsourcevalidity/init/extent unproved',
  generic_copy_destination='freshN76+3+freshU8[cachedbuffer+2],notautomaticallycachedbuffer',selected_record_timer_math='low32(2*(1250*U8[child6]-40+125*U8[child7]*U8[record1]));secondterm onlywhenrecord1nonzero',
  generic_copy_numeric_envelope_from_fresh_base=3+255+255,
  output_contiguity_pointer_equality_or_buffer_initialized_runtime_proved=False)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());pc=STARTS[index];raw=init.binding.take(data,pc,1618);check(sparse.captured(mem,pc,1618)==raw,'recordCB fullstrictHEX');b=body(raw,index);cert=certificates(b);n={d['pc']-pc:d for d in b['instructions']}
 # Complete upstream target fixes both publications of this callback literal.
 up=previous.STARTS[index];ur=init.binding.take(data,up,1000);check(sparse.captured(mem,up,1000)==ur,'recordCB reusedB120target strictHEX');ub=previous.body(ur,index);un={d['pc']-up:d for d in ub['instructions']}
 check(un[0x106]['imm']+un[0x110]['imm']==un[0x262]['imm']+un[0x266]['imm']==pc,'recordCB exactupstream callbackliteral')
 fields=previous.previous;origin=fields.origin;op=origin.STARTS[index][1];orr=init.binding.take(data,op,194);check(sparse.captured(mem,op,194)==orr,'recordCB creator strictHEX');ob=origin.body(orr,'creator',index);on={d['pc']-op:d for d in ob['instructions']}
 S=0x20003514+80*index;B=0x200033b8+80*index
 check(on[124]['imm']+on[128]['imm']==S and on[132]['imm']==32 and on[136]['imm']==76 and on[136]['rs2']==14,'recordCB conditionalS32->createdN76')
 check(n[4]['imm']+n[8]['imm']==S and n[0xc]['imm']==24 and n[0x24]['imm']==16 and n[0x2c]['op']=='blt' and n[0x2c]['rs2']==0,'recordCB capturedS24 bit15 gate')
 check(n[0x56]['imm']+n[0x5a]['imm']==n[0x56]['imm']+n[0x6e]['imm']==B and n[0x5e]['imm']==88 and n[0x5e]['rd']==8,'recordCB actualNfromB88 notincomingA0')
 irq=fields.previous.previous;ip=irq.STARTS[index];ir=init.binding.take(data,irq.SOURCES[index],260);check(sparse.captured(mem,irq.SOURCES[index],260)==ir,'recordCB reusedS24producer strictHEX');ib=irq.body(ir,index);inn={d['pc']-ip:d for d in ib['instructions']}
 check(inn[0xc]['imm']+0x20003000==S and inn[0x12]['imm']==24 and inn[0x12]['rs2']==12,'recordCB IRQstatus fullwordS24 source')
 hook=irq.hook;hs,delta,sh,ch=hook.DETAILS[index];hr=init.binding.take(data,hs,22);hc=init.binding.take(data,hs+22,48);check(sparse.captured(mem,hs,70)==hr+hc,'recordCB fullsetter/consumer strictHEX');setter=hook.body(hr,'setter',0x2000078a,delta,sh);consumer=hook.body(hc,'consumer',0x200007a0,delta,ch)
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);first=mapping['first_copy'];src=int(first['source'],16);dest=int(first['destination'],16);end=int(mapping['first_copy_end_exclusive'],16)
 check(src+0x2000078a-dest==hs and 0x200007d0<=end and n[0x34]['imm']+n[0x3a]['imm']==0x20003000+delta+4,'recordCB hookflagrearm exactslot/firstcopy')
 # Reuse whole copy helper, whose byte forward-copy contract is conditional on actual binding/access/overlap.
 copier=completion.leaves.copier;cp=0x20000332;cs=src+cp-dest;copyraw=init.binding.take(data,cs,58);check(sparse.captured(mem,cs,58)==copyraw,'recordCB copy fullstrictHEX');copy=copier.body(copyraw,'copy',cp,18,init.binding.COPY_HASH)
 check(n[0x13a]['rd']==9 and n[0x13a]['imm']==76 and n[0x1a2]['op']==n[0x1c2]['op']=='auipc','recordCB cachedTX load andcopy pair sites')
 check(n[0x19e]['imm']==2 and n[0x198]['imm']==6 and n[0x19a]['imm']==54 and n[0x1b8]['imm']==6 and n[0x1be]['imm']==8 and n[0x1ba]['imm']==4,'recordCB exact6byte copy requests')
 check(n[0x3a6]['imm']==8 and n[0x3aa]['imm']==3 and n[0x4c6]['rs2']==18 and n[0x4ca]['rs2']==23 and n[0x4c4]['imm']==76,'recordCB genericpayload capturedsource/bytecount/freshdestination')
 check(n[0x4be]['op']=='beq' and n[0x4be]['rs1']==23 and n[0x4be]['rs2']==0 and n[0x4be]['target']==pc+0x4d6,'recordCB nullsource skipscopy notlengtharithmetic')
 check(n[0x4ec]['imm']==n[0x4f6]['imm']==76 and n[0x4fe]['imm']==112 and n[0x4fe]['rs2']==14,'recordCB freshTXpointer toH112 notlength')
 check(n[0x4d8]['imm']==0 and n[0x500]['imm']==17 and n[0x502]['imm']==128,'recordCB generic mode0 andexplicitlength/configarguments')
 check(n[0x632]['op']=='jalr' and n[0x60e]['rd']==10 and n[0x60e]['imm']==8 and n[0x610]['rs1']==10,'recordCB gatedrelease capturespointer thenreloadstable/count')
 check(n[0x5e6]['imm']+n[0x5ec]['imm']==pc and n[0x538]['imm']+n[0x53c]['imm']==0x20001dd4 and n[0x550]['imm']==0,'recordCB separateprivate/self/null hookpublications')
 return dict(label=init.binding.PROFILES[index][0],body=b,CFG_certificates=cert,reused_B120_target=dict(start=up,bytes=1000,sha256=ub['sha256']),reused_creator=dict(start=op,bytes=194,sha256=ob['sha256']),reused_S24_producer=dict(start=ip,bytes=260,sha256=ib['sha256'],S24_store=inn[0x12]),reused_setter=setter,reused_consumer=consumer,reused_copy=copy,
  contract=['capturedU32[S24] bit15 gatesbody;clearbranch freshheldH108 nonzero ->hookflag=1 thenRET;setbranch N=freshB88,no Nnullguard,notincomingA0;child=freshN172;record=freshchild12+16*U8[child9]',
   'matchingrecord branch cachedTX=N76 andindependentN176source;copy6(TX2,N54),copy6(TX8,N176+4);explicitstores/copyrequests span0..35. LaterfreshN76writes require pointerequality/retention separately',
   'genericrecord branch source=U32[record8],length=U8[record3];header/optional5bytecopy, optionalpayloadcopy tofreshN76+3+freshU8[cachedTX2];nullsource skipscopy butlengtharithmetic stillusescapturedL;publishedbyteN17 wrapsmod256;freshN76 ->freshH112 pointerword thenRAM mode0 request',
   'contextfunction atG564/G644 iscapturedA5 for2e6/38a;clockslotG480/G560 freshlyloaded for578/580/5be;independentword-equalitypoll andH108poll no timeout/progress proof',
   'after optionalreleasecapturedU32[childtable+8],freshchildtable/count reloaded;bounded0..255 loop zeroes SAME capturedtable+8,countnotpointerstride. Private release ownership/validity stillopen',
   'scratchcall52d80/52e28 borrowsSP12;localstores onlySP13,14,15,SP12notexplicitlyinitialized. Unknowncallee extent/retention/content andframepreservation preventcompletepayload claim',
   'all returns restore64Bframe RA/S0..S8;callee/hardware/alias/IRQ/laterwriters mayaffectglobal/dynamicstate;no entryA0dereference orfixedscalarreply guarantee'],
  actual_installedbinding_pointerequality_inputextent_outputinit_transmission_delivery_or_full_lifetimes_proved=False)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-complete-record-callback-TX-writers-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),
  complete_phase_body_bytes=3236,complete_phase_body_instructions=1084,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,
  remaining=['private17d6/5c830/5d006 andrecordsourceproviders/actualbinding','scratchSP12origin andnotificationcallee/noescape contract','actualRXcontents/ingressbounds/TXpointerretention/providerdelivery/fullownershiplifetimes'])


def tests(carriers):
 mutations=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],1618);b=body(raw,i)
  for d in b['instructions']:
   o=d['pc']-STARTS[i];size=d['size'];bad=bytearray(raw);bad[o:o+size]=(int.from_bytes(bad[o:o+size],'little')^(4 if size==2 else 1<<20)).to_bytes(size,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('recordCB instructionmutation escaped')
   mutations+=1
  for o,_ in TYPED:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:body(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('recordCB typedmutation escaped')
   typed+=1
 check((mutations,typed)==(1084,182),'recordCB mutationcensus')
 print('PASS:1084 instruction/'+str(typed)+' typed-load mutations rejected;fullCFG/TXwrite/copy/source/scratch certificates')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes()
 check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity')
 check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,tail,z,digest in init.binding.PROFILES:
  data=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+tail+'.bin')).read_bytes()
  check(len(data)==z and sha256(data).hexdigest()==digest,'candidate identity '+label);carriers.append(data)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS]
 coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers)
 encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'recordCB exactledger replay')
 print('PASS:3236B/1084i complete recordcallbacks;strictHEX;TXsource/copy/pointerpublish joins;exactledger')
 print('PASS:NO target execution/emulation;RXextent/TXdelivery/completeinputinit/providers/lifetime UNPROVED')


if __name__=='__main__':main()
