# Reference Chart Fixtures

Fixtures in this folder use a common comparison schema.

`internal_regression_001.json` is not independent evidence. It freezes a known
current-engine result so accidental changes are detected.

Future fixtures should use:

- `verification_status: external_software_verified` after comparison with a
  named trusted Jyotish application and documented settings.
- `verification_status: expert_reviewed` after an astrologer reviews the
  derived calculations.
- Exact birth timezone, coordinates, ayanamsa, node mode, and house convention.
- A `verification_evidence` object naming the software/reviewer, version or
  credential, verification timestamp, and retained artifact reference.

No client names or unnecessary personal data should be stored in fixtures.

Preflight a proposed fixture before adding it:

```bash
python3 scripts/check_reference_fixture.py /path/to/fixture.json
```
