# SDK 啟動、slot2 與原 APP 入口

[English](readme.en.md) · [APP callback／IRQ 順序](../tsl9-original-APP-library-binding/README.md) · [LLE handler](../tsl9-resident-lle-callback-gateway/README.md)

新增 5 個完整候選 SDK 啟動 stage，共 **234 CODE bytes／67 指令**，以原始暫存器上下文的 C11／C++17 編譯。兩者物件一致；原始指令、14 relocations、兩個 far calls 與一個不寫入 RA 的 far tail 均已核對。這些是公開 SDK 候選證據，尚未確認實機 ROM 相同。

## slot2 的來源

loader `0x6DE0C..0x6DE7E` 在複製前寫入：

| Store PC | RAM word | 數值 |
| --- | --- | --- |
| `0x6DE1C` | `0x20000000` | `0x200007D0` |
| `0x6DE26` | `0x20000004` | `0x2000251C` |
| `0x6DE3C` | `0x20000008`（slot2） | `0x20002E34` |

slot2 store 在完整 loader CFG 中支配兩次 copy call 與最後的 zero tail。`0x20002E34..0x20002E6C` 的 **56-byte LLE handler** 已有完整 C/C++ 本體，來源對應 Flash `0x430A4..0x430DC`，位於第一次 copy 內。後續第二次 copy 與清零的數值範圍均避開此本體；slot2 也不在這些目的範圍內。

## 複製與入口銜接

| 階段 | Flash source／RAM destination | Bytes |
| --- | --- | --- |
| Seed | `0x40280` → `[0x20000010,0x20000040)` | 48 |
| 第一次 copy | `0x402B0` → `[0x20000040,0x20002E74)` | 11,828 |
| 第二次 copy | `0x6EAA4` → `[0x20002E70,0x20002EFC)` | 140 |
| Zero | `[0x20002EF8,0x20003618)` | 1,824 |

seed 使用半開區間；word-copy helper 的 A2 是**包含在內的最後目的 word 位址**，不是普通 memcpy 的長度。兩次 copy 在 `0x20002E70..0x20002E74` 重疊；第二次 copy 與 zero 在 `0x20002EF8..0x20002EFC` 重疊，依原碼保留。

原 APP `0x18724..0x18734` 準備 `MEPC=0x9008`，在 `0x18730` 不寫入 RA 地跳到 `0x40000`。候選入口再跳 `0x6DE7E`，設定 GP=`0x20004000`、SP=`0x20010000`。loader 釋放自身 16-byte frame 後尾跳 zero helper；沿正常返回路徑可回到 `0x6DEBE` 的 **MRET**，不是一般 C return。這些 SDK stage 沒有明確改寫 MEPC，但仍需要無中斷／CSR 干擾的條件。

原 APP 的完整 main 是 `0x9008..0x901A`；它在 `0x900C` 呼叫 `0x9250`，後者在 `0x9268` 呼叫 `0x8E88`，再連接前輪 library initializer 的 slot2 → GP+384 store。這次另核對 98 bytes／31 指令，與既有兩份原位址 C/C++ 診斷 ELF 及原 BIN 一致，沒有新增 APP code。

## 驗證與限制

[C/C++](resident_slot2_startup.c) · [數值 ABI assertions](startup_abi.c) · [證據](evidence-v1.json) · [收據](audit-result-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-resident-slot2-startup/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定的本機 BIN、SDK 參考與既有 native artifacts；驗證不下載依賴。原生 C11／C++17 編譯已在 Windows NDK LLVM 通過；跨平台驗證未確認。

完整候選組合為 **20,346 CODE＋256 DATA／6,973 指令**，沒有重複原始 CODE 位址，全部輸入 byte／symbol／relocation 均保留，兩個獨立 ELF reader 一致；仍有 **11 個具名依賴**。物件是可重定位分析產物，未按原位址整合至 APP。

第二次 copy 的來源仍缺 **`0x6EB2C..0x6EB30` 四個 bytes**。後續會清零目的內容，不代表先前來源讀取能成功。有效記憶體、callee 正常返回、GP／CSR／RAM 不受非同步覆寫，以及候選 ROM 相符等條件尚未實機驗證；更早的 IRQ exposure 也未封閉。

**尚未證明啟動完成、slot2 的實際 RAM 值或全域任何 dispatch 前皆已完成 binding。** APP 仍為 159 C/H、95.54% 位元組覆蓋率，這不是功能完成率。沒有新增 BIN、硬體／目標／HOST-model／ISA 執行或刷寫；ROM／RAM／ISA／IRQ、stack／alias、callback、Flash／OTA 仍待驗證，尚未成功重建可用替代韌體。後續唯讀診斷候選功能為顯示啟動指標來源與缺失來源範圍，尚未實作 UI。
