# Cadernos Abertos

Free mathematics textbooks for the Brazilian national curriculum. The map covers every BNCC mathematics skill from preschool through high school, with the dependencies between them written out. One unit is written as a book a student can read, and as the companion a teacher would use beside it.

The overview pages are in English. The books are in Brazilian Portuguese. Each book page has a control that shows an English gloss.

## What is written, and what is only mapped

Mapped: 247 elementary skills, 43 high-school skills, 12 preschool objectives that the number thread grows out of, and 82 concepts with gate and support links.

Written: 1º ano, Unidade 1, *Os números do dia*. It teaches quantity, order, and code; counting each thing once through 20; and comparing on the number line. It does not teach place value or addition facts. Those are the next units, and they are not written yet.

The dependency arrows are a pedagogical inference. The BNCC orders skills by year and does not publish prerequisites. `scripts/test_graph.py` pins the claims the site teaches, including that comparing numbers does not require place value, and that the irrationals wait for Pythagoras.

## Check the graph

```bash
python3 scripts/test_graph.py
```

Rebuilding `site/data/curriculum.json` needs the raw BNCC extract in `data/raw/`, which is not in git:

```bash
python3 scripts/build_curriculum.py
```

## Read it in a browser

The map loads the curriculum with `fetch`, which does not work from a `file://` page. Serve the `site` folder:

```bash
cd site
python3 -m http.server 8741 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8741/>.

## Sources

Skill wording comes from the open dataset [bncc-dados](https://github.com/bncc-dev/bncc-dados), which points each record at the MEC spreadsheet and a page of the 2018 PDF. The page locator is stored on each skill. The wording was spot-checked against that PDF for the skills the argument depends on, and not re-proofed character by character for all 302 records.

The original writing on this site is offered under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). The official BNCC sentences remain the wording of the Ministério da Educação.
