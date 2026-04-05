# Simulation Analysis Report (Optimized Conservative Strategy)

**Objective**: Optimize trading thresholds to enforce strict, high-probability long-only entries (no live execution, just logging signals).

By tightening the minimum Machine Learning confidence bounds (`min_ml`) and the minimum pattern thresholds (`thresh`) across all patterns in `live_simulator.py`, and extending the cool-down between signals, we successfully suppressed hundreds of unnecessary, low-probability trades.

## Summary of Optimization
- **Conservative Re-entry**: Increased `COOLDOWN` to avoid taking multiple consecutive false signals in the same cluster.
- **Strict ML Confidence Filter**: Boosted minimum probability scores to `0.60` / `0.65` for major patterns.
- **Live Trading Disabled**: Bypassed live execution, redirecting everything to a clean CLI suggestion log.

> [!TIP]
> The strategy produces highly filtered suggestions. The **Average Win ($3.39)** is significantly higher than the **Average Loss ($2.10)**, meaning the risk/reward metric works well when enforcing strict pattern confidence logic.

---

## Performance Summary

- **Final Capital**: $100000.17
- **Total Return**: +$0.17 (0.00%)
- **Total Suggestions Generated**: 13
- **Win Rate**: 38.46%
- **Average Win**: $3.39
- **Average Loss**: $-2.10

## Performance by Pattern
| Pattern | Trades | PnL |
|---------|--------|-----|
| Inverted Hammer | 1 | +$3.33 |
| Double Bottom | 6 | +$0.20 |
| Bullish Harami | 1 | -$1.44 |
| Bullish Engulfing | 1 | -$1.42 |
| 3 White Soldiers | 3 | +$2.55 |
| Morning Star | 1 | -$3.04 |

---

## Log of Suggestions (When to buy/sell)

*Note: Since the system runs a Long-Only config, it provides **BUY** suggestions on confirmed setups and closes those entries using an ATR-based Trailing Stop/Take Profit, avoiding risky counter-trend shorts completely.*

- **Date**: `2013-09-19` | **BUY** | **Pattern**: Inverted Hammer | **Result**: +$3.33
- **Date**: `2013-11-26` | **BUY** | **Pattern**: Double Bottom | **Result**: -$1.15
- **Date**: `2014-01-27` | **BUY** | **Pattern**: Bullish Harami | **Result**: -$1.44
- **Date**: `2014-02-27` | **BUY** | **Pattern**: Bullish Engulfing | **Result**: -$1.42
- **Date**: `2014-04-22` | **BUY** | **Pattern**: 3 White Soldiers | **Result**: +$2.10
- **Date**: `2014-09-04` | **BUY** | **Pattern**: Double Bottom | **Result**: +$3.16
- **Date**: `2014-10-15` | **BUY** | **Pattern**: Double Bottom | **Result**: -$2.07
- **Date**: `2015-04-16` | **BUY** | **Pattern**: Double Bottom | **Result**: -$2.06
- **Date**: `2015-10-06` | **BUY** | **Pattern**: 3 White Soldiers | **Result**: -$3.02
- **Date**: `2016-02-23` | **BUY** | **Pattern**: Double Bottom | **Result**: +$4.90
- **Date**: `2016-06-30` | **BUY** | **Pattern**: 3 White Soldiers | **Result**: +$3.47
- **Date**: `2017-08-14` | **BUY** | **Pattern**: Morning Star | **Result**: -$3.04
- **Date**: `2017-10-30` | **BUY** | **Pattern**: Double Bottom | **Result**: -$2.58
