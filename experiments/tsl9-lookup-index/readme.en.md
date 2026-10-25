# Offline index-provenance inspector

[繁體中文](README.md) · [Analysis evidence](../../analysis/lookup-index-2026-10-25/readme.en.md)

From the project root (Python 3.10+, standard library only; tested on Windows):

```sh
python3 experiments/tsl9-lookup-index/audit-v1.py
python3 experiments/tsl9-lookup-index/audit-v1.py --full
```

On Windows,`py -3` can replace `python3`. Existing local measured component,diagnostic ELF and source specifications referenced by the evidence are required. The inspector neither downloads nor builds them. See the [preceding integration](../../analysis/record-copy-integration-2026-10-25/readme.en.md) for reconstruction scope.

The default output is a summary; `--full` includes GP address sites,local writers,unclosed pointer escapes and sequence sources. Reads files only: no evidence writes,firmware/model execution,hardware or network access. Global index bounds and OTA compatibility remain unproved.
