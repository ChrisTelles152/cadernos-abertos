#!/usr/bin/env python3
"""The skill graph is the concept graph, drawn one official skill at a time."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from skill_graph import ancestors, build, direct_prereqs


def test_year1_numbers_follow_the_concept_gates():
    catalog = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text(encoding="utf-8"))
    graph = build(catalog)
    assert direct_prereqs(graph, "EF01MA05") == {"EF01MA04"}
    assert "EF01MA07" not in ancestors(graph, "EF01MA05")
    assert direct_prereqs(graph, "EF01MA06") == {"EF01MA04", "EF01MA07"}
    assert direct_prereqs(graph, "EF01MA08") == {"EF01MA05", "EF01MA06"}
    assert "EF02MA05" not in ancestors(graph, "EF01MA08")
    assert direct_prereqs(graph, "EF01MA01") == {"EI03ET07"}
    assert {"EI02ET07", "EI02ET08", "EI03ET07"} <= ancestors(graph, "EF01MA01")
    assert len(graph["nos"]) == len(catalog["habilidades"])


def main():
    test_year1_numbers_follow_the_concept_gates()
    print("skill graph claims hold")


if __name__ == "__main__":
    main()
