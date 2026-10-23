# SPI 寫入與位元修改提供者

[English](readme.en.md)

以 C11／C++17 重建 `[0x168DE,0x16994)`：182 bytes、68條指令、20個私有架構分區。C 負責遮罩、常數與 volatile MMIO word store；架構埠保留實體暫存器、frame、slot及呼叫順序。這些分區不是一般 C ABI 函式。

## 已確認流程

- `0x168DE`：32B frame，保存 S0@24、S1@20、RA@28。依 selector bit0／bit1 分別寫16／1至 `0x40010814`；不做 RMW。以 A0=2呼叫已重建的 `0x16896`，重新讀 then-live SP+12 的 address，再呼叫相同底層；之後先測 S0!=S1，非零長度路徑才讀取 byte並在下一次呼叫前遞增 S0。零長度仍有兩次底層呼叫，沒有 payload 讀取；不宣稱實體資料一定送出。
- `0x1693E`：32B frame，保存 RA@28；相同 selector 操作後，以 A0=5呼叫底層，再依序從 then-live SP+4／+8／+12 新讀 address／mask／value並呼叫。參數保持32-bit，不自行截成byte，也不假設 A3 在底層呼叫後仍保留資料。
- 兩段結尾都先還原 RA，再無條件將17寫至 `0x40010810`；第一段的 S0 還原在該寫入前、S1還原在後。最後 A0 保留最後一次底層返回值，未轉為布林結果。selector=0也會做結尾寫入。

## 原生與連結驗證

`build/verified-v1/{c,cpp}/verification.json`：實際182B／68i、20FUNC、13pending RELA、1strong UND（真正的 SPI提供者）、0global ABS。所有非重定位位元符合原 BIN。每種語言133項負向檢查，包含68個指令、20個weak binding、13個addend、27個IR架構埠及5個scalar／SSA wiring變更；完整 ELF／IR雜湊檢查在負向檢查時關閉。另核對含SSA運算元的scalar／volatile-store清單、完整IR與實際MD／recipes／產物。

`build/nominal-v3/{c,cpp}/verification.json`：將既有 SPI72B C來源重新編譯，與新182B提供者連到原PC `[0x16896,0x16994)`；**254B／93i／28FUNC 全部程式位元組與原 BIN 相同，0UND／0RELA／0global ABS**。每種語言有4個實際編譯、IR、連結與讀取步驟，以及97個負向檢查（93個原始指令，另加入口、code權限、LLVM位址與LLVM位元組）；檢查原入口／AX權限、無可寫LOAD、唯一配置code section與file mapping，收據保留完整ELF metadata／LLVM欄位及逐命令輸入雜湊；遞迴snapshot包含實際重用的write native.o。既有 SPI及新提供者正式收據亦實際唯讀重播。這是局部診斷 ELF，不是完整韌體。

初次 nominal-v1 實際連結成功，但 checker 沿用舊MD檢查器的 `native.o` 目標名稱，與本輪 `spi.o` 不同。原checker保留在 `history/nominal.pre-md-fix.py`，改為驗證實際 spi.o目標與相同兩個include後，全新nominal-v2編譯及唯讀重播通過。獨立審閱另指出v2的entry／權限、LLVM欄位及重用輸入檢查尚可補強；原checker保留於history/nominal.pre-metadata-fix.py，原收據保留本機。全新v3編譯通過上述補強檢查，原C來源、旗標及機器碼未修改。strict firmware gate如預期回傳1。

從repo根目錄，指定已存在且雜湊相符的Windows LLVM（輸出目錄必須全新）：

```sh
python -B experiments/tsl9-spi-write-providers/verify.py --build --out-dir experiments/tsl9-spi-write-providers/build/local-native-v1 --llvm-bin "$LLVM_BIN"
python -B experiments/tsl9-spi-write-providers/nominal.py --build --out-dir experiments/tsl9-spi-write-providers/build/local-nominal-v1 --llvm-bin "$LLVM_BIN"
```

第二個腳本目前重播本機 `build/verified-v1` 與既有SPI `verified-v3` 證據，再進行新的nominal連結；它不會替缺少原始產物的新clone下載或捏造收據。既有1162B整合及246B標記候選保持原樣，尚未將本輪新提供者加入該整合。

## 推論與限制

快取 WCH header 的 GPIOA／SPI1位址與目前MMIO相符，但不是實體晶片、腳位用途或板件組成證明。`0x02／0x05` 與先前read `0x03`、三組控制位址提供外接CAN暫存器協定的研究線索，不能直接確認型號或數量。

SPI底層會將timeout與正常收到0都表示成 A0=0；可研究新增明確timeout／原始狀態診斷，但仍須追查read wrapper才能斷定上層影響，本輪未修改功能。**實體MMIO、非同步IRQ、整機啟動、ROM及OTA相容性未證實，未產出可刷寫BIN，也未完成逆向。** 本輪未執行目標、ISA模擬、主機模型或硬體I/O。
