# 最後一個外層 ID11 初始化、4N 保留空間與 outer 返回 gate

接續[ID10 配置與NV初始化](v4160-id10-nv-initialization-static.zh-TW.md)，本次完整核對 `4d172`／`4d20a`、三個直接callee、outer epilogue及final gate。六個outer initializer至此都有原指令的本機合約；整條鏈的實際可達、provider與跨呼叫保存仍是條件，尚未完成整個v4.1.60反組譯。

| Body | V131 範圍（右端不含） | V140 範圍（右端不含） | 每版bytes／指令 |
|---|---|---|---|
| ID11 initializer | `4d172..4d1b0` | `4d20a..4d248` | 62／19 |
| factory/defaults+fill | `493f2..494ee` | `4948a..49586` | 252／72 |
| fixed defaults | `4b35e..4b456` | `4b3f6..4b4ee` | 248／72 |
| pool margin clear | `4b33c..4b35a` | `4b3d4..4b3f2` | 30／11 |
| outer epilogue | `6dd7e..6dd86` | `6df6e..6df76` | 8／3 |
| final gate | `6d572..6d682` | `6d75e..6d86e` | 272／84 |
| special ID setter | `4600e..46018` | `460a6..460b0` | 10／3 |

合計1764個原始bytes、528條指令。所有operands、呼叫／分支目標與body SHA256固定於[檢查器](check_v4160_id11_outer_tail_static.py)；完整指令、CFG、地址區間及8張gate路徑憑證見 [JSON](v4160-id11-outer-tail-static.json)。全程沒有執行或模擬原目標、provider或NV服務。

## ID11 保存與兩個 byte 發布

沿用條件性入口A0=11、A2=12，initializer用16-byte frame保存RA、S0，再以S0保存完整入口A0。它依序呼叫factory、fixed defaults、pool clear。

factory自身另有16-byte frame，會暫用S0=2並呼叫兩次RAM `2000039c`，要求清零 `20002f64`／`20002fb4`長6 bytes，以及 `2000300c`／`2000305c`長24 bytes。其正常返回必須保有自身S0及frames；它恢復的caller S0才是ID11。fixed defaults及pool clear本機不定義S0。

initializer先將S0低byte寫至 `20002edf`／`20002f2f`，fresh讀取word `20002f80`／`20002fd0`作為pool clear入口pointer，返回後再將同一ID低byte寫至 `20002eee`／`20002f3e`。

最後恢復S0／RA、釋放frame，以A0=`4cff6`／`4d08e`尾跳既有callback登記leaf。成功插入返回0；滿表返回19且不寫表。outer不測試這個返回值，也未在此執行callback。

## 4N 空間的用途接上第三個 initializer

pool clear fresh讀取 `U8[200033b5/20003405]`為N，這是較早ID6 resource寫入的low2欄位。它只讀一次count：每筆步長4，SH `ffff`至+0、SB0至+2，byte+3不寫。完整word index遞增，N的generic byte域為0..255，因此最多255筆；若原low2持續保存，可收緊為0..3。

其入口pointer由 `20002f80`／`20002fd0`取得。[較早ID8 resource](v4160-id8-initialization-static.zh-TW.md)在相同slot保存：

```text
end pointer = P + 190*N + 6
request     = 194*N + 6
```

若pointer、count、配置extent及所需provider／frame／物件條件持續一致，這次N筆4-byte區間恰好位於：

```text
[P + 190*N + 6, P + 194*N + 6)
```

這說明先前layout之後的4N保留空間與目前的資料流吻合。檢查器涵蓋全部256個N及每筆store的區間；它只證明條件性幾何，不會把跨多個未知服務保存的pointer或count當成已知實際值。每筆僅有3個bytes被本機寫入，也不能稱整個4N空間已被清零。

N=0時，pool leaf不解參考入口pointer，故pointer=0本身不阻止該leaf RET。其返回A0是入口pointer加4N（modulo32），不是強制0；後續caller沒有測試這個結果。30-byte邊界不包含緊接著的另一個LI0／RET函式。

## 兩版地址差異與來源缺口

本次模板分開固定兩版：大多數scalar RAM地址差80 decimal，但三個RAM object base差76 decimal；數個ROM pointer差496 decimal，不能全部套用同一個relocation。

fixed defaults保存的V131 ROM pointer如 `6ea80`、`6ea70`、`6ea6c`，V140對應亦超過各自候選檔右端。當前body只存pointer，沒有解參考它們，因此可以核對寫入值，**不能宣稱超出檔案的資料內容或有效性已知**。

factory與defaults的全部固定非frame stores、兩個fill目的區間均核對避開task metadata、T、相關config/source/hook、low2/count、margin pointer及final-gate快取byte。這排除已列固定區間的直接重疊；RAM code/data的實體alias、provider副作用與其他writers仍需另外證明。

## Outer frame 釋放後的三種24返回

最後initializer的callback登記leaf普通RET後，outer epilogue取回saved RA、釋放16-byte frame，以不設link的跳躍進入final gate。gate重新fresh讀config F+21，取low2；這不是沿用先前pool count的讀值。

三類返回24的本機路徑為：

1. fresh low2=0：不建立frame，直接返回24。
2. low2非零，但fresh cached ID byte `200035f5`／`20003645`不等於`ff`：恢復自己的16-byte frame，返回24。
3. low2非零且cached ID為`ff`，但task-registration返回`ff`：先將返回低byte存回cache，再恢復frame返回24。

這些gate實際值尚未確定，不能把先前某個source案例當成已證明的選路。cached ID已存在時也沒有新增task。

## 可選第13筆task與成功路徑

若low2非零、cached ID為`ff`，且fresh task count仍12、capacity仍≥14、table pointer仍T=`200047f4`，有效extent／frame／非alias等條件成立，gate以handler `6d26c`／`6d458`登記entry12=`20004824`，回覆ID12、count變13。

返回值先存入cached ID byte；通過非`ff`檢查後，它在A0未被改寫前進入已展開的special ID setter，將12寫至 `200033ae`／`200033fe`，明確覆寫較早的`ff`。

其後原指令要求：

| 服務 | V131參數地址；V140各加`50` hex |
|---|---|
| fill兩個16-byte buffer | `35d4`、`35e4` |
| NV read | `(2,16,35d4)`、`(3,16,35e4)` |
| copy16 | `35d4→35f8`、`35e4→35b8` |
| NV read | `(4,4,2ff4)` |

各copy來源／目的區間分離，但實際provider綁定、單位、輸出、保存與物件有效性仍未由地址關係確定。NV返回值沒有被測試；在所有服務正常返回並保存所需S0–S2、SP／frame／RA／GP／code等條件下，最後強制A0=0、恢復frame並普通RET。A1/A2沒有在最後服務返回後重新固定。

因此這個outer結果不能簡化成固定成功值：本機三類出口返回24；可選task成功路徑在完成服務後返回0。actual handler、callback及APP後續返回鏈仍待展開。

## 離線重播

```text
python analysis/check_v4160_id11_outer_tail_static.py
python -O analysis/check_v4160_id11_outer_tail_static.py
```

兩種模式均要求528次逐指令operand變異拒絕、256個reserved-margin域、兩版各4張gate CFG路徑與精確JSON重播。APP／candidate／SDK與上游來源身分證據一併核對。未執行或模擬目標ISA、provider、NV、callback、MMIO、CSR或trap；本次靜態證據不增加既有約88.09%的C重建基準。
