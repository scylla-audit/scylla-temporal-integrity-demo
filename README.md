# SCYLLA temporal-integrity demo

A minimal, deterministic demonstration of future-data leakage detection in a backtest decision.

## The idea

Two synthetic histories are identical through decision time **T**. They have the same hypothetical next execution open and differ only in the later close of that execution bar.

- A **safe decision** reads only observations available at or before T, so its result is identical in both histories.
- An **intentionally leaky decision** reads the later close, so changing only that future value changes the earlier decision.

That counterfactual difference is mechanical evidence that information crossed the decision boundary backward.

## Terms in plain language

- **Point-in-Time:** use only information that was available at the historical moment being simulated.
- **Look-ahead leakage:** future information influences an earlier decision.
- **Decision boundary:** the latest instant whose information a decision may legally observe.
- **Counterfactual test:** keep the past fixed, change only the future, and check whether the past changes.
- **Deterministic reproduction:** identical inputs and runtime rules produce byte-identical canonical output.

## Run

Python 3.12 or 3.13 is sufficient; the demo has no runtime dependency outside the standard library.

```bash
python -m unittest discover -s tests -v
python -m scylla_temporal_demo.demo --history-a examples/history_a.json --history-b examples/history_b.json
```

The CLI emits canonical JSON ending with:

```json
{"leaky_path_detected":true,"result":"PASS","safe_path_invariant":true}
```

## Expected interpretation

The leaky function is deliberately incorrect teaching code. Detection of its violation is the expected passing outcome.

This bounded example is not a certification of a backtesting platform, a security assessment, or a claim about trading profitability.

- Methodology: https://github.com/scylla-audit/scylla-audit-methodology
- Website: https://scylla-audit.pages.dev
- Contact: scylla.audit@gmail.com

Licensed under the MIT License.

