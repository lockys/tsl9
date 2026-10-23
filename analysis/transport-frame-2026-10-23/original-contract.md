# Transport framing 原始契約

[English](original-contract.en.md) · [完整 JSON／96 rows](original-contract.json) · [既有逐指令證據](../queue-filter-2026-10-23/next-transport.json)

官方 ID2966 V4.1.60 的 `[0x8A56,0x8B6E)` 共280 B／96 instructions，SHA256 `3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b`。本輪 fresh r2 與原 BIN、既有96 rows 全同；另依原始 encoding 核對 branch／C.J／C.JALR／C.JR，不使用 ESIL。原 BIN 與工具完整雜湊、recipe、每塊雜湊均在 JSON。

局部 CFG 有96 nodes／101 edges，所有 rows 在「opaque call 返回其 encoded RA」的語法模型下可達；不證明每條路徑實際可行。出口 `8ACA RET`、`8B50 JR T1`、`8B6C RET`。RET 後 `8B52..8B6C` 是回到 `8B0A` 的 copy block，不能截除。以下是分析切點，並非原始 symbol/FUNC 證明。

| 範圍（end exclusive） | B | i | 區塊 |
|---|---:|---:|---|
| `0x8A56`–`0x8A5E` | 8 | 2 | entry_guard |
| `0x8A5E`–`0x8A7A` | 28 | 12 | frame_capture_and_first_channel_match |
| `0x8A7A`–`0x8A90` | 22 | 7 | first_admission_call |
| `0x8A90`–`0x8A96` | 6 | 2 | first_admission_result |
| `0x8A96`–`0x8AB6` | 32 | 10 | second_admission_call |
| `0x8AB6`–`0x8ABE` | 8 | 3 | second_admission_result |
| `0x8ABE`–`0x8ACC` | 14 | 7 | ordinary_restore |
| `0x8ACC`–`0x8ACE` | 2 | 1 | select_bank_zero |
| `0x8ACE`–`0x8B0A` | 60 | 18 | header_and_checksum_seed |
| `0x8B0A`–`0x8B14` | 10 | 3 | copy_test |
| `0x8B14`–`0x8B52` | 62 | 22 | checksum_metadata_restore_tail |
| `0x8B52`–`0x8B6C` | 26 | 8 | cold_copy_body |
| `0x8B6C`–`0x8B6E` | 2 | 1 | unframed_reject_return |

`8A5A` 的 unsigned A3>1039 檢查先於 frame；拒絕時本段不改 A0／SP。通過後建立32 B frame並保存 S0/S1/S2/S3/RA，依序 capture S2=A0、S0=A3、S1=A2、S3=A1。

`GP+150`／`GP+154` 的 fresh halfword 與完整32-bit channel比對，拒絕 FFFE。`8A8E`／`8AB4` 各自 fresh 讀 `[4013C]`、C.JALR A5，RA=`8A90`／`8AB6`；A0==1選 bank0／1。第二個 port 的 A2/A3 可能是前一個 port residue，沒有從 S1/S0 回填。每次 GP、S0..S3、SP 與 memory 的後續使用均依 then-live 值，沒有普通 C ABI 保留假設。入口長度限制沒有在呼叫後重做；copy test 精確是 `u16(index)<u32(S0)`，不能宣稱 post-call 長度、終止或指標範圍已被1039限制。

位於原位的 PC-relative base=`2000B18C`，bank stride=1062，D=base+bank*1062+6。原始 store 順序為 SH magic7F55、SB len低 byte、SB len高 byte、SB command；copy從S1逐 byte讀至D+5+index，逐次加總並mask255；最後checksum放D+5+L。metadata寫 SH[bankbase+2]=u16(L+6)、SH[bankbase+4]=0。checksum的代數式是 `u8(command+u8(L)+(L>>8)+sum(payload bytes))`，須以原始迴圈正常完成為條件。這只證明 byte equations，未辨識物理協定或證明傳送成功。

尾段先 fresh restore RA/S1/S2/S3，再寫metadata；S0直到 `8B40` 才restore。`8B46` fresh LW[40050]→T1，A0=fresh LBU[GP+148+4*bank]、A1=1、SP+32，`8B50 C.JR T1`不寫RA。一般restore路徑保留A0 residue；此函式沒有統一成功回傳值，也沒有CSR指令。

Caller filter的 `8356` opaque port後，`8358`／`835C`／`8360` 分別讀 then-live S1+2／S0+2／SP+4。`832C`先存 S4、`832E`才檢查DLC，因此filter非零也不等於成功轉送。

可讀 C 可承擔比對、bank乘法、byte／checksum與copy loop；frame、fresh GP／S-register／SP取值、兩 admission、PC-relative base與真實tail留明示architecture ports。可新增的離線診斷僅是有來源snapshot的長度／alias／wrap檢視、給定byte record的format/checksum檢查，以及filter結果與傳送證據分離；不能自行補provider、隱含nonalias或將它稱為座椅／免打擾實作。

未執行target、ISA、ESIL、MMIO、硬體或網路；未重建／燒錄BIN。resident ABI、IRQ/fault、physical ownership、全域incoming references、傳送／硬體結果仍未知，`firmware_ready=false`。

已另讀 candidate `experiments/tsl9-transport-frame/src/transport_frame.v1.c`，SHA256 `6dad92397a447d83103fbddbfda661117089968967cba4676473785e92ba5f13`：已確認一個具體 mismatch，兩次 admission load 使用`0x0040013C`，原BIN實際是`0x0004013C`；撤回先前未發現 mismatch 的判斷。13個private regions在`8A90`／`8AB6`另切回續接點，保留post-call取值。這是來源閱讀結果；編譯flags、IR、96條native instruction、spill/frame、relocation及全碼相同仍須獨立實測，不能由source review代替。

位址更正：原始`LUI a5,0x40`（raw`b7070400`）產生`0x00040000`，`LW316(a5)`（raw`83a7c713`）加`0x13C`，有效位址為`0x0004013C`。本輪早先摘要誤寫`0x0040013C`；此更正依原始bytes，不代表原BIN曾變動。tail仍是`0x00040050`。兩組 admission及tail位址推導已列入JSON。
