# V4.1.60 0x8248 range transition: value/event candidate

離線、獨立候選；來源基準 main `d6e2391030eee86cc73426c206c47c7750e00c57`，不是對目前工作樹或既有文件的修改。參考映像 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長 76800，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，線性基址 0x8000。

靜態反組譯完整窗口 `[0x8248,0x828c)`：0x8248 讀 byte；0x824c、0x8250 是 **unsigned** `bltu`，所以兩端 inclusive，並非 signed 比較；輸入均為完整 32-bit 位元模式，範圍倒轉時不可能命中。範圍外且 byte 非零時寫 0；範圍內且 byte 為 0 時先寫 1，再呼叫 0xd052；其返回後 a0 完整 32 位等於 4 才 tail jump 0x167a6，參數為保存的輸入 a4。其餘情況不寫、不呼叫。原有非零 byte 在範圍內保持原值，不正規化。

`candidate.c` 回傳的是獨立分析結果，不是目標 helper 的返回值或 ABI。進入呼叫路徑時，本模型只描述 `0xd052` 已正常返回後的條件式事件摘要，不能用來觀察不返回時「已 store、已呼叫」的前綴。store 表示呼叫前的動作，不保證呼叫後記憶體仍為該值。外部呼叫可能有任意未建模副作用；`d052_result` 是以該呼叫確實返回為條件的獨立輸入，不假設其值；tail event 只描述發生與參數，不假設其返回或寄存器。堆疊、故障、別名、並行、呼叫效果及確切 ABI 不在模型內。

## 驗證與限制

```
python -I -S -B experiments/v4160-8248-range-transition-candidate/verify.py
python -I -S -B -O experiments/v4160-8248-range-transition-candidate/verify.py
```

驗證器固定映像全檔 SHA、長度、目標完整精確 bytes 和 C SHA，拒絕映像、窗口、截斷及 C 變異；Python 比較兩個獨立表述，枚舉全部 256 byte 與比較所需的所有弱序關係，跨越符號邊界及 32-bit 極值，並覆蓋 callee 結果等於 4 與不等於 4。其他寄存器值按比較等價類歸納，並非暴力枚舉 2^96 三元組。參數只在 tail event 傳遞。另有針對 Python 抽象事件的 signed 比較、old 遮罩、參數截斷、事件次序及返回值負例；這些不是 C 實作的語義變異測試。檢查使用顯式例外，在 `-O` 下仍有效。

**C 未編譯、未執行**；Python 模型測試不執行或解析 C，因此 SHA 僅固定供人工審閱的候選，不證明 C 語義一致。未執行 target、ISA simulator、compiler、硬體或網路；沒有修改任何既有檔案或配置。驗證不證明韌體動態行為。
