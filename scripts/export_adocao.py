#!/usr/bin/env python3
"""Write the adoption minute into the static site.

GitHub Pages serves files. It does not run this Python program for each
visitor. The minute is generated from the catalog and the coverage file,
then fetched by the page as data/adocao.json.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from adocao import relatorio


def main() -> None:
    catalog = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text(encoding="utf-8"))
    cobertura = json.loads((ROOT / "data" / "cobertura.json").read_text(encoding="utf-8"))
    report = relatorio(catalog, cobertura)
    out = ROOT / "site" / "data" / "adocao.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
