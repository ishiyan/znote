# Completed reference validation

The user confirmed all 56 Swami parameter combinations on 2026-10-21, including all eight cases in this folder. The expected data is generated in Python, Go, TypeScript, Rust and Zig. Each language contains 24 expected arrays and 64,512 scalar values; every array has 252 time positions. Heatmaps and per-period diagnostics also have the documented bin dimension. [reference_manifest.json](reference_manifest.json) records full parameters, warm-up boundaries, array names, dimensions and fixture SHA-256 checksums.

- 9 standard-library Python unittest checks pass here; 64 pass across all seven Swami folders.
- Every confirmed case is compared over all 252 shared observations against independently evaluated source equations. Synthetic negative prices, sine waves, jumps, plateaus and reversals cover source behavior beyond the financial fixture.
- [verify_reference_data.py](verify_reference_data.py) checks every exported value in all five languages against the 15-significant-digit rounding of the Python streaming master. Names, exact NaN masks, dimensions, both preceding comments, array counts and unchanged shared OHLC inputs are checked as well.
- All seven Go generated fixtures compile with `go test testdata_test.go`; all seven Rust fixtures compile with `rustc --test testdata.rs`.
- Zig temporary harnesses call every generated function and check all time/bin dimensions and total NaN counts. All seven harnesses pass with Zig 0.16.0.
- All seven TypeScript fixture modules load directly in Node 24.15.0 with type stripping. Runtime checks confirm all exported arrays have 252 time positions, uniform row dimensions and finite-or-NaN numeric entries. A separate TypeScript compiler is not installed.
- Regenerating every folder produces byte-identical fixture files: the generator does not duplicate arrays or alter their inputs.

To repeat checks in this self-contained folder, run `python3 -m unittest discover -s . -p 'test_swami_*.py'` or `python3 verify_reference_data.py`. To regenerate, run `python3 swami-relative-strength-index.py --generate-reference-data` and then `python3 verify_reference_data.py`. Confirmation remains recorded in `REFERENCE_CASES_CONFIRMED = True`.

Source equivalence means the selected published equations with full-precision mathematical constants and the explicitly documented standalone startup. Different chart-platform seeds, rounded printed literals, historical display shifts and vendor algorithms are documented rather than assumed identical. The native compilation/runtime checks validate fixture files; they are not implementations of the indicator in those languages.
