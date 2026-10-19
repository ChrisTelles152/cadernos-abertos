#!/usr/bin/env python3
"""The adoption minute may claim only skills a written book finishes."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from adocao import SENTENCE_PNLD, relatorio


def load():
    catalog = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text(encoding="utf-8"))
    cobertura = json.loads((ROOT / "data" / "cobertura.json").read_text(encoding="utf-8"))
    return relatorio(catalog, cobertura)


def test_no_year_can_replace_a_textbook_yet(report):
    assert all(not row["pode_substituir_o_livro_do_ano"] for row in report["anos"])
    year1 = next(row for row in report["anos"] if row["ano"] == 1)
    assert year1["total"] == 22
    assert year1["integrais"] == ["EF01MA01", "EF01MA02", "EF01MA03"]
    assert year1["parciais"] == ["EF01MA04", "EF01MA05"]
    assert "EF01MA07" in year1["faltam"]


def test_the_minute_does_not_overclaim(report):
    ata = report["ata"]
    assert SENTENCE_PNLD in ata
    assert "aprovado pelo PNLD" not in ata.lower()
    assert "EF01MA01" in ata
    assert "não substitui" in ata
    assert "EF01MA07" not in ata.split("Habilidades para as quais")[1].split("Habilidades começadas")[0]
    assert "até 100" in ata
    assert "Não pode ser a razão de guardar o livro do PNLD sem uso" in ata


def main():
    report = load()
    test_no_year_can_replace_a_textbook_yet(report)
    test_the_minute_does_not_overclaim(report)
    print("adoption claims hold")


if __name__ == "__main__":
    main()
