#!/bin/sh
# The same checks run in GitHub Actions and in the Vercel build.
# A failed check does not become the production site.
set -e
cd "$(dirname "$0")/.."
python3 scripts/export_adocao.py
if [ -d .git ]; then
  git diff --exit-code -- site/data/adocao.json
fi
python3 scripts/test_graph.py
python3 scripts/test_skill_graph.py
python3 scripts/test_adocao.py
python3 scripts/test_year1.py
python3 scripts/test_diagnostics.py
python3 scripts/test_serve.py
