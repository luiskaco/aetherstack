"""
AetherStack - Verificación de firmas Ed25519 (RFC 8032), solo biblioteca estándar.

Se usa únicamente para VERIFICAR: la clave privada nunca viaja con la app.
Implementación de referencia del RFC 8032 (sección 6), validada en tests/ con los
vectores oficiales del RFC y contra la biblioteca `cryptography`.
No es de tiempo constante: no importa aquí, porque solo procesa datos públicos.
"""
import hashlib

_P = 2 ** 255 - 19
_Q = 2 ** 252 + 27742317777372353535851937790883648493
_D = -121665 * pow(121666, _P - 2, _P) % _P
_SQRT_M1 = pow(2, (_P - 1) // 4, _P)


def _sha512_modq(data):
    return int.from_bytes(hashlib.sha512(data).digest(), "little") % _Q


def point_add(P, Q):
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % _P
    B = (P[1] + P[0]) * (Q[1] + Q[0]) % _P
    C = 2 * P[3] * Q[3] * _D % _P
    D = 2 * P[2] * Q[2] % _P
    E, F, G, H = B - A, D - C, D + C, B + A
    return (E * F % _P, G * H % _P, F * G % _P, E * H % _P)


def point_mul(s, P):
    Q = (0, 1, 1, 0)  # elemento neutro
    while s > 0:
        if s & 1:
            Q = point_add(Q, P)
        P = point_add(P, P)
        s >>= 1
    return Q


def _point_equal(P, Q):
    if (P[0] * Q[2] - Q[0] * P[2]) % _P != 0:
        return False
    if (P[1] * Q[2] - Q[1] * P[2]) % _P != 0:
        return False
    return True


def _recover_x(y, sign):
    if y >= _P:
        return None
    x2 = (y * y - 1) * pow(_D * y * y + 1, _P - 2, _P) % _P
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (_P + 3) // 8, _P)
    if (x * x - x2) % _P != 0:
        x = x * _SQRT_M1 % _P
    if (x * x - x2) % _P != 0:
        return None
    if (x & 1) != sign:
        x = _P - x
    return x


_G_Y = 4 * pow(5, _P - 2, _P) % _P
_G_X = _recover_x(_G_Y, 0)
BASE_POINT = (_G_X, _G_Y, 1, _G_X * _G_Y % _P)


def point_compress(P):
    zinv = pow(P[2], _P - 2, _P)
    x = P[0] * zinv % _P
    y = P[1] * zinv % _P
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def point_decompress(s):
    if len(s) != 32:
        return None
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    if x is None:
        return None
    return (x, y, 1, x * y % _P)


def verify(public_key, message, signature):
    """True solo si `signature` es una firma Ed25519 válida de `message` con `public_key`."""
    try:
        if len(public_key) != 32 or len(signature) != 64:
            return False
        A = point_decompress(public_key)
        R = point_decompress(signature[:32])
        if A is None or R is None:
            return False
        s = int.from_bytes(signature[32:], "little")
        if s >= _Q:
            return False
        h = _sha512_modq(signature[:32] + public_key + message)
        return _point_equal(point_mul(s, BASE_POINT), point_add(R, point_mul(h, A)))
    except Exception:
        return False
