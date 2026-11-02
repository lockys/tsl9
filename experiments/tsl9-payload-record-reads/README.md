# 新開放區段的 record 複製呼叫

[English](readme.en.md)

先前只對其他已選區段搜尋 `0x82A8` 的呼叫，新開放的 `0x14056..0x14C8A` 另有七處直接呼叫。依位置排序，其 record index 為 **1、11、5、6、7、3、4**；每處在呼叫前均設定 `a0=1`。因此這七處沒有直接以 index 14 呼叫。

原位址 `0x82A8..0x82CA` 在 `a0=1` 路徑，以 `0x2000C1B8+12*index` 作為來源、呼叫者的 `a2` 作為目的、長度 12，尾跳從 `0x4004C` 讀出的目標。若該 resident 槽確為順向複製、來源與 stack 目的均有效且不互相有害重疊，這七處是把 record 讀入 stack；不等於已證明實機槽身分、執行可達性或沒有其他 writer。

`python scripts/verify-payload-record-reads.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` 同時核對兩種來源產物的七個直接呼叫點、參數設定與 `0x82A8` 的關鍵指令，並重新建置候選 BIN。不執行韌體或硬體；間接呼叫、其他寫入方式及實機干擾仍未排除。
