import random

def miller_rabin(n, rounds=20):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False

    s, m = 0, n - 1
    while m % 2 == 0:
        s += 1
        m //= 2

    for _ in range(rounds):
        b = random.randrange(2, n - 1)
        x = pow(b, m, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True

def primo(bits):
    while True:
        c = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if miller_rabin(c): return c

def ext_gcd(a, b):
    if b == 0: return a, 1, 0
    g, x, y = ext_gcd(b, a % b)
    return g, y, x - (a // b) * y

def mod_inv(a, m):
    g, x, _ = ext_gcd(a % m, m)
    if g != 1: raise ValueError("Inverso modular não existe")
    return x % m

def gerar_chaves(bits=1024):
    p, q = primo(bits // 2), primo(bits // 2)
    while q == p: q = primo(bits // 2)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if ext_gcd(e, phi)[0] != 1:
        e = 3
        while ext_gcd(e, phi)[0] != 1: e += 2

    return (e, n), (mod_inv(e, phi), n)

def cifrar(texto: str, pub: tuple) -> list:
    e, n = pub
    return [pow(ord(c), e, n) for c in texto]

def decifrar(cifra: list, priv: tuple) -> str:
    d, n = priv
    return ''.join(chr(pow(b, d, n)) for b in cifra)

if __name__ == "__main__":
    print("Gerando chaves RSA-1024... (pode levar alguns segundos)")
    pub, priv = gerar_chaves()

    print(f"Chave pública (e): {pub[0]}")
    print(f"Módulo        (n): {pub[1]}\n")

    msg = input("Mensagem para cifrar: ")

    cifrado = cifrar(msg, pub)
    print(f"\nCifrado  : {cifrado}")
    print(f"Decifrado: {decifrar(cifrado, priv)}")
