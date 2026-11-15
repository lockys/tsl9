# TX provider boundary: limited offline evidence

Original v4.1.60 BIN SHA-256: `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.

A local bounded interpreter compared the original and candidate TX instruction windows across 27 synthetic scenarios with up to two provider returns, including selected register, stack and indirect-call-slot modifications. Six tests and the scenario run passed under ordinary Python and Python -O.

The candidate receipt and test scripts are local and not included here; this note alone does not reproduce the result. The experiment assumes mapped ordinary RAM, stable code, normal provider return and matching injected effects on both sides. It is not evidence of actual provider behavior, hardware execution, full-image equivalence, or flash readiness.
