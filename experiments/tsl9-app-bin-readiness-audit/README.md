# APP／BIN readiness：實際產物稽核

[English](readme.en.md) · [專案](../../README.md) · [檢查器](check-v1.py) · [實際報告](report-v1.json)

**目前未就緒，不能把既有診斷ELF當成可刷入BIN。** 本輪重播正式162份來源的原位址證據，讀取實際C/C++物件、ELF與固定收據；沒有新增韌體bytes或執行目標。

|門檻|目前實際證據|
|---|---|
|正式APP來源|73,478／76,800B，95.67%靜態byte覆蓋；非功能完成率|
|APP缺口|3,322B：目前排除3,128B＋其他未選194B／34段；未讀取或輸出缺口payload／個別雜湊，未補padding|
|六個source provider|實際物件仍為UND；舊報告的`compiler_UND`欄位不是六個標準compiler runtime helper|
|產物格式|實際ET_EXEC、entry0、PT_NULL、零PT_LOAD；六個hidden NOTYPE ABS僅為參考座標，不是provider本體|
|Resident ROM／ABI|SDK候選未連入APP，仍18個普通UND；有40000座標的CODE不證明原硬體已安裝相同ROM|
|啟動／IRQ／RAM|實體profile、trap綁定、RAM容量、stack／heap／APP global ownership未證|
|Flash／OTA／功能|沒有本次重建映像的實機啟動與功能證據；傳輸讀回成功須分開判定|

六個實際APP匯入如下。已存在部分DATA backing不等於可任意建立完整provider alias：

|原參考|分類／尚缺條件|
|---|---|
|40000|resident ROM／ABI依賴；不應只為消除UND就假設整個ROM必須重建進APP|
|14056|目前排除的APP CODE入口|
|1AB48|DATA provider；參考點有8B positive owner，完整使用合約仍未定義|
|1A078|DATA provider；參考點位於既有432B pool內，但匯入仍未定義|
|1A638|DATA provider；已有48B條件式讀取window，完整provider／global invariant未證|
|1A69C|目前排除的4B default DATA；未輸出內容或個別雜湊|

**兩種「缺4B」不可混用。** `[6EB2C,6EB30)`是候選SDK啟動來源的封存缺口，位於APP `[8000,1AC00)`之外；它不是APP另缺四個bytes。這項參考限制仍保留，也不代表已證明實體ROM讀取失敗。原位址入口、ROM／ABI及範圍要先分清，不能用SDK重建量直接提高APP覆蓋率。

接下來應先解決實際APP provider與允許範圍、為必要的未選區段建立語意證據、確認原硬體ROM／RAM／IRQ／Flash／OTA，再建立可載入產物。**不將六個UND換成假函式、不以hidden ABS當實作、不用填零補缺口、不把診斷ELF改副檔名。**

具備固定本機輸入與LLVM時，從專案根目錄唯讀重播：

```sh
python3 experiments/tsl9-app-bin-readiness-audit/check-v1.py --tool-dir "$LLVM_BIN"
```

此版稽核目前凍結產物：**exit2＝證據核對完成，但未就緒；exit1＝輸入漂移或稽核錯誤**。報告同時標示`evidence_audit_passed=true`與`firmware_ready=false`，不能只看前者。沒有忽略缺口的選項；輸入更新需新的可核對證據。Windows可用`py -3`與`$env:LLVM_BIN`。

本輪不更動正式src、native產物、既有MCP／Skill／Git設定；不執行target、HOST model、ISA或硬體，不呼叫廠商API。[新增功能候選](feature-candidates.json)是更新器分別呈現傳輸／映像／啟動／功能證據，App整合尚未實作。
