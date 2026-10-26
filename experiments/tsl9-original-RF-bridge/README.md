# 原始 APP／候選 RF 執行層銜接

[English](readme.en.md) · [RF_Config／callback](../tsl9-resident-callback-registration/README.md) · [trap 契約](../tsl9-trap-profile-contract/README.md)

本輪優先確認原始 APP 的實際呼叫位置，並新增 **664 bytes／216 指令、4 個完整候選 SDK 本體**：

| 本體 | 原始範圍（end exclusive） | Bytes／自身 frame |
| --- | --- | ---: |
| RF_RoleInit | 0x66056..0x66098 | 66／16 |
| Common reset | 0x641B0..0x64298 | 232／32 |
| Register initializer | 0x64298..0x6430E | 118／16 |
| Registered RF task | 0x65920..0x65A18 | 248／16 |

## 原始 APP 的直接證據

原始完整主初始化函式0x8E88..0x9008中，0x8EBE載入S0+448並於0x8EC2呼叫；在callee正常返回的完整CFG中，此呼叫支配0x8FDC對constructor0x175E8的呼叫。S0的原始base是0x40000，因此表位置為0x401C0。候選SDK此word指向0x66056，固定header將其對應RF_RoleInit／index99。

Constructor0x175E8..0x17666配置48-byte frame，在SP+0..31準備32-byte設定；保存的S1／S0／RA分別位於SP+36／+40／+44，不重疊。0x17644的AUIPC／ADDI組成callback **0x174EE**，0x1764C存到SP+16。0x17654載入S0+452，0x1765A以A0=SP呼叫：表位置0x401C4對應候選RF_Config／index100。

586個APP參考bytes（主初始化、constructor、status callback）同時與原始BIN及既有已編譯原址診斷ELF逐byte一致；沒有新增或修改APP CODE。這使前輪「caller值未知」收斂為**原始APP明確準備0x174EE**；但global0x20003550在實機是否收到此值，仍依賴ROM表一致、callee契約、有效且不重疊的stack／global記憶體。沒有把靜態slot對應當成實機API身分證明。

## 初始化與回呼

RF_RoleInit的實際本體呼叫0x64298，清零candidate context0x20003560的36 bytes，將task callback0x65920交給已有本體的event-register0x43C4E，並把返回的task ID byte存到0x20003570。0x64298釋放自己的16-byte frame後，直接尾跳到0x641B0，不能累加成仍保留該frame的一般call。

0x64298有實際pointer stores：RAM0x20003504→0x40024300、0x2000353C→0x40024200、0x20003590→0x40025000、0x20003508→0x40024100。這只證明原始寫入，未知callee或非同步作用之後是否仍保持、周邊實體身分與所有權均未證明。其他內部callback words的完整初始化順序仍未封閉。

原始status callback0x174EE不配置frame。status2路徑先檢查A1，再讀A2+1／+2／+3，並比較RAM0x2000C7AA／0x2000C7AB；因此該路徑至少需要4個可讀bytes，原碼沒有length／null guard。其他狀態保留完整測試式：排除A0==2後，A0>=2且low8(A0-17)<=1會走0x17442；符合packet bytes的路徑以A0=0尾跳0x173EE。byte／完整協定語意與實際buffer有效性未證明。APP context由原始PC-relative指令獨立解碼為0x2000C7A0，並非執行觀測。

## 驗證與限制

C11／C++17物件相同；新增664 bytes逐byte一致，52個官方Xwchc正例與12個實際操作核對通過，normal return／tail自身frame平衡。43個正大小FUNC是編譯分割區段，不是43個邏輯函式。

累計部分連結物件為 **12936 CODE＋256 DATA bytes／4507指令**、1053個FUNC區段、1個OBJECT、790個relocations；逐輸入bytes／symbols／relocations及獨立ELF readers通過。已有11個與本輪8個未提供callee合計 **19個真實具名依賴**。這不是可載入映像；原始APP與候選SDK未整合成新的BIN。

APP位元組覆蓋率仍95.54%、159個正式C/H；4-byte啟動來源缺口、ROM／RAM／ISA、GP／IRQ／frame／alias、Flash與OTA仍未通過。沒有目標、HOST model或ISA執行、硬體操作或vendor API；**尚未成功逆向出可用替代韌體**。RF初始化／status／callback來源診斷可列為未來功能，尚未實作UI。

[完整收據](audit-result-v2.json) · [摘要](summary.json) · [原始APP／SDK指令](evidence-v1.json) · [C/C++](original_RF_bridge.c)

## 重現

需要spec固定的原始APP、SDK／官方指令文件、先前native artifacts、既有原址診斷ELF及trap契約的本機官方header。不會自動下載缺少的輸入。

```sh
python experiments/tsl9-original-RF-bridge/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v2
python experiments/tsl9-original-RF-bridge/audit-v2.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1
```

Trial名稱必須未存在；保留產物時第一行改用 `--replay experiments/tsl9-original-RF-bridge/build/native-v2`，第二行省略 `--link-trial`。v1 native trial保留為歷史收據；目前正向審核使用修正metadata後的v2。工具pins為Windows NDK LLVM，跨平台編譯未驗證。
