# Code graph: design-os TypeScript kernel

A file-level graph of the kernel (`src/core`, `src/commands`, `src/adapters`, `src/types`) with a human-written meaning for every file. Built at commit `8420c62`.

- `graph.html`: the viewer. Open it in any browser; it works offline.
- `skeleton.json`: the structure only (nodes, layers, edges), produced from the AST.
- `curation.json`: the meaning, keyed by repo-relative file path. Each entry has `what`, `why`, `gotcha` and `curated_at`.
- `ast-raw.json`: the raw extractor output that `build_skeleton.py` reads.
- `build_skeleton.py`, `add_curation.py`, `rebuild_viewer.py`, `viewer-template.html`: the pipeline.

## Use the viewer

1. Open `graph.html`.
2. Click a node to see its layer, its inbound and outbound edges, and its `what` / `why` / `gotcha` text.
3. Use the search box to find a file by name, and the filter bar to show one layer or edge type.
4. A node whose `gotcha` starts with `BUG` or `DEAD CANDIDATE` has a defect noted from reading the code. Those are not reproduced unless the text says so.

Edge relations are aggregated to file level: `imports`, `calls`, `references`, `inherits`. Only cross-file edges are drawn.

## Rebuild after code changes

The pipeline is deterministic. Running it on this commit reproduces the committed files byte for byte.

```bash
cd docs/code-graph
python3 build_skeleton.py   # ast-raw.json -> skeleton.json (structure only)
python3 rebuild_viewer.py   # skeleton.json + curation.json -> graph.html
```

`ast-raw.json` was made with graphify's `extract` over `src/`, so re-extract it after the code changes.

## Add or change curation

Curation is additive. `add_curation.py` never overwrites a non-empty field.

Write a batch file with one entry per file, for example `batch.json`:

```json
{
  "src/core/example.ts": {
    "what": "What the file does, in one or two sentences.",
    "why": "Why it exists, and what breaks without it.",
    "gotcha": "The surprise a maintainer would hit. Prefix a defect with BUG or DEAD CANDIDATE."
  }
}
```

Then:

```bash
python3 add_curation.py batch.json
python3 rebuild_viewer.py
```

Rules for the text: read the whole file first, and do not derive the meaning from the name. If you add a file, run `build_skeleton.py` first so the node exists; `add_curation.py` does not check that the path exists.

## Check the data

```bash
python3 -c "
import json
sk=json.load(open('skeleton.json')); cu=json.load(open('curation.json'))
ids={n['id'] for n in sk['nodes']}
print('uncurated:', len(ids-set(cu)), 'phantoms:', len(set(cu)-ids))
"
```

Expected on this commit: `uncurated: 0 phantoms: 0`. The three zero-degree nodes are `src/core/component-kit/responsive-lint.ts` and `src/core/url-slug.ts` (dead candidates) and `src/types/css-tree-subpaths.d.ts` (a false positive; an ambient declaration produces no import edge).

## Use the design-os repo itself

design-os is the `ease-design` CLI (`ui`), a multi-runtime design tool.

```bash
npm install
npm run typecheck    # tsc --noEmit
npm run lint         # eslint src tests
npm run build        # tsup, then templates catalogue --check
npm test             # vitest run
npx ui --help        # the CLI, after a build
```

`ui guide` prints the designer-facing workflow. `ui schema --json` prints every command's flags and error codes. `CLAUDE.md` describes the working rules for this repo.

The checks above were not run as part of this commit; the graph work changed only files under `docs/code-graph/`.
