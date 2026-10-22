# Callback registers and liveGP: independent source review

[繁體中文](readme.zh-TW.md)

The sealed632B/217-instruction original proof is reused, while the actual official BIN is freshly decoded across all rd/rs1/rs2 fields. String absence is not the evidence. The old26 raw controls and unchanged HOST behavior matrix are not repeated; new controls concern only register ownership,SP0 andGP.

| Offline artifact | Bytes/instructions | S10 ports | S11 ports | GP reads | Direct frame words |
|---|---|---:|---:|---:|---:|
| Official original | 632/217 | 0 | 0 | 6 | 22 |
| Prior inline native | 658/241 | 6 | 0 | 16 | 24 |
| Fixed26/27 only | 656/240 | 0 | 0 | 16 | 22 |
| Same flags,liveGP bridge | 624/223 | 0 | 0 | 6 | 22 |
| Explicit word-order pass | 624/223 | 0 | 0 | 6 | 22 |

The original body has no explicit S10/x26 or S11/x27 operand. Unknown opaque callees may still modify either register; this does not prove callee preservation. The original saves eleven registers in a48-byte frame: S0,RA,S1..S9 at slots4..44. Its epilogue freshly reloadsRA,S0..S9 from currentSP, adds48, then jumps through freshRA. No direct originalSP0 access exists, but pointer aliasing,ROM and asynchronous access remain unknown.

The actual658-byte component usesS10 six times: SP0 save,ADDI fromS1, twoAND mask uses, oneADD and SP0 restore. Its0xFFFF arithmetic introduces observable word effects. Historical actual fingerprints/fields are retained in `baseline-658.json` and `baseline-fixed656.json`; default checks never silently read those old build archives.

The only profile additions are `-ffixed-x26 -ffixed-x27` after the immutable prior profile. Reserving both avoids shifting pressure fromS10 to another source-absent register. Actual operands,eleven register/slot pairs,no replacement spills and source/command provenance must verify the result.

OriginalGP is read at six sites:868E LBU+94,8698 LBU+98,86A8 addressGP+94,86CC GP+80,postcopy87C0 GP+80,87FC liveGP for the followingLHU+2A. The body never writesGP, while opaqueGP preservation remains unknown.

The source transformation is exact: six `s->gp` uses become `CB_GP(h)`; native entry/postcall snapshot sites are removed; a narrow fixed-x3 empty volatile output reads liveGP. The HOST macro refers to the same `h->values.gp` field already reached through stable local alias `s`. Control,arithmetic,widths and HOST API remain unchanged. This is source-equivalence evidence, not a newly executed HOST test.

Actual C/C++624-byte components contain six directGP ports,noGP write and six fixed-x3/memory-clobbered emptyIR outputs. The twoGP+80 ports feed their immediate opaque calls; postcopyGP follows the copy call and fresh target load. Clang lowers the final sourceLHU intoLH followed bySH. Low16 storage corresponds, but transient sign-extended GPR values differ; full physical-prefix identity is not claimed.

The component has one honest FUNC and exactly its allocated bytes, with no original-BIN code generation or fakeFUNC632 padding. The final explicit pass reorders existing save words to restore the relative order of the eleven saved registers; other prefix positions such asSLLI are not thereby identical. This is not pureClang output. Eight recipes include five native steps and three ordering/link/disassembly steps. Actual call-return offset sets still differ from the original. Numeric624-byte fit does not establish ownership of the remaining8 bytes. UnknownROM S/SP effects,fullABI,asynchronous behavior,tail/interior ownership,image integration and OTA remain unadmitted.

Default checks validate original source fields,current mechanical refinement and metadata with actual-native replayfalse. An explicit new formal receipt reads actual pre/orderedELF,IR,eight exact recipes,dependency closure,known tool and source pins,without requiring old build archives. Four source controls and five actual native-field controls per language target onlyS10,S11,GP writes,SP0 and freshGP; no broad matrix is added:

```sh
python3 -B check-review.py --project-root /project --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python3 -B check-review.py --project-root /project --firmware /absolute/ID-2966-V4.1.60-decoded.bin --receipt /absolute/new-native/ordered/c/verification.json
```

No RV32 execution/emulation,network,deviceI/O or flashing occurs.
