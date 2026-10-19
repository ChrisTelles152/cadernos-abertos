#!/usr/bin/env python3
"""Every year-1 skill is taught in the student book and named for the teacher."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from adocao import relatorio

# A phrase the lesson cannot omit if the official demand is actually there.
MARKERS = {
    "EF01MA01": "quantidade",
    "EF01MA02": "uma vez",
    "EF01MA03": "tem mais",
    "EF01MA04": "100",
    "EF01MA05": "28",
    "EF01MA06": "fato",
    "EF01MA07": "30 + 13",
    "EF01MA08": "Separar",
    "EF01MA09": "cor",
    "EF01MA10": "regra",
    "EF01MA11": "direita",
    "EF01MA12": "de quem",
    "EF01MA13": "cilindro",
    "EF01MA14": "quadrado",
    "EF01MA15": "cabe mais",
    "EF01MA16": "manhã",
    "EF01MA17": "Março",
    "EF01MA18": "calendário",
    "EF01MA19": "50 centavos",
    "EF01MA20": "impossível",
    "EF01MA21": "coluna",
    "EF01MA22": "30",
}


def main():
    catalog = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text(encoding="utf-8"))
    cobertura = json.loads((ROOT / "data" / "cobertura.json").read_text(encoding="utf-8"))
    report = relatorio(catalog, cobertura)
    claimed = report["habilidades"]
    # Catalog order follows the book: composition (MA07) is listed before the
    # addition facts (MA06). The official codes are what this test checks.
    codes = sorted(h["codigo"] for h in catalog["habilidades"] if h["codigo"].startswith("EF01"))
    assert codes == [f"EF01MA{n:02d}" for n in range(1, 23)]
    for code in codes:
        item = claimed[code]
        assert item["cobertura"] == "integral"
        student = (ROOT / "site" / cobertura_path(cobertura, code, "aluno")).read_text(encoding="utf-8")
        teacher = (ROOT / "site" / cobertura_path(cobertura, code, "professor")).read_text(encoding="utf-8")
        assert code in student, code
        assert code in teacher, code
        assert MARKERS[code] in student, (code, MARKERS[code])
        assert "Hipótese do erro" in teacher or code in ("EF01MA01", "EF01MA02", "EF01MA03")
        assert 'data-answer=' in student
    print("year-1 books hold")


def cobertura_path(cobertura, code, side):
    for obra in cobertura["obras"]:
        for item in obra["habilidades"]:
            if item["codigo"] == code:
                return obra[side]
    raise KeyError(code)


if __name__ == "__main__":
    main()
