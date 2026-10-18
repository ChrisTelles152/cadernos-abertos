(function () {
  const toggle = document.querySelector("[data-lang-toggle]");
  if (toggle) {
    const stored = localStorage.getItem("cadernos-lang");
    if (stored === "en") document.body.classList.add("show-en");
    const paint = () => {
      toggle.textContent = document.body.classList.contains("show-en")
        ? "Esconder o inglês"
        : "Read in English";
    };
    paint();
    toggle.addEventListener("click", () => {
      document.body.classList.toggle("show-en");
      localStorage.setItem("cadernos-lang", document.body.classList.contains("show-en") ? "en" : "pt");
      paint();
    });
  }

  document.querySelectorAll("[data-answer]").forEach((card) => {
    card.querySelectorAll("[data-pick]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const ok = btn.dataset.pick === card.dataset.answer;
        card.querySelectorAll("[data-pick]").forEach((b) => {
          b.classList.remove("good", "bad");
          b.disabled = true;
        });
        btn.classList.add(ok ? "good" : "bad");
        const fb = card.querySelector(".feedback");
        fb.hidden = false;
        fb.textContent = ok ? card.dataset.yes : card.dataset.no;
      });
    });
  });

  const words = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze", "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove", "vinte"];

  const estimate = document.getElementById("estimar");
  if (estimate) {
    estimate.querySelectorAll("[data-pick]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const ok = btn.dataset.pick === "10";
        estimate.querySelectorAll("[data-pick]").forEach((b) => (b.disabled = true));
        btn.classList.add(ok ? "good" : "bad");
        const fb = document.getElementById("fb-estimar");
        fb.hidden = false;
        fb.textContent = ok
          ? "Perto de 10 é uma boa estimativa. Estimar é chegar perto, sem contar um por um. Agora conte, para ter o número exato."
          : btn.dataset.pick === "3"
            ? "São mais do que 3. Estimar é dizer um número perto. Olhe de novo o montinho e tente outro."
            : "30 seria uma cesta bem cheia. Esse montinho é menor. Tente um número mais perto.";
        if (!ok) {
          estimate.querySelectorAll("[data-pick]").forEach((b) => (b.disabled = false));
          btn.classList.remove("bad");
        } else {
          document.getElementById("contar-paes").hidden = false;
        }
      });
    });
  }

  const paes = document.getElementById("paes");
  if (paes) {
    const total = 8;
    let counted = 0;
    const said = document.getElementById("contagem-falada");
    for (let i = 0; i < total; i++) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "bread";
      b.setAttribute("aria-label", "Pão " + (i + 1));
      b.addEventListener("click", () => {
        if (b.classList.contains("counted")) {
          said.textContent = "Esse pão já foi contado. Cada coisa, uma vez só.";
          return;
        }
        b.classList.add("counted");
        counted += 1;
        said.textContent = words[counted] + (counted === total ? ". Esse foi o último." : ".");
        if (counted === total) document.getElementById("cardinal").hidden = false;
      });
      paes.appendChild(b);
    }
    document.querySelectorAll("#cardinal [data-pick]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const ok = btn.dataset.pick === "8";
        btn.classList.add(ok ? "good" : "bad");
        document.querySelectorAll("#cardinal [data-pick]").forEach((b) => (b.disabled = true));
        document.getElementById("fb-cardinal").hidden = false;
        document.getElementById("fb-cardinal").textContent = ok
          ? "São 8. O último número que a gente fala é o total. Não é o próximo, e não é o anterior."
          : btn.dataset.pick === "9"
            ? "9 viria depois, se houvesse mais um pão. Não há. O último número falado foi 8, então são 8."
            : "7 é o pão de antes do último. O total é o último número que você falou.";
      });
    });
  }

  const copos = document.getElementById("copos");
  if (copos) {
    let stage = 0;
    const scenes = [
      { kids: 4, cups: 4, done: "Cada criança ficou com um copo e nenhum copo sobrou. Tem a mesma quantidade." },
      { kids: 4, cups: 5, done: "Sobrou um copo. Tem mais copos do que crianças. Dá para saber isso sem dizer o número." },
    ];
    const kidsEl = document.getElementById("criancas");
    const cupsEl = document.getElementById("os-copos");
    const fb = document.getElementById("fb-copos");
    const give = document.getElementById("dar-copo");

    function paint() {
      const s = scenes[stage];
      kidsEl.innerHTML = "";
      cupsEl.innerHTML = "";
      for (let i = 0; i < s.kids; i++) {
        const d = document.createElement("div");
        d.className = "person";
        d.innerHTML = '<div class="face"></div><div>criança</div>';
        d.dataset.got = "0";
        kidsEl.appendChild(d);
      }
      for (let i = 0; i < s.cups; i++) {
        const d = document.createElement("div");
        d.className = "cup";
        d.innerHTML = '<div class="cup-body"></div><div>copo</div>';
        cupsEl.appendChild(d);
      }
      fb.hidden = true;
      give.disabled = false;
      give.textContent = "Dar um copo";
    }
    paint();
    give.addEventListener("click", () => {
      const s = scenes[stage];
      const next = [...kidsEl.children].find((k) => k.dataset.got === "0");
      const cup = [...cupsEl.children].find((c) => !c.hidden);
      if (!next || !cup) return;
      next.dataset.got = "1";
      next.querySelector(".face").style.background = "#d9ead3";
      cup.hidden = true;
      const leftKids = [...kidsEl.children].filter((k) => k.dataset.got === "0").length;
      const leftCups = [...cupsEl.children].filter((c) => !c.hidden).length;
      if (leftKids === 0 || leftCups === 0) {
        give.disabled = true;
        fb.hidden = false;
        fb.textContent = s.done + (stage === 0 ? " Agora tente com um copo a mais." : "");
        if (stage === 0) {
          stage = 1;
          const again = document.createElement("button");
          again.type = "button";
          again.className = "choice";
          again.textContent = "Agora com 5 copos";
          again.addEventListener("click", () => {
            again.remove();
            paint();
          });
          fb.after(again);
        }
      }
    });
  }

  const cestas = document.getElementById("cestas");
  if (cestas) {
    const a = document.getElementById("cesta-a");
    const b = document.getElementById("cesta-b");
    let pick = null;
    let pairs = 0;
    function fruits(el, n, name) {
      for (let i = 0; i < n; i++) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "pair-btn";
        btn.textContent = name;
        btn.addEventListener("click", () => onPick(btn, el));
        el.appendChild(btn);
      }
    }
    function onPick(btn, side) {
      if (btn.classList.contains("used")) return;
      if (!pick) {
        pick = btn;
        btn.classList.add("picked");
        return;
      }
      if (pick.parentElement === side) {
        pick.classList.remove("picked");
        pick = btn;
        btn.classList.add("picked");
        return;
      }
      pick.classList.remove("picked");
      pick.classList.add("used");
      btn.classList.add("used");
      pick = null;
      pairs += 1;
      document.getElementById("fb-pares").textContent = "Pares feitos: " + pairs + ".";
      const leftA = [...a.children].filter((x) => !x.classList.contains("used")).length;
      const leftB = [...b.children].filter((x) => !x.classList.contains("used")).length;
      if (leftA === 0 || leftB === 0) {
        document.getElementById("fb-pares").textContent =
          "A cesta espalhada ficou sem fruta. Na cesta apertada sobraram " + leftB + ". Quem sobrou tem mais, e você ainda não precisou do número.";
        document.getElementById("quem-tem-mais").hidden = false;
      }
    }
    fruits(a, 5, "laranja");
    fruits(b, 7, "laranja");
    document.querySelectorAll("#quem-tem-mais [data-pick]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const ok = btn.dataset.pick === "b";
        btn.classList.add(ok ? "good" : "bad");
        document.querySelectorAll("#quem-tem-mais [data-pick]").forEach((b) => (b.disabled = true));
        const fb = document.getElementById("fb-mais");
        fb.hidden = false;
        fb.textContent = ok
          ? "A cesta B tem mais. Ela parecia menor porque as laranjas estavam juntas. O pareamento não se engana com o espaço."
          : "Olhe o que sobrou sem par. A cesta que ainda tem laranja é a que tem mais. O tamanho do desenho engana.";
      });
    });
  }

  document.querySelectorAll("[data-numeral]").forEach((block) => {
    block.querySelectorAll("[data-pick]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const ok = btn.dataset.pick === block.dataset.numeral;
        block.querySelectorAll("[data-pick]").forEach((b) => {
          b.disabled = true;
          b.classList.remove("good", "bad");
        });
        btn.classList.add(ok ? "good" : "bad");
        const fb = block.querySelector(".feedback");
        fb.hidden = false;
        fb.textContent = ok ? block.dataset.yes : block.dataset.no;
      });
    });
  });

  const reta = document.getElementById("reta");
  if (reta) {
    const questions = [
      { a: 8, b: 15, greater: 15, why: "O 15 fica mais à direita. A contagem chega nele depois do 8. Por isso ele é maior." },
      { a: 9, b: 12, greater: 12, why: "O 9 parece grande porque é o maior de um dígito. Mesmo assim a contagem passa por ele e segue até o 12. O 12 é maior." },
      { a: 20, b: 13, greater: 20, why: "O 20 é o fim desta reta. A contagem chega nele por último, então ele é o maior dos dois." },
      { a: 7, b: 17, greater: 17, why: "Não é porque o 17 tem mais dígitos. É porque, andando do zero para a direita, o 17 vem depois." },
    ];
    let q = 0;
    const row = document.getElementById("linha");
    for (let n = 0; n <= 20; n++) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "line-btn";
      b.textContent = String(n);
      b.dataset.n = String(n);
      b.addEventListener("click", () => answer(n, b));
      row.appendChild(b);
    }
    const prompt = document.getElementById("reta-pergunta");
    const fb = document.getElementById("fb-reta");
    function ask() {
      const item = questions[q];
      prompt.textContent = "Qual é maior, " + item.a + " ou " + item.b + "? Aperte o número na reta.";
      fb.hidden = true;
      row.querySelectorAll("button").forEach((b) => b.classList.remove("good", "bad", "picked"));
    }
    function answer(n, btn) {
      const item = questions[q];
      if (n !== item.a && n !== item.b) {
        fb.hidden = false;
        fb.textContent = "Aperte um dos dois números da pergunta: " + item.a + " ou " + item.b + ".";
        return;
      }
      const ok = n === item.greater;
      btn.classList.add(ok ? "good" : "bad");
      fb.hidden = false;
      fb.textContent = ok ? item.why : "Esse vem antes na contagem. Quem vem depois é o maior. Olhe quem está mais à direita.";
      if (ok) {
        q += 1;
        if (q >= questions.length) {
          prompt.textContent = "Você comparou os quatro pares pela reta, sem contar nos dedos e sem olhar quantos dígitos o número tem.";
        } else {
          setTimeout(ask, 900);
        }
      }
    }
    ask();
  }

  const feira = document.getElementById("feira");
  if (feira) {
    const steps = [...feira.querySelectorAll("[data-step]")];
    function show(i) {
      steps.forEach((s, idx) => (s.hidden = idx !== i));
    }
    show(0);
    feira.querySelectorAll("[data-step]").forEach((step) => {
      step.querySelectorAll("[data-pick]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const ok = btn.dataset.pick === step.dataset.ok;
          step.querySelectorAll("[data-pick]").forEach((b) => (b.disabled = true));
          btn.classList.add(ok ? "good" : "bad");
          const fb = step.querySelector(".feedback");
          fb.hidden = false;
          fb.textContent = ok ? step.dataset.yes : step.dataset.no;
          if (ok) {
            const next = Number(step.dataset.step) + 1;
            if (steps[next]) setTimeout(() => show(next), 700);
            else document.getElementById("feira-fim").hidden = false;
          } else {
            step.querySelectorAll("[data-pick]").forEach((b) => {
              b.disabled = false;
              b.classList.remove("bad");
            });
          }
        });
      });
    });
  }
})();
