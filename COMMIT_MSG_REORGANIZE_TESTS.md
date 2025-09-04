chore(tests): reorganize test and script files

- Move legacy root-level test_*.py files into `tests/legacy/` to declutter repository root
- Consolidate scripts under `scripts/` (ensure executable bits locally)
- Add `TESTS_RELOCATION.md` documenting new locations and next steps

This change preserves original test contents under `tests/legacy/` and adds
redirect notices in the repository root to avoid broken references. Run a full
test suite after merging and update CI discovery if it referenced root-level
test files.
