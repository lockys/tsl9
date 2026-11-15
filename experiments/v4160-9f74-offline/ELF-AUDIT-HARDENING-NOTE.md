# 0x9f74 diagnostic ELF audit hardening

Offline review identified three fail-open cases in the original selected-layout ELF audit: a partial allocated-section overlap or partial reference could be ignored; inactive or non-executable sections could be treated as code; and a symbol table could link to a section that was not a string table. A local revision rejects these cases and separates the optional safe-gap test from the older-artifact prerequisite.

On the retained local artifacts, the revised local test suite passed seven tests in normal Python and seven under `python -O`. The selected `input-state-decoders-v1` C and C++ diagnostic ELFs each had the original six bytes at 0x9f74, three static address materializations, and no PT_LOAD segments.

**Reproducibility limitation:** the audit and tests were subsequently committed, but they require retained local ELF artifacts that are not included in this note and are not established as freshly built or trustworthy. Tests requiring absent artifacts are skipped. These observations do not establish actual callback execution, live GP, full-image equivalence, device behavior, or flashability.
