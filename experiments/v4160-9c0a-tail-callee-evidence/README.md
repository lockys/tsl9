# V4.1.60：0x9c0a 包裝函數的靜態證據

## 範圍與方法

唯一映像為 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長 76800 bytes、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，以 0x8000 映射；地址不是檔案 offset。這是本機檔案身分釘選，不證明來源。只分析正常從 0x9c0a 進入的指令，不分析其他入口、中斷或例外處理。採用 indexed r2 `C:\Users\locky\Tools\radare2\bin\r2.exe`，唯讀指令：

```
r2.exe -q -n -a riscv -b 32 -m 0x8000 -c "e scr.color=0; pd 32 @ 0x9c0a" <上述映像>
```

連續視窗 `[0x9c0a,0x9c4a)` 64 bytes，SHA-256 `d30c3f9e7f6a4e4b13a2f845bf9f84c9a31afca152309a1607eb2589dd4245d5`。`verify.py` 釘完整映像及全部視窗 bytes，並從原始 little-endian 指令獨立解出五條 RV32 JAL 的 opcode、rd 與帶符號位移；其他指令的解讀依 r2，不是獨立完整反組譯或 CFG 證明。下列 callee 均未展開：**語意分析到首個未知呼叫即停止**；後續僅列指令與有條件的控制流，不假設它們必然執行。

## 正常入口控制流與實際取用

入口無條件順序執行：配置 32-byte stack frame；儲存 s0、s1、ra；`s1 = a0`，`sw a1,12(sp)`；s0 設為 136，`csrc 0x800,s0`；到達首個未知呼叫 `0x9c1e -> 0x18e98`。截至此處未直接解參照 a0、a1 或 a2：a0 的值複製至 s1，a1 的值寫入 stack，a2 未被本函數指令讀取或改寫；首個呼叫入口的 a0/a1/a2 仍為入口寄存器值。stack 寫入及 CSR 存取仍須有效且允許，CSR 效果依架構及特權環境而定。

若每次呼叫都以正常方式返回、保存暫存器及 stack frame 未遭破壞，後續本函數的順序（非 callee 內部 CFG）為：

| 呼叫位置 | 目標 | 呼叫前本函數明確設定 |
|---|---|---|
| 0x9c1e | 0x18e98 | a0/a1/a2 為入口值 |
| 0x9c26 | 0x18e90 | a0 = 49；a1/a2 未重新設定 |
| 0x9c2c | 0x18ec4 | a0 = s1，即保存的入口 a0；a1/a2 未重新設定 |
| 0x9c34 | 0x18ef2 | a0 = s1；a1 從 `12(sp)` **重新載入**；a2 未重新設定 |
| 0x9c38 | 0x18eb6 | 本函數未在前一呼叫後設定 a0/a1/a2 |

「未重新設定」不是保證保留入口值：未知 callee 可依 ABI 改寫 caller-saved a0/a1/a2，也可存取記憶體。尤其 `12(sp)` 實際在 0x9c30 重讀；若它被 callee、別名指標、其他執行環境或非預期寫入更改，傳給 0x18ef2 的 a1 是重讀值，不可無條件替換成入口 a1。入口 a0 若指向與 stack 或其他可寫區域重疊的位置，也不保證指向內容不變；本函數自身不解參照該指標，但 callee 的存取未知。s1 代表入口 a0 亦仰賴 callee 遵守保存暫存器慣例且保存區未受破壞。

所有五個呼叫正常返回後，`0x9c3c` 對 CSR 0x800 執行 `csrs` mask 136；這是設定位元，**不是**還原先前 CSR 值。然後從 stack 載入 ra/s0/s1、回收 frame，`0x9c48` ret；沒有本地條件分支。返回 a0 是最後 callee 返回後留下的值，本函數之後未改寫它；不推定其意義。正常返回還要求 stack 讀寫與 CSR 操作不 fault、已保存 ra/frame 完好及各 callee 正常返回；若任一 callee 不返回，後續呼叫、CSR 置位及 ret 都不會由此路徑執行。不能據此推斷 callee 必返回、其存取範圍、結果或裝置行為。

## 本地驗證

```
python -B experiments/v4160-9c0a-tail-callee-evidence/verify.py
python -B experiments/v4160-9c0a-tail-callee-evidence/test_verify.py
python -B -O experiments/v4160-9c0a-tail-callee-evidence/test_verify.py
```

測試逐一翻轉視窗每個 bit、檢查截斷與視窗外突變、JAL 正負位移與無效編碼；普通及 `-O` 均使用顯式例外，不依賴可被最佳化移除的 assert。只讀原映像，未編譯、執行或模擬目標，未使用網路、硬體或修改設定。
