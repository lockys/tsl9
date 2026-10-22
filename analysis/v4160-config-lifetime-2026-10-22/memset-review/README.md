# 候選 byte-fill 與設定建立的條件式區間證明

[English](readme.en.md)

兩份已保存官方候選的 slot40048 都指向 RAM2000039C，對應 Flash4064C／4060C。實讀的完整葉函式為46 bytes／14指令，兩版本相同。

先 READ32[4002420C]、WRITE32 zero、FENCE.I，再判斷 A0 是否零；非零才計算 low32(A0+A2)，並按 A2 是否非零進入byte loop。迴圈**先A0+=1、再SB A1,-1(A0)**，直到A0等於end，跳回MMIO還原／RET。null或zero-length也會進行MMIO先後步驟；正常非零填寫後A0是進位後的end，不能宣稱是libc原pointer回傳。

靜態欄位顯示無nestedcall，也沒有S／GP／SP／RA目的暫存器；唯一顯式dest bytes為傳入區間，另有固定MMIO word。這不證明實體RAM、MMIO或非同步效果正常。兩候選共6個有效原始operand反例均拒絕。

## 與原 App 的合併條件

在「設定分支已到達、slot48確為此參考leaf、App SP+16非零且64 bytes有效、不與MMIO或code alias、無非同步變更、記憶體／MMIO正常完成」等前提下：

1. 原19A38請求A0=App當下SP+16、A1=0、A2=64，填寫SP16..79，包含staCB欄位SP68..71。
2. 原308-byte本體在此後、19AEC前只剩一個nestedcall：19AB4→18F56。已封存的[MAC helper證據](../mac-review/README.md)只寫SP8..13，且不改SP／S0。
3. 所有後續明示SP-relative store均避開68..71；唯一非SP store為已審查的六次byte-copy至SP40..45。此為固定來源的operand與區間論證，沒有執行CPU狀態。
4. 因此可導出**條件成立時，進入BLE_LibInit呼叫的App設定+52為零**；不能把條件消去，也不能宣稱實機、之後的配置callback word或整個生命週期為零。

此推論不證明版本分支可到達；V1.40與原21-byte版本期望的差異仍保留。BLE_LibInit在copy之前的numeric200004BC呼叫、live S1與其餘unknown副作用，是下一個邊界。它可能改設定來源或暫存器，所以此處不能推導allocator不觀察A2。

```sh
# Metadata與區間推導；actual flags false
python3 -B check.py --project-root ROOT
# 明示原App及兩候選，重讀全部相關bytes及6個反例
python3 -B check.py --project-root ROOT --firmware FW --candidate-root REF
```

原App／SDK欄位沿用[已封存設定證據](../../v4160-allocator-callback-2026-10-22/config-review/README.md)。未執行／模擬RV32、存取硬體、安裝工具、呼叫廠商API或產生BIN。Default metadata不能冒稱原機執行結果。
