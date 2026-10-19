# Cadernos Abertos

Free mathematics textbooks for the Brazilian national curriculum. The map covers every BNCC mathematics skill from preschool through high school, with the dependencies between them written out. The 1st grade is written as a student book and a teacher book. Later years are mapped and not written.

The overview pages are in English. The books are in Brazilian Portuguese. Each book page has a control that shows an English gloss.

## What is written, and what is only mapped

Mapped: 247 elementary skills, 43 high-school skills, 12 preschool objectives that the number thread grows out of, and 82 concepts with gate and support links.

Written: the whole 1º ano, twelve units, from *Os números do dia* through the class survey. Years 2 through 9 and high school are not written.

The dependency arrows are a pedagogical inference. The BNCC orders skills by year and does not publish prerequisites. `scripts/test_graph.py` pins the concept claims, including that comparing numbers does not require place value. `scripts/test_skill_graph.py` pins the same idea one skill at a time: EF01MA05 depends on the count to 100, and not on composition. The picture of that graph is `site/grafo.html`.

## Check the graph, the adoption rule, and the diagnostic

```bash
python3 scripts/test_graph.py
python3 scripts/test_skill_graph.py
python3 scripts/test_adocao.py
python3 scripts/test_year1.py
python3 scripts/test_diagnostics.py
python3 scripts/test_serve.py
```

Rebuilding `site/data/curriculum.json` needs the raw BNCC extract in `data/raw/`, which is not in git:

```bash
python3 scripts/build_curriculum.py
python3 scripts/skill_graph.py
```

## Read it in a browser

The map, the adoption minute, and the mastery record are served together. A plain static server cannot log a teacher in, and a `file://` page cannot load the curriculum.

```bash
python3 scripts/serve.py
```

Then open <http://127.0.0.1:8741/>. The process binds to this computer only. Student names are written to `data/school/`, which is not committed.

## What a school may adopt

`scripts/adocao.py` builds the minute a school council can paste into the pedagogical proposal. A skill is adoptable when a written book finishes it. A year may replace a textbook only when every mathematics skill of that year is finished. The 1º ano may. Years 2 through 9 and high school may not. The tests fail if the minute claims more, or if it calls the work a PNLD book.

## What a wrong answer means

`scripts/diagnostics.py` checks that every option of an item is a different assumption, and that the correct option loads the target plus its school-age prerequisites. A false rule such as “more digits means larger” does not open a gap in place value. `scripts/test_diagnostics.py` and `scripts/test_serve.py` pin that.

## Sources

Skill wording comes from the open dataset [bncc-dados](https://github.com/bncc-dev/bncc-dados), which points each record at the MEC spreadsheet and a page of the 2018 PDF. The page locator is stored on each skill. The wording was spot-checked against that PDF for the skills the argument depends on, and not re-proofed character by character for all 302 records.

The original writing on this site is offered under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). The official BNCC sentences remain the wording of the Ministério da Educação.
