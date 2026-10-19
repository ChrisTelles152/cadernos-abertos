#!/usr/bin/env python3
"""Build the math curriculum catalog and the inferred dependency graph.

The skill wording comes from the open dataset bncc-dados, which traces each
record to the MEC spreadsheet exported from downloadbncc.mec.gov.br and to a
page of the homologated BNCC PDF. The edges do not. The BNCC never publishes
prerequisites. Every edge here is a pedagogical inference, marked exige
(the later idea is unfinished without the earlier one) or apoia (the earlier
idea makes the later one much stronger, and a careful teacher can start).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "site" / "data" / "curriculum.json"

# fio, nome, nome_pt, resumo, nota, exige, apoia, porque, habilidades, livro
# ano is computed from the skills. porque must explain every exige and apoia edge.

CONCEITOS = [
    {
        "id": "EI-CONTAR",
        "fio": "infancia",
        "nome": "Oral counting and recording how many",
        "nome_pt": "Contar de boca e registrar quantos",
        "resumo": "In preschool the child says the count aloud, matches it to objects, and begins to write a number for a quantity. This is lived experience, not a textbook chapter. Brazilian early childhood does not use a textbook the way fundamental school does.",
        "exige": [],
        "apoia": [],
        "porque": {},
        "habilidades": ["EI02ET07", "EI02ET08", "EI03ET07"],
    },
    {
        "id": "EI-COMPARAR",
        "fio": "infancia",
        "nome": "Compare, sort, and record without a standard unit",
        "nome_pt": "Comparar, classificar e registrar",
        "resumo": "Bigger, heavier, same shape, a different color. Preschool comparison and sorting are the root of measurement, of geometry, and of data. A basic picture-graph of the class already appears here.",
        "exige": [],
        "apoia": [],
        "porque": {},
        "habilidades": ["EI02ET01", "EI02ET05", "EI03ET01", "EI03ET04", "EI03ET05", "EI03ET08"],
    },
    {
        "id": "EI-ESPACO",
        "fio": "infancia",
        "nome": "Lived space and lived time",
        "nome_pt": "Espaço e tempo vividos",
        "resumo": "In, on, under, beside, before, during, after. These words are in the body before they are in a lesson. Year 1 geometry and the calendar both start from here.",
        "exige": [],
        "apoia": [],
        "porque": {},
        "habilidades": ["EI01ET04", "EI02ET04", "EI02ET06"],
    },
    {
        "id": "N-SENTIDO",
        "fio": "numero",
        "nome": "Quantity, order, and code",
        "nome_pt": "Quantidade, ordem e código",
        "resumo": "A number does three different jobs. It tells how many, it tells which position, or it is only a name, like a bus line or a jersey. The first job of year 1 is to stop treating those as the same thing.",
        "nota": "This is the root of the number thread and the unit written in the student book.",
        "livro": "aluno/os-numeros-do-dia.html",
        "exige": ["EI-CONTAR"],
        "apoia": [],
        "porque": {
            "EI-CONTAR": "Preschool already pairs a spoken count with things. Year 1 splits that act into three social jobs: quantity, order, and a code that does not answer 'how many'.",
        },
        "habilidades": ["EF01MA01"],
    },
    {
        "id": "N-CONTAGEM",
        "fio": "numero",
        "nome": "Exact count, estimate, and pairing",
        "nome_pt": "Contagem exata, estimativa e pareamento",
        "resumo": "Count each object once, in a stable order, and let the last word be the size of the whole collection. Estimate first. Pair when you want to compare without numerals. The base asks for this up to about 20 for comparison and up to 100 for the count itself.",
        "nota": "Unit 1 counts through 20. Unit 2, Dez e mais dez, counts collections to 100 and records the result in words and in numerals.",
        "livro": "aluno/dez-e-dez.html",
        "exige": ["N-SENTIDO"],
        "apoia": [],
        "porque": {
            "N-SENTIDO": "Exact counting is the quantity-use of a number. A child who still thinks every numeral is a bus line has nothing stable to count.",
        },
        "habilidades": ["EF01MA02", "EF01MA03", "EF01MA04"],
    },
    {
        "id": "N-COMPARAR",
        "fio": "numero",
        "nome": "Which number is later is larger",
        "nome_pt": "Quem vem depois na contagem é maior",
        "resumo": "Compare numerals up to two orders by the count sequence and by a number line. The later number in the count is the greater one.",
        "nota": "This does not require place value. Unit 1 compares through 20 and refuses the digit rule. Unit 2 finishes two-digit comparison, on the line and off it. 'More digits means bigger' still fails inside two orders when both numbers have two digits, as in 28 and 31.",
        "livro": "aluno/dez-e-dez.html",
        "exige": ["N-CONTAGEM"],
        "apoia": [],
        "porque": {
            "N-CONTAGEM": "You can only say that 15 is larger than 8 because 15 comes later in a count you trust, or because pairing leaves some of the 15 unmatched. The number line is that count laid on a cord.",
        },
        "habilidades": ["EF01MA05"],
    },
    {
        "id": "N-COMPOR",
        "fio": "numero",
        "nome": "Break numbers into sums, up to two orders",
        "nome_pt": "Compor e decompor até duas ordens",
        "resumo": "Build and break numbers up to 99 as sums, with materials in the hands. This is the first sight of the decimal system: groups, not just a long count.",
        "livro": "aluno/dez-e-dez.html",
        "exige": ["N-CONTAGEM"],
        "apoia": [],
        "porque": {
            "N-CONTAGEM": "A ten is a counted group. If the count is unreliable, the group is only a pile with a hopeful label.",
        },
        "habilidades": ["EF01MA07"],
    },
    {
        "id": "N-FATOS",
        "fio": "numero",
        "nome": "Basic addition and subtraction facts",
        "nome_pt": "Fatos básicos da adição e da subtração",
        "resumo": "Know the small sums and differences well enough to use them, instead of restarting the count from one every time.",
        "livro": "aluno/fatos.html",
        "exige": ["N-CONTAGEM", "N-COMPOR"],
        "apoia": [],
        "porque": {
            "N-CONTAGEM": "A fact the child cannot check by counting is a jingle. The count is the check.",
            "N-COMPOR": "7 = 5 + 2 is a decomposition. The facts are the decompositions used so often they become available in the head.",
        },
        "habilidades": ["EF01MA06", "EF02MA05"],
    },
    {
        "id": "N-ADDSUB",
        "fio": "numero",
        "nome": "Addition and subtraction as actions",
        "nome_pt": "Juntar, acrescentar, separar, retirar, comparar, completar",
        "resumo": "Year 1 works four meanings: join, add on, separate, take away. Year 3 adds compare and complete. The algorithms arrive as one strategy among others, not as the definition of the operation.",
        "livro": "aluno/juntar-retirar.html",
        "exige": ["N-FATOS", "N-COMPARAR"],
        "apoia": ["N-COMPOR"],
        "porque": {
            "N-FATOS": "The small facts are the pieces a child moves while solving. Without them every problem restarts at the count.",
            "N-COMPARAR": "'How many more' and 'how many to complete' are comparison questions. They are not the same as take-away, and the base holds them until the comparison idea exists.",
            "N-COMPOR": "Breaking a number to cross a ten is a decomposition strategy. It helps, and a child can solve join-problems with a count before they have it.",
        },
        "habilidades": ["EF01MA08", "EF02MA03", "EF02MA06", "EF03MA05", "EF03MA06", "EF04MA03"],
    },
    {
        "id": "N-CENTENA",
        "fio": "numero",
        "nome": "Place value to the hundreds, and the job of zero",
        "nome_pt": "Centenas e a função do zero",
        "resumo": "Read, write, order, and break numbers up to 999. Zero is a position with nothing in it, not a number that 'doesn't count'.",
        "exige": ["N-COMPOR", "N-COMPARAR"],
        "apoia": [],
        "porque": {
            "N-COMPOR": "Hundreds are the two-order decomposition extended by the same rule: ten of these make one of those.",
            "N-COMPARAR": "Ordering to 999 still means deciding which is greater. Place value becomes the tool, but the question is the old comparison question.",
        },
        "habilidades": ["EF02MA01", "EF02MA02", "EF02MA04"],
    },
    {
        "id": "N-MILHAR",
        "fio": "numero",
        "nome": "The same system, through the thousands",
        "nome_pt": "O sistema até a ordem dos milhares",
        "resumo": "Read, write, compare, and decompose numbers through four and five orders. The rule does not change. The number of positions does.",
        "exige": ["N-CENTENA"],
        "apoia": [],
        "porque": {
            "N-CENTENA": "A thousand is ten hundreds. A child who does not yet trust hundreds cannot see the next position as the same idea.",
        },
        "habilidades": ["EF03MA01", "EF03MA02", "EF04MA01", "EF04MA02"],
    },
    {
        "id": "N-RETA",
        "fio": "numero",
        "nome": "The number line as a scale",
        "nome_pt": "A reta numérica como escala",
        "resumo": "Place naturals on a line with equal steps, and use the line to order them and to support calculation.",
        "exige": ["N-COMPARAR", "N-CENTENA"],
        "apoia": [],
        "porque": {
            "N-COMPARAR": "The walked cord of year 1 is the ancestor. Year 3 needs the steps to be equal, so position means size.",
            "N-CENTENA": "Equal steps only stay honest once the order of the larger numbers is known, including the jumps at 10, 100, and the empty place marked by zero.",
        },
        "habilidades": ["EF03MA04"],
    },
    {
        "id": "N-MULT",
        "fio": "numero",
        "nome": "Multiplication: equal groups, arrays, proportion",
        "nome_pt": "Multiplicação: parcelas iguais, retângulo, proporção",
        "resumo": "Year 2 starts with repeated addition, factors 2 through 5. Year 4 requires three meanings side by side: equal groups, the rectangular array, and proportionality. Basic multiplication facts sit in between.",
        "exige": ["N-ADDSUB"],
        "apoia": [],
        "porque": {
            "N-ADDSUB": "The first meaning the base uses is equal groups, and equal groups are addition repeated. The array and the rate come after that meaning is available.",
        },
        "habilidades": ["EF02MA07", "EF03MA03", "EF03MA07", "EF04MA06"],
    },
    {
        "id": "N-METADE",
        "fio": "numero",
        "nome": "Double, half, triple, third",
        "nome_pt": "Dobro, metade, triplo e terça parte",
        "resumo": "Half by pairing, double as two equal groups, and the language of a third. This is the oral ancestor of the unit fractions, still done with objects.",
        "exige": ["N-CONTAGEM"],
        "apoia": ["N-MULT"],
        "porque": {
            "N-CONTAGEM": "Half of a collection can be made by pairing, before any division algorithm exists.",
            "N-MULT": "Double and triple are equal groups. Once multiplication has that name, the words dobro and triplo have somewhere to live.",
        },
        "habilidades": ["EF02MA08"],
    },
    {
        "id": "N-DIV",
        "fio": "numero",
        "nome": "Division: share, measure, and remainder",
        "nome_pt": "Divisão: repartir, medir, e o resto",
        "resumo": "Share equally, or ask how many groups of a given size fit. Remainder zero and remainder not zero are both part of the idea. Half, third, fourth, fifth, and tenth are named as quotients here, before they are written as fractions.",
        "exige": ["N-MULT"],
        "apoia": ["N-METADE"],
        "porque": {
            "N-MULT": "Sharing and measuring undo equal groups. Without the groups, the two questions (how many in each, how many groups) have no parent operation.",
            "N-METADE": "The words metade and terça parte have already been used with objects. Division is where those words become quotients.",
        },
        "habilidades": ["EF03MA08", "EF03MA09", "EF04MA07"],
    },
    {
        "id": "N-RELACAO",
        "fio": "numero",
        "nome": "Operations know each other",
        "nome_pt": "Relações e propriedades das operações",
        "resumo": "Addition undoes subtraction. Multiplication undoes division. The properties are tools for calculating, not a list to recite.",
        "exige": ["N-ADDSUB", "N-MULT", "N-DIV"],
        "apoia": [],
        "porque": {
            "N-ADDSUB": "You cannot see that addition and subtraction undo each other before you have used both.",
            "N-MULT": "Multiplication becomes invertible only after the student has built equal groups and can ask what was grouped.",
            "N-DIV": "Division is the other half of that pair. The inverse relationship is a discovery about operations the child already performs.",
        },
        "habilidades": ["EF04MA04", "EF04MA05", "EF04MA13"],
    },
    {
        "id": "N-COMBINA",
        "fio": "numero",
        "nome": "Counting combinations",
        "nome_pt": "Contagem de combinações",
        "resumo": "Each item of one collection with every item of another. Year 4 does this with objects and drawings. Year 5 states the product. Year 8 names the multiplicative principle, and high school adds ordered and unordered groupings.",
        "exige": ["N-MULT"],
        "apoia": [],
        "porque": {
            "N-MULT": "The combination count is the rectangular meaning of multiplication, used to count pairings rather than objects in a grid.",
        },
        "habilidades": ["EF04MA08", "EF05MA09", "EF08MA03", "EM13MAT310"],
    },
    {
        "id": "N-FRACAO",
        "fio": "numero",
        "nome": "Fractions: part, quotient, ratio, operator",
        "nome_pt": "Frações: parte, quociente, razão, operador",
        "resumo": "Unit fractions first (1/2, 1/3, 1/4, 1/5, 1/10, and the family of 1/100). Then several meanings at once, equivalence, comparison, a fraction of a quantity, and addition and subtraction of positive fractions.",
        "exige": ["N-DIV", "G-PLANO"],
        "apoia": ["N-METADE"],
        "porque": {
            "N-DIV": "A fraction is a fair share that did not come out a whole number, and it is the quotient of a division. The share has to be a familiar question first.",
            "G-PLANO": "The other picture the base requires is a part of a shape. Without plane figures, 'part of a whole' has nothing to point at.",
            "N-METADE": "Metade and terça parte are already words for these same cuts. The fraction notation names them.",
        },
        "habilidades": ["EF04MA09", "EF05MA03", "EF05MA04", "EF05MA05", "EF06MA07", "EF06MA09", "EF06MA10", "EF07MA08"],
    },
    {
        "id": "N-DECIMAL",
        "fio": "numero",
        "nome": "Finite decimals, and the passage to fractions",
        "nome_pt": "Decimais finitos e a ida e volta com a fração",
        "resumo": "Tenths and hundredths as money and as measurement, then as points on the number line, then under the four operations. Year 6 asks the student to move between the fraction writing and the decimal writing of the same positive rational.",
        "nota": "A decimal is not two whole numbers with a dot between them. The dot marks where the ones sit. That mark is meaningless without place value on the left and tenths, as fractions, on the right.",
        "exige": ["N-MILHAR", "N-FRACAO"],
        "apoia": [],
        "porque": {
            "N-MILHAR": "The positions to the right of the ones obey the same ten-for-one rule as the positions to the left. The rule has to be trusted first.",
            "N-FRACAO": "A tenth is a fraction with denominator 10. Without that, 0.1 has no size, and equivalence between 1/2 and 0.5 is a trick.",
        },
        "habilidades": ["EF04MA10", "EF05MA02", "EF05MA07", "EF05MA08", "EF06MA08", "EF06MA11"],
    },
    {
        "id": "N-PORCENTO",
        "fio": "numero",
        "nome": "Percent",
        "nome_pt": "Porcentagem",
        "resumo": "10%, 25%, 50%, 75%, and 100% arrive as a tenth, a fourth, a half, three fourths, and a whole. Later: increase and decrease, successive percents, and financial contexts. The base explicitly says not to open with the cross-multiplication rule.",
        "exige": ["N-FRACAO", "N-DECIMAL"],
        "apoia": ["A-PROP"],
        "porque": {
            "N-FRACAO": "The first percents in the base are unit-fraction language. Percent is a fraction per hundred, not a new species of number.",
            "N-DECIMAL": "Money and the decimal writing of a rate are where percent gets used. The decimal has to already be a number.",
            "A-PROP": "Year 6 ties percent to proportionality. The proportion makes the strategies faster. It is not required to understand that 50% is a half.",
        },
        "habilidades": ["EF05MA06", "EF06MA13", "EF07MA02", "EF08MA04", "EF09MA05"],
    },
    {
        "id": "N-GRANDE",
        "fio": "numero",
        "nome": "Large naturals, and rounding to powers of ten",
        "nome_pt": "Naturais grandes e arredondamento",
        "resumo": "Read and order naturals past the thousands, recognize the decimal system as a system (base, place, zero), and round to a nearby power of ten.",
        "exige": ["N-MILHAR"],
        "apoia": [],
        "porque": {
            "N-MILHAR": "A million is the same positions, one more time. Rounding to a power of ten is choosing which position still matters.",
        },
        "habilidades": ["EF05MA01", "EF06MA01", "EF06MA02", "EF06MA12"],
    },
    {
        "id": "N-OPERAR",
        "fio": "numero",
        "nome": "Fluent operations with naturals",
        "nome_pt": "Cálculo com naturais, inclusive uma primeira potência",
        "resumo": "Mental, written, and approximate calculation with naturals, calculator included, with the student able to say what the steps did. Powers sit inside this skill as one of the operations, before roots are studied.",
        "exige": ["N-RELACAO", "N-GRANDE"],
        "apoia": [],
        "porque": {
            "N-RELACAO": "Fluent calculation is the use of the relationships between operations, not a faster algorithm recited blind.",
            "N-GRANDE": "The numbers being operated on are large enough that a strategy matters. The student has to be able to read them.",
        },
        "habilidades": ["EF06MA03"],
    },
    {
        "id": "N-DIVIS",
        "fio": "numero",
        "nome": "Multiples, divisors, primes, divisibility",
        "nome_pt": "Múltiplos, divisores, primos e divisibilidade",
        "resumo": "Even and odd, divisibility criteria, prime and composite, gcd and lcm, without being handed the algorithms as the only route.",
        "exige": ["N-DIV", "A-PADRAO"],
        "apoia": [],
        "porque": {
            "N-DIV": "A divisor is what division by that number leaves remainder zero. The remainder has to be a familiar object.",
            "A-PADRAO": "Year 4 already built the sequences of multiples, and the families of numbers that leave the same remainder. Divisibility names that pattern.",
        },
        "habilidades": ["EF06MA05", "EF06MA06", "EF07MA01"],
    },
    {
        "id": "N-INTEIRO",
        "fio": "numero",
        "nome": "Integers",
        "nome_pt": "Números inteiros",
        "resumo": "Debts, temperatures below zero, floors below the ground. Order them, put them on the line, and operate. The sign is a direction, not a decoration.",
        "exige": ["N-ADDSUB", "N-RETA"],
        "apoia": [],
        "porque": {
            "N-ADDSUB": "A negative appears when take-away does not stop at zero. The operation is old. The refusal to stop is new.",
            "N-RETA": "The integer is a position on the line in the direction opposite the count. Without the line, the sign has no geometry.",
        },
        "habilidades": ["EF07MA03", "EF07MA04"],
    },
    {
        "id": "N-RACIONAIS",
        "fio": "numero",
        "nome": "Rational numbers as one object",
        "nome_pt": "Números racionais",
        "resumo": "The same number in fraction form and decimal form, ordered on the line, multiplied and divided, including negatives. A repeating decimal is given back its generating fraction.",
        "exige": ["N-DECIMAL", "N-FRACAO", "N-INTEIRO"],
        "apoia": [],
        "porque": {
            "N-DECIMAL": "One of the two writings is the finite or repeating decimal.",
            "N-FRACAO": "The other writing is the fraction. Equivalence between them is the content, so both writings already have to mean a size.",
            "N-INTEIRO": "The rationals in year 7 are no longer only the positive ones. The sign comes from the integers.",
        },
        "habilidades": ["EF07MA10", "EF07MA11", "EF07MA12", "EF08MA05"],
    },
    {
        "id": "N-POTENCIA",
        "fio": "numero",
        "nome": "Powers and roots",
        "nome_pt": "Potenciação e radiciação",
        "resumo": "A root written as a power with a fractional exponent, then calculation with real numbers including those exponents.",
        "exige": ["N-OPERAR", "N-MULT"],
        "apoia": ["N-RACIONAIS"],
        "porque": {
            "N-OPERAR": "Year 6 already used a power as one operation among the others. Year 8 studies the relationship with the root.",
            "N-MULT": "A positive integer power is multiplication repeated. That meaning has to be available before the exponent stops being a whole number.",
            "N-RACIONAIS": "A fractional exponent refers to a root and to a fraction. The rational number makes the exponent readable.",
        },
        "habilidades": ["EF08MA02", "EF09MA03"],
    },
    {
        "id": "N-CIENCIA",
        "fio": "numero",
        "nome": "Scientific notation",
        "nome_pt": "Notação científica",
        "resumo": "Write very large and very small numbers as a number between 1 and 10 times a power of ten, and use that writing in problems. High school adds significant digits.",
        "exige": ["N-POTENCIA", "N-DECIMAL"],
        "apoia": [],
        "porque": {
            "N-POTENCIA": "The exponent on the ten is a power. Without powers, the notation is a ritual with a superscript.",
            "N-DECIMAL": "The coefficient is a decimal between 1 and 10. The student has to be able to read it as a number.",
        },
        "habilidades": ["EF08MA01", "EF09MA04", "EM13MAT313"],
    },
    {
        "id": "N-REAIS",
        "fio": "numero",
        "nome": "Irrationals and the real line",
        "nome_pt": "Irracionais e a reta real",
        "resumo": "Once a unit of length is fixed, some segments have no rational length. The diagonal of the unit square is the standard shock. An irrational is then a real whose decimal never ends and never repeats, located approximately on the line.",
        "nota": "The dependency runs from Pythagoras to the irrationals. Do not use the real numbers to justify Pythagoras. In this curriculum the theorem comes first and the new kind of number is what the theorem forces.",
        "exige": ["N-RACIONAIS", "G-PITAGORAS"],
        "apoia": [],
        "porque": {
            "N-RACIONAIS": "The claim is that some lengths are not rational. The student has to know what a rational is, in both writings, before a number can fail to be one.",
            "G-PITAGORAS": "The base introduces the need through geometry: the diagonal of a polygon, the altitude of a triangle, when a side is the unit. Those lengths are Pythagorean. The number is the name of a length the rationals cannot reach.",
        },
        "habilidades": ["EF09MA01", "EF09MA02"],
    },
    {
        "id": "A-ATRIBUTO",
        "fio": "algebra",
        "nome": "Sort by an attribute",
        "nome_pt": "Ordenar por um atributo",
        "resumo": "Organize familiar objects by color, shape, or size. This is the whole of year-1 'algebra'. There is no letter and no equation.",
        "livro": "aluno/uma-marca.html",
        "exige": ["EI-COMPARAR"],
        "apoia": [],
        "porque": {
            "EI-COMPARAR": "Sorting by one attribute is the preschool classification, now done on purpose and said aloud.",
        },
        "habilidades": ["EF01MA09"],
    },
    {
        "id": "A-PADRAO",
        "fio": "algebra",
        "nome": "Patterns and recursive sequences",
        "nome_pt": "Padrões e sequências",
        "resumo": "Say the rule, then fill the gap. Repeating patterns and recursive ones (add 1, add 2, subtract 1). Later: sequences of multiples, equal remainders, and recursive sequences that are no longer only 'add a constant'.",
        "livro": "aluno/uma-marca.html",
        "exige": ["A-ATRIBUTO", "N-CONTAGEM"],
        "apoia": [],
        "porque": {
            "A-ATRIBUTO": "A pattern is an attribute that repeats or grows. Seeing the attribute is the sorting skill, pointed along a sequence.",
            "N-CONTAGEM": "The numeric patterns are a count that jumps. The ordinary count has to be stable before the jump is visible.",
        },
        "habilidades": ["EF01MA10", "EF02MA09", "EF02MA10", "EF02MA11", "EF03MA10", "EF04MA11", "EF04MA12", "EF08MA10", "EF08MA11"],
    },
    {
        "id": "A-IGUAL",
        "fio": "algebra",
        "nome": "Equality as sameness, not as 'here comes the answer'",
        "nome_pt": "Igualdade como equivalência",
        "resumo": "Different sums can name the same number. Adding, subtracting, multiplying, or dividing both sides by the same number keeps the equality. This is the gate to the unknown.",
        "exige": ["N-ADDSUB"],
        "apoia": ["N-RELACAO"],
        "porque": {
            "N-ADDSUB": "A child sees that two writings name the same value only after they have built one number in more than one way.",
            "N-RELACAO": "Knowing that multiplication undoes division makes the legal moves on an equality feel like operations, not like rules about a symbol.",
        },
        "habilidades": ["EF03MA11", "EF04MA14", "EF04MA15", "EF05MA10", "EF05MA11", "EF06MA14"],
    },
    {
        "id": "A-PROP",
        "fio": "algebra",
        "nome": "Direct and inverse proportion",
        "nome_pt": "Proporcionalidade direta e inversa",
        "resumo": "Direct proportion from year 5, in price and recipe situations. Inverse proportion from year 7. Year 9 adds ratios of unlike quantities (speed, density) and several quantities at once, including scale.",
        "exige": ["N-MULT", "N-FRACAO"],
        "apoia": [],
        "porque": {
            "N-MULT": "A constant rate is a multiplication. Doubling one quantity doubles the other. That is the equal-groups meaning, read across a situation.",
            "N-FRACAO": "The rate itself is written as a fraction or a ratio. Without fractions the rate has no numeral.",
        },
        "habilidades": ["EF05MA12", "EF05MA13", "EF07MA17", "EF08MA12", "EF08MA13", "EF09MA08"],
    },
    {
        "id": "A-RAZAO",
        "fio": "algebra",
        "nome": "Ratio, including unlike quantities",
        "nome_pt": "Razão",
        "resumo": "Share a quantity into two unequal parts and say the ratio of the parts, and of a part to the whole. Connect ratio to fraction. Later, speed and population density: a ratio of two different kinds of measure. High school studies quantities defined as a ratio or a product of others.",
        "exige": ["A-PROP", "N-FRACAO"],
        "apoia": [],
        "porque": {
            "A-PROP": "A ratio is a proportion read inside one situation. The constant rate has to be a familiar idea.",
            "N-FRACAO": "The base writes the ratio 2 to 3 as the fraction 2/3. The fraction is the notation, so it cannot be new at the same moment.",
        },
        "habilidades": ["EF06MA15", "EF07MA09", "EF09MA07", "EM13MAT314"],
    },
    {
        "id": "A-LETRA",
        "fio": "algebra",
        "nome": "Variable and unknown",
        "nome_pt": "Variável e incógnita",
        "resumo": "A letter names a number. Sometimes it is an unknown to find. Sometimes it is a variable that runs. Equivalent expressions come from seeing the regularity in a geometric pattern or a number pattern.",
        "exige": ["A-IGUAL", "N-RELACAO"],
        "apoia": [],
        "porque": {
            "A-IGUAL": "A letter inside an equality only makes sense if the equality is a statement of sameness that can be rewritten.",
            "N-RELACAO": "Rewriting an expression uses the properties of the operations. Otherwise the algebra is letter-moving.",
        },
        "habilidades": ["EF07MA13", "EF07MA14", "EF07MA15", "EF07MA16", "EF08MA06"],
    },
    {
        "id": "A-EQ1",
        "fio": "algebra",
        "nome": "First-degree equations and systems",
        "nome_pt": "Equações e sistemas do 1º grau",
        "resumo": "Problems that become ax + b = c. Then a linear equation in two unknowns as a line, and a 2×2 system. High school returns to simultaneous linear equations with a wider set of techniques.",
        "nota": "Integers are the same year as the first equations. Equations whose solution is a natural number can come first, in the same term. Equations that need a negative solution wait until the integer is a number.",
        "exige": ["A-LETRA", "N-INTEIRO"],
        "apoia": ["G-CARTES"],
        "porque": {
            "A-LETRA": "The unknown is a letter that already behaves like a number.",
            "N-INTEIRO": "The solution of ax + b = c is not always positive. By year 7 the base has integers available, and the equation should be allowed to land on them.",
            "G-CARTES": "Seeing ax + by = c as a line needs the plane. The algebraic solution of one equation in one unknown does not.",
        },
        "habilidades": ["EF07MA18", "EF08MA07", "EF08MA08", "EM13MAT301"],
    },
    {
        "id": "A-EQ2",
        "fio": "algebra",
        "nome": "Second-degree equations",
        "nome_pt": "Equações do 2º grau",
        "resumo": "Year 8 solves ax² = b. Year 9 factorizes and uses remarkable products to solve the general quadratic, in problems.",
        "exige": ["A-EQ1", "N-POTENCIA"],
        "apoia": [],
        "porque": {
            "A-EQ1": "Isolating a term, and keeping both sides equal, is the first-degree craft. The quadratic adds the square. It does not replace the craft.",
            "N-POTENCIA": "ax² = b asks for a number whose square is known. The square is a power, and the root undoes it.",
        },
        "habilidades": ["EF08MA09", "EF09MA09"],
    },
    {
        "id": "A-FLUXO",
        "fio": "algebra",
        "nome": "Algorithms and flowcharts",
        "nome_pt": "Algoritmos e fluxogramas",
        "resumo": "Write a procedure in ordinary language and as a flowchart, first for a simple decision such as 'is this number even'. Year 7 generalizes: problems with the same structure share a procedure. High school records an algorithm and begins to write it in a programming language.",
        "exige": ["N-DIV", "A-IGUAL"],
        "apoia": ["N-DIVIS"],
        "porque": {
            "N-DIV": "The first flowchart in the base decides parity, which is division by 2 and a remainder. The decision needs a remainder.",
            "A-IGUAL": "A procedure is worth writing down when a whole family of problems has the same structure and returns the same kind of answer. That is the equality-and-structure idea.",
            "N-DIVIS": "Once primes, multiples, and divisibility criteria exist, the flowchart has harder decisions to express than even and odd.",
        },
        "habilidades": ["EF06MA04", "EF07MA05", "EF07MA06", "EF07MA07", "EM13MAT315", "EM13MAT405"],
    },
    {
        "id": "A-FUNCAO",
        "fio": "algebra",
        "nome": "Functions, starting with the affine",
        "nome_pt": "Funções, a partir da função afim",
        "resumo": "Year 9 defines a function as a univocal dependence and uses tables, formulas, and graphs. High school investigates the affine function from tables, converts formula to graph, separates the proportional case, and reads piecewise graphs such as a utility bill. Rates of change in real situations belong here.",
        "exige": ["A-EQ1", "G-CARTES", "A-PROP"],
        "apoia": [],
        "porque": {
            "A-EQ1": "The formula of an affine function is the expression inside the first-degree equation, now allowed to vary instead of being solved once.",
            "G-CARTES": "The graph is the set of pairs on the plane. Coordinates have to already locate a point.",
            "A-PROP": "The line through the origin is direct proportion. The base asks students to distinguish that case. Proportion is the old idea, seen as a function.",
        },
        "habilidades": ["EF09MA06", "EM13MAT101", "EM13MAT302", "EM13MAT401", "EM13MAT404", "EM13MAT501", "EM13MAT506"],
    },
    {
        "id": "A-QUAD",
        "fio": "algebra",
        "nome": "Quadratic functions",
        "nome_pt": "Função quadrática",
        "resumo": "Recognize y = ax² from a table, draw it, distinguish the proportional-to-the-square case, and investigate maxima and minima in area, finance, and motion.",
        "exige": ["A-FUNCAO", "A-EQ2"],
        "apoia": [],
        "porque": {
            "A-FUNCAO": "A quadratic is a function. The table, the formula, and the graph are already the representations. The new shape is the parabola.",
            "A-EQ2": "The square in the formula, and the question of where it is zero, are the second-degree equation. The function is that equation set in motion.",
        },
        "habilidades": ["EM13MAT402", "EM13MAT502", "EM13MAT503"],
    },
    {
        "id": "A-EXP",
        "fio": "algebra",
        "nome": "Exponential and logarithm",
        "nome_pt": "Exponencial e logaritmo",
        "resumo": "Exponential functions in growth situations, logarithms as the inverse reading, and the passage between table, formula, and graph. A geometric sequence is the exponential function on a discrete domain.",
        "exige": ["A-FUNCAO", "N-POTENCIA"],
        "apoia": ["A-PADRAO"],
        "porque": {
            "A-FUNCAO": "Exponential change is a function whose growth is the object of study. The function idea is already in place.",
            "N-POTENCIA": "The variable is in the exponent of a power. Powers and roots are the arithmetic underneath.",
            "A-PADRAO": "A geometric sequence is a recursive pattern, the kind built since year 1, now recognized as exponential.",
        },
        "habilidades": ["EM13MAT304", "EM13MAT305", "EM13MAT403", "EM13MAT508"],
    },
    {
        "id": "A-JUROS",
        "fio": "algebra",
        "nome": "Simple and compound interest",
        "nome_pt": "Juros simples e compostos",
        "resumo": "Tell a straight accumulation from a curved one. Simple interest is a fixed percent of the original amount. Compound interest applies the percent to the new amount.",
        "exige": ["N-PORCENTO", "A-EXP"],
        "apoia": [],
        "porque": {
            "N-PORCENTO": "The interest rate is a percent. Reading it as 'a tenth' or 'five per hundred' is the percent skill.",
            "A-EXP": "Compound interest is exponential. The graph is how the base asks students to see the difference, so the exponential graph has to be readable.",
        },
        "habilidades": ["EM13MAT303"],
    },
    {
        "id": "A-CICLO",
        "fio": "algebra",
        "nome": "Periodic phenomena",
        "nome_pt": "Fenômenos periódicos",
        "resumo": "Sound, moon phases, and other quantities that return. The function repeats. This is the curricular home of the periodic model, short of a full trigonometry course.",
        "exige": ["A-FUNCAO", "G-CIRC"],
        "apoia": [],
        "porque": {
            "A-FUNCAO": "A repeating quantity is still a dependence between two variables, now with a period.",
            "G-CIRC": "The circle is the reason a quantity can come back to its start: an angle that has gone all the way around.",
        },
        "habilidades": ["EM13MAT306"],
    },
    {
        "id": "A-PA",
        "fio": "algebra",
        "nome": "Arithmetic sequences as affine functions",
        "nome_pt": "Progressões aritméticas",
        "resumo": "An arithmetic sequence is an affine function whose domain is the counting numbers. Some of the usual formulas can be deduced from that, not memorized first.",
        "exige": ["A-FUNCAO", "A-PADRAO"],
        "apoia": [],
        "porque": {
            "A-FUNCAO": "The base asks for the sequence to be recognized as an affine function on a discrete domain. The function comes first.",
            "A-PADRAO": "Add-the-same-amount has been a recursive pattern since year 1. The progression names it.",
        },
        "habilidades": ["EM13MAT507"],
    },
    {
        "id": "A-PLANILHA",
        "fio": "algebra",
        "nome": "Spreadsheets as a mathematical tool",
        "nome_pt": "Planilhas",
        "resumo": "Plan an action, run it, and analyze it in a spreadsheet: a table whose cells are functions of other cells.",
        "exige": ["A-FUNCAO", "E-DADOS"],
        "apoia": [],
        "porque": {
            "A-FUNCAO": "A formula in a cell is a function. If a function is still a mystery, the spreadsheet hides it.",
            "E-DADOS": "The sheet is also a table of data. Reading a table is the old statistics skill.",
        },
        "habilidades": ["EM13MAT203"],
    },
    {
        "id": "G-ONDE",
        "fio": "geometria",
        "nome": "Position needs a reference",
        "nome_pt": "Localização e referência",
        "resumo": "Right, left, in front, behind, first from one's own body, then from a stated reference. The words change when the reference changes. Then maps, sketches, and routes of familiar places.",
        "livro": "aluno/de-que-lado.html",
        "exige": ["EI-ESPACO"],
        "apoia": [],
        "porque": {
            "EI-ESPACO": "In, on, under, and beside are already lived. Year 1 adds a demand: say which body, or which object, the word is measured from.",
        },
        "habilidades": ["EF01MA11", "EF01MA12", "EF02MA12", "EF02MA13", "EF03MA12", "EF04MA16"],
    },
    {
        "id": "G-SOLIDO",
        "fio": "geometria",
        "nome": "Solids in ordinary objects",
        "nome_pt": "Sólidos do cotidiano",
        "resumo": "Cylinder, cone, sphere, rectangular block, then pyramid and prism. Name them in objects, then relate them to their faces and their nets.",
        "livro": "aluno/caixa-lata-bola.html",
        "exige": ["EI-COMPARAR"],
        "apoia": [],
        "porque": {
            "EI-COMPARAR": "Naming the shape of a can is classification by form, which preschool already practices on objects.",
        },
        "habilidades": ["EF01MA13", "EF02MA14", "EF03MA13", "EF03MA14", "EF04MA17", "EF05MA16", "EF06MA17"],
    },
    {
        "id": "G-PLANO",
        "fio": "geometria",
        "nome": "Plane figures",
        "nome_pt": "Figuras planas",
        "resumo": "Circle, square, rectangle, triangle, then trapezoid and parallelogram. Sides, vertices, angles. Polygons classified by sides and by angles.",
        "livro": "aluno/caixa-lata-bola.html",
        "exige": ["EI-COMPARAR"],
        "apoia": ["G-SOLIDO"],
        "porque": {
            "EI-COMPARAR": "Telling a round thing from a square thing is preschool sorting, now given the standard names.",
            "G-SOLIDO": "One of the two places the base asks children to see a plane figure is on the face of a solid. The other is a drawing. Solids support the face relationship. They are not required to recognize a drawn triangle.",
        },
        "habilidades": ["EF01MA14", "EF02MA15", "EF03MA15", "EF05MA17", "EF06MA18", "EF06MA19", "EF06MA20"],
    },
    {
        "id": "G-CONGRU",
        "fio": "geometria",
        "nome": "Congruence",
        "nome_pt": "Congruência",
        "resumo": "Year 3: two figures coincide by laying one on the other, including on a grid. Year 8: congruence cases of triangles, used to argue about quadrilaterals.",
        "exige": ["G-PLANO"],
        "apoia": ["G-ANGULO"],
        "porque": {
            "G-PLANO": "Congruence compares plane figures. There must be figures, with sides and vertices, to lay on each other.",
            "G-ANGULO": "The triangle congruence cases speak in angles as well as sides. The year-3 laying-on does not need the angle measure yet. The year-8 proofs do.",
        },
        "habilidades": ["EF03MA16", "EF08MA14"],
    },
    {
        "id": "G-ANGULO",
        "fio": "geometria",
        "nome": "Angles",
        "nome_pt": "Ângulos",
        "resumo": "Right and not-right, by folding and with a set square. Then measure, then the angles made by a transversal on parallel lines, then the angle sum of a triangle. Year 9 asks for a short demonstration of the parallel-line relations.",
        "nota": "Several of these skills sit in the BNCC unit Grandezas e medidas, because an angle is also a magnitude. The dependency is geometric: an angle is a relation between two lines.",
        "exige": ["G-PLANO"],
        "apoia": [],
        "porque": {
            "G-PLANO": "An angle is the opening between two sides of a figure, or between two lines. The figure comes first.",
        },
        "habilidades": ["EF04MA18", "EF06MA25", "EF06MA26", "EF06MA27", "EF07MA23", "EF09MA10"],
    },
    {
        "id": "G-SIMETRIA",
        "fio": "geometria",
        "nome": "Reflection, translation, rotation",
        "nome_pt": "Simetrias",
        "resumo": "Mirror symmetry by folding in year 4. The three isometries in year 7 and their compositions in year 8. High school uses them, and homotheties, to build figures and to read objects and organisms.",
        "exige": ["G-PLANO"],
        "apoia": [],
        "porque": {
            "G-PLANO": "Symmetry is a property of a figure, or a move applied to a figure. No figure, no symmetry.",
        },
        "habilidades": ["EF04MA19", "EF07MA21", "EF08MA18", "EM13MAT105"],
    },
    {
        "id": "G-CARTES",
        "fio": "geometria",
        "nome": "The coordinate plane",
        "nome_pt": "Plano cartesiano",
        "resumo": "Year 5 uses the first quadrant only: coordinates of points, and figures on the grid. Year 6 attaches the vertices of a polygon to ordered pairs. The other quadrants wait until the integers exist.",
        "exige": ["N-COMPARAR", "G-ONDE"],
        "apoia": ["N-INTEIRO"],
        "porque": {
            "N-COMPARAR": "A coordinate is a number, and the order of the numbers is the order on the line. Year 5 stays in the first quadrant, so negatives are not required yet.",
            "G-ONDE": "A pair of coordinates is a location from a stated origin. Location-from-a-reference is the old geometry skill, now numeric.",
            "N-INTEIRO": "The other three quadrants are the integer number line crossed with itself. They can wait.",
        },
        "habilidades": ["EF05MA14", "EF05MA15", "EF06MA16"],
    },
    {
        "id": "G-ESCALA",
        "fio": "geometria",
        "nome": "Enlargement and reduction on a grid",
        "nome_pt": "Ampliação e redução",
        "resumo": "Enlarge and reduce polygons on a square grid. Angles stay the same. Corresponding sides stay proportional. Year 6 builds similar figures by that route.",
        "exige": ["G-PLANO", "N-CONTAGEM"],
        "apoia": ["A-PROP"],
        "porque": {
            "G-PLANO": "What gets enlarged is a polygon. Sides and angles have to be nameable.",
            "N-CONTAGEM": "On a grid, the first method is counting squares. The count is enough to start.",
            "A-PROP": "The base also asks the student to see that the sides grew by a constant factor. Proportion is the explanation. The grid can be started beside it, in the same year, rather than after a finished proportion unit.",
        },
        "habilidades": ["EF05MA18", "EF06MA21"],
    },
    {
        "id": "G-CONSTRUIR",
        "fio": "geometria",
        "nome": "Constructions",
        "nome_pt": "Construções com instrumentos",
        "resumo": "Parallel and perpendicular lines, the circle as the set of points at a fixed distance, angles of 90, 60, 45, and 30 degrees, regular polygons, perpendicular bisector and angle bisector. Year 9 writes the construction of a regular polygon as an algorithm.",
        "exige": ["G-ANGULO"],
        "apoia": ["G-PLANO"],
        "porque": {
            "G-ANGULO": "The constructions make angles and the relations between lines. An angle has to be an object before a tool can be asked to produce a 60° one.",
            "G-PLANO": "The polygons being constructed were classified earlier. The construction gives a new way to produce them.",
        },
        "habilidades": ["EF06MA22", "EF06MA23", "EF07MA22", "EF07MA27", "EF07MA28", "EF08MA15", "EF08MA16", "EF08MA17", "EF09MA15"],
    },
    {
        "id": "G-TRI",
        "fio": "geometria",
        "nome": "Triangles: build them, and the angle sum",
        "nome_pt": "Triângulos",
        "resumo": "Can these three lengths make a triangle. Build it. The sum of the interior angles is a straight angle.",
        "exige": ["G-ANGULO", "G-CONSTRUIR"],
        "apoia": [],
        "porque": {
            "G-ANGULO": "The angle sum is a statement about angles. It cannot precede the angle.",
            "G-CONSTRUIR": "The base asks students to construct the triangles and to meet the existence condition with a tool, not only to look at a picture.",
        },
        "habilidades": ["EF07MA24", "EF07MA25", "EF07MA26"],
    },
    {
        "id": "G-TRANSF",
        "fio": "geometria",
        "nome": "Transformations on the coordinate plane",
        "nome_pt": "Transformações no plano cartesiano",
        "resumo": "Multiply coordinates to enlarge or reduce a polygon on the plane. This is the grid enlargement, now done with numbers.",
        "exige": ["G-CARTES", "N-MULT", "G-ESCALA"],
        "apoia": [],
        "porque": {
            "G-CARTES": "The vertices are ordered pairs. The plane has to exist.",
            "N-MULT": "The transformation in this skill is a multiplication of the coordinates.",
            "G-ESCALA": "Enlargement on a grid, with angles preserved, is the geometric fact being arithmetized.",
        },
        "habilidades": ["EF07MA19", "EF07MA20"],
    },
    {
        "id": "G-VISTA",
        "fio": "geometria",
        "nome": "Plans, views, and perspective",
        "nome_pt": "Plantas, vistas e perspectiva",
        "resumo": "Floor plans and aerial views, then orthogonal views of solids and a perspective drawing.",
        "exige": ["G-SOLIDO", "G-ONDE"],
        "apoia": [],
        "porque": {
            "G-SOLIDO": "A view is a solid seen from one side. The solid is the object.",
            "G-ONDE": "Choosing a view is choosing a reference. Front and above are references.",
        },
        "habilidades": ["EF06MA28", "EF09MA17"],
    },
    {
        "id": "G-SEMELHANCA",
        "fio": "geometria",
        "nome": "Similarity of triangles",
        "nome_pt": "Semelhança de triângulos",
        "resumo": "The necessary and sufficient conditions for two triangles to be similar. This is the tool year 9 uses to prove the metric relations.",
        "exige": ["G-ANGULO", "A-PROP", "G-TRI"],
        "apoia": ["G-ESCALA"],
        "porque": {
            "G-ANGULO": "The conditions are statements about equal angles.",
            "A-PROP": "The conditions are also statements about proportional sides. Proportion is the rate.",
            "G-TRI": "The figures are triangles, including the constraint on which lengths can form one.",
            "G-ESCALA": "Grid enlargement already showed angles staying equal while sides grow together. Similarity names the relation that enlargement was producing.",
        },
        "habilidades": ["EF09MA12"],
    },
    {
        "id": "G-PITAGORAS",
        "fio": "geometria",
        "nome": "Metric relations and Pythagoras",
        "nome_pt": "Relações métricas e Pitágoras",
        "resumo": "Demonstrate the metric relations in a right triangle, Pythagoras among them, using similarity. Then use them, and the proportionality theorems for parallel lines cut by secants.",
        "exige": ["G-SEMELHANCA"],
        "apoia": [],
        "porque": {
            "G-SEMELHANCA": "The base names the method: similarity of triangles. A memorized a² + b² = c² that the student cannot connect to a similar triangle is not this skill.",
        },
        "habilidades": ["EF09MA13", "EF09MA14"],
    },
    {
        "id": "G-CIRC",
        "fio": "geometria",
        "nome": "Arcs and angles in the circle",
        "nome_pt": "Arcos e ângulos na circunferência",
        "resumo": "Relate a central angle, an inscribed angle, and the arc they see.",
        "exige": ["G-ANGULO", "G-CONSTRUIR"],
        "apoia": [],
        "porque": {
            "G-ANGULO": "A central angle and an inscribed angle are angles standing on the same arc. The angle has to already be an object with a measure.",
            "G-CONSTRUIR": "The circle has already been built as the set of points at a fixed distance. The arc is a piece of that circle.",
        },
        "habilidades": ["EF09MA11"],
    },
    {
        "id": "G-DIST",
        "fio": "geometria",
        "nome": "Distance and midpoint on the plane",
        "nome_pt": "Distância e ponto médio",
        "resumo": "Find the midpoint and the distance between two points from their coordinates, without a memorized formula, and use that to measure polygons drawn on the plane.",
        "exige": ["G-CARTES", "G-PITAGORAS"],
        "apoia": [],
        "porque": {
            "G-CARTES": "The points are given by coordinates. The plane is the setting.",
            "G-PITAGORAS": "The distance is the hypotenuse of the right triangle the coordinates form. The base forbids hiding this inside a formula the student cannot see. The relation itself is the tool.",
        },
        "habilidades": ["EF09MA16"],
    },
    {
        "id": "G-LADRILHO",
        "fio": "geometria",
        "nome": "Tilings of the plane",
        "nome_pt": "Ladrilhamento",
        "resumo": "Which regular polygons tile the plane, and which combinations do. The test is how angles fit around a point.",
        "exige": ["G-ANGULO"],
        "apoia": ["G-CONSTRUIR"],
        "porque": {
            "G-ANGULO": "A tiling closes up when the angles around a vertex sum to a full turn. The angle is the fact being used.",
            "G-CONSTRUIR": "Regular polygons, and how to construct them, give the tiles.",
        },
        "habilidades": ["EM13MAT505"],
    },
    {
        "id": "G-TRIG",
        "fio": "geometria",
        "nome": "Trigonometry in solving triangles",
        "nome_pt": "Trigonometria no triângulo",
        "resumo": "Use the metric relations, including the laws of sines and cosines, together with congruence and similarity, to solve and pose problems about triangles.",
        "exige": ["G-PITAGORAS", "G-SEMELHANCA"],
        "apoia": [],
        "porque": {
            "G-PITAGORAS": "The right triangle is the special case already demonstrated. Sine and cosine compare its sides.",
            "G-SEMELHANCA": "The laws for a general triangle are similarity and proportionality extended past the right angle. The base names congruence and similarity as the route.",
        },
        "habilidades": ["EM13MAT308"],
    },
    {
        "id": "G-MAPA",
        "fio": "geometria",
        "nome": "Map projections distort",
        "nome_pt": "Projeções cartográficas",
        "resumo": "Different projections of the sphere onto the plane deform angles and areas differently. The student investigates that, not as a slogan but as a geometric fact.",
        "exige": ["G-CARTES", "A-PROP"],
        "apoia": ["G-ANGULO"],
        "porque": {
            "G-CARTES": "A projection lands on a plane with coordinates. Reading the result needs the plane.",
            "A-PROP": "Scale is a proportion. A projection that cannot keep one scale everywhere is a proportion that fails, and the student has to know what a kept proportion would have looked like.",
            "G-ANGULO": "The other thing a projection may fail to keep is an angle. The angle has to be an object that can be compared.",
        },
        "habilidades": ["EM13MAT509"],
    },
    {
        "id": "M-COMPARAR",
        "fio": "medidas",
        "nome": "Compare lengths, masses, and capacities directly",
        "nome_pt": "Comparar grandezas sem unidade padrão",
        "resumo": "Longer, shorter, heavier, holds more. Year 2 adds personal and nonstandard units, and the first standard ones (liter, kilogram) as names, still beside the direct comparison.",
        "livro": "aluno/maior-mais-pesado.html",
        "exige": ["EI-COMPARAR"],
        "apoia": [],
        "porque": {
            "EI-COMPARAR": "Heavier and bigger are preschool comparisons. Year 1 makes the comparison deliberate and extends it to length and capacity.",
        },
        "habilidades": ["EF01MA15", "EF02MA16", "EF02MA17"],
    },
    {
        "id": "M-UNIDADE",
        "fio": "medidas",
        "nome": "A measure depends on the unit",
        "nome_pt": "A medida depende da unidade",
        "resumo": "The same object gives a different number when the unit changes. Choose a unit and an instrument. Use the usual standard units, and convert among the common ones.",
        "exige": ["M-COMPARAR", "N-CONTAGEM"],
        "apoia": [],
        "porque": {
            "M-COMPARAR": "Before a unit, the child can already say which is longer. The unit answers 'longer by how many of these'.",
            "N-CONTAGEM": "A measurement is a count of copies of the unit. The count is the arithmetic.",
        },
        "habilidades": ["EF03MA17", "EF03MA18", "EF03MA19", "EF03MA20", "EF04MA20", "EF05MA19", "EF06MA24", "EF07MA29"],
    },
    {
        "id": "M-TEMPO",
        "fio": "medidas",
        "nome": "Time, calendar, and clock",
        "nome_pt": "Tempo, calendário e relógio",
        "resumo": "Order the events of a day. Week, month, year. Write a date. Duration between dates. Read a digital clock, then an analog clock, including minutes.",
        "livro": "aluno/o-dia-inteiro.html",
        "exige": ["EI-ESPACO", "N-SENTIDO"],
        "apoia": [],
        "porque": {
            "EI-ESPACO": "Before, during, and after are the preschool time words. The calendar is that order, written down.",
            "N-SENTIDO": "A date and a hour are numbers. Some of them are orders (the third day) and some are measures of duration. The child has to already know that a number can do more than one job, or the clock is a code they cannot use.",
        },
        "habilidades": ["EF01MA16", "EF01MA17", "EF01MA18", "EF02MA18", "EF02MA19", "EF03MA22", "EF03MA23", "EF04MA22"],
    },
    {
        "id": "M-DINHEIRO",
        "fio": "medidas",
        "nome": "Brazilian coins and bills",
        "nome_pt": "Sistema monetário",
        "resumo": "Recognize coins and bills. Then exchange them. Then solve small buying and selling problems, including comparison of amounts of money.",
        "livro": "aluno/moedas.html",
        "exige": ["N-SENTIDO"],
        "apoia": ["N-ADDSUB", "N-DECIMAL"],
        "porque": {
            "N-SENTIDO": "Year 1 only asks the child to recognize a coin or a bill and relate its value. The number on a bill is a quantity of money, which requires knowing that a number can name a quantity at all.",
            "N-ADDSUB": "Paying and making change are addition and subtraction. They matter from year 2 on. They are not required to recognize a 2-real coin.",
            "N-DECIMAL": "Cents are the first decimals many children meet. The decimal system explains them. It is not required for the year-1 recognition.",
        },
        "habilidades": ["EF01MA19", "EF02MA20", "EF03MA24", "EF04MA25"],
    },
    {
        "id": "M-AREA",
        "fio": "medidas",
        "nome": "Area",
        "nome_pt": "Área",
        "resumo": "Compare areas by looking and by laying one figure on another. Count squares on a grid. Relate area and perimeter. Then the formulas for quadrilaterals, triangles, and circles, and the high-school return to deriving area formulas by cutting and rearranging.",
        "exige": ["G-PLANO", "N-MULT"],
        "apoia": ["M-UNIDADE"],
        "porque": {
            "G-PLANO": "Area is a magnitude of a plane figure. The figure comes first.",
            "N-MULT": "The area of a rectangle is the array meaning of multiplication: rows of squares. Counting squares one by one works before this, and the base moves to the array.",
            "M-UNIDADE": "Choosing square centimeters rather than square meters is the unit idea applied to area.",
        },
        "habilidades": ["EF03MA21", "EF04MA21", "EF05MA20", "EF06MA29", "EF07MA31", "EF07MA32", "EF08MA19", "EM13MAT307"],
    },
    {
        "id": "M-VOLUME",
        "fio": "medidas",
        "nome": "Volume and capacity",
        "nome_pt": "Volume e capacidade",
        "resumo": "Year 5 opens the idea of volume. Year 7 counts unit cubes in a rectangular block. Year 8 relates the liter to the cubic decimeter. Year 9 does right prisms and cylinders. High school derives the formulas, including Cavalieri, and uses them on real solids.",
        "exige": ["M-AREA", "G-SOLIDO"],
        "apoia": [],
        "porque": {
            "M-AREA": "The volume of a prism is a stack of equal areas. Area is the two-dimensional count that volume extends.",
            "G-SOLIDO": "The solid being filled is a prism, a pyramid, a cylinder, a cone. Naming and imagining the solid comes from the geometry thread.",
        },
        "habilidades": ["EF05MA21", "EF07MA30", "EF08MA20", "EF08MA21", "EF09MA19", "EM13MAT309", "EM13MAT504"],
    },
    {
        "id": "M-GRAU",
        "fio": "medidas",
        "nome": "Temperature in degrees Celsius",
        "nome_pt": "Temperatura",
        "resumo": "Read and record temperatures, and put them in a graph.",
        "exige": ["N-COMPARAR", "E-DADOS"],
        "apoia": ["M-UNIDADE"],
        "porque": {
            "N-COMPARAR": "A temperature is a number on a scale. Comparing 18 °C and 31 °C is the number comparison, with a unit attached.",
            "E-DADOS": "The base asks for the temperatures inside a graph. Reading the graph is the statistics skill.",
            "M-UNIDADE": "The degree is a unit. The general idea that a measure names its unit supports the reading.",
        },
        "habilidades": ["EF04MA23", "EF04MA24"],
    },
    {
        "id": "M-CIRCULO",
        "fio": "medidas",
        "nome": "Length of a circle",
        "nome_pt": "Comprimento da circunferência",
        "resumo": "The length of a circle is a little more than three times the diameter. The number is not an integer. This is a measure, of a curve the student can draw.",
        "exige": ["M-UNIDADE", "G-CONSTRUIR", "N-DECIMAL"],
        "apoia": [],
        "porque": {
            "M-UNIDADE": "The length is a measure in a stated unit.",
            "G-CONSTRUIR": "The circle has been constructed as a locus. The curve being measured is that circle.",
            "N-DECIMAL": "The ratio of circumference to diameter is not a whole number. Reporting it uses a decimal.",
        },
        "habilidades": ["EF07MA33"],
    },
    {
        "id": "M-ESCALA",
        "fio": "medidas",
        "nome": "Very large and very small units",
        "nome_pt": "Unidades muito grandes e muito pequenas",
        "resumo": "Distances between planets, sizes of cells, storage of digital information. Convert, including units outside the SI when a text uses them.",
        "exige": ["M-UNIDADE", "N-CIENCIA"],
        "apoia": [],
        "porque": {
            "M-UNIDADE": "Conversion is the unit idea: the number changes when the unit changes. Here the units are unfamiliar, the idea is not.",
            "N-CIENCIA": "These measures are written in scientific notation so the zeros do not hide the digits. The notation is the arithmetic.",
        },
        "habilidades": ["EF09MA18", "EM13MAT103"],
    },
    {
        "id": "M-PROJETO",
        "fio": "medidas",
        "nome": "Measure something in the community",
        "nome_pt": "Medir na comunidade",
        "resumo": "A high-school project: perimeter, area, and volume of a real local situation, done with other people, as a reason to use the measures.",
        "exige": ["M-AREA", "M-VOLUME"],
        "apoia": [],
        "porque": {
            "M-AREA": "The project measures areas. The area has to be a tool, not a topic still being opened.",
            "M-VOLUME": "The same project measures volumes of real containers and rooms. The volume formula has to already be a tool the class can use.",
        },
        "habilidades": ["EM13MAT201"],
    },
    {
        "id": "E-ACASO",
        "fio": "estatistica",
        "nome": "Chance, said in words",
        "nome_pt": "Acaso em palavras",
        "resumo": "Certain, maybe, impossible. Then more and less likely. Year 3 lists the possible results of a familiar random event and says which are more likely, still without a fraction.",
        "nota": "Numerical probability waits for fractions. Years 1 to 4 stay in language. Starting with a formula here skips the requirement.",
        "livro": "aluno/vai-acontecer.html",
        "exige": ["EI-COMPARAR"],
        "apoia": [],
        "porque": {
            "EI-COMPARAR": "Certain, possible, and impossible are a sorting of events. Sorting is the preschool act, applied to things that have not happened yet.",
        },
        "habilidades": ["EF01MA20", "EF02MA21", "EF03MA25", "EF04MA26"],
    },
    {
        "id": "E-DADOS",
        "fio": "estatistica",
        "nome": "Tables, graphs, and a small survey",
        "nome_pt": "Tabelas, gráficos e pesquisa pequena",
        "resumo": "Read a table and a simple column graph. Run a survey of up to 30, then 50, classmates. Two-way tables, bar graphs, and the words greater frequency and lesser frequency. Later: choose a graph that fits the data, including grouped columns and sectors.",
        "livro": "aluno/a-pesquisa.html",
        "exige": ["N-CONTAGEM"],
        "apoia": ["EI-COMPARAR"],
        "porque": {
            "N-CONTAGEM": "A column in a graph is a count made visible. Reading 'which has more' from a picture requires the count to already be a quantity.",
            "EI-COMPARAR": "Preschool already makes a basic picture of 'how many children'. The school graph is that picture with an axis.",
        },
        "habilidades": ["EF01MA21", "EF01MA22", "EF02MA22", "EF02MA23", "EF03MA26", "EF03MA27", "EF03MA28", "EF04MA27", "EF05MA24", "EF05MA25", "EF06MA31", "EF06MA32", "EF06MA33", "EF06MA34", "EF07MA37", "EF08MA23", "EM13MAT406"],
    },
    {
        "id": "E-VAR",
        "fio": "estatistica",
        "nome": "Categorical and numerical variables",
        "nome_pt": "Variáveis categóricas e numéricas",
        "resumo": "Some data are names (color, yes or no). Some data are numbers. You can count either. You can only average the second.",
        "exige": ["E-DADOS"],
        "apoia": [],
        "porque": {
            "E-DADOS": "The child has already recorded both kinds, in surveys of favorite fruit and of age or count. Year 4 asks for the distinction that was implicit.",
        },
        "habilidades": ["EF04MA28"],
    },
    {
        "id": "E-PROB",
        "fio": "estatistica",
        "nome": "Probability as a ratio",
        "nome_pt": "Probabilidade como razão",
        "resumo": "List the sample space. For equally likely results, probability is the fraction favorable over possible. Then experiments, the multiplicative principle, the fact that the probabilities sum to 1, dependent and independent events, and successive experiments. High school includes unequal likelihood and risk in ordinary decisions.",
        "nota": "The fraction is load-bearing. Words for chance are not a warm-up that can be skipped, and the fraction is not a notation pasted on at the end.",
        "exige": ["E-ACASO", "N-FRACAO"],
        "apoia": ["N-COMBINA"],
        "porque": {
            "E-ACASO": "The fraction quantifies a judgment the student has been making in words since year 1: more likely, less likely.",
            "N-FRACAO": "The probability is a fraction. Without fractions the answer can only stay a word, which is the earlier skill, not this one.",
            "N-COMBINA": "Listing a sample space of pairs, and the multiplicative principle in year 8, are the combination count applied to outcomes.",
        },
        "habilidades": ["EF05MA22", "EF05MA23", "EF06MA30", "EF07MA34", "EF08MA22", "EF09MA20", "EM13MAT106", "EM13MAT311", "EM13MAT312", "EM13MAT511"],
    },
    {
        "id": "E-RESUMO",
        "fio": "estatistica",
        "nome": "Mean, median, mode, range",
        "nome_pt": "Média, mediana, moda e amplitude",
        "resumo": "The mean as a fair share, with the range as a first look at spread. Then median and mode, and the choice of a graph that shows the center. High school interprets these for a real set of data. Year 8 also groups a continuous variable into classes.",
        "exige": ["E-VAR", "N-DIV"],
        "apoia": ["N-ADDSUB"],
        "porque": {
            "E-VAR": "The mean of a categorical variable is nonsense. The distinction between kinds of variable is what makes the mean legal.",
            "N-DIV": "The mean is a total shared equally. It is a division. A child who can only add cannot finish it.",
            "N-ADDSUB": "The total that gets shared is a sum. Addition is the other half of the mean.",
        },
        "habilidades": ["EF07MA35", "EF08MA24", "EF08MA25", "EF09MA22", "EM13MAT316"],
    },
    {
        "id": "E-AMOSTRA",
        "fio": "estatistica",
        "nome": "Census and sample",
        "nome_pt": "Censo e amostra",
        "resumo": "Why a sample instead of everybody: cost, ethics, time. Simple, systematic, and stratified samples. Plan one, run it, and report center, range, and a fitting graph.",
        "exige": ["E-DADOS", "E-RESUMO"],
        "apoia": [],
        "porque": {
            "E-DADOS": "A sample is a survey. Planning questions, tables, and graphs is the survey skill, now on people you did not all reach.",
            "E-RESUMO": "The report the base asks for highlights mean, median, mode, and range. The summaries have to mean something before they are the conclusion of a study.",
        },
        "habilidades": ["EF07MA36", "EF08MA26", "EF08MA27", "EF09MA23", "EM13MAT202"],
    },
    {
        "id": "E-MIDIA",
        "fio": "estatistica",
        "nome": "Graphs that mislead",
        "nome_pt": "Gráficos que enganam",
        "resumo": "A truncated axis, a missing source, a missing date, a pictograph whose picture grows in area. Year 9 names these. High school reads published studies and compares histogram, box plot, and stem-and-leaf.",
        "exige": ["E-DADOS", "E-AMOSTRA"],
        "apoia": [],
        "porque": {
            "E-DADOS": "You can only see that a scale is dishonest if you can read an honest scale.",
            "E-AMOSTRA": "A common trick is a sample presented as if it were everybody. Census versus sample is the distinction being abused.",
        },
        "habilidades": ["EF09MA21", "EM13MAT102", "EM13MAT407"],
    },
    {
        "id": "E-RELACAO",
        "fio": "estatistica",
        "nome": "Two numerical variables together",
        "nome_pt": "Duas variáveis numéricas",
        "resumo": "Look at paired numerical data and, when it is appropriate, describe the relation. This is the statistical cousin of the function, used on data that did not come from a formula.",
        "exige": ["E-DADOS", "A-FUNCAO"],
        "apoia": ["E-VAR"],
        "porque": {
            "E-DADOS": "The scatter plot is a graph. Building and reading graphs is the old skill.",
            "A-FUNCAO": "Asking whether one variable depends on the other is the function question. The function gives the language of dependence. The data may refuse to be a function, and that refusal is part of the skill.",
            "E-VAR": "Both variables have to be numerical. The categorical-versus-numerical distinction says when a scatter plot is even legal.",
        },
        "habilidades": ["EM13MAT510"],
    },
    {
        "id": "E-INDICE",
        "fio": "estatistica",
        "nome": "Indices and rates in public life",
        "nome_pt": "Índices e taxas",
        "resumo": "HDI, inflation, and other published rates. Investigate how the number was calculated, then argue with it.",
        "exige": ["N-PORCENTO", "E-MIDIA"],
        "apoia": [],
        "porque": {
            "N-PORCENTO": "These indices are rates and percents. The arithmetic is percent.",
            "E-MIDIA": "The critical half is the statistics half: who measured, what was left out, which picture was chosen. A correct percent can still be a misleading claim.",
        },
        "habilidades": ["EM13MAT104"],
    },
]


SPOT_CHECKS = {
    "EF01MA01": "código de identificação",
    "EF01MA03": "tem a mesma quantidade",
    "EF01MA07": "sistema de numeração decimal",
    "EF09MA01": "número racional",
    "EF09MA13": "Pitágoras",
    "EM13MAT303": "juros",
    "EI03ET07": "antes, o depois",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build() -> dict:
    ef = load_json(RAW / "ef.json")
    em = load_json(RAW / "em.json")
    ei = load_json(RAW / "ei.json")
    est = load_json(RAW / "estrutura.json")

    nomes = {x["id"]: x["nome"] for x in ef["contextos_organizacao"]}
    faixas = {x["id"]: x for x in est["recortes_temporais"] if x["id"].startswith("ei-grupo")}
    campos = {x["id"]: x["nome"] for x in est["campos_experiencias"]}

    habilidades_ef = [h for h in ef["habilidades"] if h["componente"] == "ef-comp-ma"]
    habilidades_em = [h for h in em["habilidades"] if h.get("area") == "em-area-mat"]
    by_code = {h["codigo"]: h for h in habilidades_ef}
    by_code.update({h["codigo"]: h for h in habilidades_em})
    ei_by = {o["codigo"]: o for o in ei["objetivos"]}

    def competencia_textos(prefix: str) -> list[dict]:
        rows = [c for c in est["competencias_especificas"] if c["id"].startswith(prefix)]
        rows.sort(key=lambda c: c["numero"])
        return [{"numero": c["numero"], "texto": c["texto"], "id": c["id"]} for c in rows]

    gerais = sorted(est["competencias_gerais"], key=lambda c: c["numero"])

    conceito_por_hab: dict[str, str] = {}
    for c in CONCEITOS:
        for codigo in c["habilidades"]:
            if codigo in conceito_por_hab:
                raise SystemExit(f"{codigo} assigned to {conceito_por_hab[codigo]} and {c['id']}")
            conceito_por_hab[codigo] = c["id"]

    faltando = [h["codigo"] for h in habilidades_ef + habilidades_em if h["codigo"] not in conceito_por_hab]
    desconhecidos = [codigo for codigo in conceito_por_hab if codigo not in by_code and codigo not in ei_by]
    if faltando or desconhecidos:
        raise SystemExit(f"unmapped: {faltando}\nunknown: {desconhecidos}")

    for codigo, trecho in SPOT_CHECKS.items():
        texto = by_code.get(codigo, ei_by.get(codigo, {})).get("texto", "")
        if trecho not in texto:
            raise SystemExit(f"spot check failed for {codigo}: {trecho!r} not in {texto!r}")

    ids = {c["id"] for c in CONCEITOS}
    for c in CONCEITOS:
        for origem in c["exige"] + c["apoia"]:
            if origem not in ids:
                raise SystemExit(f"{c['id']} cites missing concept {origem}")
            if origem not in c["porque"]:
                raise SystemExit(f"{c['id']} has no reason for {origem}")
        extras = set(c["porque"]) - set(c["exige"]) - set(c["apoia"])
        if extras:
            raise SystemExit(f"{c['id']} explains unknown edges {extras}")

    def ano_de(c) -> int:
        anos = []
        for codigo in c["habilidades"]:
            if codigo.startswith("EI"):
                anos.append(0)
            elif codigo.startswith("EM"):
                anos.append(10)
            else:
                anos.append(min(by_code[codigo]["anos"]))
        return min(anos)

    # Exige-edges must be acyclic. Apoia-edges may point at a partner learned
    # in the same stretch of school; they are not gates.
    exige_adj = {c["id"]: list(c["exige"]) for c in CONCEITOS}
    cor = {i: 0 for i in ids}

    def visitar(no: str, trilha: list[str]) -> None:
        cor[no] = 1
        for viz in exige_adj[no]:
            if cor[viz] == 1:
                raise SystemExit("cycle: " + " -> ".join(trilha + [viz]))
            if cor[viz] == 0:
                visitar(viz, trilha + [viz])
        cor[no] = 2

    for i in ids:
        if cor[i] == 0:
            visitar(i, [i])

    def registro_habilidade(codigo: str) -> dict:
        if codigo.startswith("EI"):
            o = ei_by[codigo]
            grupo = faixas[o["grupo_etario"]]
            return {
                "codigo": codigo,
                "texto": o["texto"],
                "etapa": "EI",
                "ano": 0,
                "anos": [0],
                "ano_rotulo": f"{grupo['nome']} ({grupo['faixa']})",
                "unidade": campos[o["campo_experiencias"]],
                "objetos": [],
                "conceito": conceito_por_hab[codigo],
                "fonte": o["fonte"]["localizador"],
            }
        h = by_code[codigo]
        if codigo.startswith("EM"):
            comps = []
            for cid in h["competencias_especificas"]:
                numero = cid.rsplit("-", 1)[-1]
                comps.append(str(int(numero)))
            return {
                "codigo": codigo,
                "texto": h["texto"],
                "etapa": "EM",
                "ano": 10,
                "anos": [10],
                "ano_rotulo": "Ensino Médio",
                "unidade": "Matemática e suas Tecnologias",
                "objetos": [],
                "competencias": comps,
                "conceito": conceito_por_hab[codigo],
                "fonte": h["fonte"]["localizador_pdf"],
            }
        ut = nomes[h["organizacao"]["unidade_tematica"]]
        objetos = [nomes[i] for i in h["objetos_conhecimento"]]
        return {
            "codigo": codigo,
            "texto": h["texto"],
            "etapa": "EF",
            "ano": min(h["anos"]),
            "anos": h["anos"],
            "ano_rotulo": f"{min(h['anos'])}º ano",
            "unidade": ut,
            "objetos": objetos,
            "conceito": conceito_por_hab[codigo],
            "fonte": h["fonte"]["localizador_pdf"],
        }

    conceitos_out = []
    for c in CONCEITOS:
        habs = [registro_habilidade(codigo) for codigo in c["habilidades"]]
        conceitos_out.append({
            "id": c["id"],
            "fio": c["fio"],
            "ano": ano_de(c),
            "nome": c["nome"],
            "nome_pt": c["nome_pt"],
            "resumo": c["resumo"],
            "nota": c.get("nota", ""),
            "livro": c.get("livro", ""),
            "exige": c["exige"],
            "apoia": c["apoia"],
            "porque": c["porque"],
            "habilidades": [h["codigo"] for h in habs],
        })

    todas = []
    for c in CONCEITOS:
        for codigo in c["habilidades"]:
            todas.append(registro_habilidade(codigo))

    n_exige = sum(len(c["exige"]) for c in CONCEITOS)
    n_apoia = sum(len(c["apoia"]) for c in CONCEITOS)

    return {
        "meta": {
            "titulo": "Matemática na BNCC, com as dependências explícitas",
            "documento": "Base Nacional Comum Curricular, homologada em 2018",
            "fonte_dados": "https://github.com/bncc-dev/bncc-dados",
            "fonte_oficial": "http://basenacionalcomum.mec.gov.br/",
            "aviso": "Os textos das habilidades são os da BNCC. As arestas de dependência não são. A Base ordena as habilidades por ano e não publica pré-requisitos. Cada aresta é uma inferência pedagógica, com um motivo escrito.",
            "contagens": {
                "habilidades_ef": len(habilidades_ef),
                "habilidades_em": len(habilidades_em),
                "objetivos_ei": sum(1 for h in todas if h["etapa"] == "EI"),
                "conceitos": len(CONCEITOS),
                "arestas_exige": n_exige,
                "arestas_apoia": n_apoia,
            },
        },
        "competencias_gerais": [{"numero": c["numero"], "texto": c["texto"]} for c in gerais],
        "competencias_ef": competencia_textos("ef-area-matematica-ce-"),
        "competencias_em": competencia_textos("em-area-mat-ce-"),
        "fios": [
            {"id": "infancia", "nome": "Early childhood", "nome_pt": "Educação Infantil"},
            {"id": "numero", "nome": "Numbers", "nome_pt": "Números"},
            {"id": "algebra", "nome": "Algebra", "nome_pt": "Álgebra"},
            {"id": "geometria", "nome": "Geometry", "nome_pt": "Geometria"},
            {"id": "medidas", "nome": "Magnitudes and measures", "nome_pt": "Grandezas e medidas"},
            {"id": "estatistica", "nome": "Probability and statistics", "nome_pt": "Probabilidade e estatística"},
        ],
        "conceitos": conceitos_out,
        "habilidades": todas,
    }


def main() -> None:
    catalogo = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)
        f.write("\n")
    c = catalogo["meta"]["contagens"]
    print(
        f"wrote {OUT.relative_to(ROOT)}: "
        f"{c['habilidades_ef']} EF + {c['habilidades_em']} EM + {c['objetivos_ei']} EI, "
        f"{c['conceitos']} concepts, {c['arestas_exige']} exige, {c['arestas_apoia']} apoia"
    )


if __name__ == "__main__":
    main()
