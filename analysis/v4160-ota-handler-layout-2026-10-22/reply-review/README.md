# 回覆指標的實際消費者

[English](readme.en.md)

原始S回覆的數值指標確實離開呼叫者；目前不能證明它只被當成兩個位元組的容器。這份離線審查不改C/C++、ABI橋、堆疊位置或韌體。

原9D92/9D96先寫當時SP+12/+13；UID呼叫之後，9DAC再以當時SP+12形成A2。13E98是28B包裝器：指標與長度都非零時，tail跳到90B的13B4C；否則tail跳到TX8A56。

13B4C在13B64把來源指標存到它自己的liveSP+12。13B68透過slot70呼叫配置函式時只將A0改為長度，A2仍是來源指標。因此，即使複製函式只讀內容，配置函式也可能觀察這個數值。成功後，13B70從當時SP+12重新讀指標到A1，13B6E新讀liveS1+4C作複製目標。複製結束後，13B80傳給TX的是post-copy liveS0配置緩衝區。呼叫者與callee之間沒有未證實的S/SP保存假設。

小回覆13F66自行在SP+15建立一個位元組，再進入13B4C；頁面回覆9B8E自行配置1026B並複製Flash頁面，不以S回覆指標作語義輸入。這不能消除它們的ambient暫存器與未知callee限制。

兩份既有候選的58B複製實作均為forward byte copy：非null來源以位址逐byte LBU，再SB目的位址。它們不比較特定stack範圍，卻會先保存/清零MMIO4002420C、執行FENCE.I，最後恢復MMIO；不能視為純memcpy。實機是否安裝這些候選仍未知。

只有在配置函式不觀察或保留ambientA2、live frame/slot保持所需狀態、確實執行已證明的copy、兩來源在每次fresh read有相同兩byte、沒有影響結果的alias/fault/非同步修改，且後續TX與release滿足各自未知契約時，才有「packet內容相同」的條件性投影。這些是充分條件，並非要求所有數值位址或每個RA必須相同；也尚未證明它們在硬體成立。詳見[contracts.json](contracts.json)。

實讀既有D/P兩語568B物件，response位於SP+6/+7。SP+12保存S7，硬改回原SP+12會破壞它。48B frame大小相同，不代表10個保存槽與原7個保存槽相容。

證據：546B原始範圍共209個完整指令欄位；四個App消費者113指令與實際既有ELF／LLVM逐欄相等，另96個原TX指令對照既有封存來源。五個實際raw operand反例皆拒絕；D/P C/C++四個現有native archive檢查與唯讀replay通過。未重編譯、未重跑HOST、未執行原始或重建RISC-V程式、未產BIN。

```sh
python -B reply-review/check.py --project-root ROOT
python -B reply-review/review.py --project-root ROOT --firmware FW --folder ACTUAL_MODE --image-elf OLD_ADDRESS_WITNESS --candidate-root RESIDENT_CASE --receipt NEW.json
python -B reply-review/review.py --project-root ROOT --replay NEW.json
```

`check.py`預設只核對封存來源、保留operand與反例，`metadata_only=true`，不讀generated物件。`review.py`的四個輸入旗標各自選用；有指定才讀FW/native/ELF/candidate。`--folder`僅接受既有compact568物件；未來layout物件需獨立審查。Receipt create-only，replay使用其中記錄的明確路徑，不編譯或執行目標。Shell wrapper支援`PYTHON`環境變數。

本封存只含來源與結果metadata；`build/`實際收據不納入。完整ABI、installed ROM、原始placement及硬體OTA均未准入。下一個需要的callee證據是slot70的ambient輸入與memory footprint，而非強制數值SP相等。
