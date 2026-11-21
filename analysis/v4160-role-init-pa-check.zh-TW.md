# 角色初始化主路徑：哪些參數看似指標，卻不是 PA 描述元？

限定原 APP `[0x8eb2,0x8f2e)`；取 s0=0x40000、各呼叫正常返回且保存基底與堆疊。按參考 SDK，前三個間接呼叫依序是 `GAPRole_PeripheralInit`、`GAPRole_CentralInit`、`RF_RoleInit`（索引 91/94/99），均宣告無參數。不能把當時殘留的 a0 認成描述元。接著索引 19 收到回呼位址 `0x8614`，回傳低 byte 存入 gp+157。

| 後續索引 80 的參數 ID | a1 長度 | a2 指向的資料 |
|---|---:|---|
| `0x306` 廣播資料 | 13 | `0x19dec` |
| `0x311` 最小連線間隔 | 2 | `sp+12`，先前寫入 halfword 6 |
| `0x312` 最大連線間隔 | 2 | `sp+14`，先前寫入 halfword 1000 |

最後兩次是索引 72 的純量參數 `(3,160)`、`(4,160)`。整段只有一次 GP byte store 與兩次 stack halfword store；相鄰的兩個 halfword 是兩次不同設定的輸入，不是六個 word 的結構。在這段 APP 自身的指令內，未看到構建或交付 `blePaControlConfig_t`，也沒有索引 109 呼叫。這不排除被呼叫函式的內部行為、其他路徑或預先建好的資料。

重現：`python analysis/check_v4160_role_init_args.py <decoded-app-bin>`。檢查原 BIN SHA、解碼每條指令並在間接呼叫後忘記所有 caller-saved 值；SP/GP 用合成基底，記錄的是發出的呼叫參數與直接 store，不模擬外部記憶體副作用。型別來源見[參考 SDK 檢查](v4160-pa-descriptor-sdk.zh-TW.md)。
