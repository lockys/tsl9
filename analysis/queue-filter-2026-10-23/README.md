# 封裝／轉送入口與傳輸層

[English](readme.en.md) · [C實作與正式檢查](../../experiments/tsl9-queue-filter/README.md) · [原始69指令](../queue-consumer-2026-10-23/next-filter.json)

本輪完成82D2的188B C／C++重建與獨立驗證。診斷ET_REL仍保留7筆relocation；下游8A56與動態resident效果未閉合，並非原機可執行image。

另以真正的C物件[部分連結queue、filter與兩個GP provider](../../experiments/tsl9-queue-dispatch-component/README.md)：526B／184指令／19 FUNC。三個呼叫符號已綁定真實定義，仍有6個strong UND與32筆pending RELA；符號綁定不代表控制立即數已套用。此元件與先前的九區段IRQ圖分別驗證，尚未合成整機。

正式C／C++檢查、獨立唯讀replay及拒絕刷寫就緒的strict gate已核對。[里程碑收據索引](summary.json)保留來源與產物雜湊。filter收據逐byte保留；含本機絕對路徑的部分連結與整理收據提供明示的path-only公開衍生版，原始收據保留本機。

| 證據 | 已確認事實 | 限制 |
| --- | --- | --- |
| `82D2..8304` | 64B frame、S0..S9／RA，初值table`2000C794`、selector0 | table值需要原PC配置；完整memory ownership未知 |
| `8308..8326` | stride4；比sentinel FFFE、kind2、非零flag | opaque call後都使用then-live S-register，不保證固定兩筆 |
| `8328..8356` | 保存flag至S4，再檢查長度、封裝ID／tag，fresh `[S9+76]`間接呼叫 | flag先於拒絕過長資料更新，非零不證明傳送 |
| `8358..8368` | fresh byte `[S1+2]`、halfword `[S0+2]`、SP+4；A3加2、A1=C0，C.JAL8A56 | 正常byte讀取時A3介於2..257；provider後的memory validity仍未知 |
| `836A..838C` | 使用then-live S2決定cold loop；回傳then-live S4；cold path設selector1 | C.JAL返回836A，不能誤用4-byte call或不寫RA的jump |

另已核對完整下游 [8A56傳輸封裝](next-transport.md)：280B／96指令，包含兩個admission間接呼叫、checksum loop與tail provider。這是下一個C重建目標，尚未把其完整行為歸類為BLE／UART／CAN硬體實作，也未證座椅或免打擾對應。

值得加入的診斷功能（尚未實作）：離線frame長度／checksum檢查、routing條件可視化，以及將「flag非零／呼叫發生／provider接收／實際送出」分開的紀錄。它們有助定位更新或資料傳輸問題；不改原協定、routing layout或硬體行為。
