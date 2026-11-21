# v4.1.60：按重定位類型驗證直接引用

延續[第一個 HI20 別名實驗](v4160-direct-boot-main-alias.zh-TW.md)。在暫存 ET_REL 副本改成直接引用具名定義，分別移除各自的別名，確認重定位的區段、偏移、類型、addend 及輸入配置區段投影不變；只刪別名不改引用，則增加預期的未定義符號。

| 類型 | 輸入區段及偏移 | 直接引用 |
|---|---|---|
| `R_RISCV_PCREL_HI20` (23) | `.text.tsl9_boot_18724+0x0` | `tsl9_main_family_entry_9008` |
| `R_RISCV_JAL` (17) | `.text.tsl9_callback_state_10766+0x14` | `tsl9_callback_provider_entry_12b24` |
| `R_RISCV_RVC_JUMP` (45) | `.text.tsl9_record_consumer_block_c78a+0xc` | `tsl9_record_decode_entry_c6a8` |
| `R_RISCV_32` (1) | `.rodata.tsl9_original_vectors+0x90` | `tsl9_ring_irq_entry_12c24` |

一般 Python 與 `-O` 各重跑 C / C++ 的基準與 split/leaf 候選四路，共 32 次單項對照。每次保留 71 個別名，6,364 個配置區段內容與位址等於各路未替換的診斷連結，其覆蓋的 76,800 bytes 與原 BIN 一致。這不是同時移除四個別名，也未測具多筆引用或非零 addend 的別名。resident 仍是數值見證；非正式來源整合、獨立建置或可刷寫證據。

下一步：先一起改這四個別名，檢查同一輸入物件上的替換是否互相影響，再按完整引用清單測多引用別名。本提交只發布報告；本機診斷入口為 `experiments/v4160-aggregate-no-ident-next/verify.py --full`。
