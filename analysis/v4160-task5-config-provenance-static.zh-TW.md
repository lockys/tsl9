# task5 配置參數的 APP 來源與條件性 400-byte 請求

接續 [物件與 backing 配置](v4160-task5-allocation-static.zh-TW.md)，本次把原本完整值域的 n、flag、h，接回兩條 APP 設定建立流程。**現有原指令支援 n=8、h=251、flag=0 的來源候選；若這些欄位保留至配置時的兩次 n 讀取，backing 請求就是 400 bytes。** 這不是實際 provider 已綁定、設定已同時可達或配置已成功的證明。

本階段重用已驗證函式，新增程式碼覆蓋計數為 **0**；C 重建覆蓋率不變。未執行韌體、target ISA、provider、callback、MMIO 或硬體。

## 第一份 64-byte 設定：n=8 與 h 的輸入 251

APP 完整設定建立端位於 `0x199E2..0x19B16`，呼叫 `0x400A4` 時傳入 SP+16。以下是直接寫入與欄位換算：

| 原指令 | APP frame 位置 | 設定內位置 | 位元值 |
| --- | --- | --- | --- |
| `0x19A54/0x19A56/0x19A5A` | U16[SP+30] | U16[config+14] | 4096−2045 = `0x0803` |
| `0x19A5E/0x19A62` | U16[SP+32] | U16[config+16] | 251 |

在 little-endian 合約下，`0x0803` 的低位 byte 是 3，高位 byte 是 **8**。配置公式讀的是 config+15，因此 n 來源是 8，不能誤用 config+14 的 3。

候選 `0x43C7E`／`0x43D0A` 請求將 64 bytes 複製至 F=`0x200031EC`／`0x2000323C`。copy 後的 defaults 對 F+15 僅在原值為零時寫 5；F+16 的 halfword 僅在零時寫 27。因此原 8／251 在相應未受干擾的 copy 與 defaults 路徑上會保留。

接著角色 initializer `0x5362E`／`0x536DC` 重新讀取 U16[F+16]，計算：

```text
h = min(fresh U16[F+16],251)
U16[B+46] = h
```

B=`0x200033B8`／`0x20003408`。來源若仍為 251，就寫 h=251；不論入口 halfword 是多少，這個特定 store 的 h 都介於 0..251。但該界線不能自動延伸越過後續 calls、tail、其他 writers 到實際配置時。

checker 核對 APP 後續直接 frame stores、UID helper 輸入區間與 UID 複製迴圈目的區間均不覆蓋上述 SP+31、SP+32..33。它沒有把間接呼叫或硬體副作用當作不存在；這些仍需要對應的保存前提。

## 第二份 16-byte 設定：flag 來自另一條來源

上一輪配置函式讀的 flag 是 C+164；C=F−80，因此也就是 **F+84**。此位址不在第一份 F..F+63 的 64-byte 設定裡。

另一個 APP constructor `0x19B56..0x19BD4`，在 `0x19B66` 將自身 SP+12..15 清零。完成前置呼叫後，以 SP 作為另一份 16-byte 設定的指標，經 `0x40074` 交給候選 `0x43F46`／`0x43FD2`。

該候選的目的區間是 F+72..F+87；其 byte12 正是 F+84=C+164。因此，第二份設定的 byte12=0 若經已接受的 copy 路徑保留，便提供配置公式的 flag=0。

兩份目的區間不重疊。不能將第一份設定的 config+12，或某個未辨識的 flag，拿來替代第二份的 byte12。

既有完整前置 callees 合約已核對 constructor 的 32-byte frame 內那份 16-byte 設定，在正常返回與有效 stack／MMIO、無外部干擾等前提下保留；其中 mode3 helper 的 80-byte child frame 寫入區間位於 caller SP 以下。這是條件性 frame 保存，沒有證明輪詢一定完成。

另外，第二個候選會在驗證與 copy **之前**呼叫 optional hook。hook 可能修改來源；因此 APP 呼叫點的零值不等於 post-hook copy 時必然仍是零。函式的 null-config 分支也會直接將目的 byte12 寫零，但本輪沒有將 APP 的 nonnull frame 指標套入該 null 分支。

## 將來源與配置公式接起來

上一輪已驗證的公式是：

```text
D = n+1 if flag==0 else 2*n
K = D-n
R = (32*floor((h+33)/32)) & 0xFFFF
W = (16*D + R*K) & 0xFFFF
```

| 保留的來源值 | D | R | 請求 W |
| --- | --- | --- | --- |
| n=8、h=251、flag=0 | 9 | 256 | **400** |
| n=8、h=251、flag 非零 | 16 | 256 | **2304** |

因此只要 n=8 及 initializer 寫入的 h 界線保持，即使暫時不確定 flag，這兩類大小都不會發生 U16 截斷。完整 65,536 個 initializer 輸入 halfword 經 clamp，再分 flag 的零／非零兩類，共核對 131,072 組純算術組合：

- flag=0 時，R 為 32..256，W 為 176..400。
- flag 非零時，W 為 512..2304。

這是來源限制下的算術域；前一輪完整 n／h 域中出現的截斷組合，仍不能稱為實際可達錯誤。

若配置前後兩次 n 都是 8，且 h=251、flag=0，正常非零配置路徑會形成 9 筆 descriptor、1 筆 payload row、8 筆另一類 row。descriptor 區佔 144 bytes，payload 需求為 256 bytes，合計 400；backing initializer 返回 P+144，B172 保存 base P。這個布局仍依賴 core 實際返回有效 extent、地址有效、fresh n 保留及無衝突別名等前提，不代表配置成功或 payload 已填妥。

## 尚未封閉的保存界線

本次證明的是來源、位址關係及相應條件下的算術結果。下列缺口仍保留：

- 第一份設定 copy／defaults 後的 APP callback `0x197F0`、其他 nested callees 與 writers。
- initializer 在 h store 後的三個 calls、tail，以及 object 建立與 backing 配置前的其他流程。
- 第二份設定的 optional hook、實際輸入／目的內容及 copy 後的其他 writers。
- n、flag、h 是否在同一次配置中同時保持來源值，尤其 allocator 返回後重讀的 fresh n。
- 實際 installed provider 綁定、配置／release 的 ownership、release 後存取與 V34 下游。

沒有以 snapshot 假設替代 fresh reads，也沒有以 forward copy 合約推論 memmove／原子快照或來源指標保存期。

## 重播驗證

[checker](check_v4160_task5_config_provenance_static.py) 與 [精確 ledger](v4160-task5-config-provenance-static.json)

```powershell
python -B analysis/check_v4160_task5_config_provenance_static.py
python -O -B analysis/check_v4160_task5_config_provenance_static.py
```

36 個 APP／候選 producer-source 指令變異須被拒絕；一般與 `-O` 須逐 byte 重現同一 ledger。原 APP、兩候選、SDK、既有 copy／配置／前置 callee 合約與 Xwchc 來源向量均重新核對。GitHub 僅新增這三份分析／驗證檔案，原始 BIN 與其他工作不變。
