#!/usr/bin/env python3
"""Turn the concept graph into one node per official skill.

Math Academy draws a knowledge graph as circles (topics) and arrows
(prerequisites). The BNCC does not publish that graph. This file derives
one, and only one, from the concept edges already in the catalog:

- Skills of the same concept are chained in the order the concept lists them.
- The first skill of a concept also depends on a gate skill of each concept
  it requires. The gate is the last listed skill of that concept whose year
  is not later than the dependent skill. A year-2 continuation therefore
  does not become a prerequisite of a year-1 skill.

Support edges (apoia) stay off this picture. They are not gates.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "site" / "data" / "curriculum.json"
OUT = ROOT / "site" / "data" / "skill-graph.json"

CHAIN = "A habilidade seguinte do mesmo conceito, na ordem em que o conceito lista as suas habilidades."


def year_of(code: str) -> int:
    if code.startswith("EI"):
        return 0
    if code.startswith("EM"):
        return 10
    if code.startswith("EF"):
        return int(code[2:4])
    raise ValueError(code)


def build(catalog: dict) -> dict:
    concepts = {c["id"]: c for c in catalog["conceitos"]}
    concept_of = {}
    for concept in catalog["conceitos"]:
        for code in concept["habilidades"]:
            if code in concept_of:
                raise ValueError(f"{code} está em dois conceitos")
            concept_of[code] = concept["id"]

    edges = []
    seen = set()

    def add(src: str, dst: str, tipo: str, porque: str) -> None:
        key = (src, dst)
        if key in seen:
            return
        seen.add(key)
        edges.append({"de": src, "para": dst, "tipo": tipo, "porque": porque})

    for concept in catalog["conceitos"]:
        habs = concept["habilidades"]
        for earlier, later in zip(habs, habs[1:]):
            add(earlier, later, "mesmo-conceito", CHAIN)
        if not habs:
            continue
        first = habs[0]
        limit = year_of(first)
        for required in concept["exige"]:
            earlier_skills = concepts[required]["habilidades"]
            eligible = [code for code in earlier_skills if year_of(code) <= limit]
            if not eligible:
                raise ValueError(f"{concept['id']} exige {required}, mas não há habilidade até o ano {limit}")
            gate = eligible[-1]
            reason = concept["porque"].get(required)
            if not reason:
                raise ValueError(f"falta o porque de {concept['id']} para {required}")
            add(gate, first, "exige", reason)

    nodes = []
    outgoing = {}
    incoming = {}
    for edge in edges:
        outgoing.setdefault(edge["de"], []).append(edge["para"])
        incoming.setdefault(edge["para"], []).append(edge["de"])
    for skill in catalog["habilidades"]:
        code = skill["codigo"]
        nodes.append(
            {
                "id": code,
                "ano": year_of(code),
                "conceito": concept_of[code],
                "fio": concepts[concept_of[code]]["fio"],
                "exige": incoming.get(code, []),
                "libera": outgoing.get(code, []),
            }
        )

    graph = {
        "aviso": (
            "Cada círculo é uma habilidade oficial, ou um objetivo da Educação Infantil. "
            "A seta sai do pré-requisito e chega na habilidade que depende dele. "
            "A BNCC não publica essas setas. Elas vêm do grafo de conceitos, "
            "com a regra escrita em scripts/skill_graph.py."
        ),
        "nos": nodes,
        "arestas": edges,
    }
    validate(graph)
    return graph


def validate(graph: dict) -> None:
    ids = [node["id"] for node in graph["nos"]]
    if len(ids) != len(set(ids)):
        raise ValueError("habilidade repetida")
    known = set(ids)
    indegree = {code: 0 for code in known}
    outgoing = {code: [] for code in known}
    for edge in graph["arestas"]:
        if edge["de"] not in known or edge["para"] not in known:
            raise ValueError(f"aresta solta {edge}")
        if edge["de"] == edge["para"]:
            raise ValueError(edge)
        if year_of(edge["de"]) > year_of(edge["para"]):
            raise ValueError(f"pré-requisito de ano posterior: {edge['de']} → {edge['para']}")
        outgoing[edge["de"]].append(edge["para"])
        indegree[edge["para"]] += 1
    queue = [code for code, n in indegree.items() if n == 0]
    seen = 0
    while queue:
        code = queue.pop()
        seen += 1
        for nxt in outgoing[code]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    if seen != len(known):
        raise ValueError("o grafo de habilidades tem ciclo")


def direct_prereqs(graph: dict, code: str) -> set[str]:
    return {edge["de"] for edge in graph["arestas"] if edge["para"] == code}


def ancestors(graph: dict, code: str) -> set[str]:
    found = set()
    stack = [code]
    incoming = {}
    for edge in graph["arestas"]:
        incoming.setdefault(edge["para"], []).append(edge["de"])
    while stack:
        current = stack.pop()
        for parent in incoming.get(current, []):
            if parent not in found:
                found.add(parent)
                stack.append(parent)
    return found


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    graph = build(catalog)
    OUT.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(graph['nos'])} skills, {len(graph['arestas'])} arrows")


if __name__ == "__main__":
    main()
