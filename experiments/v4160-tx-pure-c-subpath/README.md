# V4.1.60 TX：header 與 checksum seed 的純 C 切片

選擇原廠 `[0x8ACE,0x8B0A)`，而不是整個 TX：這 18 條指令是一段完整的 header 寫入與 checksum 初值計算，沒有中間呼叫，對後續 payload 複製有實際價值。它不是完整傳送事件、函式或可直接部署的替代品。`header.c` 是 ISO C11 候選，沒有 inline asm、指令 bytes 或 callback；尚未編譯或執行。

## 證據與切點

- [完整原始指令契約](../../analysis/transport-frame-2026-10-23/original-contract.md)及其 JSON：60 bytes／18 指令、原位 base、實際寫入順序及 post-call 寄存器限制。
- [現有歷史完整來源 v6](../tsl9-transport-frame/src/transport_frame.v6.c)與[整理來源](../../src/native/receive/transport_frame.c) 的 `tsl9_transport_pack_8ace`；二者混用 C 和架構 ports，並非純 C。
- [guard-compare](../tsl9-tx-guard-compare/README.md)：前段兩版除 sentinel 分支及 MUL 交換來源外相同；此切片兩個 MUL 運算元交換不影響低 32 位結果。該比較不能證明整個 ABI 或硬體等價。
- 本目錄 Python 從原廠 BIN **只讀**此 60-byte 窗口，固定 raw 並獨立檢查 MUL、AUIPC/ADDI 和四個 store 的 operand。每個 byte 的最低位翻轉與截短都是固定視窗負例；另直接對 operand 檢查做不經固定視窗比對的變異負例。它只檢查完整 BIN 的長度而非完整雜湊，非反組譯器或全程式證明。

入口是已成功 admission 後之 then-live `a2=bank`、`s0=length`、`s3=command`；正常選擇路徑 bank 為 0 或 1。不能因入口 guard 就假定 opaque call 後的 `s0<=1039`。不滿足 bank 或 RAM 前提時，C 行為不在此候選的契約內，不模擬原機故障。

## 記憶體及計算

`tx_ram` 是兩個 1062-byte bank 的**明確 C 物件模型**，概念基址 `0x2000b18c`；每 bank +6 是對齊的 `uint16_t magic`，+8/+9/+10 分別是 command、高長度、低長度。`_Static_assert` 排除不合適的 C 佈局。它不會自動配置到真實固定地址，也不宣稱該 RAM 現有的物件生命週期或所有權。呼叫方必須提供有效物件，回傳值是一般 C 值而非映射到目標寄存器的 ABI。

`D = (0x2000b18c + bank*1062 + 6) mod 2^32`。按順序執行 `SH [D]=0x7f55`、`SB [D+4]=length低8`、`SB [D+3]=(length>>8)低8`、`SB [D+2]=command低8`；可能超過 32 位的 checksum 加總先使用 `uintmax_t` 無號運算再轉回 `uint32_t`，避免特殊實作的有號整數提升溢位；出口 `a4=((length>>8)+(length&255)+command) & 255`、`a1=0`、`a5=D`、`a2=bank`、`a3=base`。其餘暫存器、控制與記憶體狀態不由 C ABI 承諾。數值例：bank 0、length 0x1234、command 0x1ff 的 seed 為 0x45。

此切片不讀 payload，因此不把 source 與 destination 設成互不 alias；後續來源可以指向剛寫過的 header，必須讀當時的 RAM，不能提前 snapshot。這也是不在此延伸實作 copy loop 的原因之一。原迴圈比較 `u16(index)<u32(s0)`，位址卻使用完整 index；大於 65535 的長度可能不終止，並有 32-bit 位址回捲、重疊與記憶體有效性問題。不能以普通陣列 `memcpy` 或上述入口 guard 消去這些差異。

## 邊界與驗證

C 的四個 volatile 存取在抽象機中有序，但 volatile 的存取構成、實際 bus 寬度、endianness、對齊、MMIO 與中斷／DMA 的觀察均依實作；`uint16_t` 的 0x7f55 對應原 little-endian 的 `55 7f` 僅在適當實作成立。C 不保證計算指令或暫存器次序、原址 AUIPC、private ABI、provider 的副作用、callee 保存或尾跳。既有工程的 relocation／編譯結果不能轉移為此候選的證據。需要另外的目標特定整合和獨立驗證；不得據此聲稱可燒錄。

執行 `python -B experiments/v4160-tx-pure-c-subpath/test_offline.py` 及 `python -B -O experiments/v4160-tx-pure-c-subpath/test_offline.py`：僅做原始位元組 operand／負例與獨立 Python 抽象事件例子，包括寫後 alias、bank 邊界、32-bit 邊界及迴圈窄化差異。SHA-256 pin 固定 `header.c` 身分，不證明行為；**Python 沒有測試、編譯或呼叫 C**。也沒有執行 target、ISA／模擬、網路或硬體。
