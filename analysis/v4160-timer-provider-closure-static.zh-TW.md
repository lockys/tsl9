# v4.1.60：clock191c6／fallback0 的條件性呼叫圖

本階段重用既有完整本體，新增來源、分支排除及呼叫圖串接證據；**新增原指令 bytes=0，C 重建覆蓋率不變**。完整證據見 [ledger](v4160-timer-provider-closure-static.json)。

主要結論是：若 timer 捕捉的 clock pointer 為 matching APP `191c6`，相關 failure／fallback reads 保持0，且 code／table／frame／heap／global 存取有效且不互相破壞，這段 timer／event-wrapper 子圖便可連到已核對的本機函式。這不等同實際 installed binding 或全域 writers 已被證明。

全程離線讀取原 bytes、解碼、處理圖與主機 scalar identities；沒有執行或模擬目標 ISA、clock、allocator、provider、MMIO、裝置或 mutable register／RAM machine。

## 槽位角色先分清楚

| 角色 | V1.31 | V1.40 |
|---|---|---|
| 64-byte config base F | `200031ec` | `2000323c` |
| failure／allocator fallback，F+52 | `20003220` | `20003270` |
| optional config apply hook，F+48 | `2000321c` | `2000326c` |
| timer clock-service word，F-12 | `200031e0` | `20003230` |
| 16-byte clock config copy，F+72 | `20003234` | `20003284` |
| word-source primary，F+36 | `20003210` | `20003260` |
| clock callback，F+68 | `20003230` | `20003280` |

相鄰欄位不是同一個 hook。跨版本偶然相同的絕對位址，也不能推論同一份 binary 的角色互為 alias。

timer 與 allocator 確實讀同一個 F+52，但非零時參數不同：

- allocator exhaustion：A0=1，A1=`full_tag OR(rounded_request<<16)`，A2 為 then-live 值。
- timer allocation failure：A0=4，A1=完整 saved task，A2 為 then-live 值。

兩者都丟棄 hook 回覆並返回0，沒有因 hook 返回而重試配置。非零 raw word 也只代表會進間接轉移；JALR 清除 bit0，不保證有效 function pointer。其他已核對的 record producer／RAM tail 也使用這個欄位，因此這不是整個 binary 只有兩個 reader 的清單。

## Failure 欄位為零的來源及保存缺口

APP builder `199e2..19b16` 的 64-byte config 在 live SP+16。matching `40048` fill 請求清除這64 bytes 後，field52 位於 **SP+68..71**，不是 SP+52。

完整 builder 的 direct stores、UID 輸出 SP+8..13、UID copy-loop SP+40..45 都不覆寫 SP+68..71。因此在匹配 fill 正常完成、source／frame／registers 保持、沒有干擾 writes 前提下，`19aec` 提出 config 請求時，field52 的四個來源 bytes 為零。

matching resident 64-byte config copy 把這四個 bytes 寫到 F+52..55；八個 defaults stores 不碰該欄位。另一個 clock config 是 F+72 的16-byte copy，其 service publication 位於 F-12，亦不重疊 F+52。

這是已識別的來源鏈，不是從 source 一直保存到 timer 的無條件證明：64-byte config 再次執行可重寫 F+52，其他 calls、動態 headers／tables、alias 或 IRQ／DMA／reentry writes 仍可能改變它。startup zero-range 雖也涵蓋此 word，不能當作後續 read 必為零的證據。

## Clock191c6 的輸出與保存性質

APP constructor `19b56..19bd4` 已有完整證據。若13個前置 call／frame 保存條件保持，其16-byte來源為：

```text
c6 91 01 00 ff ff ff ff 80 3e e8 03 00 00 00 00
```

matching `40074` config consumer 將16 bytes 複製到 F+72，之後 fresh 載入 copy word0，發布到 F-12。發布的是 code value `191c6`，不是 short-lived source stack pointer；但這不排除其他 upstream callees 曾保存 stack pointer。

reader `191c6..19220` 共90 bytes／28 instructions，沒有 frame、calls 或 stores，只定義 A0～A5，本機不寫 S registers、GP、SP、RA、A6、A7。timer 傳入 A0 的前一個商值不會被當成物件 pointer；reader 在使用 A0 形成結果前先覆寫它。

其 fresh reads 依序為：

1. `40002818` 的一對 U16，相同才取得 H0。
2. `4000281c` 的一對 U16，相同才取得 L0。
3. `40002818` 的另一對 U16，相同才取得 H1。
4. H0!=H1 時，再取 `4000281c` 的一對 U16，作 L1。

本機返回 `(H1<<16)|L0` 或 `(H1<<16)|L1`。第四對讀取後沒有再查 high halfword。四個 retry loops 沒有 timeout 或固定迭代界限；paired equality、位址常數與打包公式都不證明物理時鐘的 coherent／monotonic／atomic snapshot，亦不保證 reader 返回。

## 零值如何排除兩處未知 hook

allocator 在 exhaustion 的 fresh load 後，零值 branch 直接通往 control-word／frame restore 及返回0；其 hook call 不可達。pruned core 圖有67個 reachable instructions，沒有任何 child calls。

讀取 fallback 前，沒有其他 child call；search 路徑只讀取鏈表，fit 路徑才有 heap stores，而 fit 路徑不會回到 fallback。故在 entry zero、frame／control／slot 分離及無外部 writes 前提下，零值能保持到 exhaustion read。

從這次零值 read 到 core 返回，只有固定 control-word store；timer allocation reply=0 後，至下一個 fresh fallback read 之間沒有 store。因此在同一組保存前提下，timer 也會讀到0、跳過 failure hook。它的 pruned 圖有109個 reachable instructions，剩下五個已解析 callsites。

不能僅由「兩次讀同址」把 snapshots 合併；此串接明確使用中間沒有相關 writes／未知 calls，以及 frame、control、slot 不 alias 的前提。

## 條件性呼叫圖及 frame 界線

在上述值與 mapping 前提下，保留的 calls 為：

- event wrapper → timer、timer lookup、算術 helper。
- APP wrapper 的最後 timer tail → timer。
- timer → 算術 helper兩次、APP reader191c6、timer lookup、allocator core。
- reader、lookup、算術 helper、zero-fallback core → 無 child calls。

所有被保留的動態 calls 已由原始 operands 與條件綁到上述本體。這個 call graph 無遞迴；它不是整個 APP constructor 或 N+136 callback 的完整呼叫圖。

本機 frame32（event wrapper）+48（timer）+16（core），得出此子圖內最大96 bytes；APP timer tail 在轉移前已恢復自己的 frame，timer子圖為64 bytes。這不包含更外層 caller、IRQ、reentry 或整個韌體的 stack 需求。

call graph 無環也不代表函式一定返回：reader 的 paired retries、lookup／allocator search／timer append 都仍有局部迴圈。已核對的正常 frame restores 與 no-S-write leaves，只能在有效且不受干擾的存取下縮小保存義務；不能證明硬體 critical section、實際 allocator ownership 或 async completion。

## 啟動尾段 K=192000 的額外收斂

完整 APP wrapper `19b16..19b56` 在 constructor 返回後，重新讀取 saved task byte，再形成 A1=8192、**A2=192000**，以 fresh `then-live S1+88` 作 unlinked tail。只有 S1 仍為40000及 matching slot40058等條件保持時，才進入上述 timer；constructor 的回覆不作為 task。

沿用 [除數1600的50-node證據](v4160-timer-wrapper-composition-static.zh-TW.md)，此新參數域有：

```text
N = H×192000+800
N highword ∈ 0..2 <1600
floor(N/1600) = 120×H
H ∈ 0..65535，商值 ∈ 0..7,864,200
```

normalization 及兩個 zero correction-products 均保持，走相同50條指令；A1仍為0。checker 窮舉所有65,536個 H 的純 scalar identities，沒有執行算術 helper，也沒有擴大到任意 denominator。

若 timer 入口的16-byte clock config 仍保留來源值，則 H=16000、period=`ffffffff`。在兩次 H／period observations 之前，選定前段及已解析 children 只做 frame／固定 control stores；在不 alias、無外部干擾前提下，兩次讀值可保持，而不是憑同址假設相等。

此名義條件下 Q0=Q1=**1,920,000**，小於 admission threshold=`fe363c7f`，所以 task／service gates 已通過時，threshold 不拒絕。reader 的實際 packed 回覆 R 仍不指定物理單位。

deadline 的單次減法在這組條件下可收斂為：

```text
deadline = (R + 1920000) mod (2^32-1)
```

理由是 period=2³²-1、0<delta<period、R+delta<2×period：若32位加法 overflow，原分支以 modulo2³²減 period，恰等於加回1；無 overflow 而 sum=period 時歸零，其餘保持 sum。這個特定代數結果不改變先前「一般 period 的單次減法不是通用 modulo」界線，也不保證 task admission、配置成功或初始化實際到達。

## 重播與剩餘範圍

[Checker](check_v4160_timer_provider_closure_static.py) 驗證60個指定 raw mutations：28個 reader operands、8個 LHU→LH、6個 core、8個 timer、6個 config 與4個 startup operands。另核對196,608組 packing、65,536個 startup H、pruned graphs 與96／64-byte frame界線。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_timer_provider_closure_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_timer_provider_closure_static.py
```

一般／`-O` 均需精確重播 ledger。後續仍需追查來源欄位至使用點的保存、其他 fallback consumers／非零 ABI、global writers、實際 installed profile，以及 heap／list／node生命週期、MMIO、迴圈進展和事件效果。
