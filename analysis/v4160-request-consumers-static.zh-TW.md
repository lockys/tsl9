# Request 消費端：query 1055、參數快照與 slot 清除

接續 [special request](v4160-special-request-static.zh-TW.md)，本次展開查詢、fallback及清理函式。範圍是resident參考候選的本機指令與資料表，實際provider安裝、RAM值與硬體執行仍未證明。

| 函式 | V131範圍（右端不含） | V140範圍（右端不含） | 每版bytes／指令 |
|---|---|---|---|
| query | `6bc2e..6bd82` | `6be12..6bf66` | 340／111 |
| fallback | `48070..4819a` | `48108..48232` | 298／109 |
| cleanup | `47fc8..47fec` | `48060..48084` | 36／13 |

另核對 `6e6c0/6e8b0` 的35-word跳表，每版140 bytes。合計1348指令bytes、466條指令、280表格bytes、70個entry。全部operands、SHA256、閉合CFG與84條選定路徑見 [JSON](v4160-request-consumers-static.json)，以[檢查器](check_v4160_request_consumers_static.py)重播。

## Query 1055 的輸出已縮小為本機單byte寫入

query建立16-byte frame，保存RA／S0，S0保存入口輸出pointer A1。分派index是：

```text
index = low16(entryA0 − 1024)
index <= 34 才讀跳表
```

所以入口ID的高16位有別名，不能用完整32-bit的`1024..1058`範圍判斷取代原式。35個table entry全部由原始bytes核對，並驗證目標落在已解碼指令邊界。

1055對應index31，跳到query+272；路徑為：

```text
fresh U8[20002fb8 / 20003008]
  → SB 至入口A1+0
  → A0=0
  → 恢復frame並RET
```

這條選定路徑沒有call provider，沒有把輸出pointer寫入持久物件。於有效可讀source、有效可寫output、非別名frame／code／table及正常返回的前提下，可以確認單byte寫入和返回0。它仍未證明RAM byte的writer、啟動值或實際執行時的值。

因此，上游request的SP+7與本次fallback的SP+95，若確實呼叫這份candidate query1055，可由這個本機store提供輸出；不用再把1055本身整段視為未知輸出provider。此結論不適用於query所有ID，也不證明同一RAM source在多次讀取間保持不變。

## Query 其他 ID 與版本差異

| 路徑 | 輸出／返回 |
|---|---|
| 本機byte或bit選擇 | 寫1 byte，返回0 |
| word來源 | 寫4 bytes，返回0 |
| 兩個copy分支 | 對RAM `20000332`提出copy16，輸出與保存合約仍未知 |
| index21 | 呼叫 `6af88/6b16c`，將回覆低byte寫到輸出，返回0 |
| table外或default，原始unsigned ID不超過版本上限 | 呼叫 `45f9c/46034`，SH回覆低16位至輸出，返回0 |
| table外或default，原始unsigned ID大於上限 | 返回2，不寫輸出 |

最後一層比較使用**原始完整入口ID**。V131的上限為65，V140為66，不能只按固定地址delta視為相同行為。

table的index16、22..29、32共10個entry指向default；其canonical ID為1040、1046..1053、1056，皆大於上述上限，因此會返回2而不初始化輸出。不能把「跳表涵蓋35格」推論成35種有效輸出。

## Fallback 使用第二次 fresh query 的值

fallback建立144-byte frame，保存RA及S0–S8。令 `g=20003000/20003050`、slot=`g−236`。

- fresh slot為null：直接返回1，不呼叫query或最終request callee。
- slot非null：連續兩次呼叫 `(1055,SP+95)`。兩次都從上述RAM source重新讀取；稍後本機讀SP+95時，使用的是**第二次輸出**。
- 將 `bool(fresh U8[g+586]) + 2*bool(SP95)` 保存到SP+76，結果為0..3。這裡是role byte是否非零，並非role是否等於3。

檢查器遍歷兩個byte的全部65536組合；結果0／1／2／3的組數為1／255／255／65025。未假設兩次source讀值相等。

## 三次物件快照不可直接合併

後續資料來自三次fresh slot讀取：

1. P0：以 `U8[P0+3]`、`P0+4`呼叫 `45612/456aa`，保存完整回覆。
2. P1：在該call返回後讀取，保存 `U8[P1+2]`；再取得query3與query4的完整回覆。
3. P2：在query4返回後讀取，保存 `U8[P2+10]`、`U8[P2+11]`，並保留P2供最後pointer參數使用。

中間的callee可能修改slot或物件；不能無條件令P0=P1=P2。有效12-byte配置、非別名extent與所需保存合約仍是前提。

接著query順序是25、26、28、27、29、30、64、65。最終呼叫 `533ce/5347c` 的實參如下；這是呼叫位置與值的還原，未宣告實際C prototype或callee消費範圍。

| 位置 | 值 |
|---|---|
| A0 | 1 |
| A1 | P1 byte+2（零擴展） |
| A2／A3 | query3／query4的完整回覆 |
| A4 | P2 byte+10（零擴展） |
| A5 | 上述0..3組合值 |
| A6 | `45612/456aa`的完整回覆 |
| A7 | P2+4（借用pointer） |
| stack word SP+0 | P2 byte+11（零擴展） |
| stack word SP+4 | query25的**signed low8** |
| stack words SP+8..32 | query26、28、27、29、30、64、65各自的unsigned low8 |

query25使用SLLI24／SRAI24，範圍為−128..127；其餘截成0..255。總共8個register位置與9個32-bit stack words。callee是否依此prototype讀取、是否保存A7或stack位置仍未知。

非null-slot路徑返回最終call的實際A0，epilogue沒有強制改成成功碼。本機store全部位於frame內；這不代表callee沒有持久副作用。

## Cleanup 的順序與保存期界線

cleanup建立16-byte frame，保存RA／S0，重新讀同一固定slot：

- null：略過call與store，以A0=0普通返回。
- 非null P：以P作A0呼叫RAM `20000110`；必須等callee返回，才對固定slot寫0，最後返回provider的實際A0。

沒有在call後重讀slot、檢查是否仍等於P；若中間替換了slot，後續store仍寫0。這只證明「服務呼叫後邏輯slot清除」，不證明物理free、銷毀、清除資料、唯一所有權或保存期已結束。

串回上一階段request：fallback回覆先存入S0；非零才呼叫cleanup，而request返回時忽略cleanup的A0，仍返回所需保存的fallback回覆。fallback返回0的這條本機路徑不呼叫cleanup，因此也不能宣稱request每次返回都會清slot。

## 重播與剩餘工作

```text
python analysis/check_v4160_request_consumers_static.py
python -O analysis/check_v4160_request_consumers_static.py
```

兩種模式要求466次逐指令operand變異與70次逐table-entry變異拒絕、84條選定CFG路徑、65536個low16 ID及65536組flag組合，並精確重播ledger。所有原始APP／candidate／SDK與上游來源身分一併核對。

仍需展開 `45612/456aa`、`533ce/5347c`、source writers、其他query與release provider，以及callback枚舉和缺失ROM pattern。本次沒有執行或模擬目標ISA、provider、callback、RF、NV、MMIO、CSR或trap；既有約88.09%的C重建基準不變。
