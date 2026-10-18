(function () {
  const boardScroll = document.getElementById("board-scroll");
  const board = document.getElementById("board");
  const panel = document.getElementById("panel");
  const browser = document.getElementById("skill-browser");
  if (!board) return;

  const NS = "http://www.w3.org/2000/svg";
  const years = [
    { id: 0, label: "EI" },
    { id: 1, label: "1º" },
    { id: 2, label: "2º" },
    { id: 3, label: "3º" },
    { id: 4, label: "4º" },
    { id: 5, label: "5º" },
    { id: 6, label: "6º" },
    { id: 7, label: "7º" },
    { id: 8, label: "8º" },
    { id: 9, label: "9º" },
    { id: 10, label: "EM" },
  ];

  fetch("data/curriculum.json")
    .then((r) => r.json())
    .then((data) => render(data))
    .catch((err) => {
      panel.textContent = "Could not load the curriculum file. Serve this folder over http, not as a file opened from disk.";
      console.error(err);
    });

  function render(data) {
    const byId = new Map(data.conceitos.map((c) => [c.id, c]));
    const skillsByConcept = new Map();
    data.habilidades.forEach((h) => {
      if (!skillsByConcept.has(h.conceito)) skillsByConcept.set(h.conceito, []);
      skillsByConcept.get(h.conceito).push(h);
    });

    const head = document.createElement("div");
    head.className = "thread-row";
    const corner = document.createElement("div");
    corner.className = "yearhead corner";
    corner.textContent = "Thread";
    head.appendChild(corner);
    years.forEach((y) => {
      const cell = document.createElement("div");
      cell.className = "yearhead";
      cell.textContent = y.label;
      head.appendChild(cell);
    });
    board.appendChild(head);

    data.fios.forEach((fio) => {
      const row = document.createElement("div");
      row.className = "thread-row";
      row.dataset.fio = fio.id;
      const label = document.createElement("div");
      label.className = "rowlabel";
      label.style.color = getComputedStyle(document.documentElement).getPropertyValue("--" + fio.id) || "inherit";
      label.textContent = fio.nome_pt;
      row.appendChild(label);
      years.forEach((y) => {
        const cell = document.createElement("div");
        cell.className = "cell";
        data.conceitos
          .filter((c) => c.fio === fio.id && c.ano === y.id)
          .forEach((c) => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "node" + (c.livro ? " has-book" : "");
            btn.dataset.id = c.id;
            btn.dataset.fio = c.fio;
            btn.innerHTML =
              '<span class="node-pt"></span><span class="node-en"></span>';
            btn.querySelector(".node-pt").textContent = c.nome_pt;
            btn.querySelector(".node-en").textContent = c.livro ? c.nome + " · livro" : c.nome;
            btn.addEventListener("click", () => select(c.id));
            cell.appendChild(btn);
          });
        row.appendChild(cell);
      });
      board.appendChild(row);
    });

    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("class", "edges");
    board.appendChild(svg);

    const state = { focus: null, showAll: false, fios: new Set(data.fios.map((f) => f.id)), query: "" };

    function nodeEl(id) {
      return board.querySelector('.node[data-id="' + id + '"]');
    }

    function visible(id) {
      const el = nodeEl(id);
      if (!el) return false;
      const c = byId.get(id);
      if (!state.fios.has(c.fio)) return false;
      if (state.query && !matches(c, state.query)) return false;
      return true;
    }

    function matches(c, q) {
      const blob = (c.id + " " + c.nome + " " + c.nome_pt + " " + c.resumo).toLowerCase();
      if (blob.includes(q)) return true;
      return (skillsByConcept.get(c.id) || []).some((h) =>
        (h.codigo + " " + h.texto).toLowerCase().includes(q)
      );
    }

    function applyFilter() {
      board.querySelectorAll(".node").forEach((el) => {
        const c = byId.get(el.dataset.id);
        const show = state.fios.has(c.fio) && (!state.query || matches(c, state.query));
        el.parentElement.style.display = "";
        el.hidden = !show;
      });
      board.querySelectorAll(".thread-row").forEach((row) => {
        if (!row.dataset.fio) return;
        row.hidden = !state.fios.has(row.dataset.fio);
      });
      draw();
    }

    function chain(id) {
      const edges = [];
      const seen = new Set();
      function up(node) {
        const c = byId.get(node);
        ["exige", "apoia"].forEach((kind) => {
          c[kind].forEach((parent) => {
            const key = parent + ">" + node + kind;
            if (seen.has(key)) return;
            seen.add(key);
            edges.push({ from: parent, to: node, kind });
            up(parent);
          });
        });
      }
      function down(node) {
        data.conceitos.forEach((c) => {
          ["exige", "apoia"].forEach((kind) => {
            if (!c[kind].includes(node)) return;
            const key = node + ">" + c.id + kind;
            if (seen.has(key)) return;
            seen.add(key);
            edges.push({ from: node, to: c.id, kind });
            down(c.id);
          });
        });
      }
      up(id);
      down(id);
      return edges;
    }

    function center(el) {
      const r = el.getBoundingClientRect();
      const b = board.getBoundingClientRect();
      return {
        x: r.left - b.left + r.width / 2,
        y: r.top - b.top + r.height / 2,
      };
    }

    function draw() {
      const w = board.scrollWidth;
      const h = board.scrollHeight;
      svg.setAttribute("width", w);
      svg.setAttribute("height", h);
      svg.setAttribute("viewBox", "0 0 " + w + " " + h);
      svg.replaceChildren();
      let edges = [];
      if (state.focus) edges = chain(state.focus);
      else if (state.showAll) {
        data.conceitos.forEach((c) => {
          c.exige.forEach((p) => edges.push({ from: p, to: c.id, kind: "exige" }));
          c.apoia.forEach((p) => edges.push({ from: p, to: c.id, kind: "apoia" }));
        });
      }
      const hotNodes = new Set();
      if (state.focus) {
        hotNodes.add(state.focus);
        edges.forEach((e) => {
          hotNodes.add(e.from);
          hotNodes.add(e.to);
        });
      }
      board.querySelectorAll(".node").forEach((el) => {
        el.classList.toggle("active", el.dataset.id === state.focus);
        el.classList.toggle("dim", state.focus && !el.hidden && !hotNodes.has(el.dataset.id));
      });
      edges.forEach((e) => {
        if (!visible(e.from) || !visible(e.to)) return;
        const a = center(nodeEl(e.from));
        const b = center(nodeEl(e.to));
        const path = document.createElementNS(NS, "path");
        const dx = Math.max(36, Math.abs(b.x - a.x) * 0.4);
        path.setAttribute(
          "d",
          "M " + a.x + " " + a.y + " C " + (a.x + dx) + " " + a.y + ", " + (b.x - dx) + " " + b.y + ", " + b.x + " " + b.y
        );
        path.setAttribute("class", "edge " + e.kind + (state.focus ? " hot" : ""));
        svg.appendChild(path);
      });
    }

    function select(id) {
      state.focus = id;
      const c = byId.get(id);
      const skills = skillsByConcept.get(id) || [];
      history.replaceState(null, "", "#" + id);
      panel.innerHTML = "";
      const h = document.createElement("h2");
      h.textContent = c.nome_pt;
      panel.appendChild(h);
      const en = document.createElement("p");
      en.innerHTML = "<em></em>";
      en.querySelector("em").textContent = c.nome;
      panel.appendChild(en);
      const tags = document.createElement("p");
      const fio = data.fios.find((f) => f.id === c.fio);
      tags.innerHTML =
        '<span class="tag"></span><span class="tag"></span>';
      tags.children[0].textContent = fio.nome_pt;
      tags.children[1].textContent = c.ano === 0 ? "Educação Infantil" : c.ano === 10 ? "Ensino Médio" : "a partir do " + c.ano + "º ano";
      panel.appendChild(tags);
      const resumo = document.createElement("p");
      resumo.textContent = c.resumo;
      panel.appendChild(resumo);
      if (c.nota) {
        const note = document.createElement("p");
        note.className = "note";
        note.textContent = c.nota;
        panel.appendChild(note);
      }
      addEdges(panel, "Requires", c.exige, c, byId);
      addEdges(panel, "Supported by", c.apoia, c, byId);
      const unlocks = data.conceitos.filter((o) => o.exige.includes(id) || o.apoia.includes(id));
      if (unlocks.length) {
        const p = document.createElement("p");
        p.innerHTML = "<strong>Unlocks. </strong>";
        unlocks.forEach((o, i) => {
          if (i) p.append(" · ");
          const a = document.createElement("a");
          a.href = "#" + o.id;
          a.textContent = o.nome_pt;
          a.addEventListener("click", (ev) => {
            ev.preventDefault();
            select(o.id);
          });
          p.appendChild(a);
          p.append(o.exige.includes(id) ? " (requires this)" : " (helped by this)");
        });
        panel.appendChild(p);
      }
      if (c.livro) {
        const a = document.createElement("a");
        a.className = "button";
        a.href = c.livro;
        a.textContent = "Open the student book";
        panel.appendChild(document.createElement("p")).appendChild(a);
      }
      const hs = document.createElement("h3");
      hs.textContent = "Official requirements";
      panel.appendChild(hs);
      skills.forEach((s) => {
        const div = document.createElement("div");
        div.className = "skill";
        const b = document.createElement("b");
        b.className = "code";
        b.textContent = s.codigo + " · " + s.ano_rotulo;
        div.appendChild(b);
        if (s.unidade) {
          const u = document.createElement("div");
          u.textContent = s.unidade;
          div.appendChild(u);
        }
        const t = document.createElement("div");
        t.textContent = s.texto;
        div.appendChild(t);
        panel.appendChild(div);
      });
      draw();
      const el = nodeEl(id);
      if (el) el.scrollIntoView({ block: "nearest", inline: "nearest" });
    }

    function addEdges(container, title, ids, concept, byIdMap) {
      if (!ids.length) return;
      const h = document.createElement("h3");
      h.textContent = title;
      container.appendChild(h);
      ids.forEach((pid) => {
        const p = document.createElement("p");
        p.className = "porque";
        const a = document.createElement("a");
        a.href = "#" + pid;
        a.textContent = byIdMap.get(pid).nome_pt;
        a.addEventListener("click", (ev) => {
          ev.preventDefault();
          select(pid);
        });
        p.appendChild(a);
        p.append(" — " + concept.porque[pid]);
        container.appendChild(p);
      });
    }

    const filterBox = document.getElementById("filters");
    data.fios.forEach((fio) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.checked = true;
      input.addEventListener("change", () => {
        if (input.checked) state.fios.add(fio.id);
        else state.fios.delete(fio.id);
        applyFilter();
      });
      label.appendChild(input);
      label.append(" " + fio.nome_pt);
      filterBox.appendChild(label);
    });
    document.getElementById("show-all").addEventListener("change", (ev) => {
      state.showAll = ev.target.checked;
      draw();
    });
    document.getElementById("q").addEventListener("input", (ev) => {
      state.query = ev.target.value.trim().toLowerCase();
      applyFilter();
    });

    const yearSelect = document.getElementById("year");
    const unitSelect = document.getElementById("unit");
    const list = document.getElementById("skill-list");
    const yearOptions = [
      ["all", "All years"],
      ["0", "Educação Infantil"],
      ...years.filter((y) => y.id > 0 && y.id < 10).map((y) => [String(y.id), y.label + " ano"]),
      ["10", "Ensino Médio"],
    ];
    yearOptions.forEach(([value, label]) => {
      const o = document.createElement("option");
      o.value = value;
      o.textContent = label;
      yearSelect.appendChild(o);
    });
    const units = ["All units", ...new Set(data.habilidades.map((h) => h.unidade).filter(Boolean))];
    units.forEach((u) => {
      const o = document.createElement("option");
      o.value = u;
      o.textContent = u;
      unitSelect.appendChild(o);
    });

    function paintSkills() {
      const year = yearSelect.value;
      const unit = unitSelect.value;
      const q = (document.getElementById("skill-q").value || "").trim().toLowerCase();
      list.innerHTML = "";
      const rows = data.habilidades.filter((h) => {
        if (year !== "all" && String(h.ano) !== year) return false;
        if (unit !== "All units" && h.unidade !== unit) return false;
        if (q && !(h.codigo + " " + h.texto).toLowerCase().includes(q)) return false;
        return true;
      });
      document.getElementById("skill-n").textContent = rows.length + " requirements";
      rows.forEach((h) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "skill-row";
        const b = document.createElement("b");
        b.textContent = h.codigo;
        btn.appendChild(b);
        btn.append(" · " + h.ano_rotulo + " · " + (h.unidade || ""));
        const d = document.createElement("div");
        d.textContent = h.texto;
        btn.appendChild(d);
        btn.addEventListener("click", () => select(h.conceito));
        list.appendChild(btn);
      });
    }
    yearSelect.addEventListener("change", paintSkills);
    unitSelect.addEventListener("change", paintSkills);
    document.getElementById("skill-q").addEventListener("input", paintSkills);
    paintSkills();

    const initial = location.hash.replace("#", "");
    if (byId.has(initial)) select(initial);
    else {
      panel.innerHTML =
        "<h2>Choose a requirement</h2><p>Each box is a concept. The official BNCC skills sit inside it. Click one to see what it requires and what it unlocks. A green box is the unit written in the student book.</p><p>Solid arrows are gates. Dashed arrows are support: the earlier idea helps, and a teacher can start without it. Turn on “Show every dependency” to see the whole graph at once. It is dense on purpose.</p>";
    }
    window.addEventListener("resize", draw);
    boardScroll.addEventListener("scroll", () => {
      if (state.focus || state.showAll) draw();
    });
  }
})();
