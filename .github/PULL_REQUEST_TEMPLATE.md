<!--
Thanks for the contribution! A few quick checks before reviewers dive in:
-->

### What does this PR change?

<!-- One paragraph. Link the issue with `Fixes #NNN` if applicable. -->


### Type of change

- [ ] Bug fix (UI, spec, generator, test)
- [ ] New feature (page, tool, page-level capability)
- [ ] New / regenerated specs (touches `swagger-*-model/` or `releases/*/swagger-*-model/`)
- [ ] Generator / scripts change (touches `generators/` or `scripts/`)
- [ ] Docs only (README / CONTRIBUTING / CHANGELOG / about.html)
- [ ] CI / tests only (`.github/workflows/`, `tests/`)


### Validation

- [ ] `python -m pytest tests -q` passes locally (paste the final line below)
- [ ] If you regenerated specs, you also re-ran `scripts/enrich_v2_specs.py`
- [ ] If you added a UI page or moved a file, the sitemap (`scripts/generate_sitemap.py`) is refreshed
- [ ] If you added decorative emoji you removed them again (see `tests/test_no_emoji.py`)
- [ ] No `console.log` / debug code left behind

```text
# Paste the last line of `python -m pytest tests -q` here:
```


### Screenshots / before-after (UI changes)

<!-- Drag-and-drop screenshots into the editor. For deep-link / share-link
     changes, paste the exact URL you reproduced the result with. -->


### Notes for reviewers

<!-- Anything reviewers should look at carefully, performance numbers,
     follow-up work that is deliberately out of scope, etc. -->
