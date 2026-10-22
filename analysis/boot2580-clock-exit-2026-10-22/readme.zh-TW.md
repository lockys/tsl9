# 原始 clock 正常出口契約

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

這是來源契約草稿，不是新的 native 實作。檢查器重讀官方 BOOT ID2580 與 Runtime ID2966，核對相同234B／93指令、既有來源 ledger、全部 own-written RD、正常出口關鍵 operands及兩個reset caller後綴。不執行HOST／ISA／target／MMIO，也不編譯或連網。

## 契約與前提

令 **W** 是 BOOT `0x2CF8`（Runtime `0x187CA`）那一次 `LW A4,12(SP)` 新讀出的完整u32。

| Normal RET condition | A2 | A3 | A4 | A5 |
|---|---|---|---|---|
| Fresh `W != 1` | `0x20000` | `0x40021000` | full u32 `W` | `1` |
| Coherent private stack, no interference; skip | same | same | `0` | `1` |
| `W == 1`, both later polls return normally | same | same | `8` | `8` |

共同前提是執行已核對的原始leaf、沒有改寫程式碼或暫存器的非同步干擾、所列存取／RET正常完成；任一正常RET才適用，沒有保證兩個後段poll終止。第二列另需有效、disjoint、coherent的private stack，沒有外部或alias寫入，讓先前寫入的selector0／1被原樣讀回。任意live ready word範圍只約束該次memory observation，不允許任意改寫GPR或控制流；不能把第二列的A4=0套用到此較寬範圍。A0不是本函式成功碼。

關鍵最後寫入均由原始raw核對：

| Role | BOOT PC | Runtime PC | Raw / operand |
|---|---|---|---|
| A2 fixed | `2C8C` | `1875E` | `37060200` LUI A2,0x20 |
| skip A3 | `2CCA` | `1879C` | `b7160240` LUI A3,0x40021 |
| fresh W / skip A4 | `2CF8` | `187CA` | `3247` LW A4,12(SP) |
| skip A5 | `2CFA` | `187CC` | `8547` LI A5,1 |
| skip edge | `2CFC` | `187CE` | `631ff704` BNE A4,A5,2D5A |
| configure A3 | `2D40` | `18812` | `b7160240` LUI A3,0x40021 |
| configure A4 | `2D50` | `18822` | `2147` LI A4,8 |
| configure fresh A5 | `2D52/54` | `18824/26` | `dc42/b18b` LW A5,4(A3); ANDI A5,12 |
| configure exit | `2D56` | `18828` | `e39ee7fe` BNE A5,A4,2D52 |

skip邊直接到共同SP恢復／RET，故A4=W、A5=1；configure正常退出最後poll必有masked A5=A4=8。完整RD清單證明A2無後續覆寫，兩條路徑的A3最後定值亦未被覆寫。沒有把一般ABI慣例當作原始碼證據。

## 靜態條件反例

- 若允許fresh W=`0xDEADBEEF`，skip正常出口A4也為此值，A5=1；因此一般live-word契約不能聲稱A4總是0。
- 第一poll曾讀到ready，之後 `0x2CEA` fresh control bit17卻為0，private coherent stack仍走skip；不能沿用先前ready值。
- 第一poll到counter4096才退出，但 `0x2CEA` fresh bit17為1，仍選configure；不能將先前timeout樣本當最後狀態。能否最終RET仍取決後兩poll。

這些是從原始條件推導的資料選擇反例，不是執行、模擬或硬體觀察。

## Reset 後綴與仍然 live 的值

BOOT call `2C4E` 返回 `2C52`；Runtime call `18720` 返回 `18724`。兩者接著各有4條指令：AUIPC T0、ADDI T0、CSRW MEPC,T0、no-link JAL x0,`40000`。BOOT設定MEPC=`1A52`，Runtime=`9008`。檢查器直接讀原BIN並核對這10條call／suffix raw與operand，不引用舊絕對路徑收據。

後綴不讀寫A2–A5，也沒有其他callee；這些殘值被原樣帶至外部resident交接，**不代表dead registers**。未證明resident、後續callee、IRQ或硬體不觀察它們，也未證明installed resident身分。

## 重播

```sh
python analysis/boot2580-clock-exit-2026-10-22/check.py --project-root .
```

`--emit-ledger`只向stdout輸出草稿JSON，不寫檔。預設重播重讀兩原檔／tracked依賴、核對[ledger.json](ledger.json)，另以6個實際raw operand XOR變異驗證A2定值、fresh slot offset、A5常數、skip branch、A3目的register及最終mask的拒絕。變異走operand gate，並非只依整體firmware hash拒絕。完整93row表沿用[已發布clock來源](../boot2580-clock-2026-10-22/README.md)，不重複複製。
