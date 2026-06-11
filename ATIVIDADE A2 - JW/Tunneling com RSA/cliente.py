"""
Uso:
  python cliente.py alice 5001
  python cliente.py bob   5002
"""
import sys
import time
import threading
import requests
from flask import Flask, request as freq, jsonify
from rsa import gerar_chaves, cifrar, decifrar

# ── args ──────────────────────────────────────────────────

if len(sys.argv) < 3:
    print("Uso: python cliente.py <usuario> <porta-webhook>")
    sys.exit(1)

USUARIO  = sys.argv[1]
PORTA    = int(sys.argv[2])
SERVIDOR = "http://localhost:5000"
WEBHOOK  = f"http://localhost:{PORTA}/receber"

DESTINOS = {"alice": "bob", "bob": "alice"}
if USUARIO not in DESTINOS:
    print(f"Usuário deve ser 'alice' ou 'bob'.")
    sys.exit(1)

DESTINO = DESTINOS[USUARIO]

# ── chaves RSA ────────────────────────────────────────────

print(f"[{USUARIO}] Gerando chaves RSA-512...")
pub, priv = gerar_chaves(bits=512)
print(f"[{USUARIO}] Pronto!\n")

# ── registro no servidor ──────────────────────────────────

requests.post(f"{SERVIDOR}/registrar", json={
    "usuario": USUARIO,
    "e": pub[0],
    "n": pub[1],
    "webhook": WEBHOOK,
})
print(f"[{USUARIO}] Registrado  webhook={WEBHOOK}")

# ── webhook local ─────────────────────────────────────────

hook = Flask(__name__)

@hook.route("/receber", methods=["POST"])
def receber_webhook():
    msg = freq.json
    texto = decifrar(msg["mensagem"], priv)
    print(f"\n[{msg['de']}]: {texto}")
    print(f"[{USUARIO}]: ", end="", flush=True)
    return jsonify({"status": "ok"})

threading.Thread(
    target=lambda: hook.run(port=PORTA, debug=False, use_reloader=False),
    daemon=True
).start()

# ── aguarda chave do destino ──────────────────────────────

def buscar_chave():
    while True:
        try:
            r = requests.get(f"{SERVIDOR}/chave/{DESTINO}")
            if r.status_code == 200:
                d = r.json()
                return (d["e"], d["n"])
        except: pass
        print(f"[{USUARIO}] Aguardando {DESTINO}...")
        time.sleep(2)

chave_destino = buscar_chave()
print(f"[{USUARIO}] Chave de {DESTINO} obtida. Digite sua mensagem:\n")

# ── polling de fallback ───────────────────────────────────

def polling():
    while True:
        try:
            r = requests.get(f"{SERVIDOR}/receber/{USUARIO}")
            for msg in r.json().get("mensagens", []):
                texto = decifrar(msg["mensagem"], priv)
                print(f"\n[{msg['de']}]: {texto}")
                print(f"[{USUARIO}]: ", end="", flush=True)
        except: pass
        time.sleep(2)

threading.Thread(target=polling, daemon=True).start()

# ── envio ─────────────────────────────────────────────────

while True:
    texto = input(f"[{USUARIO}]: ")
    if texto.lower() == "sair": break
    cifrado = cifrar(texto, chave_destino)
    requests.post(f"{SERVIDOR}/enviar", json={
        "de": USUARIO, "para": DESTINO, "mensagem": cifrado
    })
