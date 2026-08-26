# Wiki source

These Markdown pages and D2 sources are the source-controlled LyricVid wiki. Run `./scripts/render-wiki.sh` before publishing so each page's SVG exists. Copy the Markdown pages and `diagrams/` directory into the repository's GitHub Wiki checkout.


## Offline/local diagram icons

All D2 diagrams use SVG icons vendored under `wiki/icons/`. The wiki renderer does not depend on `icons.d2lang.com`, so diagram builds remain reproducible even when the hosted icon service is unavailable or returns HTTP 403.
