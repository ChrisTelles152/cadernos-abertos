(function () {
  const ESTADOS = {
    unseen: "ainda não visto",
    evidenced: "consistente com saber",
    gap: "hipótese sobre o erro",
    bloqueado: "bloqueado pela lacuna anterior",
    conflito: "crédito em conflito com uma lacuna",
  };

  const painelSenha = document.getElementById("painel-senha");
  const formSenha = document.getElementById("form-senha");
  const senhaTexto = document.getElementById("senha-texto");
  const senhaTitulo = document.getElementById("senha-titulo");
  const senhaBotao = document.getElementById("senha-botao");
  const senhaErro = document.getElementById("senha-erro");
  const painelTurma = document.getElementById("painel-turma");
  const lista = document.getElementById("lista");
  const ficha = document.getElementById("ficha");
  const diagnostico = document.getElementById("diagnostico");

  let modo = "entrar";
  let itens = [];
  let aluno = null;

  function api(path, payload) {
    const options = { headers: { "X-Cadernos": "1" }, credentials: "same-origin" };
    if (payload !== undefined) {
      options.method = "POST";
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(payload);
    }
    return fetch(path, options).then(async (response) => {
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        const error = new Error(body.erro || "falha");
        error.status = response.status;
        throw error;
      }
      return body;
    });
  }

  function showError(error) {
    senhaErro.hidden = false;
    senhaErro.textContent = error.message;
  }

  function paintAluno(row) {
    aluno = row;
    ficha.hidden = false;
    document.getElementById("ficha-nome").textContent = row.nome;
    const map = document.getElementById("mapa-aluno");
    map.innerHTML = "";
    row.conceitos.filter((concept) => concept.na_unidade || concept.estado !== "unseen").forEach((concept) => {
      const block = document.createElement("article");
      block.className = "activity";
      const title = document.createElement("p");
      const badge = document.createElement("span");
      badge.className = "estado " + concept.estado;
      badge.textContent = ESTADOS[concept.estado] || concept.estado;
      title.append(badge, " ", concept.nome_pt);
      block.appendChild(title);
      concept.hipoteses.forEach((note) => {
        const p = document.createElement("p");
        p.textContent = note.hipotese;
        block.appendChild(p);
      });
      concept.evidencias.forEach((note) => {
        const p = document.createElement("p");
        p.textContent = note.hipotese + " Chance de chute nesta pergunta: " + note.chance + ".";
        block.appendChild(p);
      });
      if (concept.estado === "gap") {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "choice";
        button.textContent = "Arquivar a hipótese depois de reensinar";
        button.addEventListener("click", () => {
          api("/api/reparo", { aluno: row.id, conceito: concept.id })
            .then((body) => paintAluno(body.aluno))
            .catch((error) => alert(error.message));
        });
        block.appendChild(button);
      }
      map.appendChild(block);
    });
    const quiet = row.bloqueados_sem_tentativa || [];
    if (quiet.length) {
      const gapYears = row.conceitos.filter((concept) => concept.estado === "gap").map((concept) => concept.ano || 1);
      const horizon = Math.max(1, ...gapYears) + 1;
      const near = quiet.filter((item) => item.ano <= horizon).sort((a, b) => a.ano - b.ano || a.nome_pt.localeCompare(b.nome_pt));
      const later = quiet.length - near.length;
      const p = document.createElement("p");
      p.className = "note";
      const names = near.map((item) => item.nome_pt).join(", ");
      p.textContent = "A lacuna bloqueia o que ainda não foi perguntado e depende dela. O mais próximo: " + (names || "nada neste ano") + ". " + later + " conceitos de anos seguintes ficam bloqueados do mesmo modo. Bloqueado não é reprovado.";
      map.appendChild(p);
    }
    const questions = document.getElementById("perguntas");
    questions.innerHTML = "";
    itens.forEach((item) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "choice";
      button.textContent = item.leitura;
      button.addEventListener("click", () => openItem(item));
      questions.appendChild(button);
    });
  }

  function openItem(item) {
    diagnostico.hidden = true;
    const box = document.getElementById("pergunta");
    box.hidden = false;
    document.getElementById("leitura").textContent = item.leitura;
    document.getElementById("leitura-en").textContent = item.gloss;
    const options = document.getElementById("opcoes");
    options.innerHTML = "";
    item.opcoes.forEach((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "choice";
      button.textContent = option.texto;
      button.addEventListener("click", () => {
        options.querySelectorAll("button").forEach((el) => (el.disabled = true));
        api("/api/responder", { aluno: aluno.id, item: item.id, opcao: option.id })
          .then((body) => {
            showJudgement(body.julgamento);
            paintAluno(body.aluno);
          })
          .catch((error) => {
            options.querySelectorAll("button").forEach((el) => (el.disabled = false));
            alert(error.message);
          });
      });
      options.appendChild(button);
    });
    box.scrollIntoView({ block: "nearest" });
  }

  function showJudgement(judged) {
    diagnostico.hidden = false;
    diagnostico.innerHTML = "";
    const title = document.createElement("h3");
    title.textContent = judged.certa ? "Consistente com o modelo do item" : judged.tipo_opcao === "inconclusivo" ? "Ainda não sabemos" : "Hipótese registrada";
    diagnostico.appendChild(title);
    const p = document.createElement("p");
    p.textContent = judged.hipotese || judged.explica_o_que_nao_diz;
    diagnostico.appendChild(p);
    if (judged.certa) {
      const chance = document.createElement("p");
      chance.textContent = "Isto também sai num chute em " + judged.chance + " das razões que diagnosticam. Não é prova.";
      diagnostico.appendChild(chance);
    }
    if (judged.nao_confundir_com && judged.nao_confundir_com.length) {
      const avoid = document.createElement("p");
      avoid.textContent = "Não registrar como falta de: " + judged.nao_confundir_com.join(", ") + ".";
      diagnostico.appendChild(avoid);
    }
  }

  function paintRoster(rows) {
    lista.innerHTML = "";
    rows.forEach((row) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "choice";
      const gaps = row.conceitos.filter((concept) => concept.estado === "gap").length;
      button.textContent = row.nome + (gaps ? " · " + gaps + " hipótese(s)" : "");
      button.addEventListener("click", () => paintAluno(row));
      lista.appendChild(button);
    });
  }

  function enterApp() {
    painelSenha.hidden = true;
    painelTurma.hidden = false;
    Promise.all([api("/api/itens"), api("/api/alunos")])
      .then(([bank, roster]) => {
        itens = bank.itens;
        paintRoster(roster.alunos);
      })
      .catch((error) => alert(error.message));
  }

  formSenha.addEventListener("submit", (event) => {
    event.preventDefault();
    senhaErro.hidden = true;
    const path = modo === "criar" ? "/api/setup" : "/api/login";
    api(path, { senha: document.getElementById("senha").value })
      .then(() => enterApp())
      .catch(showError);
  });

  document.getElementById("form-aluno").addEventListener("submit", (event) => {
    event.preventDefault();
    const input = document.getElementById("novo-nome");
    api("/api/alunos", { nome: input.value })
      .then((row) => {
        input.value = "";
        return api("/api/alunos").then((roster) => {
          paintRoster(roster.alunos);
          paintAluno(row);
        });
      })
      .catch((error) => alert(error.message));
  });

  document.getElementById("sair").addEventListener("click", () => {
    api("/api/logout", {}).then(() => location.reload());
  });

  api("/api/me")
    .then((me) => {
      if (me.entrou) {
        enterApp();
        return;
      }
      formSenha.hidden = false;
      if (!me.tem_professor) {
        modo = "criar";
        senhaTitulo.textContent = "Criar a senha do professor";
        senhaTexto.textContent = "A primeira senha fica só neste computador. Oito caracteres ou mais. Não há recuperação nesta versão: quem perde a senha perde o arquivo local.";
        senhaBotao.textContent = "Criar e entrar";
        document.getElementById("senha").autocomplete = "new-password";
      } else {
        senhaTexto.textContent = "A senha já existe neste computador.";
      }
    })
    .catch(() => {
      senhaTexto.textContent = "Este sítio público não recebe nome de aluno. A ata proíbe ceder dado de criança a terceiro. O cálculo continua no repositório e roda nos testes; não há base de alunos na nuvem.";
    });
})();
