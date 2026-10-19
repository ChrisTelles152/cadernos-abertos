#!/usr/bin/env python3
"""Each option is one assumption, and the fold does not launder it into another concept."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from diagnostics import expected_load, fold, index_concepts, judgement, validate_bank


def load():
    catalog = json.loads((ROOT / "site" / "data" / "curriculum.json").read_text(encoding="utf-8"))
    bank = json.loads((ROOT / "data" / "diagnostico.json").read_text(encoding="utf-8"))
    return catalog, bank


def answer(item, option):
    return {"tipo": "resposta", "item": item, "opcao": option}


def test_every_item_loads_its_school_age_prerequisites(catalog, bank):
    validate_bank(catalog, bank)
    concepts = index_concepts(catalog)
    by_id = {item["id"]: item for item in bank["itens"]}
    assert expected_load(concepts, "N-COMPARAR") == {"N-COMPARAR", "N-CONTAGEM", "N-SENTIDO"}
    assert "N-COMPOR" not in expected_load(concepts, "N-COMPARAR")
    comparar = by_id["q-comparar"]
    certa = next(o for o in comparar["opcoes"] if o["tipo"] == "certa")
    assert certa["id"] == "depois"
    digit = next(o for o in comparar["opcoes"] if o["id"] == "mais-digitos")
    assert digit["tipo"] == "regra_falsa"
    assert "12" in digit["texto"]


def test_more_digits_is_not_a_place_value_gap(catalog, bank):
    judged = judgement(catalog, bank, "q-comparar", "mais-digitos")
    assert judged["certa"] is False
    assert judged["regra"] == "F-MAIS-DIGITOS"
    assert "N-COMPOR" in judged["nao_confundir_com"]
    report = fold(catalog, bank, [answer("q-comparar", "mais-digitos")])
    assert report["conceitos"]["N-COMPARAR"]["estado"] == "gap"
    assert "N-COMPOR" not in report["conceitos"]
    assert report["bloqueados_sem_tentativa"] == []
    assert "99 e 100" in report["conceitos"]["N-COMPARAR"]["hipoteses"][0]["hipotese"]


def test_a_missing_count_blocks_comparison_and_place_value_without_failing_them(catalog, bank):
    report = fold(catalog, bank, [answer("q-comparar", "nao-sei-a-ordem")])
    assert report["conceitos"]["N-CONTAGEM"]["estado"] == "gap"
    assert report["conceitos"]["N-COMPARAR"]["estado"] == "bloqueado"
    assert "N-COMPOR" in report["bloqueados_sem_tentativa"]
    assert report["conceitos"].get("N-COMPOR", {}).get("estado") != "gap"


def test_a_false_rule_stays_put_when_a_later_lacuna_blocks_the_descendants(catalog, bank):
    report = fold(
        catalog,
        bank,
        [answer("q-comparar", "mais-digitos"), answer("q-comparar", "nao-sei-a-ordem")],
    )
    assert report["conceitos"]["N-COMPARAR"]["estado"] == "gap"
    assert report["conceitos"]["N-CONTAGEM"]["estado"] == "gap"
    assert "N-COMPOR" in report["bloqueados_sem_tentativa"]
    assert report["conceitos"].get("N-COMPOR", {}).get("estado") != "gap"


def test_a_later_correct_answer_does_not_erase_the_hypothesis(catalog, bank):
    report = fold(
        catalog,
        bank,
        [answer("q-comparar", "mais-digitos"), answer("q-comparar", "depois")],
    )
    node = report["conceitos"]["N-COMPARAR"]
    assert node["estado"] == "gap"
    assert node["evidencias"]
    assert "1/5" in node["evidencias"][0]["chance"]


def test_credit_conflicts_with_a_later_gap_under_it(catalog, bank):
    report = fold(
        catalog,
        bank,
        [answer("q-comparar", "depois"), answer("q-contagem", "nome-do-prato")],
    )
    assert report["conceitos"]["N-SENTIDO"]["estado"] == "gap"
    assert report["conceitos"]["N-COMPARAR"]["estado"] == "conflito"
    assert report["conceitos"]["N-CONTAGEM"]["estado"] == "conflito"


def test_archiving_a_lacuna_lifts_the_block_and_does_not_grant_credit(catalog, bank):
    report = fold(
        catalog,
        bank,
        [
            answer("q-comparar", "nao-sei-a-ordem"),
            {"tipo": "reparo", "conceito": "N-CONTAGEM"},
        ],
    )
    assert "N-CONTAGEM" not in report["conceitos"]
    assert report["conceitos"]["N-COMPARAR"]["estado"] == "unseen"
    assert "N-COMPOR" not in report["bloqueados_sem_tentativa"]
    assert report["conceitos"]["N-COMPARAR"]["evidencias"] == []


def test_no_reason_changes_nothing(catalog, bank):
    report = fold(catalog, bank, [answer("q-comparar", "sem-razao")])
    assert report["conceitos"] == {}
    assert report["bloqueados_sem_tentativa"] == []


def test_pointing_at_the_greater_number_for_the_digit_rule_is_not_credit(catalog, bank):
    wrong = judgement(catalog, bank, "q-comparar", "mais-digitos")
    right = judgement(catalog, bank, "q-comparar", "depois")
    assert wrong["certa"] is False and right["certa"] is True
    assert set(right["credito"]) == {"N-SENTIDO", "N-CONTAGEM", "N-COMPARAR"}
    assert "N-COMPOR" not in right["credito"]


def main():
    catalog, bank = load()
    test_every_item_loads_its_school_age_prerequisites(catalog, bank)
    test_more_digits_is_not_a_place_value_gap(catalog, bank)
    test_a_missing_count_blocks_comparison_and_place_value_without_failing_them(catalog, bank)
    test_a_false_rule_stays_put_when_a_later_lacuna_blocks_the_descendants(catalog, bank)
    test_a_later_correct_answer_does_not_erase_the_hypothesis(catalog, bank)
    test_credit_conflicts_with_a_later_gap_under_it(catalog, bank)
    test_archiving_a_lacuna_lifts_the_block_and_does_not_grant_credit(catalog, bank)
    test_no_reason_changes_nothing(catalog, bank)
    test_pointing_at_the_greater_number_for_the_digit_rule_is_not_credit(catalog, bank)
    print("diagnostic claims hold")


if __name__ == "__main__":
    main()
