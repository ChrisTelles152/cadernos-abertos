#!/usr/bin/env python3
"""The local teacher API records the assumption and does not record a different one."""

import json
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import serve


def request(base, path, payload=None, cookie=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {}
    if payload is not None:
        headers["Content-Type"] = "application/json"
        headers["X-Cadernos"] = "1"
    if cookie:
        headers["Cookie"] = f"cadernos={cookie}"
    req = urllib.request.Request(base + path, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            token = None
            set_cookie = response.headers.get("Set-Cookie") or ""
            if "cadernos=" in set_cookie:
                token = set_cookie.split("cadernos=", 1)[1].split(";", 1)[0]
            return response.status, json.loads(response.read().decode("utf-8")), token or cookie
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8")), cookie


def main():
    with tempfile.TemporaryDirectory() as tmp:
        httpd = serve.make_server("127.0.0.1", 0, Path(tmp))
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{port}"
        try:
            status, report, _ = request(base, "/api/adocao")
            assert status == 200, status
            year1 = next(row for row in report["anos"] if row["ano"] == 1)
            assert year1["pode_substituir_o_livro_do_ano"] is True
            assert serve.adocao.SENTENCE_PNLD in report["ata"]

            status, body, cookie = request(base, "/api/setup", {"senha": "curta"})
            assert status == 400, body
            status, body, cookie = request(base, "/api/setup", {"senha": "caderno-local"})
            assert status == 200 and cookie, body

            status, body, _ = request(base, "/api/alunos", cookie=None)
            assert status == 401

            status, aluno, cookie = request(base, "/api/alunos", {"nome": "Nara"}, cookie)
            assert status == 200, aluno
            assert aluno["nome"] == "Nara"
            assert any(row["id"] == "N-COMPARAR" and row["estado"] == "unseen" for row in aluno["conceitos"])

            status, body, cookie = request(
                base,
                "/api/responder",
                {"aluno": aluno["id"], "item": "q-comparar", "opcao": "mais-digitos"},
                cookie,
            )
            assert status == 200, body
            assert body["julgamento"]["regra"] == "F-MAIS-DIGITOS"
            assert body["julgamento"]["certa"] is False
            states = {row["id"]: row for row in body["aluno"]["conceitos"]}
            assert states["N-COMPARAR"]["estado"] == "gap"
            assert states["N-COMPARAR"]["ano"] >= 1
            assert "99 e 100" in states["N-COMPARAR"]["hipoteses"][0]["hipotese"]
            blocked = {row["id"] for row in body["aluno"]["bloqueados_sem_tentativa"]}
            assert "N-COMPOR" not in states
            assert blocked == set()
        finally:
            httpd.shutdown()
    print("server claims hold")


if __name__ == "__main__":
    main()
