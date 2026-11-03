(function () {
  const status = document.getElementById("ado-status");
  const years = document.getElementById("ado-anos");
  const skills = document.getElementById("ado-skills");
  const ata = document.getElementById("ata");
  fetch("data/adocao.json")
    .then((response) => {
      if (!response.ok) throw new Error(String(response.status));
      return response.json();
    })
    .then((report) => {
      const year1 = report.anos.find((row) => row.ano === 1);
      status.textContent = year1.pode_substituir_o_livro_do_ano
        ? "Year 1 mathematics can replace a textbook. Every skill is finished."
        : "Year 1 cannot replace a mathematics textbook yet. " + year1.por_que_nao.join(" ");
      years.innerHTML = "";
      const table = document.createElement("table");
      table.innerHTML = "<thead><tr><th>Year</th><th>Skills</th><th>Finished</th><th>Started only</th><th>May replace the year’s book</th></tr></thead>";
      const body = document.createElement("tbody");
      report.anos.forEach((row) => {
        const tr = document.createElement("tr");
        [row.ano + "º", row.total, row.integrais.length, row.parciais.length, row.pode_substituir_o_livro_do_ano ? "yes" : "no"].forEach((value) => {
          const td = document.createElement("td");
          td.textContent = String(value);
          tr.appendChild(td);
        });
        body.appendChild(tr);
      });
      table.appendChild(body);
      years.appendChild(table);

      const claimed = Object.values(report.habilidades).sort((a, b) => a.codigo.localeCompare(b.codigo));
      skills.innerHTML = "";
      claimed.forEach((item) => {
        const p = document.createElement("p");
        const strong = document.createElement("strong");
        strong.textContent = item.codigo + " · " + (item.cobertura === "integral" ? "finished, adoptable" : "started, not adoptable as done");
        p.appendChild(strong);
        p.append(" " + item.nota);
        skills.appendChild(p);
      });
      ata.value = report.ata;
    })
    .catch(() => {
      status.textContent = "The adoption minute could not be loaded. It is published as data/adocao.json with the site.";
    });

  document.getElementById("copiar").addEventListener("click", async () => {
    if (!ata.value) return;
    try {
      await navigator.clipboard.writeText(ata.value);
      document.getElementById("copiar").textContent = "Ata copiada";
    } catch {
      ata.focus();
      ata.select();
    }
  });
})();
