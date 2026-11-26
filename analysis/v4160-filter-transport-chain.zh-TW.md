# v4.1.60 filter 至 transport 的雙層封包與返回

2026-11-26。本機原廠 APP：76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批將前兩批分開驗證的 [filter](v4160-queue-filter-cpu.zh-TW.md) 與 [transport](v4160-transport-frame-cpu.zh-TW.md) 原指令接起來，不再合成 `0x8a56` 的返回值。全程離線，未知服務仍不執行。

## 實際串接的資料流

原 `0x82d2` 從合成 snapshot 組出兩個 header bytes，再透過固定身分的 V1.31 參考 copy body 搬入 L 個 payload bytes。SDK reference 不等於設備已安裝 provider；loader／installed binding 仍未證。

```text
inner = [((ID>>8)|(tag<<4))&255, ID&255, payload 的 L bytes]
N = L+2
outer = [55,7f,c0,N_hi,N_lo, inner 的 N bytes, checksum]
checksum = (0xc0+N_hi+N_lo+sum(inner))&255
descriptor length = N+6 = L+8
```

例如 ID=`0x123`、tag=2、payload=`a0..a7`，被測案例的 bank frame 為：

```text
55 7f c0 00 0a 21 23 a0 a1 a2 a3 a4 a5 a6 a7 2a
```

這是合成記憶體的組包結果，不是線路封包擷取或實際傳送紀錄。

`0x8a56` 實際執行 GP handle 檢查、lookup 呼叫邊界、bank 選擇、header／payload／checksum 寫入及 descriptor 更新。lookup 精確返回 1 才會選中 bank。完成後尾跳 `[0x40050]`，此時 RA 已恢復成 filter 的 `0x836a`，SP 也恢復至 filter frame。

測試在事件服務入口核對參數與**當時整個兩-bank buffer**，然後只在明示正常返回假設下直接接回 `0x836a`，沒有重跑 transport epilogue 或假造另一層 call。

## 非零 filter flag 不代表 bank frame 已建立

組合測試確認：兩個 filter 位置合格、長度 8，但 lookup 全部返回 0 時，確實提出兩次 `0x8a56` request，卻沒有 bank 寫入、沒有事件尾跳，filter 最後仍返回非零 flag。GP handle 無匹配時也不會建立 frame。

另一類是 snapshot 長度大於 8：filter 本身就不提出 request，但仍可留下非零 flag。這與「request 已提出、transport 未選中 bank」是不同路徑，均不能據非零 filter 返回宣稱轉送成功。

兩個位置選到同一 bank 時，原指令可以重寫同一 buffer、兩度到達同一事件服務參數邊界。本批只證明兩個邊界與相應 buffer snapshot；不推論服務保存了兩份 packet、累計兩次事件或實機傳送兩次。

## 重現與驗證

```powershell
python analysis/test_v4160_filter_transport_chain.py
python -O analysis/test_v4160_filter_transport_chain.py
```

需要標準庫、原 APP、既有 V1.31 carrier 與前批同目錄依賴。可用 `--carrier <path>` 指定相同身分的本機 carrier，不自動下載。一般與 `-O` 均通過：

```text
PASS: 2880 filter/transport cases; 128 oversized-filter cases; 75 nested-header/event-return probes; nonzero flag with no admitted frame; repeated same-bank events; 2 mutations; unknown services NOT executed
```

2,880 組為四種 filter 位置通過組合 × L=0–8 × 五種 GP handle 配置 × lookup 兩次各四種返回值。128 組為兩位置各八種 handle/kind/flag 狀態 × 長度 9／255；另有 5 個 ID × 5 個 tag × 三種事件返回值，共 75 組。

逐例核對 filter 的完整 request／packet、參考 copy 次數、lookup 呼叫序列、transport 實際返回值、事件參數與當下完整 buffer、最終 buffer、filter flag、snapshot／控制 word 保留及 caller RA/SP/S0–S9 恢復。事件服務的返回 0、1、`0xffffffff` 均不決定 filter flag。

兩個記憶體複本負向對照改錯事件 A1 常數，以及第一 bank admission 常數，必須被事件／buffer 檢查抓出。原 APP／carrier 未改，沒有修改共用解譯器。

## 未執行的服務與剩餘界線

`[0x4013c]` 與 `[0x40050]` 仍是指定合成 target。停在入口後只提供正常返回，刻意改寫 caller-saved 暫存器，保存 SP／S／GP、stack、table、snapshot、source、queue、bank buffer 及 CSR／MMIO；沒有替它們產生額外副作用。這些是測試假設，不是已證的服務保存合約。

本批沒有接入 consumer 的整個掃描或執行其零返回後 handlers；該分支仍沿用[前批消費端證據](v4160-consumer-detach-cpu.zh-TW.md) 的限制。也沒有設備 resident、真實事件服務、IRQ、傳送或 ACK 證據，舊封存 README drift 仍未解。

本批增加的是原指令組合驗證，沒有新增 C/C++ 重建 bytes 或重算覆蓋率。可接續追查 consumer 零返回後的分類與本機 handlers，或在已有離線參考中研究未知事件服務。
