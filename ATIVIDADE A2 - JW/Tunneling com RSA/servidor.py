from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

chaves   = {}   # usuario -> (e, n)
webhooks = {}   # usuario -> url
caixa    = {}   # usuario -> [msgs]

# ── registro ──────────────────────────────────────────────

@app.route("/registrar", methods=["POST"])
def registrar():
    d = request.json
    u = d["usuario"]
    chaves[u]   = (d["e"], d["n"])
    webhooks[u] = d.get("webhook", "")
    caixa.setdefault(u, [])
    print(f"[servidor] {u} registrado  webhook={webhooks[u] or 'nenhum'}")
    return jsonify({"status": "ok"})

# ── chave pública ─────────────────────────────────────────

@app.route("/chave/<usuario>")
def chave(usuario):
    if usuario not in chaves:
        return jsonify({"erro": "não encontrado"}), 404
    e, n = chaves[usuario]
    return jsonify({"e": e, "n": n})

# ── envio (tenta webhook; cai no polling) ─────────────────

@app.route("/enviar", methods=["POST"])
def enviar():
    d    = request.json
    dest = d["para"]
    if dest not in chaves:
        return jsonify({"erro": "destinatário inválido"}), 404

    pacote = {"de": d["de"], "mensagem": d["mensagem"]}

    url = webhooks.get(dest, "")
    if url:
        try:
            requests.post(url, json=pacote, timeout=2)
            print(f"[servidor] webhook entregue → {dest}")
            return jsonify({"status": "webhook"})
        except Exception as ex:
            print(f"[servidor] webhook falhou ({ex}), guardando na caixa")

    caixa[dest].append(pacote)
    return jsonify({"status": "caixa"})

# ── polling (fallback) ────────────────────────────────────

@app.route("/receber/<usuario>")
def receber(usuario):
    if usuario not in caixa:
        return jsonify({"erro": "inválido"}), 404
    msgs, caixa[usuario] = caixa[usuario][:], []
    return jsonify({"mensagens": msgs})

if __name__ == "__main__":
    print("[servidor] http://localhost:5000")
    app.run(port=5000, debug=False)
