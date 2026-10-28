# Controller state helper 與 slot／數值指標缺口

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 候選本體](resident_controller_state_helpers.c)

新增 **4個完整原始函式，780 CODE bytes／273指令**。C11／C++17與原指令、51筆直接控制及1組遠tail（53重定位）相符，完整CFG/frame檢查通過。5個單元匯入中4個由真實父provider解析；補齊4個舊普通UND、另帶出561B8，因此整體由22降至 **19普通UND**，沒有stub或alias。

|完整範圍（尾端不含）|靜態確認|
|---|---|
|55C6E..55CC4，86B／28指令／frame32|slot38不等於255時呼叫43A14，之後寫255；保留record42 OR0x60及`uint16(record64+record72)`至70。恢復frame後tail至43874|
|55CC4..55D00，60B／21指令／frame32|對slot39保留相應條件呼叫與寫255，再恢復frame並tail至43874|
|5649C..56574，216B／78指令／frame16|保留global count/list、record29／11／140／28條件；兩分支更新不同record欄位。以value255、length12對peer+104呼叫既有填值helper，far tail前恢復frame|
|56574..56716，418B／146指令／frame16|保留整個list選擇、REMU、signed／unsigned比較與截位；包含561B8新呼叫，以及record29的3／18／19等數值狀態|

原controller的 **56E4C→55C6E、57414／57480→55CC4、574E0→56574、57748→5649C**，均以完整CFG核對原record引數來源；新部分物件真正擁有這些正大小原始CODE本體。

兩個43874尾端引數分別為：數值`55C32`／`56CB2`、原record、保留的incoming A1、slot38／39的位址。**兩個數值目標尚無本體，也未形成typed CODE binding**；不能把它們當作已重建callback，亦不能只看普通UND數宣稱完整。43A14被呼叫不等於已證明實體清理成功。

global2000346C的count與global20003454的list參照、record29非0的阻擋分支、record28清零路徑及數值states1／2／3／18／19均保留。有效list、next pointer、除數與IRQ／DMA／重入一致性仍有條件；產品語意未確認，不新增C算術替代、clamp或強制狀態轉移。

相同C/C++部分連結為 **54,522 CODE＋412 DATA bytes／18,831指令**、4,068正大小FUNC、3,238重定位、19普通UND，無重複原始CODE。沒有新DATA或新本地間接呼叫；既有間接缺口與兩個數值指標仍保留，父bytes／globals／重定位角色不變。

**沒有新BIN、正式src納入、APP整合或最終原位址配置。** APP仍162份來源、73,478／76,800B（95.67%靜態byte覆蓋，非功能完成率）。原硬體ROM／RAM／IRQ／Flash／OTA與4B啟動來源仍未證明。未執行target、HOST model、ISA或硬體，未存取廠商API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [尚未實作的slot／數值狀態診斷候選](feature-candidates.json)

固定本機輸入與LLVM齊備時，唯讀重播：

```sh
python3 experiments/tsl9-resident-controller-state-helpers/verify-v1.py --tool-dir "$LLVM_BIN"
```
