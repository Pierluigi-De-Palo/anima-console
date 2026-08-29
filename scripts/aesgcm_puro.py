#!/usr/bin/env python3
"""
COSA FA — AES-256-GCM in Python puro: cifra e decifra un messaggio con chiave,
IV e tag di autenticazione, senza installare niente.

PERCHÉ ESISTE — il generatore della regia (`build_regia.py`) gira sul Mac del
Direttore, con il Python che c'è. Chiedere `pip install cryptography` prima di
poter pubblicare significa che un giorno, di fretta, la regia non si aggiorna.
La libreria standard non ha AES: o si dipende da qualcuno, o ci si porta il
cifrario in casa. Ci si porta il cifrario in casa, e lo si mette alla prova.

FIN DOVE ARRIVA — implementazione didattica, NON a tempo costante: le tabelle e
i rami dipendono dai dati, quindi non usarla dove un attaccante può misurare i
tempi (server condiviso, browser). Qui cifra offline sulla macchina del
Direttore, dove non c'è nessuno a cronometrare. Solo chiavi da 32 byte (AES-256)
e IV da 12 byte, che è l'unico caso che ci serve. Lenta: ~10 KB in una frazione
di secondo, va bene per un payload, non per un archivio.
La correttezza non è un'opinione: `autoprova()` gira i vettori NIST prima di
ogni uso e il generatore ridecifra sempre quello che ha appena cifrato.

USO — come modulo:
    from aesgcm_puro import cifra, decifra, autoprova
    autoprova()                                  # esplode se il cifrario sbaglia
    testa = cifra(chiave32, iv12, b"messaggio")  # -> ciphertext || tag(16)
    chiaro = decifra(chiave32, iv12, testa)      # -> b"messaggio" oppure ValueError
  come collaudo:
    python3 scripts/aesgcm_puro.py

— creato da SQUELCH, 2026-08-29
"""

# ── AES: S-box generata, non incollata ───────────────────────────────────────
# 256 byte copiati a mano sono 256 occasioni di refuso silenzioso. Qui la
# tabella nasce dalla sua definizione (inverso in GF(2^8) + trasformazione
# affine) e i vettori NIST dicono subito se è sbagliata.
def _tabella_sbox() -> bytes:
    sbox = [0] * 256
    p = q = 1
    while True:
        p = (p ^ ((p << 1) & 0xFF) ^ (0x1B if p & 0x80 else 0)) & 0xFF
        q ^= (q << 1) & 0xFF
        q ^= (q << 2) & 0xFF
        q ^= (q << 4) & 0xFF
        if q & 0x80:
            q ^= 0x09
        q &= 0xFF
        rot = lambda x, n: ((x << n) | (x >> (8 - n))) & 0xFF
        sbox[p] = (q ^ rot(q, 1) ^ rot(q, 2) ^ rot(q, 3) ^ rot(q, 4) ^ 0x63) & 0xFF
        if p == 1:
            break
    sbox[0] = 0x63
    return bytes(sbox)


SBOX = _tabella_sbox()


def _xtime(a: int) -> int:
    return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else (a << 1) & 0xFF


def _chiavi_di_turno(chiave: bytes) -> list[bytes]:
    """Espansione della chiave: 15 sottochiavi da 16 byte per AES-256."""
    nk = len(chiave) // 4          # 8 parole
    nr = nk + 6                    # 14 turni
    w = [list(chiave[4 * i:4 * i + 4]) for i in range(nk)]
    rcon = 1
    for i in range(nk, 4 * (nr + 1)):
        t = list(w[i - 1])
        if i % nk == 0:
            t = [SBOX[b] for b in t[1:] + t[:1]]
            t[0] ^= rcon
            rcon = _xtime(rcon)
        elif nk > 6 and i % nk == 4:
            t = [SBOX[b] for b in t]
        w.append([a ^ b for a, b in zip(w[i - nk], t)])
    return [bytes(w[4 * r] + w[4 * r + 1] + w[4 * r + 2] + w[4 * r + 3]) for r in range(nr + 1)]


def _cifra_blocco(turni: list[bytes], blocco: bytes) -> bytes:
    """Un blocco da 16 byte. GCM usa solo questa direzione: niente decifratura AES."""
    s = [b ^ k for b, k in zip(blocco, turni[0])]
    for r in range(1, len(turni) - 1):
        s = [SBOX[b] for b in s]
        s = [s[(4 * ((c + r_) % 4)) + r_] for c in range(4) for r_ in range(4)]  # ShiftRows
        m = []
        for c in range(4):                                                        # MixColumns
            a0, a1, a2, a3 = s[4 * c:4 * c + 4]
            m += [_xtime(a0) ^ (_xtime(a1) ^ a1) ^ a2 ^ a3,
                  a0 ^ _xtime(a1) ^ (_xtime(a2) ^ a2) ^ a3,
                  a0 ^ a1 ^ _xtime(a2) ^ (_xtime(a3) ^ a3),
                  (_xtime(a0) ^ a0) ^ a1 ^ a2 ^ _xtime(a3)]
        s = [b ^ k for b, k in zip(m, turni[r])]
    s = [SBOX[b] for b in s]
    s = [s[(4 * ((c + r_) % 4)) + r_] for c in range(4) for r_ in range(4)]
    return bytes(b ^ k for b, k in zip(s, turni[-1]))


# ── GCM ──────────────────────────────────────────────────────────────────────
_R = 0xE1 << 120


def _moltiplica(x: int, y: int) -> int:
    """Prodotto in GF(2^128) con l'ordine di bit di GCM (MSB per primo)."""
    z, v = 0, x
    for i in range(128):
        if (y >> (127 - i)) & 1:
            z ^= v
        v = (v >> 1) ^ _R if v & 1 else v >> 1
    return z


def _ghash(h: int, dati: bytes) -> int:
    y = 0
    for i in range(0, len(dati), 16):
        blocco = dati[i:i + 16].ljust(16, b"\x00")
        y = _moltiplica(y ^ int.from_bytes(blocco, "big"), h)
    return y


def _flusso(turni: list[bytes], j0: bytes, quanti: int) -> bytes:
    contatore = int.from_bytes(j0, "big")
    fuori = bytearray()
    while len(fuori) < quanti:
        contatore = (contatore & ~0xFFFFFFFF) | ((contatore + 1) & 0xFFFFFFFF)
        fuori += _cifra_blocco(turni, contatore.to_bytes(16, "big"))
    return bytes(fuori[:quanti])


def _controlla(chiave: bytes, iv: bytes) -> None:
    if len(chiave) != 32:
        raise ValueError("solo AES-256: la chiave dev'essere di 32 byte")
    if len(iv) != 12:
        raise ValueError("solo IV da 12 byte (quello che usa WebCrypto)")


def _tag(turni: list[bytes], h: int, j0: bytes, testo: bytes, aad: bytes) -> bytes:
    dato = (aad.ljust((len(aad) + 15) // 16 * 16, b"\x00")
            + testo.ljust((len(testo) + 15) // 16 * 16, b"\x00")
            + (len(aad) * 8).to_bytes(8, "big") + (len(testo) * 8).to_bytes(8, "big"))
    s = _ghash(h, dato)
    return bytes(a ^ b for a, b in zip(s.to_bytes(16, "big"), _cifra_blocco(turni, j0)))


def cifra(chiave: bytes, iv: bytes, chiaro: bytes, aad: bytes = b"") -> bytes:
    """Ritorna ciphertext || tag(16), lo stesso formato che si aspetta WebCrypto."""
    _controlla(chiave, iv)
    turni = _chiavi_di_turno(chiave)
    h = int.from_bytes(_cifra_blocco(turni, b"\x00" * 16), "big")
    j0 = iv + b"\x00\x00\x00\x01"
    testo = bytes(a ^ b for a, b in zip(chiaro, _flusso(turni, j0, len(chiaro))))
    return testo + _tag(turni, h, j0, testo, aad)


def decifra(chiave: bytes, iv: bytes, pacco: bytes, aad: bytes = b"") -> bytes:
    """Autentica e apre. Tag che non torna → ValueError, mai un chiaro «quasi giusto»."""
    _controlla(chiave, iv)
    if len(pacco) < 16:
        raise ValueError("pacco troppo corto: manca il tag")
    testo, tag = pacco[:-16], pacco[-16:]
    turni = _chiavi_di_turno(chiave)
    h = int.from_bytes(_cifra_blocco(turni, b"\x00" * 16), "big")
    j0 = iv + b"\x00\x00\x00\x01"
    atteso = _tag(turni, h, j0, testo, aad)
    # Confronto senza scorciatoie: nessun `!=` che esce al primo byte diverso.
    if sum(a ^ b for a, b in zip(atteso, tag)) != 0:
        raise ValueError("tag non valido: chiave sbagliata o dato manomesso")
    return bytes(a ^ b for a, b in zip(testo, _flusso(turni, j0, len(testo))))


# ── vettori di prova ─────────────────────────────────────────────────────────
# Provenienza dichiarata, perché un vettore inventato è peggio di nessun vettore:
#  · blocco AES-256: FIPS-197, appendice C.3 (chiave 000102…1f)
#  · GCM: casi 13, 14 e 16 di «The Galois/Counter Mode of Operation (GCM)»,
#    i tre canonici per AES-256 — riprodotti qui con OpenSSL 3.0.13 il 2026-08-29
#    e ritrovati identici da questa implementazione.
_BLOCCO_AES = ("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
               "00112233445566778899aabbccddeeff", "8ea2b7ca516745bfeafc49904b496089")

_VETTORI = [  # (chiave, iv, aad, chiaro, ciphertext, tag)
    ("00" * 32, "00" * 12, "", "", "", "530f8afbc74536b9a963b4f1c4cb738b"),
    ("00" * 32, "00" * 12, "", "00" * 16,
     "cea7403d4d606b6e074ec5d3baf39d18", "d0d1c8a799996bf0265b98b5d48ab919"),
    ("feffe9928665731c6d6a8f9467308308feffe9928665731c6d6a8f9467308308",
     "cafebabefacedbaddecaf888", "feedfacedeadbeeffeedfacedeadbeefabaddad2",
     "d9313225f88406e5a55909c5aff5269a86a7a9531534f7da2e4c303d8a318a721c3c0c959568"
     "09532fcf0e2449a6b525b16aedf5aa0de657ba637b39",
     "522dc1f099567d07f47f37a32a84427d643a8cdcbfe5c0c97598a2bd2555d1aa8cb08e48590d"
     "bb3da7b08b1056828838c5f61e6393ba7a0abcc9f662",
     "76fc6ece0f4e1768cddf8853bb2d551b"),
]


def autoprova() -> None:
    """Vettori noti. Se saltano, meglio fermarsi che pubblicare un payload che non si apre."""
    if SBOX[0x00] != 0x63 or SBOX[0x53] != 0xED or SBOX[0xFF] != 0x16:
        raise SystemExit("✗ S-box AES sbagliata: cifrario inutilizzabile")
    k, chiaro, atteso = (bytes.fromhex(x) for x in _BLOCCO_AES)
    if _cifra_blocco(_chiavi_di_turno(k), chiaro) != atteso:
        raise SystemExit("✗ blocco AES-256 fuori standard (FIPS-197 C.3)")
    for vk, viv, vaad, vpt, vct, vtag in _VETTORI:
        k, iv, aad, pt = (bytes.fromhex(x) for x in (vk, viv, vaad, vpt))
        pacco = cifra(k, iv, pt, aad)
        if pacco != bytes.fromhex(vct) + bytes.fromhex(vtag):
            raise SystemExit("✗ vettore GCM fallito: AES-GCM non affidabile su questa macchina")
        if decifra(k, iv, pacco, aad) != pt:
            raise SystemExit("✗ round-trip fallito su un vettore noto")


if __name__ == "__main__":
    import os
    autoprova()
    print("✓ vettori noti superati — FIPS-197 C.3 + GCM casi 13/14/16 (AES-256)")
    k, iv = os.urandom(32), os.urandom(12)
    msg = b"la regia non si apre senza passphrase" * 40
    pacco = cifra(k, iv, msg)
    assert decifra(k, iv, pacco) == msg
    print(f"✓ round-trip su {len(msg)} byte")
    rotto = bytearray(pacco); rotto[7] ^= 1
    try:
        decifra(k, iv, bytes(rotto))
        raise SystemExit("✗ un byte cambiato è passato: il tag non sta autenticando niente")
    except ValueError as err:
        print(f"✓ manomissione respinta — {err}")
    try:
        decifra(os.urandom(32), iv, pacco)
        raise SystemExit("✗ chiave sbagliata accettata")
    except ValueError as err:
        print(f"✓ chiave sbagliata respinta — {err}")
