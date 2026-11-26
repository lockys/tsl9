# v4.1.60：首次 registration 後的 constructor 與設定發布

接續 [首次 registration 返回](v4160-first-registration-chain-static.zh-TW.md)，本輪將 `19b30` 的索引保存串到 constructor、13 個前置呼叫、候選 `40074` provider、optional hook、16-byte copy 與 service word 發布。在各條件成立時，原 task byte 為 `3`、count 為 `4`、table entry3 為 `1995c`，並可保存到下一個尚未封閉的 registration 呼叫之前。

這次 provider 內的 registration callee 是 `43b0a`／`43b96`，不是前輪 `40080` 的 `43c4e`／`43cda`。證據止於呼叫它之前，沒有假設它返回或保存資料，也尚未接回 wrapper 的 `19b3a` 或 `40058` tail。

程式：[check_v4160_constructor_publication_chain_static.py](check_v4160_constructor_publication_chain_static.py)。逐路徑證據：[v4160-constructor-publication-chain-static.json](v4160-constructor-publication-chain-static.json)。全程只讀原始 bytes、檢查 operands／CFG 及有限欄位、區間與算術等式；未執行或模擬韌體、MMIO、copy、callback、輪詢或裝置。此輪重用既有完整本體，C 重建覆蓋率不變。

## 索引 byte 的地址來源

[reset 原指令](v4160-app-jt0-call-chain-static.zh-TW.md) 在 `186aa`／`186ae` 以 AUIPC／ADDI 形成 `GP=20004000`。這是來源證據，**不證明中間所有啟動及 provider 路徑都保存 GP**。

若到 `19b30` 仍保持此 GP，且前輪條件式 registration 回覆 `3` 成立：

```text
19b30：S0 = GP+388 = 20004184
19b34：U8[S0] = low8(A0) = 3
19b38：呼叫 constructor 19b56，返回 link 為 19b3a
```

`20004184` 是前輪名義 heap 起點 `H=2000418c` 的前 8 bytes，與仍 owned 的 table allocation 分離。不能從 reset SP 推定此刻 stack 的實際地址；下文使用符號 frame base C。

## constructor 的完整 16-byte 來源

令 C 為 constructor 執行 SP−=32 後的 SP。它先保存 RA 於 C+28，再清除 C+0、+4、+8、+12 四個 word。重用 [前 12 個呼叫合約](v4160-config-precallees-static.zh-TW.md) 與 [第 13 個 mode3 合約](v4160-mode3-frame-static.zh-TW.md)，在正常返回、有效且不別名的 frames／存取、程式碼保存及沒有不利硬體／非同步干擾時，config、所需 SP／RA／S／GP 能保存到 `19bac`。

隨後三個 word stores 形成以下 little-endian 內容；bytes12..15 沒有再次改寫：

| C 相對範圍 | 值 | 來源 |
|---|---|---|
| 0..3 | `000191c6` | AUIPC／ADDI 形成 reader code address |
| 4..7 | `ffffffff` | LI −1 |
| 8..9 | 16000 | word `03e83e80` 的低 halfword |
| 10..11 | 1000 | 同 word 的高 halfword |
| 12..15 | 0 | 初始清零加上前置 callees 的條件式保存 |

完整 16-byte 字串：`c6910100ffffffff803ee80300000000`。

`19bc8` fresh 載入 `[40074]`；`19bca` 設 A0=C；`19bcc` 間接呼叫，link=`19bce`，沒有本機 target-null guard。A1／A2 沒有在此重新建立；候選 provider 此處使用傳入的 A0 來源。

## 兩類 optional hook 與 gates

兩版候選 `40074` 入口分別是 `43f46`／`43fd2`。本輪明確要求 actual fresh mapping 符合候選，並處理兩類 hook：

- fresh hook word 為 `0`：略過 hook call。
- fresh hook word 為 `197b8`，且符合既有 mode3／reader code 與正常返回、frame 保存等條件：強制 mode3 後尾跳 `1929a`，返回 provider 再從 saved word 重載原 config pointer。

其他非零 hook 仍未封閉，沒有推定裝置實際採用上述任何一類。[既有 hook 來源與巢狀 frame 證據](v4160-optional-hook-origin-static.zh-TW.md) 的條件也仍適用。

C 必須為非零、對齊且有有效的非回繞 frame／資料存取。四個非零 gates 依序看到 `191c6`、`ffffffff`、16000、1000，因此通過；byte12 為零，跳過 state+21 的 mode gate。這只界定欄位測試，沒有宣稱 word4 的值代表可解參照的有效物件。

## copy、發布與算術

重用 [完整 gates](v4160-config-gates-static.zh-TW.md) 及 [copy／算術合約](v4160-config-arithmetic-static.zh-TW.md)。matching `20000332` leaf 在有效、完成且 source／destination 不重疊、不受干擾等條件下，向前逐 byte 複製 16 bytes；不是 atomic snapshot 或 memmove 合約。它涉及 `4002420c` 的 MMIO 與 FENCE.I，這些在本輪均未執行，正常完成與無不利副作用是前提。

| 候選 | copied config | fresh word0 發布至 | 下一個未封閉的呼叫 |
|---|---|---|---|
| V131 | `20003234` | `200031e0` | `43b0a`，呼叫點 `43fda` |
| V140 | `20003284` | `20003230` | `43b96`，呼叫點 `4406e` |

在上述 source 保存條件下，發布值是 `191c6`。之後 fresh state+23 若為零，matching 算術路徑以 h=16000 得 `floor(7*h/5000)=22`，存回該 byte；若非零則跳過 helper 與 store，保留該次 fresh byte。沒有無條件宣稱此欄位會被覆寫為 22。

每版有四條已選定的有限 normal-return 路徑：hook 有／無 × state+23 零／非零。共八條路徑均穿過 copy 與 publication，止於下一次 registration 呼叫指令之前；不走 null-config defaults 或 gate-failure epilogue。

## 保存範圍與限制

相對 C，constructor frame 是 `[0,32)`、wrapper frame 是 `[32,48)`，provider frame 是 `[-32,0)`。constructor mode3 的 stack stores 落於 `[-68,-64)` 及 `[-52,0)`；provider hook mode3 的 stores 再下移 32，落於 `[-100,-96)` 及 `[-84,-32)`。它們與 constructor config／RA、wrapper frame 不重疊；provider 自己使用自己的 frame 保存 input／S0／RA。

copy destination、service word、state+23 以及 V140 的額外 clear word，均逐一檢查不碰 task byte、count、capacity、table pointer、原 allocated header、entry3 或 hook word。全部 256 種前輪 layout 也滿足 task byte 與 allocated table 的界線。

因此，在前輪名義配置、GP 保存、matching code／fresh slots、有效非別名 stack／globals／heap、所需正常返回與沒有不利 MMIO／FENCE.I、IRQ／DMA／重入／外部 writers 等條件下，可把 task byte=3、count=4、entry3=1995c 保存到此輪截止點。數值地址分離本身不能證明實體 alias 或硬體非同步效果不存在。

16-byte copy 沒有直接保存 source-pointer register 的 store，但來源值包含 reader code address；這不能延伸為所有 provider 都不保存指標的結論。截止點時 constructor frame 仍活躍，未證明返回後的 payload／物件生命期。

## 驗證與後續

一般與 Python `-O` 均要求 ledger 逐 bytes 一致。驗證包括原 APP／兩版候選／SDK／sparse HEX／Xwchc 來源身分、完整既有本體 operands／CFG、八條選定路徑、巢狀 frame 區間、256 種 layout、256 個 state flag、65,536 個 config 算術域等式，以及 105 個 APP／config operand mutations 的拒絕。

下一步是 `43b0a`／`43b96` 的實際寫入與返回合約，再接 constructor 返回、wrapper 索引重讀與 fresh `40058` tail。實際 provider 綁定、GP 保存全鏈、field44 來源、硬體進度與後續保存期仍待釐清。
