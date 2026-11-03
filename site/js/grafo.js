(function () {
  const svg = document.getElementById("graph");
  const panel = document.getElementById("graph-panel");
  const scroll = document.getElementById("graph-scroll");
  if (!svg) return;
  const NS = "http://www.w3.org/2000/svg";

  Promise.all([
    fetch("data/curriculum.json").then((r) => r.json()),
    fetch("data/skill-graph.json").then((r) => r.json()),
    fetch("data/adocao.json").then((r) => (r.ok ? r.json() : null)).catch(() => null),
  ]).then(([catalog, graph, adoption]) => render(catalog, graph, adoption))
    .catch((error) => {
      panel.textContent = "Could not load the skill graph.";
      console.error(error);
    });

  function render(catalog, graph, adoption) {
    const skills = new Map(catalog.habilidades.map((h) => [h.codigo, h]));
    const concepts = new Map(catalog.conceitos.map((c) => [c.id, c]));
    const nodes = new Map(graph.nos.map((n) => [n.id, n]));
    const covered = new Map();
    if (adoption) {
      Object.values(adoption.habilidades).forEach((item) => covered.set(item.codigo, item.cobertura));
    }
    const incoming = new Map();
    const outgoing = new Map();
    graph.arestas.forEach((edge) => {
      if (!incoming.has(edge.para)) incoming.set(edge.para, []);
      if (!outgoing.has(edge.de)) outgoing.set(edge.de, []);
      incoming.get(edge.para).push(edge);
      outgoing.get(edge.de).push(edge);
    });

    const state = { mode: "ano1", query: "", focus: null, scale: 1, x: 40, y: 36 };
    const world = document.createElementNS(NS, "g");
    svg.appendChild(world);

    function ancestorsOf(id, allow) {
      const found = new Set();
      const stack = [id];
      while (stack.length) {
        const current = stack.pop();
        (incoming.get(current) || []).forEach((edge) => {
          if (!allow.has(edge.de) || found.has(edge.de)) return;
          found.add(edge.de);
          stack.push(edge.de);
        });
      }
      return found;
    }

    function descendantsOf(id, allow) {
      const found = new Set();
      const stack = [id];
      while (stack.length) {
        const current = stack.pop();
        (outgoing.get(current) || []).forEach((edge) => {
          if (!allow.has(edge.para) || found.has(edge.para)) return;
          found.add(edge.para);
          stack.push(edge.para);
        });
      }
      return found;
    }

    function baseSet() {
      const all = [...nodes.values()];
      if (state.mode === "all") return new Set(all.map((n) => n.id));
      if (state.mode === "ef") return new Set(all.filter((n) => n.ano < 10).map((n) => n.id));
      const year = new Set(all.filter((n) => n.ano === 1).map((n) => n.id));
      all.filter((n) => n.ano === 1).forEach((n) => {
        ancestorsOf(n.id, new Set(all.map((item) => item.id))).forEach((id) => year.add(id));
      });
      return year;
    }

    function matches(id, q) {
      const skill = skills.get(id);
      const concept = concepts.get(nodes.get(id).conceito);
      const blob = (id + " " + skill.texto + " " + concept.nome + " " + concept.nome_pt).toLowerCase();
      return blob.includes(q);
    }

    function visibleIds() {
      const allow = baseSet();
      const q = state.query.trim().toLowerCase();
      if (!q) return allow;
      const hit = new Set([...allow].filter((id) => matches(id, q)));
      const grown = new Set(hit);
      hit.forEach((id) => {
        ancestorsOf(id, allow).forEach((parent) => grown.add(parent));
        (outgoing.get(id) || []).forEach((edge) => {
          if (allow.has(edge.para)) grown.add(edge.para);
        });
      });
      return grown;
    }

    function ranksOf(ids) {
      const rank = new Map();
      const visiting = new Set();
      function rankOf(id) {
        if (rank.has(id)) return rank.get(id);
        if (visiting.has(id)) return 0;
        visiting.add(id);
        const parents = (incoming.get(id) || []).map((edge) => edge.de).filter((parent) => ids.has(parent));
        const value = parents.length ? 1 + Math.max(...parents.map(rankOf)) : 0;
        visiting.delete(id);
        rank.set(id, value);
        return value;
      }
      ids.forEach(rankOf);
      return rank;
    }

    function paint() {
      const ids = visibleIds();
      const rank = ranksOf(ids);
      const columns = new Map();
      [...ids].sort().forEach((id) => {
        const key = rank.get(id);
        if (!columns.has(key)) columns.set(key, []);
        columns.get(key).push(id);
      });
      columns.forEach((list) => {
        list.sort((a, b) => nodes.get(a).fio.localeCompare(nodes.get(b).fio) || a.localeCompare(b));
      });
      const pos = new Map();
      const colW = 150;
      const rowH = 58;
      columns.forEach((list, column) => {
        list.forEach((id, row) => pos.set(id, { x: column * colW + 28, y: row * rowH + 24 }));
      });
      const focusSet = new Set();
      if (state.focus && ids.has(state.focus)) {
        focusSet.add(state.focus);
        ancestorsOf(state.focus, ids).forEach((id) => focusSet.add(id));
        descendantsOf(state.focus, ids).forEach((id) => focusSet.add(id));
      }

      world.replaceChildren();
      graph.arestas.forEach((edge) => {
        if (!pos.has(edge.de) || !pos.has(edge.para)) return;
        const a = pos.get(edge.de);
        const b = pos.get(edge.para);
        const path = document.createElementNS(NS, "path");
        const x1 = a.x + 16;
        const x2 = b.x - 16;
        const mid = (x1 + x2) / 2;
        path.setAttribute("d", `M ${x1} ${a.y} C ${mid} ${a.y}, ${mid} ${b.y}, ${x2} ${b.y}`);
        path.setAttribute("class", "skill-edge" + (focusSet.size && (!focusSet.has(edge.de) || !focusSet.has(edge.para)) ? " dim" : focusSet.size ? " hot" : ""));
        path.setAttribute("marker-end", "url(#arrow)");
        world.appendChild(path);
      });
      pos.forEach((point, id) => {
        const node = nodes.get(id);
        const group = document.createElementNS(NS, "g");
        group.setAttribute("class", "skill-hit skill-node" + (focusSet.size && !focusSet.has(id) ? " dim" : ""));
        group.setAttribute("transform", `translate(${point.x} ${point.y})`);
        const circle = document.createElementNS(NS, "circle");
        circle.setAttribute("r", "13");
        const color = getComputedStyle(document.documentElement).getPropertyValue("--" + node.fio).trim() || "#1b4636";
        const done = covered.get(id) === "integral";
        circle.setAttribute("fill", done ? color : "#fffaf3");
        circle.setAttribute("stroke", color);
        circle.setAttribute("stroke-width", state.focus === id ? "3" : "2");
        const label = document.createElementNS(NS, "text");
        label.setAttribute("y", "24");
        label.setAttribute("text-anchor", "middle");
        label.textContent = id;
        group.append(circle, label);
        group.addEventListener("click", (event) => {
          event.stopPropagation();
          state.focus = id;
          show(id);
          paint();
        });
        world.appendChild(group);
      });
      if (!svg.querySelector("#arrow")) {
        const defs = document.createElementNS(NS, "defs");
        const marker = document.createElementNS(NS, "marker");
        marker.setAttribute("id", "arrow");
        marker.setAttribute("viewBox", "0 0 10 10");
        marker.setAttribute("refX", "8");
        marker.setAttribute("refY", "5");
        marker.setAttribute("markerWidth", "7");
        marker.setAttribute("markerHeight", "7");
        marker.setAttribute("orient", "auto");
        const head = document.createElementNS(NS, "path");
        head.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");
        head.setAttribute("fill", "#8a7b68");
        marker.appendChild(head);
        defs.appendChild(marker);
        svg.prepend(defs);
      }
      state.bounds = pos;
      apply();
    }

    function show(id) {
      const skill = skills.get(id);
      const node = nodes.get(id);
      const concept = concepts.get(node.conceito);
      panel.replaceChildren();
      const code = document.createElement("p");
      code.className = "eyebrow";
      code.textContent = id + " · " + skill.ano_rotulo;
      const title = document.createElement("h2");
      title.textContent = concept.nome_pt;
      const text = document.createElement("p");
      text.textContent = skill.texto;
      panel.append(code, title, text);
      const status = document.createElement("p");
      status.className = "note";
      const cobertura = covered.get(id);
      status.textContent = cobertura === "integral"
        ? "The student book covers this skill in full."
        : cobertura === "parcial"
          ? "A book has started this skill and does not finish it."
          : adoption
            ? "No finished book claims this skill yet."
            : "Coverage was not published with this page.";
      panel.appendChild(status);
      if (concept.livro) {
        const link = document.createElement("p");
        const a = document.createElement("a");
        a.href = concept.livro;
        a.textContent = "Open the student page for this concept";
        link.appendChild(a);
        panel.appendChild(link);
      }
      addLinks("Requires", (incoming.get(id) || []).map((edge) => edge.de), (edgeId) => {
        const edge = (incoming.get(id) || []).find((item) => item.de === edgeId);
        return edge ? edge.porque : "";
      });
      addLinks("Unlocks", (outgoing.get(id) || []).map((edge) => edge.para), () => "");
    }

    function addLinks(heading, ids, reason) {
      if (!ids.length) return;
      const h = document.createElement("h3");
      h.textContent = heading;
      panel.appendChild(h);
      ids.forEach((id) => {
        const p = document.createElement("p");
        const button = document.createElement("button");
        button.type = "button";
        button.className = "choice";
        button.textContent = id;
        button.addEventListener("click", () => {
          state.focus = id;
          show(id);
          paint();
        });
        p.appendChild(button);
        const why = reason(id);
        if (why) {
          const small = document.createElement("span");
          small.className = "porque";
          small.textContent = " " + why;
          p.appendChild(small);
        }
        panel.appendChild(p);
      });
    }

    function apply() {
      world.setAttribute("transform", `translate(${state.x} ${state.y}) scale(${state.scale})`);
    }

    function fit() {
      const points = [...(state.bounds ? state.bounds.values() : [])];
      if (!points.length) return;
      const maxX = Math.max(...points.map((p) => p.x)) + 90;
      const maxY = Math.max(...points.map((p) => p.y)) + 40;
      const rect = scroll.getBoundingClientRect();
      state.scale = Math.min(1.15, rect.width / maxX, rect.height / maxY);
      state.x = 24;
      state.y = 28;
      apply();
    }

    document.querySelectorAll(".graph-modes button").forEach((button) => {
      button.addEventListener("click", () => {
        state.mode = button.dataset.mode;
        state.focus = null;
        document.querySelectorAll(".graph-modes button").forEach((item) => {
          item.setAttribute("aria-pressed", item === button ? "true" : "false");
        });
        paint();
        fit();
        panel.replaceChildren();
        const note = document.createElement("p");
        note.textContent = "Click a circle. The panel names the skill, what it requires, and what it unlocks.";
        panel.appendChild(note);
      });
    });
    document.getElementById("graph-q").addEventListener("input", (event) => {
      state.query = event.target.value;
      paint();
      fit();
    });
    document.getElementById("graph-fit").addEventListener("click", fit);

    let drag = null;
    scroll.addEventListener("pointerdown", (event) => {
      if (event.target.closest(".skill-hit")) return;
      drag = { x: event.clientX, y: event.clientY, ox: state.x, oy: state.y };
      scroll.setPointerCapture(event.pointerId);
    });
    scroll.addEventListener("pointermove", (event) => {
      if (!drag) return;
      state.x = drag.ox + event.clientX - drag.x;
      state.y = drag.oy + event.clientY - drag.y;
      apply();
    });
    scroll.addEventListener("pointerup", () => { drag = null; });
    scroll.addEventListener("wheel", (event) => {
      event.preventDefault();
      const next = Math.min(2.4, Math.max(0.25, state.scale * (event.deltaY > 0 ? 0.92 : 1.08)));
      const rect = scroll.getBoundingClientRect();
      const px = event.clientX - rect.left;
      const py = event.clientY - rect.top;
      state.x = px - ((px - state.x) * next) / state.scale;
      state.y = py - ((py - state.y) * next) / state.scale;
      state.scale = next;
      apply();
    }, { passive: false });

    paint();
    fit();
    const intro = document.createElement("p");
    intro.textContent = graph.aviso;
    panel.replaceChildren(intro);
  }
})();
