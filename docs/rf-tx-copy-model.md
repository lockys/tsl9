# Conditional RF transmit copy model

This isolated data model is adapted from commit `44049b08`. It models only
normal completion of the selected V1.31 RF transmit prefix stores and forward
copy, including overlapping memory and a potentially self-overwriting pointer.
Memory is supplied by the caller; it does not access a device or firmware.

The tests use synthetic memory and do not establish that a particular ROM
implements this model. They do not cover guards, MMIO, interrupts, exceptions,
or subsequent calls. No original instruction bytes or third-party SDK are
included. Run from the repository root:

```sh
python -m unittest discover -s tests -p test_rf_tx_copy_model.py
```
