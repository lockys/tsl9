# 初始化回呼內的清零與外設設定

接續[初始化複製後的直接寫入](v4160-clock-hook-after-init-copy.zh-TW.md)。名義 frame SP=`0x2000fed0` 時，`0x19814 → 0x8520` 以對齊位址 `0x2000fef0`、值 0、長度 32 呼叫。原指令走兩輪，每輪四個 word store，精確寫 `[0x2000fef0,0x2000ff10)`；餘數為零，不進尾段。

`0x19896 → 0x1892e` 的 a1 是上述 32-byte 區塊，a0 是 s1=`0x40012400`。這次方向不同：從 a1+24/0/28/4/12/16/8 讀 word，從 +20 讀 byte；只寫 a0+4/+8/+44，沒有寫回 a1。以三個外設 word 各自的讀值 X 表示，三次寫入依序為 `X & 0xe0f0feff`、`(X & 0xfff1f7fd) | 0x000e0000`、`X & 0xff0fffff`。其中 frame+44 的 word 是 `0xe0000`，frame+52 的 byte 是 1；不能用全零設定代替。

這兩段都不直接寫校準回呼槽 `[0x2000321c,0x20003220)`。驗證器從固定 SHA 的 APP 取指，比對 8+3 次寫入的順序、寬度和值；使用三組合成外設初值。它跳過兩次呼叫之間的其他函式，假定其保持 SP、s1 與相應設定資料，並非連續執行或實機測試。重現：`python analysis/check_v4160_clock_hook_two_calls.py <decoded APP> <rasm2>`。
