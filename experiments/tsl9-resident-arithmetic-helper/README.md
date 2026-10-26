# 時鐘算術 helper 候選 C/C++

[English](readme.en.md) · [時鐘服務](../tsl9-resident-clock-services/README.md) · [Timer 服務](../tsl9-resident-timer-service/README.md)

重建完整 `0x6DF1A..0x6E2AC`：**914 bytes／296 條指令**，以及它實際引用的 **256-byte 查表** `0x6E95C..0x6EA5C`。這是公開 SDK V1.31 候選，尚未確認實機 ROM 相同。[C/C++ 來源](resident_arithmetic_helper.c)保留原始暫存器／C/assembly 與真正的 const byte table，不能當成一般 HOST C API 呼叫。

## 已驗證

- C11／C++17 物件相同；還原原位址編碼後，全部 CODE 與 DATA bytes 吻合。81 個正尺寸 FUNC、1 個真實 OBJECT、65 筆重定位。三個 AUIPC/ADDI 指向真實表物件，沒有用 stub 取代 helper。
- 查表的全部 256 項等於 unsigned 索引的 bit length。三個 byte load 以 unsigned 區間與 0/8/16/24-bit 右移選取索引，靜態範圍為 0..255。三條條件式 Xwchc 指令依官方定義與 28 個向量核對；實體 ISA profile 仍未確認。
- 完整靜態 CFG 的所有指令皆可由入口到達，沒有循環、外部呼叫、記憶體寫入或 SP operand。至返回最多 98 條 CFG 指令；這是保守靜態路徑上限，**不是硬體耗時量測**。
- 時鐘服務的三處呼叫 `0x43FCC`／`0x43D94`／`0x43DC6` 均明確設定 A3=0。WaitWindow 的 denominator 引數為 1,000,000；delta 路徑使用 live ClockFrequency，仍需非零與狀態穩定的契約。

## 推論與未確認

指令使用 32-bit DIVU／REMU、base-65536 normalization 與 quotient correction，**符合 unsigned 64-bit 除法候選模式**。尚未完成全部輸入的數學語意證明，不能只因出現 DIVU 就宣稱整個 helper 等同 `uint64_t / uint64_t`。原始程式有零除數分支；未執行這條路徑或負向測試。

編譯期 assertion 僅核對 RV32 pointer 與 unsigned 32/64-bit 大小；它不證明原函式的 register ABI。沒有執行目標、HOST 模型或 ISA 模擬。

## 真實部分連結

既有 `tsl9_candidate_external_flash_6df1a` 匯入已由完整真實本體解析。C／C++ 非載入式 ET_REL 均為 **4426 bytes CODE＋256 bytes DATA／1538 條指令**，393 個正尺寸 FUNC、1 個 OBJECT、289 筆重定位；保留每個輸入 byte、符號與重定位。

仍缺 RAM `0x2000061A`／`0x20002610` 與 Flash `0x63DD0`，以及整體 raw RAM／callback 契約。保留 **4-byte 啟動來源缺口**；尚未做原位址執行連結或 APP 整合，沒有新增 BIN。APP byte 覆蓋維持 **95.54%**，不代表功能完成率；實機 RAM／ROM／ISA／IRQ／stack／Flash／OTA 相容性仍未確認。

證據：[完整稽核 v2](audit-result-v2.json)、[摘要](summary.json)、[原始指令與查表](evidence-v1.json)、[規格與雜湊](spec-v1.json)。Clock normalization／baseline 診斷是候選新功能，尚未實作。

## 重跑

先備齊 spec／evidence／audit 指定的原 APP、SDK／標頭／指令參考與既存 native 產物；此提交未附原 SDK 與 native 產物，不會自動下載。從專案根目錄，以固定雜湊的 Windows NDK LLVM 執行：

```sh
python experiments/tsl9-resident-arithmetic-helper/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-arithmetic-helper/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；有既存產物時，第一個改用 `--replay experiments/tsl9-resident-arithmetic-helper/build/native-v1`，第二個省略 `--link-trial`。未存取硬體或廠商 API。
