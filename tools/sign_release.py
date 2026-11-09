"""
AetherStack - Firma de releases (solo para quien publica).

Uso:
    python tools/sign_release.py init      # crea la clave privada (una sola vez) y muestra la pública
    python tools/sign_release.py pubkey    # muestra la clave pública en hexadecimal

La clave privada vive FUERA del repositorio, en la carpeta personal del usuario de Windows
(o en la ruta de la variable AETHERSTACK_SIGNING_KEY). Nunca se imprime ni se sube a Git.
Si se pierde, hay que generar una nueva y publicar a mano una versión con la clave pública nueva.
"""
import base64
import getpass
import hashlib
import os
import subprocess
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)
import sigverify as sv

DEFAULT_KEY_PATH = os.path.join(os.path.expanduser("~"), ".aetherstack-signing", "release.key")


def key_path():
    return os.environ.get("AETHERSTACK_SIGNING_KEY", DEFAULT_KEY_PATH)


def signing_message(version, sha256_hex):
    """Lo que se firma: ata la firma a UNA versión y a UN contenido (evita reutilizar zips viejos)."""
    return f"aetherstack-code\nversion={version}\nsha256={sha256_hex}\n".encode("ascii")


def _expand(seed):
    h = hashlib.sha512(seed).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def public_key_from_seed(seed):
    a, _ = _expand(seed)
    return sv.point_compress(sv.point_mul(a, sv.BASE_POINT))


def sign(seed, message):
    """Firma Ed25519 determinista (RFC 8032)."""
    a, prefix = _expand(seed)
    pub = sv.point_compress(sv.point_mul(a, sv.BASE_POINT))
    r = sv._sha512_modq(prefix + message)
    Rs = sv.point_compress(sv.point_mul(r, sv.BASE_POINT))
    h = sv._sha512_modq(Rs + pub + message)
    s = (r + h * a) % sv._Q
    return Rs + int.to_bytes(s, 32, "little")


def load_seed(path=None):
    path = path or key_path()
    if not os.path.exists(path):
        sys.exit(f"No hay clave de firma en {path}\nCrea una con: python tools/sign_release.py init")
    with open(path, "r", encoding="ascii") as f:
        seed = bytes.fromhex(f.read().strip())
    if len(seed) != 32:
        sys.exit("La clave de firma está dañada (se esperaban 32 bytes).")
    return seed


def init_key(path=None):
    path = path or key_path()
    if os.path.exists(path):
        sys.exit(f"Ya existe una clave en {path}. No se sobrescribe: bórrala a mano solo si estás seguro.")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    seed = os.urandom(32)
    with open(path, "w", encoding="ascii") as f:
        f.write(seed.hex() + "\n")
    # Solo el usuario actual puede leerla (en Windows; en otros sistemas, permisos 600)
    if os.name == "nt":
        subprocess.run(["icacls", path, "/inheritance:r", "/grant:r", f"{getpass.getuser()}:F"],
                       capture_output=True)
    else:
        os.chmod(path, 0o600)
    return public_key_from_seed(seed)


def sign_zip(zip_path, version, path=None):
    """Firma el zip y devuelve la ruta del .sig (firma en base64, una línea)."""
    h = hashlib.sha256()
    with open(zip_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    seed = load_seed(path)
    signature = sign(seed, signing_message(version, h.hexdigest()))
    sig_path = zip_path + ".sig"
    with open(sig_path, "w", encoding="ascii", newline="\n") as f:
        f.write(base64.b64encode(signature).decode("ascii") + "\n")
    return sig_path


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "init":
        pub = init_key()
        print("Clave de firma creada en:", key_path())
        print("Clave pública (pégala en RELEASE_PUBLIC_KEY de updater.py):")
        print(pub.hex())
        print("\nGuarda una COPIA de la clave privada en un lugar seguro (gestor de contraseñas).")
    elif cmd == "pubkey":
        print(public_key_from_seed(load_seed()).hex())
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
