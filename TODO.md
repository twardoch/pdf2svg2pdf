# TODO

Done in this pass is recorded in `CHANGELOG.md`. What remains:

## Bigger ideas
- [ ] Decide whether the modern `core/` + `backends/` + `filters/` layer earns
      its complexity, or whether the classic script-style pipeline should become
      the single supported implementation. Right now both exist and only the
      classic/legacy paths are covered by tests.
- [ ] Wire the modern `Converter` into the test suite with mocked backends so the
      async pipeline is actually exercised (it currently only runs via the CLI).
- [ ] Add an `inkscape` backend for PDF↔SVG as an alternative to poppler/cairo.
- [ ] Ship the filter registry filters (`grayscale`, `compress`, `optimize`,
      `transparent_white`) as first-class CLI options rather than eval strings.

## Housekeeping
- [ ] Publish to PyPI and confirm the `pip install pdf2svg2pdf` badge.
- [ ] Turn on GitHub Pages for the `docs/` Jekyll site.
- [ ] Add a small sample PDF under `tests/fixtures/` for the integration test
      instead of generating one at runtime (optional).
