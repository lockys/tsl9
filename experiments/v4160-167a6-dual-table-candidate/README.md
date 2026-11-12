# V4.1.60 0x167a6 second-loop candidate

基準 main `d6e2391030eee86cc73426c206c47c7750e00c57`，並非要求工作樹 HEAD 等於此 commit。固定 image `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 76800，base 0x8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

精確機器視窗 `[0x167de,0x16846)`：

```text
9d 4a 05 44 93 89 41 06 13 8a 81 06 13 09 40 02
03 a7 09 00 56 97 83 46 07 00 03 47 17 00 93 77
17 00 a2 07 d5 8f 63 98 97 00 09 8b 09 c7 a2 85
01 45 ef 10 a0 17 03 27 0a 00 56 97 83 46 07 00
03 47 17 00 93 77 17 00 a2 07 d5 8f 63 98 f4 00
09 8b 09 c7 a2 85 05 45 ef 10 40 15 05 04 13 74
f4 0f 9d 0a e3 16 24 fb
```

## 指令與抽象

0x167de–0x167ed 設 offset=7、index=1、slot addresses GP+100/104、limit=36。0x167ee 讀第一 slot，0x167f4/0x167f8 依序讀同一 pointer 的 low 和 high；0x167fc–0x16804 構成 `low | ((high & 1) << 8)` 並比較完整 event；0x16808 檢查**已讀取的** high bit 1，相符才在 0x16810 呼叫 0x1798a，參數 0、index。0x16814 才讀第二 slot，0x1681a/1e 依序讀 low/high，0x16822–30 同樣比對及檢查，0x16836 呼叫同目標，參數 1、index。0x1683a–45 index 加一並截為 byte、offset 加七，直到 index=36；因此索引 1..35，offset 7..245。第一 dispatch 可以修改第二 slot 或後續內容；不提前讀或共用 slot。每次 low、high 必讀一次，即使 key 不匹配；旗標不另外讀。函式其他部分不在範圍。

`candidate.c` SHA-256 `3ec9f2f2dee8313c9ef5e5f82f01ed21f6b5af8bcca33644407c0a06018c6419`；`candidate.h` SHA-256 `f4f27dd828de497eec73bdb2a0ed26ac0d37f165b903712d219d26c6270e3769`。

callbacks 是觀察介面而非實機呼叫：呼叫者須提供有效且執行期間不變的 ops/context、有效 snapshot 和定義明確的讀取；所有 callbacks 必須正常返回。允許 callback 改變 slots、資料；每次讀取回傳值即為該次快照。此模型不聲稱 ABI、C 與機器碼等價、並行安全或完整函式行為。

## 離線測試

```text
python -I -S -B experiments/v4160-167a6-dual-table-candidate/verify.py
python -I -S -B -O experiments/v4160-167a6-dual-table-candidate/verify.py
```

固定 image、精確視窗與 C/header 雜湊，逐 bit 窗口 mutation、截斷及 fixture/source mutation；Python 測試 field 位元、完整 event、所有讀取順序、slot 更換、dispatch 修改第二 slot、high 不重讀及邊界。這些是 Python 模型及靜態 pin 檢查；不編譯、執行或語義驗證 C，亦非指令模擬、target differential 或硬體證據。不使用 compiler、target、simulator、hardware、network 或設定。
