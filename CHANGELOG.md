# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-17

### Added

- `actual_360(d1, d2)`: Actual/360 year fraction (ISDA 2006 Section 4.16(e)).
- `actual_365_fixed(d1, d2)`: Actual/365 Fixed year fraction (ISDA 2006 Section 4.16(d)).
- `actual_actual_isda(d1, d2)`: Actual/Actual ISDA year fraction with split-year leap handling (ISDA 2006 Section 4.16(b)).
- `thirty_360_us(d1, d2)`: 30/360 US Bond Basis with end-of-February rules (ISDA 2006 Section 4.16(f)).
- `thirty_e_360(d1, d2)`: 30E/360 Eurobond (ISDA 2006 Section 4.16(g)).
- `Convention` str-enum with canonical names for all five conventions.
- `year_fraction(d1, d2, convention)`: dispatcher accepting Convention or string.
- `accrued_interest(face, rate, d1, d2, convention)`: accrued interest helper.
- Zero runtime dependencies; Python 3.10+ required.
- Full type annotations and `py.typed` marker.
- pytest test suite with golden values from ISDA 2006 and QuantLib references.

### Notes

PyPI publication is pending (new-project rate limit).  Install from GitHub in the meantime:

```bash
pip install git+https://github.com/amaar-mc/daycounts.git
```

[0.1.0]: https://github.com/amaar-mc/daycounts/releases/tag/v0.1.0
