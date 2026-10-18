#!/usr/bin/env python3
"""Pin the dependency claims the site teaches.

These are inferences, not lines from the BNCC. The tests fail if a later edit
silently reverses one of them.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_curriculum import build


def index(catalog):
    return {c["id"]: c for c in catalog["conceitos"]}


def requires(concepts, later, earlier):
    seen = set()

    def walk(node):
        if node in seen:
            return False
        seen.add(node)
        if node == earlier:
            return True
        return any(walk(parent) for parent in concepts[node]["exige"])

    return walk(later)


def test_coverage(catalog):
    ef = [h for h in catalog["habilidades"] if h["etapa"] == "EF"]
    em = [h for h in catalog["habilidades"] if h["etapa"] == "EM"]
    assert len(ef) == 247, len(ef)
    assert len(em) == 43, len(em)
    assert len({h["codigo"] for h in catalog["habilidades"]}) == len(catalog["habilidades"])


def test_comparison_does_not_need_place_value(concepts):
    assert not requires(concepts, "N-COMPARAR", "N-COMPOR")
    assert requires(concepts, "N-COMPARAR", "N-CONTAGEM")
    assert requires(concepts, "N-COMPOR", "N-CONTAGEM")


def test_decimals_need_place_value_and_fractions(concepts):
    assert requires(concepts, "N-DECIMAL", "N-MILHAR")
    assert requires(concepts, "N-DECIMAL", "N-FRACAO")
    assert not requires(concepts, "N-FRACAO", "N-DECIMAL")


def test_probability_number_waits_for_fractions(concepts):
    assert requires(concepts, "E-PROB", "N-FRACAO")
    assert requires(concepts, "E-PROB", "E-ACASO")
    assert not requires(concepts, "E-ACASO", "N-FRACAO")


def test_irrationals_come_after_pythagoras(concepts):
    assert requires(concepts, "N-REAIS", "G-PITAGORAS")
    assert requires(concepts, "G-PITAGORAS", "G-SEMELHANCA")
    assert not requires(concepts, "G-PITAGORAS", "N-REAIS")


def test_every_edge_has_a_reason(concepts):
    for concept in concepts.values():
        for parent in concept["exige"] + concept["apoia"]:
            reason = concept["porque"].get(parent, "")
            assert len(reason) > 40, (concept["id"], parent)


def main():
    catalog = build()
    concepts = index(catalog)
    test_coverage(catalog)
    test_comparison_does_not_need_place_value(concepts)
    test_decimals_need_place_value_and_fractions(concepts)
    test_probability_number_waits_for_fractions(concepts)
    test_irrationals_come_after_pythagoras(concepts)
    test_every_edge_has_a_reason(concepts)
    print("graph claims hold")


if __name__ == "__main__":
    main()
