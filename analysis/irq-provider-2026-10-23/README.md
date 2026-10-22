# IRQ provider 與九段原位接收鏈

[English](readme.en.md)

[src/native/receive/irq_provider.c](../../src/native/receive/irq_provider.c) 已以C／C++重建官方ID2966 `[0x18D78,0x18E1C)`。六個private區域共164B／53指令，原位完整程式與原廠相同；不是原始碼還原或普通C ABI。**尚未完成整機逆向，沒有新的可燒錄BIN。**

| 證據 | 本輪實測 | 限制 |
| --- | --- | --- |
| Provider單體 | 164B／53指令，6個真實FUNC區域，native3個RVC edge，原位無UND／RELA | MMIO身分與實機時序未知 |
| 九段原位整合 | 802B／280指令，35個真實FUNC區域，32處symbolic control已解析，無UND／RELA | ring的動態resident call仍UNKNOWN |
| C／C++正式檢查 | 每語言provider125個負例、整合119個raw-ELF負例，完整replay通過 | strict readiness均拒絕，不是硬體驗證 |
| `src/`整理 | 53個C/H、27個native編譯入口，54組比對／108個物件 | 未連成完整韌體；舊HOST矩陣未重跑 |

Provider的16個靜態LW32、12個SB8與4個SW32位置／順序皆有核對；這是整個函式所有分支的指令數，不是每次呼叫的動態次數。保留每次fresh讀取、最後A5覆寫、A4殘值、兩個RET，以及A0／A1／A2等其他GPR不被自身改寫的局部契約。v1雖同為164B，兩個返回區塊改寫A1；v2增加A5值埠修正，失敗來源與本機原始量測保留。

九段為ring92、IRQ52、SPI72、register-read72、register-write76、packet142、receiver70、flag-consumer62、provider164B。完整802B串接SHA256為`1946d38e90500f279c650b7f80df32004f05507a2bafeaeceb372ab4b53ee169`；所有原位區段均與官方BIN相同，沒有以原廠raw bytes或ABS符號冒充provider。

**ELF的RX LOAD共25,172B，內含五段、合計24,370B未驗證間隙。** 這是連結證據容器，不是完整APP／BOOT或平面韌體。`LW[0x0004004C] → JALR A5`仍為動態未知；無UND不代表所有呼叫ABI已閉合。新graph重播舊586B、IRQ52與provider164正式證據，明確綁定156個輸入pins、11份完整inventory（114個繼承檔案），共56條producer配方。

重播需保留本機build artifacts；公開JSON本身不含編譯物：

```sh
python3 -B experiments/tsl9-irq-provider/verify.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-irq-provider/build/verified-v3/c/verification.json
python3 -B experiments/tsl9-irq-provider/verify_receive_graph.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-irq-provider/build/receive-graph-verified-v3/c/verification.json
python3 -B scripts/verify-curated-source.py --replay build/curated-source/irq-provider-20261023-v1/verification.json
```

Windows可用`python`；只實測本機已有的Windows NDK LLVM18，其他OS／工具鏈未驗證。不自動下載或搜尋旗標。C／C++ replay均exit0；`--require-firmware-ready`均exit1。現行正式目錄均為v3；中途privacy誤判／序列化差異版本保留本機，不列為當前重播目標。

[summary.json](summary.json)記錄source／checker／收據雜湊及負例分類。Provider的125個負例分為97個raw-ELF、7個parsed typed、16個結構SSA、2個完整IR pin與3個MD，不能統稱為raw-ELF測試。整合119個負例則均重讀修改後的raw ELF，關閉whole-file hash gate。

四份`receipts/provider-{c,cpp}.json`／`graph-{c,cpp}.json`是原本採變數路徑的LF原件，公開副本逐位元組相同。[curated-source.json](receipts/curated-source.json)是匿名路徑衍生檔：原件SHA256`7cd1cf744430b0b98ad2862e59526515eac8f4f3bd9cb626bf2c32e595b1984f`留在本機，只替換路徑字串／鍵，反向JSON相等，不宣稱衍生檔可按原件直接replay。原始BIN／APK、舊收據及Git歷史未改寫。

整理收據含108個輸入、325個artifact及108條配方／MD；舊52組結果與313個artifact雜湊不變。下一段是[314B佇列消費與dispatch](next-consumer.md)。長度／欄位有效性及ID0 occupancy是待查的診斷功能線索，實機錯誤尚未證明，未新增filter／clamp／layout變更。

未執行target／ISA／MMIO、硬體或第三方API。完整startup、resident、IRQ／fault、記憶體所有權、晶片與OTA相容性仍未證。
