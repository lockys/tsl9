# v4.1.60：0x105c4 與直接連結依賴的原位驗證

延續[兩個位址引用](v4160-105c4-direct-caller-link.zh-TW.md)，將診斷暫放的 0x107c6 與 0x1083c 移回原址。LLD 直接連結原個別輸入，不經 `ld -r`，不使用數值替代符號，並啟用 `--no-relax --gc-sections --no-undefined`。兩段引用與目標為根，其餘依賴由連結器保留。

| 原址 | 與 BIN 相符的機碼 bytes |
|---|---:|
| 0x105c4 | 12 |
| 0x107c6 | 18 |
| 0x1083c | 12 |
| 0x10944 | 22 |
| 0x10bbe | 4 |
| 0x10bde | 26 |

普通 Python 與 `-O` 各四路（C/C++ 基準及 split/leaf 候選），每路六段共 94 bytes 逐位元組符合原 BIN。兩組 AUIPC/ADDI 仍解碼為 0x105c4。C++ 的 `.eh_frame` 只做基準／候選比較，不計入 BIN 相符機碼。此結果是局部保留集合，不是新增反組譯覆蓋、整圖或硬體驗證，也未解決聚合的 `sh_link=0`。原 BIN 和正式來源未改。下一階段應按現有配置表擴大直接連結並逐段對照，而非繼續重驗這六段。

本機重跑：`experiments/v4160-aggregate-no-ident-next/verify.py --baseline <saved baseline> --objcopy <llvm-objcopy.exe>`；本提交只發布報告。
