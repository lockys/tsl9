# 0x9884 / 0x9888 LO12_S anchor 靜態證據

此目錄只用 Python 標準庫唯讀解析指定 ELF32 LE RISC-V ET_REL；不編譯、不執行或模擬目標、不使用網路或硬體，也不修改原 guard。這不是 linker、ABI 完整實作，亦不證明完整 BIN 的內容或執行行為。

本機指定物件存在，長度 10236，SHA-256 `62ff2fa9dde7e667280b945cb901484ea5829047c88c4d058da2c00db40ef784`。它不在目前 Git 追蹤清單中，因此不是 public test 的必要輸入。`vector_native.c` 另行固定 SHA-256 `bcbb0a67e1f473c1f92ed44a67ca4fa64a86f12d53a9786302fc3fa34ff322dd`；兩個 hash 是各自的內容身分，不證明編譯來源關係或來源可信。缺少任一檔案或 hash 不符時 CLI fail closed；測試在缺檔時跳過本機實物檢驗，合成測試仍可重播。若檔案存在但不符 pin，測試失敗。

實物 `.text.tsl9v4160.handler_979e` 的 section-relative HI/LO offsets 為 `0xe6`/`0xea`；依此 section 名稱所記位址 `0x979e` 對應 `0x9884`/`0x9888`，並非 ELF section 的載入位址證明。LO type 25、addend 0，其 symbol `.Lvec_00009884` 位於相同 section 的 0xe6；唯一 HI type 23 指向未定義 symbol `__tsl9v4160_data_2000bebc`，addend 0。對應 bytes 為 `97270020`、`23aca762`，AUIPC rd 與 store rs1 都是 x15。名字中的位址不代表已解析的 symbol value。

```text
python -B experiments/v4160-lo12s-anchor-evidence/evidence.py
python -B -m unittest discover -s experiments/v4160-lo12s-anchor-evidence -v
python -B -O -m unittest discover -s experiments/v4160-lo12s-anchor-evidence -v
```

測試以程式合成的 ELF 覆蓋成功、錯誤 relocation 類型、缺少及重複 HI、anchor、指令與暫存器、addend、索引及界限等負例；合成資料不是對實物的獨立實證。解析器限縮至選定 section、指定兩個 offset 和一組 symtab/rela，不是通用 ELF 驗證器；不處理 extended section numbering。只接受實物所示的狹義樣本策略：program header 的 offset、entry size、count 均須為零；symtab 的 null symbol 必須全零，`sh_info` 必須界定 local 與非 local 符號，anchor 必須是非零 local symbol。選定的 HI、LO 各 offset 最多一筆 type 51，且 symbol index 和 addend 均為零；它不計入 HI/LO 唯一性證明，也不解讀其語意。這些限制不假定其他 ELF 組合普遍不合法。
