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


def test_year1_can_replace_a_mathematics_textbook(report):
    year1 = next(row for row in report["anos"] if row["ano"] == 1)
    assert year1["total"] == 22
    assert year1["pode_substituir_o_livro_do_ano"] is True
    assert year1["parciais"] == []
    assert year1["faltam"] == []
    assert len(year1["integrais"]) == 22
    assert "EF01MA07" in year1["integrais"]
    for row in report["anos"]:
        if row["ano"] == 1:
            continue
        assert row["pode_substituir_o_livro_do_ano"] is False


def test_the_minute_does_not_overclaim(report):
    ata = report["ata"]
    assert SENTENCE_PNLD in ata
    assert "aprovado pelo PNLD" not in ata.lower()
    assert "EF01MA01" in ata
    assert "1º ano: pode substituir o livro do ano." in ata
    assert "2º ano: não substitui." in ata
    assert "EF01MA07" in ata.split("Habilidades para as quais")[1].split("Habilidades começadas")[0]
    assert "Não pode ser a razão de guardar o livro do PNLD sem uso" in ata


def test_the_published_minute_is_the_static_file(report):
    published = json.loads((ROOT / "site" / "data" / "adocao.json").read_text(encoding="utf-8"))
    assert published == report
    for name in ("adocao.js", "grafo.js"):
        source = (ROOT / "site" / "js" / name).read_text(encoding="utf-8")
        assert "data/adocao.json" in source, name
        assert "/api/adocao" not in source, name


def main():
    report = load()
    test_year1_can_replace_a_mathematics_textbook(report)
    test_the_minute_does_not_overclaim(report)
    test_the_published_minute_is_the_static_file(report)
    print("adoption claims hold")


if __name__ == "__main__":
    main()
