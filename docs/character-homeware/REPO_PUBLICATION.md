# Existing repository and publication convention

Inspected October 6, 2026 through the authenticated GitHub connector; no commit or push was performed by this inspection.

- Repository: [gdayoub/george-Print-files](https://github.com/gdayoub/george-Print-files)
- Default branch: `main`; visibility: **private**; connector reports push permission.
- Main commit: `266b5093f6ab01defeaac3ab0bc5da19ca14e681` (Venom two-size release).
- Commit tree: `b67c18366ebab09b36d4db125ea248c1b770a728`.
- Recursive tree: 808 entries, `truncated = false`; no King Shark path existed.
- No root `AGENTS.md` was present. An AGENTS file exists only inside `prints/venom-core-case/`, outside the new design destinations.
- No local repository was found in the task directory; it has no Git status/remote. `gh` was not available on PATH. Use the existing authorized GitHub connection or a deliberately prepared local checkout; do not infer an unrelated directory is this repository.

## Observed layout

The gallery uses `prints/<kebab-case-design>/`. The current template calls for one clear recommended version, actual-geometry renders or labelled photographs, dimensions and print settings, assembly instructions, explicit validation status, and source credits. It also calls for a root README gallery entry and a `catalog.json` entry. [Existing template](https://github.com/gdayoub/george-Print-files/blob/main/templates/print/README.md)

```text
prints/king-shark-47cm/
  README.md
  project.json
  CREDITS.md
  images/
  files/3mf/
  files/stl/
  source/
  docs/
  validation/
```

The existing Venom statue lives in `prints/venom-muscular-statue/`, with explicit source-license/private-backup status and separate size variants. Earlier source backups under `Desktop-Prints/` and `Desktop-Prints-Archive/` are retained as history; new curated designs belong under `prints/`.

Existing `.gitattributes` declares 3MF/STL/PNG/ZIP binary and text LF endings for Markdown/JSON/Python. It does not configure Git LFS. Existing `.gitignore` omits ordinary `*.gcode`, `*.gcode.3mf`, caches, temporary files and environment files. Keep JSON validation summaries and selected artifacts, not local runtimes or massive slice logs.

## Intended additions

- `prints/king-shark-47cm/`: original realistic v2, compatible all-red replacement shorts, and fast legs/feet as clearly named variants. Preserve the existing torso exactly. Historical reports are retained with a current status note.
- A separate folder each for the new King Shark accessory shelf, Venom accessory shelf, and King Shark catchall bowl. Root owns their exact slugs, final files, README/catalog integration and publishing.
- Markdown handoff and progress files should be published with the collection or linked from each design's documentation. Do not include credentials or claim publication before the resulting commit is verified.

## Gaps and factual limits

King Shark previously existed only in local deliveries; none of its statue revisions were in the inspected remote tree. The new homewares also require publication. Source licensing for the King Shark fan interpretation has not been assigned a blanket open license. The Venom source retains the prior credited creator and Standard Digital File License; public redistribution permission remains unverified. Keep the repository private unless the user separately requests a visibility change.

Original King Shark delivery notes predate the user's report that the torso/head printed successfully. Preserve those original notes as historical artifacts, but use the updated project README/status records as the current interpretation. Do not claim whole-statue or homeware physical validation.
