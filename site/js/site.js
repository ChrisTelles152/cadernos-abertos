(function () {
  const page = document.body.dataset.page;
  document.querySelectorAll(".nav a").forEach((a) => {
    if (a.dataset.page === page) a.setAttribute("aria-current", "page");
  });

  const needsData = document.querySelector("[data-count], #counts");
  if (!needsData) return;

  const url = document.body.dataset.data || "data/curriculum.json";
  fetch(url)
    .then((r) => r.json())
    .then((data) => {
      const c = data.meta.contagens;
      const map = {
        ef: c.habilidades_ef,
        em: c.habilidades_em,
        ei: c.objetivos_ei,
        conceitos: c.conceitos,
        exige: c.arestas_exige,
        apoia: c.arestas_apoia,
      };
      document.querySelectorAll("[data-count]").forEach((el) => {
        const n = map[el.dataset.count];
        if (n != null) el.textContent = String(n);
      });
    })
    .catch(() => {});
})();
