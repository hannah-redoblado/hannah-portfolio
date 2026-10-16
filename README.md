# Hannah Redoblado · Engineering portfolio

Static site served by GitHub Pages: `index.html` plus the photos and PDFs in `assets/`. No build step needed to host it.

`tools/make_live.py` turns the editable portfolio (the version with edit buttons) into this read-only `index.html`:

```
python3 tools/make_live.py <editable index.html> index.html forest
```

The last argument picks a color scheme from `tools/themes/`.
