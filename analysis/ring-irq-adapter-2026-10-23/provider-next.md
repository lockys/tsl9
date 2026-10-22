# 下一個 provider：0x18D78

[English](provider-next.en.md) · [逐指令證據](provider-decode.json)

官方 ID2966 `[0x18D78,0x18E1C)` 為 164B／53 指令，SHA256 `678a3cbf42bc02d5c730973675858a18e538af9fdc1cb74dd9296f220f487ae3`。這是 bounded RV32 靜態解碼，尚未重建成可讀 C；舊 `callee_native.c` 的 `.4byte` 封存不等於可讀 C 或 ABI 證明。

這個範圍內沒有 call、SP 寫入或 RA 寫入，只有兩個 RET；可支持這個入口的局部 SP／RA 保存判斷。它不證明完整 interrupt context、其他入口、實體 MMIO 或晶片型號。

可直接由指令確認的資料流：

- A5 = A0 + (A1 << 4)。所有下述讀取都是各自 fresh LW32，不可合併或快取。
- `[A5+432] & 4` 寫 output+8。為零時再次讀 word，右移21後 SW 到 output+0；非零時再次讀 word，右移3後 SW 到 output+4，再接回共用路徑。
- 再讀 `[A5+432] & 2` 寫 output+9；`[A5+436] & 15` 寫 output+10，另一次讀右移8寫 output+19。
- `[A5+440]` 與 `[A5+444]` 每個 byte 都重新讀 word，再以 0／8／16／24 位移寫 output+11..18。最後一次讀入 A5，須保留原順序與暫存器覆寫。
- A1=0 時 fresh LW／OR32／SW 到 `[A0+12]`；否則操作 `[A0+16]`，之後 RET。寄存器及 bit5 的硬體用途尚未由實體／官方 register 文件證明。

IRQ adapter 的實際參數是 A0=`0x40006400`、A1=0、A2=SP+12，因此此 provider 的最後一筆 output+19 位於 SP+31，落在 adapter 自建的32B frame內。這項結論限於此 direct call 和所解碼路徑；ring 的動態 resident 呼叫仍未證。

值得追查的功能線索：output+10 僅 mask15，adapter 再讀 byte，沒有 ≤8 檢查；output+8 非零的路徑只寫 output+4，不寫 adapter 後續讀取的 output+0。這說明本地資料流存在長度／欄位有效性依賴，**不能直接宣稱實機有溢位、錯誤封包或支援特定延伸格式**。硬體設定、可達輸入、caller/provider 約定仍需確認。未新增 filter、clamp、layout 或硬體行為；未執行 MMIO 或裝置。

下一步以 C 的 volatile word讀取、位移與byte／word寫入重建，保留 fresh 次數、cold blocks 與兩個真正 RET，再以正式物件／原位連結證據接回 IRQ。不得拿原廠 raw bytes 當假 provider 來宣稱 C 重建完成。
