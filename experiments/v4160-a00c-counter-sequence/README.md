# Conditional 0xa00c counter sequence

This isolated host-only Python state model represents one byte and a selected
control-flow edge, not target execution. `initialize()` models a separate store
of 25. `step(counter, a0)` accepts a byte and an unsigned 32-bit input, returns
the updated byte and either `None` (return) or the selected tail address
`0x9fc8`. The tail's behavior is not modeled; selection does not mean it was
executed or returned. Invalid model inputs are rejected, not truncated.

## Static evidence and assumptions

- `analysis/state-action-support-2026-10-25/provider-contracts.json` records
  `li a5, 25` at `0xa024` and `sb a5, 173(gp)` at `0xa026`;
  `analysis/state-action-support-2026-10-25/evidence.json` records the
  corresponding image identity and instruction bytes.
- `analysis/runtime-service-links-2026-10-25/evidence.json`, selected function
  `tsl9_settings_state_inputs_provider_a00c`, records the unsigned comparison,
  byte load/store, return and jump at `0xa00c`–`0xa022`. The model interprets
  these static records; it does not automatically verify instruction semantics.
- `analysis/settings-state-inputs-2026-10-25/evidence.json` records the caller
  loading its input byte from `7(s0)` before the call and reloading that input
  at `0xcffc` after return. This is not identified as the `173(gp)` counter;
  the evidence does not establish whether those locations alias. This model
  stops at the helper's return or tail selection and does not simulate the
  caller. The sequence assumes no intervening counter writers, including during
  or between modeled calls, and that the same valid counter location is accessed
  each time. Valid memory and correct `gp` are assumed.
- Initialization and the specified calls are hypothetical: no dynamic
  reachability, calling frequency or real execution ordering is established.
  This is not an ABI proof, BIN equivalence proof, or formal-C proof. No
  register, memory, callee side effects, or return values beyond the abstract
  counter and selected edge are claimed.

## Tests

From this directory, using an existing Python 3 installation:

```text
python -B -m unittest -v test_model
python -B -O -m unittest -v test_model
```

The tests check the initialized sequence, persistent nonzero behavior,
65,536 byte/input pairs against a separately expressed oracle, and uint32
boundary values for every byte. Two deliberately incorrect model alternatives
are distinguished by specific threshold and decrement-to-zero witnesses.
These tests validate the model against that oracle, not the target instructions.
