# F030 C hypotheses: bounded host snapshots

This host-only harness directly includes `../v4160-f030-purec-real-bd46-next/candidate.c` and `leaf.c` under distinct names. Their Git blob IDs at the tested parent were `c1d4609548921cd43e8c4009225f3483cf86bb95` and `1bdf16d308a89ea5466bd3765e8bebbe160947bb`. It does not include the real BD46 function: its deliberately modifying provider is a host stub.

For values 0 through 511 and `UINT_MAX`, it tests a 24-byte volatile array with `base` at offset 3. The target starts different from the expected low byte. At stub entry the harness checks the entire array, then the stub changes two bytes; after return it checks the entire array again. The leaf is separately checked for no stub call and its final array snapshot. Each input is tested in a fresh initialized array; `CHAR_BIT == 8` is required. These are snapshots at specific points, not a trace of every read or write and not a proof of bounds safety for other implementations or inputs.

## Local observation

In a fresh temporary directory, MSVC `cl.exe` SHA-256 `88c8344236a27a6e727e0a8edc49aaa2690bdc7a9464b9d18cc7abe70a9f1c0d` and `link.exe` SHA-256 `ca11e6c45debd34bf652dfe984c5360a531a005ed78bf72852330c9c2590cf0d` compiled C11 with `/W4 /WX /Od`, with and without `/DNDEBUG`. Each host executable exited 0 and printed `PASS 513 values: stub-time and final array snapshots match`; each had a 15-second external timeout. Headers, libraries, OS, runtime and all inherited environment were not pinned. Tool hashes alone do not establish trust or reproducibility.

Seven separate temporary source mutants compiled and exited 1: wrong store offset, flipped value, omitted stub call, call before store, skipping store for value 165 in adapter or leaf, and an extra temporary write visible to the stub. The actual candidate files were not modified. These controls cover only those errors; no published automation reconstructs the mutants.

To repeat the positive host test, copy this directory and the two sibling C files to a fresh directory preserving their relative layout; set up a suitable C11 host compiler and choose fresh output paths. For example, with a configured MSVC environment: `cl /nologo /std:c11 /W4 /WX /Od /DNDEBUG /Fe:<fresh-output> harness.c`, then run that host executable with an external timeout. This instruction is not an automated identity verifier.

This is not target execution, an RV32 code-generation test, an ABI or hardware proof, or a complete image check. In particular the real F030 uses a private register interface and a call to BD46; the C adapter and store-only leaf do not establish a byte-identical or ABI-compatible replacement.
