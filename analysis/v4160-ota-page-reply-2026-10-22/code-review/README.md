# OTA 頁面回覆：獨立 C/C++ 審查

[English](readme.en.md)

本輪檢查已固定的可讀函式 `experiments/tsl9-v4160-ota-page-reply/src/page_reply.c` 與具名合成 HOST adapter，和原始124 bytes／50指令的證據分開封存。原始證據為 `../source-review/seal.json`，SHA256 `2fe1ed8e78cbb6e054a0368c330b5d1d15f9c75bc0510769340371464b3d32f3`。測試依原始契約建立有限效果 oracle，沒有執行或解譯 RV32 指令。

## 實際獨立結果

C11、C++17 各通過 **3組、90個案例、6,699次斷言**，每種語言另有 **10個實際編譯的語意錯誤版本**被拒絕。`expected-effects.c` 使用獨立固定21效果順序表，比對原始來源推導的位址、寬度、參數及終止結果，不匯入製作者的預期輸出或測試 fixture。涵蓋：

- 13個完整案例：10種完整32位元 index，包含65536、環繞相關值及高位元值；配置回傳零時變更保存 RA 與不透明 caller 殘留值；於具名呼叫中合併變更 S1/S2/S0/S3/S4/SP 及三份合成堆疊；以及將未知 TX A1 保持未知並傳入尾端呼叫。
- 14個資料不可確認案例：配置結果、S1或SP未知；9個不同讀取點資料未知；以及拒絕「已返回但修改暫存器或 known mask」的記憶體 callback。
- 63個停止前綴：在21個效果點分別回覆 UNKNOWN／HALT／TRANSFER，確認精確前綴長度及沒有補造後續效果。

每個正向與錯誤版本的可執行檔，都經固定的 native-host guard `76c6d512164da18cd0fc4641940301f2df2362251c584de0e6b049c21d0ad189` 於執行前後檢查。本次 Windows 使用實際 PE machine0x8664，每種語言共11次受保護執行，沒有啟動 RV32 程式。C11 使用 MSVC `/TC /std:c11`，C++17 使用 `/TP /std:c++17`，均開啟 `/W4 /WX`。首次獨立 fixture 編譯遇到 signed／unsigned 斷言警告，失敗日誌留在本機；修正測試斷言後才取得本次成功結果，沒有修改產品來源。

10個實際編譯的錯誤版本，各只修改一處有限來源片段：縮窄來源 index、顛倒標頭寫入順序、快取複製 slot base、複製長度錯誤、快取釋放 slot base、使用過期 free buffer、快取還原 SP、將尾端結果統一成零、覆寫 TX A1，以及未清除奇數釋放目標的 bit0。每個版本都成功編譯，先檢查主機格式才執行，再由獨立語意斷言拒絕。這些數量與製作者6個控制及原始指令18個控制分開記錄。

本次獨立收據保存在本機 `code-review/build/independent-9307d2c1418f4fef9faf85eab1441c10/{c,cpp}`，SHA256 分別為 `4da39eda271a8975a55af77b1f8a8386c9fa722d62a455466194cf22a4c58107`、`d66e2e6a042e98e739908a96d6a39c59ea0ab346e5818f4f1dc95f3ec617fe0c`。兩份實體封存均已另行唯讀重查，沒有再次執行。`selected-receipts.json` 只保存精簡來源、工具及結果身分，不包含產生的二進位或完整封存內容。

製作者最終 HOST CLI 為 `92e3d7bf90b7255a8efee6a90c4126df802c15225586e006170aa006d779e332`。其獨立的標準 C/C++ 測試各為3組／87案例／3634檢查，另有6個編譯錯誤控制；本輪也唯讀重查兩份實體封存。這些結果明確歸屬製作者，不替代本次獨立90案例 oracle。

## 結果代表的範圍

測試區分複製來源公式中的完整32位元 index 與標頭低16位元輸出，確認先寫低位元組、再寫高位元組。不透明呼叫後會重新使用當下 S2 取得後續 slot；堆疊讀取使用當下 SP，可觀察新提供的保存資料及已變更／奇數 caller link。slot／link 原始值與 JALR 清除 bit0 後的目標分開呈現。free 使用還原 S0 之前選出的當下 S0；TX A1/A2/A3 殘留值保留到不透明尾端呼叫。尾端 provider 自行提供結果，沒有補造共同成功值或狀態碼。

HOST 契約允許 READ／WRITE callback 修改合成記憶體或保存區，但已返回的記憶體 callback 不得修改暫存器或 known bits；違反時回報 UNKNOWN 及明確診斷。只有具名不透明呼叫邊界允許任意修改公開的暫存器、SP及known mask。provider 必須依契約透過 `op_event` 提供結果，直接修改 A0 不是另一種返回值管道。呼叫效果仍不透明：此 oracle 沒有重建或驗證複製資料內容、配置器內部、TX或釋放函式。

`OP_RETURNED` 代表合成 provider／模型抵達其宣告的終止邊界，不證明實體尾端呼叫會返回原始 caller。原始／重新讀回的 link 另行回報，釋放函式仍可能轉移或永不返回。UNKNOWN／HALT／TRANSFER 前綴只證明有限效果行為，不代表實體指令邊界的 GPR 殘留值。native SP／堆疊及 callee-save 前提、ABI 順序處理、固定位址整合、ROM身分、硬體及藍芽更新接受條件，仍需各自證據。本次審查沒有 native 目標執行、實體存取、網路請求或產生新韌體映像。

## 跨平台檢查與重新測試

由工作區根目錄執行；發布版將 `apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22` 改成 `analysis/v4160-ota-page-reply-2026-10-22`：

```sh
python3 -B apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22/code-review/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
python3 -B apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22/code-review/run-effects.py --project-root . --language both
```

兩者都有接受相同參數的 shell wrapper，需要時設定 `PYTHON`。重新測試需要 `scripts/portable_verify.py` 支援的本機 C/C++ compiler 與已固定 guard。macOS guard 需要符合本機的 thin Python executable；fat／universal 輸入會被拒絕，不會猜測。

預設檢查重新核對已封存檔案、目前5份來源／oracle／guard／helper／最終製作者 CLI，以及原始50條指令／18個控制。這是**來源與選定 metadata 檢查**，會輸出 `actual_archived_artifacts_replayed:false`；發布不包含 build 封存。若要檢查實際獨立封存，加上 `--receipt PATH/verification.json`，可重複指定。唯讀模式會檢查實際檔案、主機可執行格式、精確編譯來源／旗標／輸出角色、日誌／結束碼，以及只變更一處的錯誤來源；不啟動二進位，也不宣稱讀回不存在的本機封存。重新測試會在只允許新建的本機 `build/` 目錄產生新收據。
