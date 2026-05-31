# Git hooks

`pre-commit` regenerates the static site (`index.html`, `guides/`, `c/`,
`sitemap.xml`) from `data/articles.json` whenever that file is part of a commit,
then stages the output. This keeps the served HTML in sync with the data — which
is what the AdSense crawler and search engines actually read.

Git does not install hooks from the repo automatically. After cloning, run:

```bash
cp hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

To rebuild manually at any time:

```bash
python3 build.py
```
