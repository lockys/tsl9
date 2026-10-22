# 輪詢輸入 byte 與時脈欄位的條件式關係

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

從原始 ID2966 重新核對 `0x1973C..0x19764` 的完整 40 bytes／11 列，以及 `0x19770` 的 4-byte unsigned byte load。後者是另一份 timer 來源審查範圍的子集，不應相加成全新 coverage。沿用已封存的標準欄位解析器及原始列，不重跑舊時脈查詢、HOST 或原生執行。

來源依序讀 live GP+108 的 word，做 unsigned 除以 8000000，再遮罩為 byte q；將 q 寫至 GP+382，然後將 q*1000 的低 16 bits 寫至 GP+380。byte 截斷在乘法之前，不能改用未截斷 quotient。timer 重新讀 live GP+382 的 unsigned byte，並使用其與完整輸入值相乘的低 32 bits。

只有在兩函式的 GP 相同，且相關 byte 沒有被其他程式、alias 或非同步事件改寫時，才能把 timer 的這次新讀取連到先前的 q。這裡沒有證明真實 frequency word、初始化呼叫的可達性與順序、所有中間呼叫的 GP 保存，或此 byte 的完整生命期；更沒有證明實際時脈與時間單位。

七個實際 raw bit 反例會分別改變 frequency word 偏移、DIVU／DIV、quotient 遮罩、byte 目的位址、乘數、halfword 寫入寬度與 timer byte 偏移，均須拒絕。保留的純算術例子可區分高位 unsigned 除法、byte 回繞與 32-bit 乘法回繞；它們不執行 CPU／ISA，也不是硬體量測。q 可以為零，但不能只憑此推論硬體會卡住或延遲多久。

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --firmware /original/ID2966.bin
```

預設 metadata，明示 firmware 才讀原始檔並重播反例。沒有網路、MMIO、native／CPU／ISA／ESIL、HOST 矩陣、硬體或 BIN 生成。可新增的離線診斷提案是列出校準值為零、回繞及生命期未證條件；不藉此更改原機輪詢或虛構逾時成功。shell runtime 尚未驗證，既有 Git Bash 拒絕沒有重試。
