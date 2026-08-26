# Wiki source

These Markdown pages and D2 sources are the source-controlled LyricVid wiki. Run `./scripts/render-wiki.sh` before publishing so each page's SVG exists. Copy the Markdown pages and `diagrams/` directory into the repository's GitHub Wiki checkout.

D2 icon URLs are intentionally public hosted assets from icons.d2lang.com; D2 bundles referenced assets into SVG by default. No credentials belong in wiki source or generated diagrams.

## Offline/local diagram icons

All D2 diagrams use SVG icons vendored under `wiki/icons/`. The wiki renderer does not depend on `icons.d2lang.com`, so diagram builds remain reproducible even when the hosted icon service is unavailable or returns HTTP 403.
