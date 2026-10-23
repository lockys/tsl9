The first replay attempt stopped at `ValueError: Exact static-fact replay`.
The builder returns tuple records for PC-relative ports; JSON receipts retain
the equivalent arrays. Replay now compares the JSON-normalized facts. This
was a checker representation correction, without source/object/receipt edits.
