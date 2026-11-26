# v4.1.60 D05C 本機寫入與兩個 callback 的清除流程

2026-11-26。decoded APP：76800 bytes，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。延續 [A204與10816](v4160-a204-local-cpu.zh-TW.md)，本批在有限CPU內執行原 `0xd05c`、`0x9f74`、`0x1061c`，接上原 `0x901a` dispatcher與 `0x90b0` 取消流程。

所有記憶體、服務指標及事件皆為離線fixture，沒有設備或provider執行。C已有 `src/native/receive/state_output_dependencies.c`、`rom_dependencies.c`、`callback_flow.c` 對應；本批只新增驗證及說明，未重建C、未改共享CPU或提高C覆蓋百分比。

## `0xd05c` 可以直接自然返回

原函式不建立frame、不呼叫其他函式，PC-relative buffer為 `0x2000bf38`。依序寫四個bytes：

```text
[1, low8(A0), low8(-A2), low8(A1)]
```

A2本身變成 `(-原A2)&0xffffffff`，A4=1、A5=buffer；A0/A1、RA/SP、GP及S暫存器保持。RET直接返回caller。這只證明本機資料布局，不賦予其通訊協定或硬體語意。

先前 [A204](v4160-a204-local-cpu.zh-TW.md) 的GP+172非零分支會尾跳 `d05c(3,1,0)`；本批已直接執行至原RET，buffer=`[1,3,0,1]`，A0=3。1530組實際A204/D05C串接取代此分支先前的未知callee邊界，沒有假造返回。這些結果仍基於合成GP狀態，不證明實機可達時序。

## `0x9f74` 只清 GP+175

原指令只有 `U8[GP+175]=0` 及RET，所有暫存器包括傳入payload A0都保持，沒有frame或服務呼叫。全部256個舊byte × 3種payload已核對，左右鄰欄位保持。

270組實際 `901a → 表中key → 9f74 → 905a → caller` 涵蓋每槽、row flag={0,1,255}、payload={0,1,全1}、raw key={9f74,9f75}。JALR清key最低bit，因此兩個raw key均可執行此函式。一次性槽由dispatcher先清；保留槽則保持表內容。callback只清GP+175，不解參照payload。

## `0x1061c` 先清旗標，再取消自己的偶數key

原函式依序：

1. 清 `U8[0x2000bfb8]=0`。
2. 將A0覆寫為完整key `0x1061c`。
3. 無連結尾跳 `0x90b0`，保持caller RA/SP。

輸入payload被覆寫，沒有解參照。取消函式搜尋**第一個完整word等於1061c**的表槽，並不是依本次事件index定位。

| dispatcher及表狀態 | 實際續段 |
|---|---|
| 一次性flag=0，無其他同key | dispatcher已清原key/payload；取消miss，自然返回1至905a，dispatcher再自然返回剩餘16-bit mask |
| 保留flag非零，偶數key、payload=0 | 取消命中，清key/payload後尾跳 `[4005c]`，停在未知event服務入口 |
| 保留flag非零，偶數key、payload非零 | 取消命中，先呼叫 `[40068]`，停在未知free入口，尚未清槽 |
| 存在其他偶數duplicate | 取消最低index的相同key，可能不是此次事件選中的槽；event bit使用被取消槽index |

一次性原槽的payload即使非零，也已在callback前清掉；無duplicate時取消不會因此進free。這是原路徑的可見行為，不能由此推論payload ownership、實際配置或釋放合約。

取消函式的nested frame為dispatcher caller_SP−32。miss或event尾跳時恢復到dispatcher frame（caller_SP−16）、RA=`0x905a`；free入口RA=`0x90e0`，nested frame仍存活。只有實際miss自然返回後才執行dispatcher epilogue；沒有把event/free入口當作已返回。

## 奇數raw key：能執行同一函式，不一定能取消同一槽

表中raw key=`0x1061d`時，JALR清bit0，仍進入原1061c。但callback傳給90b0的是**偶數1061c**，取消使用完整word比較，所以不匹配原奇數key。

無其他偶數duplicate且原槽為保留槽時，self-cancel會miss，奇數key仍留在表中；callback的BFB8旗標則已清零。若另有偶數duplicate，可能取消那個槽。此差異已納入所有槽及一次性／保留矩陣，不能把執行位址相同簡化為表key相同。

## 註冊至注入事件的條件性串接

30組先執行原9124，分別註冊key9f74或1061c至每一槽，採用既有 `[40058]` 正常返回0假設，再由fixture明示輸入事件。原dispatcher會先清一次性槽；9f74直接返回，1061c則self-cancel miss，兩者都執行原dispatcher返回。

這30組保留服務的正常返回／保存前提，只證明表格式與APP消費者相容，**不證明provider實際儲存callback、投遞事件或保證該時序**。

## 驗證

[test_v4160_callback_closeout_cpu.py](test_v4160_callback_closeout_cpu.py) 使用 `check()`，一般與 `-O` 模式檢查一致：

```text
python analysis/test_v4160_callback_closeout_cpu.py
python -O analysis/test_v4160_callback_closeout_cpu.py
```

輸出：

```text
PASS: 65536 packet byte pairs; 768 full-word negations; 1530 actual A204/D05C returns; 768 pending-clear cases
PASS: 270 clear callback/dispatcher chains; self-cancel/duplicate chains {'miss': 360, 'event': 3630, 'free': 4110}; 180 retained odd-key misses; 30 registration/injected-event returns; 4 mutations
PASS: exact stores/frame/key equality; nonzero one-shot payload not freed on no-duplicate path; free/event providers NOT executed
```

65536配對窮舉A0/A1低bytes並帶非零高位；另768組覆蓋A2完整word前綴與所有低byte的二補數負值。8100組self-cancel矩陣包含每槽、raw key偶/奇、三種row flag、三種原payload、無duplicate或每個其他duplicate位置、零/非零duplicate payload；統計不表示8100組都自然返回。event/free分支只驗證到服務入口。

四個記憶體副本mutation：NEG改ADD、GP+175 store來源zero改A0、BFB8清零來源改A5、self-cancel key1061c改1061e。均由指定的stores或參數檢查拒絕，不把解碼或unmapped錯誤當作偵測。原BIN未修改；每段完整核對存取、stores、frame、返回及canary。

原區段SHA-256（右界不含）：

| 範圍 | SHA-256 |
|---|---|
| `d05c..d07c` | `7aeb37e5fa35b5285db6506c1cb8a34b1774f2ed427169e29dd2405aaafa5259` |
| `9f74..9f7a` | `551e0bd058e88a00ef29c2d561808a758ace0ff36fdb09af56e8a915ccdd31e8` |
| `1061c..10630` | `f274d15ad8921781d519c0757976841267827eaee180fcbb02f4b794f0ece0ca` |

後續仍需追查BF38/BF0C等狀態的消費者、bit1 handler `0x13d48`、真正provider綁定與保存／payload合約，以及完整啟動與非同步事件。沒有執行未知provider、IRQ或設備操作。
