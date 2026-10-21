# Clock register and caller evidence

The new readable implementation is `experiments/tsl9-v4160-clock-registers/`.
It preserves source-specific normal-return register values alongside the
earlier memory effects. Preserving only conventional callee-saved registers
would lose A3, which reaches an unresolved callback in the captured init path.

| Evidence | Scope |
| --- | --- |
| [Original register source facts](source-review/readme.en.md) | Reused 214 bytes / 69 instructions; destination fields and static residue formulas |
| [Caller evidence](caller-review/readme.en.md) | 298 bytes / 98 instructions; concrete A3 passthrough and unresolved callback |
| [Independent shared-C review](code-review/readme.en.md) | Memory effects, register outputs and actually compiled countercases |
| [Compiler and native review](compiler-review/readme.en.md) | Actual bounded compiler probes, full ELF coverage, register writes and field pattern |

The query candidate is 196 bytes and does not fit the original 174-byte extent.
The field candidate is 38 bytes within its original 40 bytes. Neither has
replaced an original entry. Query all-path machine semantics, asynchronous
register state, original IRQ/ROM/hardware and OTA compatibility remain open.
No original/rebuilt RV32 code is executed or emulated, no device or vendor
service is contacted, and no new BIN is made.

On 2026-10-21 the user reported selecting an official BIN and successfully
updating firmware using `tsl9-morphe`. This is a user-reported official-image
OTA baseline, recorded in `ota-user-report.json`; exact APK/BIN identities,
versions and readback evidence have not yet been supplied. It does not prove
that a rebuilt image boots, is accepted, or can be recovered after failure.

Full historical compiler-probe and independent-review archives remain in the
investigation workspace. Delivery and Git publication carry the selected
sources, scripts, language-separated guides and sealed evidence metadata;
fresh host/native verifiers create their own local ignored archives. Retained
metadata referencing excluded historical builds does not claim those files
are present in a fresh clone. The original BINs/APK and earlier image gate
remain unchanged.
