# NV 寫入／計時器的獨立原生物件審查

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

這份審查支持新 C/C++ 寫入函式與計時器的「有條件正常存取／呼叫／A0 結果投影」。完整原始暫存器 ABI、故障／IRQ 等價、原位替換、Flash 寫入成功與硬體相容性均未證明。沒有執行原生函式、MMIO、ISA 模擬、舊 HOST 矩陣、連結或產生新韌體 BIN。

`source.py` 以保留的原始位元組重新解碼六段 294 bytes／115 條指令，並對實際 ID2966 韌體檔比對相同範圍。此獨立結果亦與另外封存的 source-review 相符。`check.py` 直接讀取實際 ELF、完整 LLVM 反組譯與 IR，沒有把 producer replay 當作判決。

| 實際全域函式 | bytes | 指令 |
| --- | ---: | ---: |
| status 18E90 | 8 | 3 |
| unlock 18E98 | 30 | 10 |
| lock 18EB6 | 14 | 6 |
| erase 18EC4 | 46 | 19 |
| program 18EF2 | 100 | 38 |
| 未選用的 quarter 9C0A | 64 | 23 |
| 新 timer 19764 | 60 | 23 |
| 新 write 197BE | 72 | 26 |

C 與 C++ 的八個真實定義合計皆為 394 bytes／148 條指令；八個配置區段完整解碼，UND 0、RELA 10、全域 ABS 0。五個 CALL_PLT 是新寫入函式的真實 C 呼叫；另五個 JAL 屬保留的 quarter。所有重定位均指向物件內真實定義，沒有 stub、ABS provider 或省略未選函式。來源／工具／Python／編譯器 stdint 資源均有雜湊；完整 `-MD` 閉包包含新 C/header、三個原 Flash 檔與 stdint。採單一普通第一輪 profile，沒有追逐旗標。

新寫入函式依序執行 unlock(destination)、erase(destination)、program(destination, source)、lock(program 的 A0)、timer(1)，最後 A0=0。第二個輸入未使用。原始 program 呼叫入口的 A2 也含來源指標；原 callee 在讀取 A2 前先定義 count=256，因此這個雙參數 C 表面只支持所述效果投影，不能稱為完整原始呼叫原型或入口狀態。program 仍交錯讀取 64 個新鮮來源 word、寫入目標 word 及輪詢。

原 write 使用 32-byte frame，來源保存在 entrySP-20，並在擦除後重新讀取；新 write 使用 16-byte frame，來源保存在 S0、目標保存在 S1，另保存並還原 RA/S0/S1。新 frame 在 entrySP-12 保存輸入 S1，未重現原來源槽；正常結果需要有效私有 frame、沒有不利別名／介入寫入且不觀察私有殘值。原函式先恢復 RA/S0 再清零 A0，新函式先清零 A0 再恢復，故障前綴不同。

timer 有 12 個最少新鮮 volatile 效果：STATUS+4 讀／清 bit0 寫、GP+382 byte 讀、CMP+16 乘積寫、CNT+20 零寫、CTRL+0 新鮮讀／OR16 寫、再新鮮讀／OR33 寫、STATUS+4 重複讀至 bit0 設定、CTRL+0 新鮮讀／清 bit0 寫。乘積為完整輸入與 byte 的低 32 bits。GP 是實際 `mv` 讀取，原 GP 不變；單位、物理延遲與終止沒有證明。

原 timer 保留 A0/A1，出口 A2=乘積、A3=0、A4=最終 CTRL&~1、A5=E000F000。新 timer 無 frame、只寫 A1/A2，仍保留 A0，但出口 A1=E000F000、A2=最終 CTRL&~1，A3/A4/A5 保持入口值。組合新 write 後 A3=8000、A4=40022000、A5=lock 最後的新鮮 CTRL|8000，A6=最後來源 word。這些確定差異使完整 ABI 維持 false。

保留的未選 quarter 的 ASM 宣告沒有列出本輪 ordinary unlock／erase 實際新增的 A1 寫入。檢查器機械核對這兩個缺口；此實際 quarter 在呼叫前保存來源，擦除後重新載入，中間沒有編碼 A1 讀取，因此未觀察到該有限機器路徑的反例。這不補足一般 ASM／編譯器契約，也不認證 quarter 的完整 ABI。舊來源沒有修改。

每語言各有 12 個實際反例：八個合法單欄位原始指令修改，涵蓋 STATUS／GP offset、OR33、輪詢目標、來源保存、固定 count、stride、呼叫 link register；四個 IR 修改涵蓋 program→lock A0、來源參數、timer(1) 與完整輸入乘積。全部拒絕。此範圍沒有新增 ROM slot 或 word-count shift，沒有虛造不適用的測試。

```sh
python3 check.py --project-root ROOT
python3 check.py --project-root ROOT --folder ROOT/experiments/tsl9-nv-write-callback/build/native-v1/c --receipt NEW.json
python3 check.py --project-root ROOT --replay NEW.json
python3 check.py --project-root ROOT --firmware ORIGINAL.bin
```

預設僅查 metadata／保留來源，沒有讀取 native 物件。`--folder` 直接審查實物並以 create-only 寫收據；`--replay` 唯讀重查該實物。原韌體模式也可指定新的 `--receipt`，不宣稱讀取其他映像。D／P 各 199 個現存外部依賴雜湊相符，來源／原生 reader context 可解析。另有兩個已明確核對為缺少的 canonical reader 別名：`analysis/function-hardware/fifty-fifth-round/independent-service-events-contract/elf_service_events.py` 與 `analysis/function-hardware/fifty-seventh-round/independent-provider-witness/audit_gp_elf.py`。Parent 將依 `delivery-dependencies.json` 的原檔雜湊補齊相同相對階層，保留舊檔、producer seal 與物件；本封存不宣稱別名已交付或 D／P 已完成新編譯。Python／POSIX sh 原始碼可攜，不代表已在其他作業系統執行。沒有重試先前被拒絕的 Git Bash，sh runtime 未驗證。

原始碼與實際物件僅支持明示的正常前提：所有存取正常完成、GP 與指標有效、輪詢有限終止、沒有非同步觀察／修改，且實際 provider 未被替換。`machine-findings.json` 記錄精確差異；原始封存與既有候選映像保持不動。
