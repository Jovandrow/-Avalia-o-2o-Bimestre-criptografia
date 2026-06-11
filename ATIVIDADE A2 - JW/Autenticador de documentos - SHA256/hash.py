import sys
import os
from sha256 import sha256

def assinar(path: str):
    if not os.path.exists(path):
        print(f"[erro] Arquivo não encontrado: {path}")
        return

    digest = sha256(open(path, "rb").read())
    out = path + ".hash"
    open(out, "w").write(digest)

    print(f"Arquivo : {path}")
    print(f"SHA-256 : {digest}")
    print(f"Salvo em: {out}")

def verificar(path: str, hash_ref: str):
    if not os.path.exists(path):
        print(f"[erro] Arquivo não encontrado: {path}")
        return

    if os.path.exists(hash_ref):
        esperado = open(hash_ref).read().strip()
    else:
        esperado = hash_ref.strip().lower()

    calculado = sha256(open(path, "rb").read())
    ok = calculado == esperado

    print(f"Arquivo        : {path}")
    print(f"Hash esperado  : {esperado}")
    print(f"Hash calculado : {calculado}")
    print()
    print("✅ AUTÊNTICO" if ok else "❌ INVÁLIDO")

def main():
    uso = (
        "Uso:\n"
        "  python hash.py assinar  <arquivo>\n"
        "  python hash.py verificar <arquivo> <hash|arquivo.hash>"
    )

    if len(sys.argv) < 3:
        print(uso); sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "assinar":
        assinar(sys.argv[2])
    elif cmd == "verificar":
        if len(sys.argv) < 4:
            print("Informe o hash ou o arquivo .hash."); sys.exit(1)
        verificar(sys.argv[2], sys.argv[3])
    else:
        print(f"Comando desconhecido: '{cmd}'"); sys.exit(1)

if __name__ == "__main__":
    main()
