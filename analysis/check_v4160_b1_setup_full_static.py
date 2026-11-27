"""Offline complete setup original body: length adjustment, copy requests and return.
Original operands/immutable CFG/frame/def-use and closed host scalar identities.
No target execution/emulation, mutable buffer/IRQ/provider model or hardware.
"""
import argparse,json,sys
from collections import deque
from pathlib import Path
from hashlib import sha256
sys.setrecursionlimit(max(sys.getrecursionlimit(),3000))
import check_v4160_b1_setup_options_static as previous
init,sparse,check,decode=previous.init,previous.sparse,previous.check,previous.decode
FIELDS,BRANCHES=previous.FIELDS,previous.BRANCHES
OUT=Path(__file__).with_name('v4160-b1-setup-full-static.json')
STARTS=(0x5d006,0x5d14e)
SIZE=1470
COUNT=467
HASHES=('15b74855cb82a508fafe78a714b3be6b28f9eba22a3f2f4aaf9e99656dd4a666', '9b36cbc6d8bf1cf7f60923fdbdde4e2439cef62693bd5e37fc01caf39410e9e4')
LITERALS="""
000 addi 2 2 -80
002 store 2 9 68 4
004 lui 9 536883200
008 store 2 18 64 4
00a load 13 9 1340 4
00e lui 18 536883200
012 load 12 18 1288 4
016 store 2 1 76 4
018 store 2 19 60 4
01a store 2 20 56 4
01c store 2 21 52 4
01e store 2 24 40 4
020 store 2 8 72 4
022 store 2 22 48 4
024 store 2 23 44 4
026 store 2 25 36 4
028 store 2 26 32 4
02a store 2 27 28 4
02c addi 14 0 160
030 store 13 14 100 4
032 load 14 12 44 4
034 lui 19 536883200
038 mv 24 10
03a andi 14 14 -4
03c ori 14 14 1
040 store 12 14 44 4
042 load 14 12 0 4
044 lui 10 3342336
048 lui 20 536883200
04c andi 14 14 -385
050 store 12 14 0 4
052 load 14 12 0 4
054 andi 14 14 -385
058 ori 14 14 256
05c store 12 14 0 4
05e load 14 19 1424 4
062 load 11 14 8 4
064 or 11 11 10
066 store 14 11 8 4
068 addi 11 0 90
06c store 13 11 80 4
06e load 11 14 44 4
070 li 10 1
072 andi 11 11 -3
074 store 14 11 44 4
076 load 14 24 126 1
07a andi 11 14 127
07e load 14 12 0 4
080 andi 14 14 -128
084 or 14 14 11
086 store 12 14 0 4
088 load 14 13 4 4
08a lui 11 2181038080
08e addi 11 11 -1
090 andi 14 14 -2
092 store 13 14 4 4
094 load 14 24 104 1
098 andi 14 14 63
09c slli 13 14 25
0a0 load 14 12 44 4
0a2 and 14 14 11
0a4 or 14 14 13
0a6 store 12 14 44 4
0a8 load 14 24 140 4
0ac addi 11 0 35
0b0 store 12 14 8 4
0b2 load 14 24 144 4
0b6 store 12 14 4 4
0b8 addi 14 20 1300
0bc store 14 0 3 1
0c0 jal 1 278122
0c4 load 21 24 76 4
0c8 li 14 7
0ca store 24 14 16 1
0ce store 24 10 126 1
0d2 store 21 14 0 1
0d6 li 14 1
0d8 store 21 0 3 1
0dc store 21 14 2 1
0e0 load 14 24 84 4
0e4 addi 20 20 1300
0e8 andi 14 14 512
0ec beqz 14 290
0ee li 14 4
0f0 store 21 14 3 1
0f4 load 14 24 182 1
0f8 load 12 24 181 1
0fc load 13 24 76 4
100 slli 14 14 6
102 or 14 14 12
104 store 13 14 4 1
106 load 14 21 2 1
10a li 13 0
10c addi 14 14 1
10e store 21 14 2 1
112 load 12 24 184 1
116 load 11 24 181 1
11a load 10 24 182 1
11e jal 1 408938
122 load 14 24 84 4
126 andi 14 14 1024
12a beqz 14 366
12c load 13 21 3 1
130 load 14 24 76 4
134 load 12 21 2 1
138 ori 13 13 8
13c store 21 13 3 1
140 load 13 24 138 2
144 add 14 14 12
146 store 14 13 3 1
148 load 14 21 2 1
14c load 13 24 76 4
150 load 12 24 127 1
154 add 13 13 14
156 load 14 24 138 2
15a slli 12 12 4
15c srli 14 14 8
15e andi 14 14 15
160 or 14 14 12
162 store 13 14 4 1
164 load 14 21 2 1
168 addi 14 14 2
16a store 21 14 2 1
16e load 11 21 2 1
172 load 13 24 132 2
176 addi 14 0 253
17a lui 8 536883200
17e sub 14 14 11
180 addi 8 8 952
184 bge 14 13 918
188 load 13 24 128 1
18c li 14 2
18e beq 13 14 910
192 li 12 1
194 addi 14 0 1064
198 beq 13 12 418
19c lui 14 4096
19e addi 14 14 -1976
1a2 li 13 30
1a4 addi 14 14 439
1a8 div 14 14 13
1ac load 12 8 124 1
1b0 lui 10 4096
1b2 ori 12 12 16
1b6 store 8 12 124 1
1ba load 12 9 1340 4
1be store 12 10 8 4
1c0 mul 13 14 13
1c4 slli 13 13 1
1c6 store 12 13 96 4
1c8 load 12 21 3 1
1cc ori 12 12 16
1d0 store 21 12 3 1
1d4 load 13 24 76 4
1d8 load 12 24 126 1
1dc add 13 13 11
1de store 13 12 3 1
1e0 load 12 21 2 1
1e4 load 13 24 76 4
1e8 add 13 13 12
1ea store 13 14 4 1
1ec load 13 21 2 1
1f0 load 12 24 76 4
1f4 srai 14 14 8
1f6 add 12 12 13
1f8 load 13 24 128 1
1fc slli 13 13 5
1fe or 14 14 13
200 store 12 14 5 1
202 load 14 21 2 1
206 addi 14 14 3
208 store 21 14 2 1
20c load 14 24 96 1
210 andi 14 14 64
214 beqz 14 572
216 load 13 21 3 1
21a load 14 24 76 4
21e load 12 21 2 1
222 ori 13 13 64
226 store 21 13 3 1
22a load 13 24 21 1
22e add 14 14 12
230 store 14 13 3 1
232 load 14 21 2 1
236 addi 14 14 1
238 store 21 14 2 1
23c load 14 24 124 1
240 li 13 1
242 addi 14 14 -16
244 andi 14 14 255
248 bltu 13 14 692
24c load 22 21 2 1
250 lui 11 536883200
254 li 12 5
256 addi 14 22 3
25a load 22 24 76 4
25e addi 11 11 1214
262 add 22 22 14
264 li 14 8
266 store 22 14 0 1
26a addi 14 0 40
26e store 22 14 1 1
272 addi 10 22 2
276 auipc 1 536489984
27a jalr 1 1 182
27e load 13 24 124 1
282 li 14 16
284 bne 13 14 932
288 load 14 24 136 2
28c addi 14 14 8
28e store 24 14 130 2
292 li 14 17
294 store 24 14 124 1
298 load 14 24 130 1
29c store 22 14 7 1
2a0 load 14 24 130 2
2a4 srli 14 14 8
2a6 store 22 14 8 1
2aa load 14 21 2 1
2ae addi 14 14 9
2b0 store 21 14 2 1
2b4 load 12 24 132 2
2b8 li 22 0
2ba beqz 12 768
2bc load 13 21 2 1
2c0 load 10 24 76 4
2c4 load 11 24 168 4
2c8 addi 14 13 3
2cc add 10 10 14
2ce load 14 21 3 1
2d2 andi 14 14 16
2d4 beqz 14 952
2d6 li 22 -2
2d8 sub 22 22 13
2dc andi 22 22 255
2e0 mv 12 22
2e2 auipc 1 536489984
2e6 jalr 1 1 74
2ea load 14 24 168 4
2ee add 14 14 22
2f0 store 24 14 120 4
2f4 load 14 24 132 2
2f8 sub 14 14 22
2fc store 24 14 114 2
300 load 13 21 2 1
304 lui 10 348160
308 li 11 0
30a andi 14 13 63
30e addi 14 14 1
310 add 22 22 14
312 andi 22 22 255
316 store 24 22 17 1
31a store 21 13 2 1
31e load 14 24 76 4
322 addi 10 10 1152
326 lui 23 4096
328 store 14 22 1 1
32c addi 14 0 -105
330 load 13 24 76 4
334 store 24 14 11 1
338 load 14 9 1340 4
33c lui 21 16384
33e addi 26 0 90
342 store 14 13 112 4
344 jal 1 277288
348 load 12 24 17 1
34c load 11 24 128 1
350 li 10 0
352 li 22 7
354 auipc 1 536498176
358 jalr 1 1 864
35c addi 21 21 656
360 jal 1 409176
364 addi 27 23 -1976
368 load 14 8 124 1
36c andi 14 14 16
36e bnez 14 966
370 load 1 2 76 4
372 load 8 2 72 4
374 load 9 2 68 4
376 load 18 2 64 4
378 load 19 2 60 4
37a load 20 2 56 4
37c load 21 2 52 4
37e load 22 2 48 4
380 load 23 2 44 4
382 load 24 2 40 4
384 load 25 2 36 4
386 load 26 2 32 4
388 load 27 2 28 4
38a addi 2 2 80
38c jr 1
38e lui 14 16384
390 addi 14 14 656
394 jump 418
396 load 14 8 124 1
39a andi 14 14 239
39e store 8 14 124 1
3a2 jump 524
3a4 load 13 24 136 2
3a8 load 14 24 130 2
3ac sub 14 14 13
3ae li 13 2
3b0 blt 13 14 664
3b4 li 14 18
3b6 jump 660
3b8 auipc 1 536489984
3bc jalr 1 1 -140
3c0 load 22 24 132 1
3c4 jump 768
3c6 load 14 8 124 1
3ca andi 14 14 32
3ce beqz 14 966
3d0 load 14 8 124 1
3d4 load 11 9 1340 4
3d8 load 13 18 1288 4
3dc andi 14 14 207
3e0 store 8 14 124 1
3e4 addi 15 0 160
3e8 store 11 15 100 4
3ea load 14 13 44 4
3ec lui 15 3342336
3f0 andi 14 14 -4
3f2 ori 14 14 1
3f6 store 13 14 44 4
3f8 load 14 13 0 4
3fa andi 14 14 -385
3fe store 13 14 0 4
400 load 14 13 0 4
402 andi 14 14 -385
406 ori 14 14 256
40a store 13 14 0 4
40c load 14 19 1424 4
410 load 12 14 8 4
412 or 12 12 15
414 store 14 12 8 4
416 store 11 26 80 4
41a load 12 14 44 4
41c andi 12 12 -3
41e store 14 12 44 4
420 load 14 24 126 1
424 andi 12 14 127
428 load 14 13 0 4
42a andi 14 14 -128
42e or 14 14 12
430 store 13 14 0 4
432 load 25 24 76 4
436 store 24 22 16 1
43a li 13 1
43c store 25 22 0 1
440 store 25 0 3 1
444 store 25 13 2 1
448 load 13 24 84 4
44c andi 13 13 1024
450 beqz 13 1160
452 li 13 8
454 store 25 13 3 1
458 load 13 24 76 4
45c load 12 24 138 2
460 store 13 12 4 1
462 load 13 25 2 1
466 load 12 24 76 4
46a load 11 24 127 1
46e add 12 12 13
470 load 13 24 138 2
474 slli 11 11 4
476 srli 13 13 8
478 andi 13 13 15
47a or 13 13 11
47c store 12 13 4 1
47e load 13 25 2 1
482 addi 13 13 2
484 store 25 13 2 1
488 load 10 25 2 1
48c load 13 24 114 2
490 addi 12 0 254
494 sub 12 12 10
496 bge 12 13 1308
49a load 12 24 128 1
49e li 11 2
4a0 mv 13 21
4a2 beq 12 11 1202
4a6 li 11 1
4a8 addi 13 0 1064
4ac beq 12 11 1202
4b0 mv 13 27
4b2 addi 12 13 439
4b6 li 13 30
4b8 div 12 12 13
4bc load 11 8 124 1
4c0 ori 11 11 16
4c4 store 8 11 124 1
4c8 load 11 9 1340 4
4cc store 11 23 8 4
4d0 mul 13 12 13
4d4 slli 13 13 1
4d6 store 11 13 96 4
4d8 load 11 25 3 1
4dc ori 11 11 16
4e0 store 25 11 3 1
4e4 load 13 24 76 4
4e8 load 11 24 126 1
4ec add 13 13 10
4ee store 13 11 3 1
4f0 load 11 25 2 1
4f4 load 13 24 76 4
4f8 add 13 13 11
4fa store 13 12 4 1
4fc load 13 25 2 1
500 load 11 24 76 4
504 srai 12 12 8
506 add 11 11 13
508 load 13 24 128 1
50c slli 13 13 5
50e or 13 13 12
510 store 11 13 5 1
512 load 13 25 2 1
516 addi 13 13 3
518 store 25 13 2 1
51c load 12 24 114 2
520 li 13 0
522 beqz 12 1390
524 load 17 25 2 1
528 load 16 25 3 1
52c load 10 24 76 4
530 addi 13 17 3
534 andi 16 16 16
538 add 10 10 13
53a load 11 24 120 4
53e beq 16 0 1452
542 li 13 -2
544 sub 13 13 17
548 andi 13 13 255
54c mv 12 13
54e store 2 13 12 4
550 auipc 1 536489984
554 jalr 1 1 -548
558 load 12 24 120 4
55c load 13 2 12 4
55e add 12 12 13
560 store 24 12 120 4
564 load 12 24 114 2
568 sub 12 12 13
56a store 24 12 114 2
56e load 11 25 2 1
572 li 10 0
574 andi 12 11 63
578 addi 12 12 1
57a add 13 13 12
57c andi 13 13 255
580 store 24 13 17 1
584 store 25 11 2 1
588 load 14 24 76 4
58c store 14 13 1 1
58e load 12 24 17 1
592 load 11 24 128 1
596 addi 14 0 -105
59a store 24 14 11 1
59e store 20 0 3 1
5a2 auipc 1 536498176
5a6 jalr 1 1 274
5aa jump 872
5ac auipc 1 536489984
5b0 jalr 1 1 -640
5b4 load 13 24 114 1
5b8 store 24 0 114 2
5bc jump 1390
"""
PATCHES={10: ('load', [13, 9, 1420, 4]), 18: ('load', [12, 18, 1368, 4]), 94: ('load', [14, 19, 1504, 4]), 184: ('addi', [14, 20, 1380]), 192: ('jal', [1, 278262]), 228: ('addi', [20, 20, 1380]), 286: ('jal', [1, 409172]), 384: ('addi', [8, 8, 1032]), 442: ('load', [12, 9, 1420, 4]), 606: ('addi', [11, 11, 1294]), 634: ('jalr', [1, 1, -146]), 742: ('jalr', [1, 1, -254]), 802: ('addi', [10, 10, 1374]), 824: ('load', [14, 9, 1420, 4]), 836: ('jal', [1, 277428]), 856: ('jalr', [1, 1, 612]), 864: ('jal', [1, 409410]), 956: ('jalr', [1, 1, -468]), 980: ('load', [11, 9, 1420, 4]), 984: ('load', [13, 18, 1368, 4]), 1036: ('load', [14, 19, 1504, 4]), 1224: ('load', [11, 9, 1420, 4]), 1364: ('jalr', [1, 1, -876]), 1446: ('jalr', [1, 1, 22]), 1456: ('jalr', [1, 1, -968])}
TYPED=[(10, 2), (18, 2), (94, 2), (118, 4), (148, 4), (168, 2), (178, 2), (196, 2), (224, 2), (244, 4), (248, 4), (252, 2), (262, 4), (274, 4), (278, 4), (282, 4), (290, 2), (300, 4), (304, 2), (308, 4), (320, 5), (328, 4), (332, 2), (336, 4), (342, 5), (356, 4), (366, 4), (370, 5), (392, 4), (428, 4), (442, 2), (456, 4), (468, 2), (472, 4), (480, 4), (484, 2), (492, 4), (496, 2), (504, 4), (514, 4), (524, 4), (534, 4), (538, 2), (542, 4), (554, 4), (562, 4), (572, 4), (588, 4), (602, 2), (638, 4), (648, 5), (664, 4), (672, 5), (682, 4), (692, 5), (700, 4), (704, 2), (708, 2), (718, 4), (746, 2), (756, 5), (768, 4), (798, 2), (816, 2), (824, 2), (840, 4), (844, 4), (872, 4), (918, 4), (932, 5), (936, 5), (960, 4), (966, 4), (976, 4), (980, 2), (984, 2), (1036, 2), (1056, 4), (1074, 2), (1096, 2), (1112, 2), (1116, 5), (1122, 4), (1126, 2), (1130, 4), (1136, 5), (1150, 4), (1160, 4), (1164, 5), (1178, 4), (1212, 4), (1224, 2), (1240, 4), (1252, 2), (1256, 4), (1264, 4), (1268, 2), (1276, 4), (1280, 2), (1288, 4), (1298, 4), (1308, 5), (1316, 4), (1320, 4), (1324, 2), (1338, 2), (1368, 2), (1380, 5), (1390, 4), (1416, 2), (1422, 4), (1426, 4), (1460, 4)]
QK=[(260, 'd8a2', 'qk.c.sb'), (326, '34b3', 'qk.c.sb'), (354, 'd8a2', 'qk.c.sb'), (478, 'b0b2', 'qk.c.sb'), (490, 'd8a2', 'qk.c.sb'), (512, '58b2', 'qk.c.sb'), (560, '34b3', 'qk.c.sb'), (1120, 'd0a2', 'qk.c.sb'), (1148, '54a2', 'qk.c.sb'), (1262, 'acb2', 'qk.c.sb'), (1274, 'd0a2', 'qk.c.sb'), (1296, 'd4b1', 'qk.c.sb'), (1420, '14b3', 'qk.c.sb')]
STORES=[(2, 2, 9, 68, 4), (8, 2, 18, 64, 4), (22, 2, 1, 76, 4), (24, 2, 19, 60, 4), (26, 2, 20, 56, 4), (28, 2, 21, 52, 4), (30, 2, 24, 40, 4), (32, 2, 8, 72, 4), (34, 2, 22, 48, 4), (36, 2, 23, 44, 4), (38, 2, 25, 36, 4), (40, 2, 26, 32, 4), (42, 2, 27, 28, 4), (48, 13, 14, 100, 4), (64, 12, 14, 44, 4), (80, 12, 14, 0, 4), (92, 12, 14, 0, 4), (102, 14, 11, 8, 4), (108, 13, 11, 80, 4), (116, 14, 11, 44, 4), (134, 12, 14, 0, 4), (146, 13, 14, 4, 4), (166, 12, 14, 44, 4), (176, 12, 14, 8, 4), (182, 12, 14, 4, 4), (188, 14, 0, 3, 1), (202, 24, 14, 16, 1), (206, 24, 10, 126, 1), (210, 21, 14, 0, 1), (216, 21, 0, 3, 1), (220, 21, 14, 2, 1), (240, 21, 14, 3, 1), (260, 13, 14, 4, 1), (270, 21, 14, 2, 1), (316, 21, 13, 3, 1), (326, 14, 13, 3, 1), (354, 13, 14, 4, 1), (362, 21, 14, 2, 1), (438, 8, 12, 124, 1), (446, 12, 10, 8, 4), (454, 12, 13, 96, 4), (464, 21, 12, 3, 1), (478, 13, 12, 3, 1), (490, 13, 14, 4, 1), (512, 12, 14, 5, 1), (520, 21, 14, 2, 1), (550, 21, 13, 3, 1), (560, 14, 13, 3, 1), (568, 21, 14, 2, 1), (614, 22, 14, 0, 1), (622, 22, 14, 1, 1), (654, 24, 14, 130, 2), (660, 24, 14, 124, 1), (668, 22, 14, 7, 1), (678, 22, 14, 8, 1), (688, 21, 14, 2, 1), (752, 24, 14, 120, 4), (764, 24, 14, 114, 2), (790, 24, 22, 17, 1), (794, 21, 13, 2, 1), (808, 14, 22, 1, 1), (820, 24, 14, 11, 1), (834, 14, 13, 112, 4), (926, 8, 14, 124, 1), (992, 8, 14, 124, 1), (1000, 11, 15, 100, 4), (1014, 13, 14, 44, 4), (1022, 13, 14, 0, 4), (1034, 13, 14, 0, 4), (1044, 14, 12, 8, 4), (1046, 11, 26, 80, 4), (1054, 14, 12, 44, 4), (1072, 13, 14, 0, 4), (1078, 24, 22, 16, 1), (1084, 25, 22, 0, 1), (1088, 25, 0, 3, 1), (1092, 25, 13, 2, 1), (1108, 25, 13, 3, 1), (1120, 13, 12, 4, 1), (1148, 12, 13, 4, 1), (1156, 25, 13, 2, 1), (1220, 8, 11, 124, 1), (1228, 11, 23, 8, 4), (1238, 11, 13, 96, 4), (1248, 25, 11, 3, 1), (1262, 13, 11, 3, 1), (1274, 13, 12, 4, 1), (1296, 11, 13, 5, 1), (1304, 25, 13, 2, 1), (1358, 2, 13, 12, 4), (1376, 24, 12, 120, 4), (1386, 24, 12, 114, 2), (1408, 24, 13, 17, 1), (1412, 25, 11, 2, 1), (1420, 14, 13, 1, 1), (1434, 24, 14, 11, 1), (1438, 20, 0, 3, 1), (1464, 24, 0, 114, 2)]


def guard(raw,index):
 pc=STARTS[index];n=decode(raw,pc);spec={}
 for row in LITERALS.splitlines():
  if not row:continue
  off,op,*v=row.split();o=int(off,16);v=list(map(int,v))
  if index and o in PATCHES:op,v=PATCHES[o]
  check(len(v)==len(FIELDS[op]),'setupfull literalfields');f=dict(zip(FIELDS[op],v));f['op']=op
  if op in BRANCHES|{'jump'}:f['target']+=pc
  spec[pc+o]=f
 check(n.keys()==spec.keys(),'setupfull completeboundaries')
 for a,f in spec.items():init.g(n,a,'setupfull '+hex(a-pc),**f)
 check((len(raw),len(n),sha256(raw).hexdigest())==(SIZE,COUNT,HASHES[index]),'setupfull completeidentity')
 for o,f3 in TYPED:check(int.from_bytes(raw[o:o+4],'little')&0x707f==(f3<<12|3),'setupfull typedload')
 for o,h,m in QK:check(raw[o:o+2].hex()==h and n[pc+o].get('mnemonic')==m,'setupfull QKexactwidth')
 return n


def body(raw,index):
 import check_v4160_callback_dispatch_static as graph
 pc=STARTS[index];n=guard(raw,index);e={};calls=[];rets=[]
 for a,d in n.items():
  op=d['op'];q=[a+d['size']]
  if op in BRANCHES:q.append(d['target'])
  elif op=='jump':q=[d['target']]
  elif op=='jr':check(d['rs1']==1,'setupfull ordinaryRET');q=[];rets.append(a-pc)
  elif op in ('jal','jalr'):
   check(d['rd']==1,'setupfull linkedcall');t=d.get('target')
   if op=='jalr':
    u=n[a-4];check(u['op']=='auipc' and u['rd']==d['rs1']==1,'setupfull PCpair');t=(a-4+u['imm']+d['imm'])&0xfffffffe
   calls.append(dict(offset=a-pc,target=t))
  check(op not in ('ecall','mret','csr','call_indirect') and all(z in n for z in q),'setupfull closedlocalCFG');e[a]=q
 targets=[(0xc0,0x43e6a+140*index),(0x11e,0x63d6a+234*index),(0x27a,0x20000332),(0x2e6,0x20000332),(0x344,0x43b28+140*index),(0x358,0x200026ba+76*index),(0x360,0x63e58+234*index),(0x3bc,0x20000332),(0x554,0x20000332),(0x5a6,0x200026ba+76*index),(0x5b0,0x20000332)]
 check(calls==[dict(offset=o,target=t) for o,t in targets] and rets==[0x38c],'setupfull exact11calls/soleRET')
 seen=set();todo=[pc]
 while todo:
  a=todo.pop()
  if a not in seen:seen.add(a);todo.extend(e[a])
 check(seen==set(n) and sum(map(len,e.values()))==485,'setupfull all467nodes/485edges')
 stores=[(a-pc,d['rs1'],d['rs2'],d['imm'],d['width']) for a,d in n.items() if d['op']=='store'];check(stores==STORES and len(stores)==98,'setupfull exact98stores')
 cycles=[sorted(a-pc for a in g) for g in graph.common.sccs(e) if len(g)>1 or g[0] in e[g[0]]]
 check(len(cycles)==1 and (len(cycles[0]),min(cycles[0]),max(cycles[0]))==(160,0x368,0x5bc),'setupfull cyclicSCCcensus')
 return dict(start=pc,bytes=len(raw),sha256=HASHES[index],instructions=list(n.values()),CFG=e,linked_calls=calls,returns=rets,stores=stores,cyclic_SCC_offsets=cycles,complete_normal_entry_body=True,complete_callee_semantics_or_physical_behaviour_proved=False)


def certificates(b):
 pc=b['start'];e=b['CFG'];n={d['pc']:d for d in b['instructions']};pred={a:[] for a in e}
 for a,qs in e.items():
  for z in qs:pred[z].append(a)
 def path(a,z):
  todo=deque([(a,[a])]);seen=set()
  while todo:
   a,p=todo.popleft()
   if a==z:return p
   if a not in seen:seen.add(a);todo.extend((v,p+[v]) for v in e[a])
  return None
 walks=[]
 for a,qs in e.items():
  for z in qs:
   p=path(pc,a)+[z]+path(z,pc+0x38c)[1:];check(all(v in e[u] for u,v in zip(p,p[1:])),'setupfull edgewitness');walks.append([a-pc for a in p])
 dom={a:({pc} if a==pc else set(e)) for a in e};changed=True
 while changed:
  changed=False
  for a in e:
   if a==pc:continue
   d={a}|set.intersection(*(dom[z] for z in pred[a]))
   if d!=dom[a]:dom[a]=d;changed=True
 def last_before(a,reg):
  todo=pred[a][:];seen=set();hits=set();entry=(a==pc)
  while todo:
   a=todo.pop();d=n[a]
   if d.get('rd')==reg or (reg==10 and d['op'] in ('jal','jalr')):hits.add(a-pc);continue
   if a==pc:entry=True
   if a not in seen:seen.add(a);todo.extend(pred[a])
  return hits,entry
 sp=[(a-pc,d['imm']) for a,d in n.items() if d.get('rd')==2];check(sp==[(0,-80),(0x38a,80)],'setupfull onlySPalloc/restore')
 saves={(d['rs2'],d['imm']) for d in n.values() if d['op']=='store' and d['rs1']==2 and d['imm']>=28};loads={(d['rd'],d['imm']) for d in n.values() if d['op']=='load' and d['rs1']==2 and d['imm']>=28}
 check(saves==loads and len(saves)==13 and {pc+o for o in range(0x370,0x38c,2)}<=dom[pc+0x38c],'setupfull all13saves/restores/dealloc dominateRET')
 for a,d in n.items():
  if d['op'] in ('load','store') and d['rs1']==2:check(pc in dom[a] and path(pc+0x38a,a) is None,'setupfull validlocalframephase')
  if d['op'] in ('load','store') and d['rs1']==24:check(last_before(a,24)==({0x38},False),'setupfull allP accesses usecapturedentryP')
  if d['op'] in ('load','store') and d['rs1']==21:check(last_before(a,21)==({0xc4},False),'setupfull firstQusesbeforeS5reassignment')
  if d['op'] in ('load','store') and d['rs1']==25:check(last_before(a,25)==({0x432},False),'setupfull secondQ independentcapture')
 check(pc+0x54e in dom[pc+0x55c] and n[pc+0x54e]['rs2']==13 and n[pc+0x55c]['rd']==13,'setupfull savedpartiallength SP12 beforecopy/reload')
 check(last_before(pc+0x38c,10)==({0x360,0x5a6},False),'setupfull RETforwardsopaque childreply notfixedsuccess')
 check(n[pc+0x3ce]['target']==pc+0x3c6 and n[pc+0x5aa]['target']==pc+0x368 and n[pc+0x36e]['target']==pc+0x3c6,'setupfull flagpoll/reassemblycycle')
 # Immutable liveness search: a copy scalar reply is never consumed as a byte
 # count before an explicit new A0 definition on these four payload paths.
 kills={}
 for o,expected in ((0x2e6,0x304),(0x3bc,0x304),(0x554,0x572),(0x5b0,0x572)):
  seen=set();todo=e[pc+o][:];hits=set();uses=[]
  while todo:
   a=todo.pop()
   if a in seen:continue
   seen.add(a);d=n[a]
   if d.get('rs1')==10 or d.get('rs2')==10 or d['op'] in ('jal','jalr'):uses.append(a-pc);continue
   if d.get('rd')==10:hits.add(a-pc);continue
   todo.extend(e[a])
  check(not uses and hits=={expected},'setupfull payloadcopyreply killedbeforeread/call');kills[hex(o)]=sorted(hits)
 selected=(0x188,0x27a,0x2e6,0x358,0x38c,0x38e,0x396,0x3a4,0x3bc,0x3c6,0x488,0x554,0x5a6,0x5b0)
 return dict(all_edge_witness_count=len(walks),all_edge_witness_sha256=sha256(json.dumps(walks,separators=(',',':')).encode()).hexdigest(),selected_syntactic_entry_RET_walks={hex(o):[a-pc for a in path(pc,pc+o)+path(pc+o,pc+0x38c)[1:]] for o in selected},frame_bytes=80,paired_saved_register_offsets=sorted(saves),normal_RET_A0_reaching_calls=[0x360,0x5a6],payloadcopy_A0_kill_offsets=kills,own_frame_restored_on_encoded_normal_RET=True,callee_saved_register_frame_preservation_and_nonaliasing_required=True,finite_witnesses_do_not_prove_poll_exit_actualpathfeasibility_or_target_execution=True)


def selected_contracts(b,index):
 pc=b['start'];n={d['pc']-pc:d for d in b['instructions']}
 check(n[0x184]['op']==n[0x496]['op']=='bge' and n[0x176]['imm']==253 and n[0x490]['imm']==254,'setupfull distinctsignedinitial/remaining gates')
 check(n[0x18e]['target']==pc+0x38e and n[0x38e]['imm']+n[0x390]['imm']==17040 and n[0x394]['target']==pc+0x1a2,'setupfull mode2 participatesincommonpack')
 check(n[0x194]['imm']==1064 and n[0x19c]['imm']+n[0x19e]['imm']==2120 and n[0x1a4]['imm']==439 and n[0x1a8]['op']=='div' and n[0x1a2]['imm']==30,'setupfull firstmodequotientconstants')
 check(n[0x4a0]['rs2']==21 and n[0x4a0]['rd']==13 and n[0x4b0]['op']=='mv' and n[0x4b0]['rs2']==27 and n[0x4b8]['op']=='div','setupfull secondpack usesretainedmodeconstants')
 check(n[0x33c]['imm']==0x4000 and n[0x35c]['imm']==656 and n[0x364]['imm']==-1976 and n[0x326]['imm']==4096,'setupfull S5/S11 areconstants onsecondphase')
 check(n[0x23c]['imm']==124 and n[0x242]['imm']==-16 and n[0x244]['imm']==255 and n[0x248]['op']=='bltu','setupfull byte16/17 test')
 check(n[0x25e]['imm']==1214+80*index and n[0x254]['imm']==5 and n[0x272]['imm']==2,'setupfull fixed5byte copyrequest')
 check(n[0x288]['imm']==136 and n[0x28c]['imm']==8 and n[0x28e]['imm']==130 and n[0x292]['imm']==17 and n[0x3a4]['imm']==136 and n[0x3a8]['imm']==130 and n[0x3b0]['op']=='blt','setupfull independentlengthupdate paths')
 check(n[0x2b4]['imm']==132 and n[0x2c4]['imm']==168 and n[0x2d2]['imm']==16 and n[0x2d6]['imm']==-2 and n[0x2dc]['imm']==255 and n[0x3c0]['width']==1,'setupfull initialcopy U16 request/freshlow8 count')
 check(n[0x51c]['imm']==114 and n[0x53a]['imm']==120 and n[0x542]['imm']==-2 and n[0x548]['imm']==255 and n[0x5b4]['width']==1 and n[0x5b8]['rs2']==0 and n[0x5b8]['imm']==114,'setupfull remainingcopy source/low8/clear')
 for call,defs in ((0x358,(0x350,0x34c,0x348)),(0x5a6,(0x572,0x592,0x58e))):
  a0,a1,a2=defs;check(n[a0]['rd']==10 and n[a0]['imm']==0 and n[a1]['rd']==11 and n[a1]['imm']==128 and n[a2]['rd']==12 and n[a2]['imm']==17,'setupfull two dispatchrequests args')
 check(n[0x342]['op']=='store' and n[0x342]['imm']==112 and n[0x330]['imm']==76,'setupfull T112 publishesfreshP76 not payloadsource')
 check(n[0xd6]['imm']==1 and n[0xdc]['rs2']==14 and n[0xdc]['imm']==2 and n[0xd8]['rs2']==0 and n[0xd8]['imm']==3,'setupfull actualinitial Q2=1 Q3=0;prior prose count2 corrected')
 return dict(first_length_gate='signed(253-freshU8Q2)>=freshU16P132',second_length_gate='signed(254-freshU8Qprime2)>=freshU16P114',mode_table={'1':dict(base=1064,q=50),'2':dict(base=17040,q=582),'other':dict(base=2120,q=85)},mode2_is_not_pack_bypass=True,
  initial_payload_copy=dict(source='freshP168',destination='freshP76+freshQ2+3',bit4_set_length='low8(254-c)',bit4_clear_length='capturedU16P132',post_fullcopy_N='freshU8P132;not copy reply',post_partial_source='freshP168+heldN ->P120',post_partial_remaining='low16(freshP132-N) ->P114'),
  remaining_payload_copy=dict(source='freshP120',destination='freshP76+freshQprime2+3',bit4_set_length='low8(254-c)',bit4_clear_length='capturedU16P114',post_fullcopy_N='freshU8P114;thenSH0P114',post_partial_N_saved_SP12=True,post_partial_source='freshP120+heldN ->P120',post_partial_remaining='low16(freshP114-N) ->P114'),
  header_formula='low8(N+1+(freshcount&63)) ->P17 andfreshP76+1;dispatch A2 separatelyreloadsP17',pointer_publication='firstphase T112=freshP76 beforedispatch;not ownership transfer or actual TX proof',initial_Q2_correction=dict(encoded_initial_value=1,previous_options_prose_and_conditional_count2_family_superseded=True,stable_family='1+bit9+2*bit10;1..4 under field-stability/nonaliasing/normal-return premises'),opaque_calls=['43b28/43bb4','RAM200026ba/20002706','63e58/63f42'],physical_completion_capacity_actualcopyextent_and_no_retention_proved=False)


def reused_copy(data,mem,index):
 import check_v4160_app_nv_callbacks_static as copies
 mapping=init.binding.profile(data,init.binding.PROFILES[index][0]);fc=mapping['first_copy'];src=int(fc['source'],16)+0x20000332-int(fc['destination'],16);raw=init.binding.take(data,src,58)
 check(sparse.captured(mem,src,58)==raw and 0x20000332+58<=int(mapping['first_copy_end_exclusive'],16),'setupfull completecopy firstcopy/strictHEX')
 b=copies.body(raw,'copy',0x20000332,18,init.binding.COPY_HASH);check(b['encoded_GPR_writes']==[13,14,15,16],'setupfull matchingcopy noA0/SP/RA/Sdefs')
 return dict(start=0x20000332,source=src,bytes=58,sha256=b['sha256'],local_frame_and_nested_calls=False,normal_A0='unchanged entry destination',null_src_or_dst_or_zero_length_skips_byte_loop=True,caller_updates_not_proof_of_copied_bytes=True,forward_byte_loop_not_memmove_or_valid_extent_proof=True,physical_controlword_FENCEI_or_completion_not_proved=True)


def profile(data,hexraw,index):
 _,mem=sparse.inspect(hexraw,sparse.parser());raw=init.binding.take(data,STARTS[index],SIZE);check(sparse.captured(mem,STARTS[index],SIZE)==raw,'setupfull entire1470B strictHEX');b=body(raw,index)
 # The first392B are already frozen by the two published prefix checkpoints.
 old=previous.previous.prefix(raw[:238],index);opt=previous.body(raw[238:392],'options',index)
 check(old['start']==b['start'] and opt['start']==b['start']+238,'setupfull exactold/newprefixjoin')
 return dict(label=init.binding.PROFILES[index][0],body=b,certificates=certificates(b),selected_contracts=selected_contracts(b,index),reused_copy=reused_copy(data,mem,index),reused_entry_prefix_sha256=old['sha256'],reused_options_sha256=opt['sha256'],new_tail_bytes=1078,actual_provider_buffer_identity_aliases_IRQprogress_and_complete_lifetimes_proved=False)


def domains():
 mode_cases=0
 for bit9 in (0,1):
  for bit10 in (0,1):check(1<=1+bit9+2*bit10<=4,'setupfull corrected conditional initialcount family')
 for mode in range(256):
  base=1064 if mode==1 else 17040 if mode==2 else 2120;q=(base+439)//30
  check(q==({1:50,2:582}.get(mode,85)) and 60*q in (3000,34920,5100),'setupfull positive signedDIV quotient')
  for freshmode in range(256):check(((q>>8)|(freshmode<<5))&255==(freshmode%8)*32+(2 if mode==2 else 0),'setupfull pack usesseparatemodebyte');mode_cases+=1
 for count in range(256):
  N=(-2-count)&255;check(N==(254-count)%256 and (N==0)==(count==254),'setupfull unsignedpartialcount')
  for increment in (1,3,9):check((count+increment)&255==(count+increment)%256,'setupfull bytecountincrements')
 for length in range(65536):
  check((length+8)&65535==(length+8)%65536,'setupfull P130low16sum')
  for count in (1,2,3,4):check((253-count>=length)==(length+count<=253),'setupfull corrected stablecount firstgate family')
  for N in (0,1,2,3,127,254,255):check((length-N)&65535==(length-N)%65536,'setupfull U16remaining subtraction')
 for value in range(256):check(((value-16)&255)<=1 if value in (16,17) else ((value-16)&255)>1,'setupfull exact16/17bytepredicate')
 return dict(mode_and_freshmode_scalar_pairs=mode_cases,mode_quotients=[50,582,85],corrected_stable_initial_counts=[1,2,3,4],corrected_firstgate_U16_family_cases=65536*4,partialcount_cases=256,remaining_U16_family_cases=65536*7,all_byte16_17_predicate_cases=256,source_length_or_index_stability_capacity_and_runtime_reachability_proved=False,closed_host_scalar_identities_only=True,no_target_buffers_or_packet_objects_constructed=True)


def derive(image,carriers,header,coverage,hexes):
 previous.derive(image,carriers,header,coverage,hexes)
 return dict(schema='TSL9-B1-complete-setup-original-CFG-frame-length-copy-static-v1',APP_sha256=sha256(image).hexdigest(),profiles=[profile(d,h,i) for i,(d,h) in enumerate(zip(carriers,hexes))],domains=domains(),complete_body_validation_bytes=2940,complete_body_validation_instructions=934,previously_guarded_prefix_bytes=784,previously_guarded_prefix_instructions=260,newly_guarded_tail_bytes=2156,newly_guarded_tail_instructions=674,C_reconstruction_coverage_changed=False,target_execution_or_emulation=False,hardware_accessed=False,network_analysis=False,remaining=['43b28/63e58/RAM200026ba callees and actual preservation/sideeffects','buffer/source allocation and actual copy sizes/nonaliasing','physical IRQ/flag progress/installed providers','fullpointerownership/consumption-release lifetime beyond local return'])


def tests(carriers):
 mutated=typed=0
 for i,data in enumerate(carriers):
  raw=init.binding.take(data,STARTS[i],SIZE);n=guard(raw,i)
  for d in n.values():
   o=d['pc']-STARTS[i];z=d['size'];bad=bytearray(raw);bad[o:o+z]=(int.from_bytes(bad[o:o+z],'little')^(4 if z==2 else 1<<20)).to_bytes(z,'little')
   try:guard(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('setupfull instructionmutation escaped')
   mutated+=1
  for o,_ in TYPED:
   bad=bytearray(raw);bad[o:o+4]=(int.from_bytes(bad[o:o+4],'little')^(1<<14)).to_bytes(4,'little')
   try:guard(bad,i)
   except RuntimeError:pass
   else:raise RuntimeError('setupfull typedmutation escaped')
   typed+=1
 check((mutated,typed)==(934,226),'setupfull mutationcensus')
 print('PASS:934 instruction/226 typed-load mutations rejected;complete setup originalbody')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 image=init.binding.APP.read_bytes();header=init.core.outer.HEADER.read_bytes();check(len(image)==76800 and sha256(image).hexdigest()==init.binding.APP_HASH,'APP identity');check(len(header)==243435 and sha256(header).hexdigest()==init.core.outer.HEADER_HASH,'SDK identity')
 carriers=[]
 for label,folder,last,z,digest in init.binding.PROFILES:
  raw=(sparse.CANDIDATES/folder/('REFERENCE-CANDIDATE-ONLY-00040000-'+last+'.bin')).read_bytes();check(len(raw)==z and sha256(raw).hexdigest()==digest,'candidateidentity '+label);carriers.append(raw)
 hexes=[(sparse.CANDIDATES/d[0]/'wchble_rom.hex').read_bytes() for d in sparse.DETAILS];coverage=sparse.derive(image,carriers,header,hexes,sparse.parser());ledger=derive(image,carriers,header,coverage,hexes)
 ledger['sources'],ledger['official_Xwchc_vectors']=init.timer.source_contract();tests(carriers);encoded=(json.dumps(ledger,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 if args.write:
  with OUT.open('xb') as f:f.write(encoded)
 else:check(OUT.read_bytes()==encoded,'setupfull exactledger replay')
 print('PASS:2940B/934i fullsetup;2156B/674i newlyguarded;strictHEX/485edges/frame80/copyrequests/soleRET;exactledger')
 print('PASS:NO target execution/emulation;polltermination/actualcapacity/binding/physicaleffects/fullownership UNPROVED')


if __name__=='__main__':main()
