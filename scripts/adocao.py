"""What a school may legally name as its mathematics material.

The BNCC requires the skills. It does not require a purchased book.
A year may be adopted in place of a textbook only when every mathematics
skill of that year is covered in full by a written student lesson and the
matching teacher lesson. A partial unit is adoptable for the skills it
finishes, and the minute says so. The minute never says the work is a
PNLD book.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

SENTENCE_PNLD = (
    "Esta obra não foi aprovada em edital do PNLD e não pode ser apresentada como livro do PNLD."
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def year_of(code: str) -> int | None:
    if code.startswith("EF") and len(code) >= 4 and code[2:4].isdigit():
        return int(code[2:4])
    return None


def validate_cobertura(catalog: dict, cobertura: dict, site: Path = SITE) -> None:
    skills = {h["codigo"]: h for h in catalog["habilidades"]}
    seen = set()
    if cobertura.get("licenca") != "CC-BY-4.0":
        raise ValueError("the adoption file must carry CC-BY-4.0")
    for obra in cobertura["obras"]:
        for rel in (obra["aluno"], obra["professor"]):
            if not (site / rel).is_file():
                raise ValueError(f"missing book file {rel}")
        for item in obra["habilidades"]:
            code = item["codigo"]
            if code in seen:
                raise ValueError(f"{code} is claimed by two works")
            seen.add(code)
            if code not in skills:
                raise ValueError(f"unknown skill {code}")
            if item["cobertura"] not in ("integral", "parcial"):
                raise ValueError(code)
            if len(item.get("nota", "")) < 40:
                raise ValueError(f"coverage note too short for {code}")


def relatorio(catalog: dict, cobertura: dict) -> dict:
    validate_cobertura(catalog, cobertura)
    claimed = {}
    for obra in cobertura["obras"]:
        for item in obra["habilidades"]:
            claimed[item["codigo"]] = {**item, "obra": obra["id"], "titulo": obra["titulo"]}

    by_year: dict[int, list[str]] = {}
    for skill in catalog["habilidades"]:
        year = year_of(skill["codigo"])
        if year is None:
            continue
        by_year.setdefault(year, []).append(skill["codigo"])

    anos = []
    for year in range(1, 10):
        codes = sorted(by_year.get(year, []))
        integrais = [c for c in codes if claimed.get(c, {}).get("cobertura") == "integral"]
        parciais = [c for c in codes if claimed.get(c, {}).get("cobertura") == "parcial"]
        faltam = [c for c in codes if c not in claimed]
        reasons = []
        if faltam:
            reasons.append(
                f"{len(faltam)} habilidades de Matemática do {year}º ano ainda não têm caderno."
            )
        if parciais:
            reasons.append(
                f"{len(parciais)} habilidades estão só começadas: " + ", ".join(parciais) + "."
            )
        anos.append(
            {
                "ano": year,
                "total": len(codes),
                "integrais": integrais,
                "parciais": parciais,
                "faltam": faltam,
                "pode_substituir_o_livro_do_ano": bool(codes) and not reasons,
                "por_que_nao": reasons,
            }
        )

    return {
        "licenca": cobertura["licenca"],
        "licenca_url": cobertura["licenca_url"],
        "frase_pnld": SENTENCE_PNLD,
        "anos": anos,
        "habilidades": claimed,
        "ata": ata(catalog, cobertura, claimed, anos),
    }


def ata(catalog, cobertura, claimed, anos) -> str:
    skills = {h["codigo"]: h for h in catalog["habilidades"]}
    lines = [
        "Ata de adoção de material — Matemática — Cadernos Abertos",
        "",
        "A escola registra, na proposta pedagógica, o material abaixo. O registro não pede livro comprado. Pede que cada habilidade da BNCC tenha material. Esta ata nomeia só o que o caderno ensina por inteiro.",
        "",
        SENTENCE_PNLD,
        "",
        "Licença do texto original: Creative Commons Atribuição 4.0. A escola pode imprimir, copiar e adaptar, desde que atribua a autoria e não retire o aviso de que as frases oficiais das habilidades são da BNCC (MEC, 2018). Não há mensalidade e não há cessão de dados de aluno a terceiro.",
        "",
        "Habilidades para as quais este material passa a ser o material da escola:",
    ]
    integrais = [c for c, item in claimed.items() if item["cobertura"] == "integral"]
    if not integrais:
        lines.append("Nenhuma, neste momento.")
    for code in sorted(integrais):
        item = claimed[code]
        lines.append(f"- {code}. {skills[code]['texto']} Material: {item['titulo']}. {item['nota']}")
    lines.append("")
    lines.append("Habilidades começadas e não encerradas. Não entram como cumpridas, e a escola mantém outro material para o trecho que falta:")
    parciais = [c for c, item in claimed.items() if item["cobertura"] == "parcial"]
    if not parciais:
        lines.append("Nenhuma.")
    for code in sorted(parciais):
        item = claimed[code]
        lines.append(f"- {code}. {skills[code]['texto']} Limite: {item['nota']}")
    lines.append("")
    lines.append("Anos em que este material ainda não substitui o livro didático de Matemática:")
    for row in anos:
        if row["pode_substituir_o_livro_do_ano"]:
            lines.append(f"- {row['ano']}º ano: pode substituir o livro do ano. Todas as habilidades estão integrais.")
        else:
            lines.append(f"- {row['ano']}º ano: não substitui. " + " ".join(row["por_que_nao"]))
    lines += [
        "",
        "Escola privada. A LDB, art. 12, inciso I, entrega à escola a proposta pedagógica. O art. 26 exige a base nacional comum e a parte diversificada. Nenhum dos dois exige editora. O conselho da escola pode aprovar esta ata para as habilidades integrais. Para o resto do ano, a proposta precisa nomear outro material. Um regulamento da própria mantenedora, ou um contrato com um sistema de ensino, pode ser mais estreito do que a lei federal. Esse documento manda na escola que o assinou.",
        "",
        "Escola pública cuja rede aderiu ao PNLD. O termo de adesão, nas orientações do FNDE, compromete a rede a utilizar os livros e materiais encaminhados e a conservá-los. Esta ata não desfaz esse dever. O caderno pode organizar as habilidades integrais junto com o livro recebido. Não pode ser a razão de guardar o livro do PNLD sem uso.",
        "",
        "Rede pública que recusou o PNLD. A recusa é ato da secretaria, na janela de adesão, com a justificativa que o FNDE pedir. Não é ato de uma escola sozinha, e não é ato deste sítio. Mesmo depois da recusa, a rede só pode nomear este caderno como material das habilidades integrais. O restante da BNCC de Matemática continua obrigatório.",
        "",
        "Acessibilidade. A Lei Brasileira de Inclusão exige material acessível ao estudante. Este caderno é visual e de leitura em voz alta. Estudante surdo precisa dos mesmos princípios em Libras, com o objeto deslocado. Estudante cego precisa do par tátil. Adotar só a página impressa, sem essa adaptação, não cumpre a inclusão.",
        "",
        "Dados. O registro de domínio, se a escola usar o modo local, fica no computador da escola. Conta com o primeiro nome que o professor digitou. Não pede CPF. A criança não tem senha. A escola é a controladora desses dados (LGPD e ECA). Este sítio, rodando na máquina da escola, não transmite o registro.",
    ]
    return "\n".join(lines)


def main():
    catalog = load_json(SITE / "data" / "curriculum.json")
    cobertura = load_json(ROOT / "data" / "cobertura.json")
    report = relatorio(catalog, cobertura)
    print(json.dumps({"anos": report["anos"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
