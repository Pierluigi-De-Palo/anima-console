#!/usr/bin/env python3
"""
COSA FA — genera `docs/index.html`: la PORTA di cyberboomer.io. Sopra c'è solo
  un campo per la frase di sblocco; dietro c'è IL BANCO DI LAVORO del Direttore
  (strumenti, stato, chiavi, comandi), cifrato in AES-GCM-256.

PERCHÉ ESISTE — dal 30/08 cyberboomer.io non è più una vetrina: è l'officina
  privata del Direttore, il posto da cui «si va a lavorare in agenzia» da
  remoto senza laptop. Una vetrina si apre a tutti; un'officina ha una porta.

FIN DOVE ARRIVA — e questo va detto in chiaro, non nascosto:
  · Quello che sta DIETRO la porta (l'elenco strumenti, lo stato, il registro
    chiavi) è **cifrato davvero**: senza la frase è rumore, anche scaricando il
    file dal repo. Questa parte è una serratura.
  · Le PAGINE che la porta elenca (`/fake-checker/`, `/braindance/`, …) restano
    raggiungibili una per una da chi ne indovina l'indirizzo, finché il repo è
    pubblico e il sito sta su GitHub Pages. Per quelle la porta è una tenda.
  · La tenda diventa serratura quando davanti al dominio c'è Cloudflare Access
    (piano deciso dal Direttore il 29/08). Le due cose si sommano: Access ferma
    chi bussa, la cifratura protegge il contenuto anche se il file gira.

LA CHIAVE — è la STESSA della regia (`systema77.regia` nel Portachiavi): una
  frase sola apre tutta l'officina. Non se ne inventa una seconda da ricordare.

USO — dal Mac, con la frase MAI sulla riga di comando (la history è un log):
    bash squadra/chiavi.sh setta regia        # una volta sola, se non c'è
    python3 scripts/build_porta.py            # la prende dal Portachiavi
  oppure, se la frase è già in un file protetto:
    export REGIA_PASSPHRASE="$(cat ~/.frase-regia)" && python3 scripts/build_porta.py
  In entrambi i casi il comando che finisce nella history non contiene la frase.
  `--salt-nuovo` rigenera sale e blocchi da zero (dopo un cambio di frase).

— creato da D.R.A.G.O., 2026-08-30
"""

import base64
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aesgcm_puro  # AES-GCM in Python puro: la libreria di sistema qui è rotta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
USCITA = os.path.join(DOCS, "index.html")

ITERAZIONI = 210_000          # il motore in pagina rifiuta payload sotto 200.000
FRASE_MINIMA = 12
SEGNO = "PORTA_PAYLOAD"       # marcatore del blocco JSON dentro la pagina


# ── la frase ─────────────────────────────────────────────────────────────────
def passphrase() -> str:
    """Dall'ambiente o dal Portachiavi. Mai da riga di comando."""
    frase = os.environ.get("REGIA_PASSPHRASE", "")
    da = "REGIA_PASSPHRASE"
    if not frase:
        chiavi = os.path.join(ROOT, "squadra", "chiavi.sh")
        if os.path.exists(chiavi):
            r = subprocess.run(["bash", chiavi, "leggi", "regia"],
                               capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                frase, da = r.stdout.strip(), "chiavi.sh leggi regia"
    if not frase:
        raise SystemExit(
            "✗ nessuna frase di sblocco.\n"
            "  export REGIA_PASSPHRASE=\"$(cat <file>)\"   (mai come argomento)\n"
            "  oppure: bash squadra/chiavi.sh setta regia   e rilancia.")
    if len(frase) < FRASE_MINIMA:
        raise SystemExit(f"✗ frase di {len(frase)} caratteri: qui la sicurezza è tutta lì "
                         f"dentro, ne servono almeno {FRASE_MINIMA}.")
    print(f"· frase presa da: {da}")
    return frase


def deriva(frase: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", frase.encode("utf-8"), salt, ITERAZIONI, 32)


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


# ── i contenuti del banco, letti dai file veri ───────────────────────────────
def leggi_verdetti() -> list:
    """I verdetti pubblicati, con la loro età reale. Niente scritto a mano."""
    fuori = []
    cartella = os.path.join(DOCS, "data")
    for nome in sorted(os.listdir(cartella)):
        if not re.match(r"^\d{4}-.*\.json$", nome):
            continue
        with open(os.path.join(cartella, nome), encoding="utf-8") as f:
            v = json.load(f)
        d = v.get("data_verifica", "")
        eta = None
        if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            y, m, g = (int(x) for x in d.split("-"))
            eta = (date.today() - date(y, m, g)).days
        fuori.append({
            "id": nome[:4],
            "titolo": v.get("titolo", "")[:70],
            "punteggio": v.get("punteggio"),
            "data": d,
            "eta": eta,
        })
    return fuori


def blocco_stato(verdetti: list) -> dict:
    vecchi = [v for v in verdetti if v["eta"] is not None and v["eta"] > 21]
    bd = os.path.join(DOCS, "data", "braindance.json")
    n_bd, agg_bd = 0, "?"
    if os.path.exists(bd):
        with open(bd, encoding="utf-8") as f:
            d = json.load(f)
        n_bd, agg_bd = len(d.get("verdetti", [])), d.get("aggiornato", "?")
    return {
        "generato": date.today().isoformat(),
        # Anche le ETICHETTE stanno qui dentro, non nel modello di pagina: a
        # lucchetto chiuso non deve trapelare nemmeno il nome di un reparto.
        # (Questa riga nasce da un guasto vero: la guardia ha bocciato la prima
        #  versione perché «braindance» era scritto in chiaro in un'etichetta.)
        "cifre": [
            {"n": len(verdetti), "etichetta": "verdetti KIROSHI"},
            {"n": n_bd, "etichetta": f"verdetti BRAINDANCE · agg. {agg_bd}"},
            {"n": len(vecchi), "etichetta": "da riverificare"},
        ],
        "da_riverificare": [f"{v['id']} · {v['titolo']} — {v['eta']} giorni" for v in vecchi],
        "elenco": verdetti,
    }


def blocco_strumenti() -> dict:
    return {"voci": [
        {"nome": "Fake checker", "dove": "/fake-checker/",
         "cosa": "I verdetti su ditte, prodotti e venditori. Punteggio, fonti, permalink."},
        {"nome": "BRAINDANCE", "dove": "/braindance/",
         "cosa": "Le verifiche su persone pubbliche e notizie. La stanza già dichiarata attiva."},
        {"nome": "Chiedi una verifica", "dove": "/braindance/chiedi/",
         "cosa": "Il modulo: apre una richiesta in coda. Su repo privato lo usi solo tu."},
        {"nome": "Regia", "dove": "/regia/",
         "cosa": "La plancia cifrata: stato del sistema e i diciotto comandi ai caposquadra."},
        {"nome": "Commessa", "dove": "/schede/commessa.html",
         "cosa": "Il modulo per aprire una commessa e mandarla alla RONDA."},
        {"nome": "Schede", "dove": "/schede/",
         "cosa": "I documenti: competenze, termini e consenso, consiglio."},
        {"nome": "Verifica card", "dove": "/v/SYS-00/",
         "cosa": "La rotta corta stampata sul QR delle carte giocatore."},
    ]}


def blocco_chiavi() -> dict:
    """Il registro delle chiavi: NOMI e STATO, mai valori. Mai."""
    return {
        "regola": "Qui non c'è nessun valore, e non deve entrarcene mai uno. "
                  "Solo il nome della chiave, a cosa serve e dove vive.",
        "voci": [
            {"nome": "systema77.regia", "serve": "Aprire questa porta e la plancia /regia/",
             "vive": "Portachiavi del Mac", "stato": "attiva"},
            {"nome": "ANTHROPIC_API_KEY", "serve": "L'automazione dei verdetti (GitHub Actions)",
             "vive": "GitHub → Settings → Secrets → Actions", "stato": "da verificare col workflow «Prova della chiave»"},
        ],
        "comandi": [
            {"cosa": "Leggere una chiave dal Portachiavi",
             "come": "bash squadra/chiavi.sh leggi regia"},
            {"cosa": "Metterne una nuova (il valore si prende dagli appunti, poi si puliscono)",
             "come": "bash squadra/chiavi.sh setta <nome>"},
            {"cosa": "Vedere l'elenco (nomi, mai valori)",
             "come": "bash squadra/chiavi.sh lista"},
            {"cosa": "Rigenerare questa porta dopo una modifica",
             "come": "python3 scripts/build_porta.py"},
            {"cosa": "Rigenerare la plancia /regia/",
             "come": "python3 scripts/build_regia.py"},
        ],
    }


def blocco_squadra() -> dict:
    """CHI FA COSA — letto dai file veri, mai scritto a mano.

    Nasce da una domanda del Direttore (30/08): «l'agenzia è enorme e gli agenti
    girano poco, alcuni fermi da settimane; vorrei visione di chi fa cosa».
    Misurata, l'agenzia NON è enorme: gli agenti che esistono davvero sono
    quelli che hanno un file in `.claude/agents/`. Tutto il resto sono POSTI
    SULLA CARTA — mansioni descritte in una pagina di competenze, mai diventate
    un agente. Un posto sulla carta non può essere «fermo da settimane»: non è
    mai partito. Tenere le due colonne separate è tutto il senso di questo
    blocco, ed è il motivo per cui si genera dai file invece di ricopiarli:
    una tabella scritta a mano invecchia in silenzio, questa no.
    """
    veri = []
    cartella = os.path.join(ROOT, ".claude", "agents")
    for nome in sorted(os.listdir(cartella)) if os.path.isdir(cartella) else []:
        if not nome.endswith(".md"):
            continue
        percorso = os.path.join(cartella, nome)
        with open(percorso, encoding="utf-8") as f:
            testo = f.read()
        m = re.match(r"---\n(.*?)\n---\n", testo, re.S)
        testa = m.group(1) if m else ""
        def campo(k, default=""):
            r = re.search(rf"^{k}:\s*(.+)$", testa, re.M)
            return r.group(1).strip() if r else default
        desc = campo("description")
        mestiere = _mestiere(desc)
        sigla = campo("name", nome[:-3])
        # A chi risponde: i caposquadra a D.R.A.G.O.; gli specialisti al proprio
        # caposquadra, nominato nella descrizione («sotto JUDY», «di SQUELCH»).
        capo = "D.R.A.G.O."
        if "caposquadra" not in desc.lower():
            for c in ("JUDY", "SQUELCH", "ECHO", "KIROSHI", "BRAINDANCE"):
                if re.search(rf"\b(sotto|di)\s+{c}\b", desc):
                    capo = c
                    break
        nato = _prima_data(percorso)
        veri.append({
            "sigla": sigla.upper(),
            "mestiere": mestiere,
            "modello": campo("model", "?"),
            "grado": "caposquadra" if capo == "D.R.A.G.O." else "specialista",
            "capo": capo,
            "nato": nato,
        })

    carta = _posti_sulla_carta()
    n_capi = len([a for a in veri if a["grado"] == "caposquadra"])
    n_spec = len(veri) - n_capi
    return {
        "cifre": [
            {"n": len(veri), "etichetta": f"agenti veri ({n_capi} capi + {n_spec} specialisti)"},
            {"n": len(carta), "etichetta": "posti sulla carta, mai nati"},
        ],
        "veri": veri,
        "carta": carta,
        "nota": "Un agente esiste se ha un file in .claude/agents/: quello lo rende "
                "chiamabile. I posti sulla carta sono mansioni descritte in una pagina "
                "di competenze e mai diventate un agente — non sono «fermi da settimane», "
                "non sono mai partiti. Questa tabella si rigenera dai file: se qualcuno "
                "nasce o muore, cambia da sola.",
    }


def _mestiere(desc: str) -> str:
    """Una riga sola dalla descrizione dell'agente.

    La descrizione è scritta per far scegliere l'agente a chi dispaccia, quindi
    dice già la cosa giusta — ma è lunga. Si accorcia in quest'ordine, fermandosi
    appena sta in una riga di tabella: prima frase → testa prima del trattone →
    via le parentesi → taglio netto. Non si riscrive a mano: una riga ricopiata
    diverge dal file il giorno in cui il file cambia, e nessuno se ne accorge.
    """
    LIMITE = 92
    m = re.split(r"\.\s+(?=[A-Z«])", desc)[0].strip().rstrip(".")
    if len(m) > LIMITE and " — " in m:
        testa = m.split(" — ")[0].strip()
        if len(testa) > 20:
            m = testa
    if len(m) > LIMITE:
        senza = re.sub(r"\s*\([^)]*\)", "", m).strip().rstrip(",;—- ")
        if 20 < len(senza) < len(m):
            m = senza
    return m if len(m) <= LIMITE else m[:LIMITE - 3].rstrip(" ,;—-") + "…"


def _prima_data(percorso: str) -> str:
    """Il giorno del primo commit che ha creato il file. Se git non risponde
    (albero non versionato, storia troncata), si dice «?» invece di inventare."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%ad", "--date=short", "-1", "--", percorso],
            cwd=ROOT, capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or "?"
    except Exception:
        return "?"


def _posti_sulla_carta() -> list:
    """Legge la tabella «Censiti, non ancora attivabili» di squadra/SQUADRA.md.
    È l'elenco delle mansioni che esistono su una pagina e non come agente."""
    percorso = os.path.join(ROOT, "squadra", "SQUADRA.md")
    if not os.path.exists(percorso):
        return []
    with open(percorso, encoding="utf-8") as f:
        testo = f.read()
    # Il titolo di quella sezione è già cambiato una volta (era «Censiti, non
    # ancora attivabili»): si accettano entrambe le forme, così un ritocco al
    # testo non fa sparire in silenzio mezza tabella dalla porta.
    m = re.search(r"##\s*(?:Censiti|Posti sulla carta)[^\n]*\n(.*?)(?=\n##\s|\Z)",
                  testo, re.S)
    if not m:
        return []
    voci = []
    for riga in m.group(1).splitlines():
        celle = [c.strip() for c in riga.strip().strip("|").split("|")]
        if len(celle) < 3 or celle[0].startswith("---") or celle[0] == "Agente":
            continue
        voci.append({
            "nome": re.sub(r"\*\*", "", celle[0]),
            "posto": celle[1],
            "fonte": re.sub(r"`", "", celle[2]),
        })
    return voci


def blocco_note() -> dict:
    return {"voci": [
        "cyberboomer.io è il banco di lavoro del Direttore: officina privata, non vetrina. "
        "I giocatori stanno su animagame.io, i clienti su systema77.com.",
        "Questa porta cifra ciò che tiene dentro. Le singole pagine restano raggiungibili "
        "da chi ne indovina l'indirizzo finché il repo è pubblico: quel pezzo lo chiude "
        "Cloudflare Access, non questa pagina.",
        "Un limite verificato una volta ha una data di scadenza: quando una regola dice "
        "«non si può», si riprova prima di obbedirle.",
    ]}


# ── payload ──────────────────────────────────────────────────────────────────
def payload_esistente(html: str):
    m = re.search(rf'<script[^>]*id="{SEGNO}"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1).strip())
    except json.JSONDecodeError:
        return None


def costruisci_payload(blocchi: dict, frase: str, vecchio, salt_nuovo: bool) -> dict:
    """Il sale si riusa se la frase non è cambiata: così una ricostruzione senza
    modifiche non produce un diff inutile."""
    salt = os.urandom(16)
    if vecchio and not salt_nuovo:
        try:
            salt_vecchio = base64.b64decode(vecchio["salt"])
            chiave_prova = deriva(frase, salt_vecchio)
            primo = vecchio["blocchi"][0]
            aesgcm_puro.decifra(chiave_prova,
                                base64.b64decode(primo["iv"]),
                                base64.b64decode(primo["d"]))
            salt = salt_vecchio          # la frase è la stessa: sale riusato
            print("· sale riusato dal payload esistente")
        except Exception:
            print("· frase cambiata o payload alterato: sale e blocchi rifatti")

    chiave = deriva(frase, salt)
    fuori = []
    for nome, dati in blocchi.items():
        chiaro = json.dumps({"nome": nome, "dati": dati}, ensure_ascii=False).encode("utf-8")
        iv = os.urandom(12)
        fuori.append({"iv": b64(iv), "d": b64(aesgcm_puro.cifra(chiave, iv, chiaro))})
    return {"v": 1, "cifra": "AES-GCM-256", "kdf": "PBKDF2-SHA256",
            "iter": ITERAZIONI, "salt": b64(salt), "blocchi": fuori}


# ── la pagina ────────────────────────────────────────────────────────────────
def pagina(payload: dict) -> str:
    p = json.dumps(payload, indent=1, ensure_ascii=False)
    return PAGINA.replace("{{PAYLOAD}}", p).replace("{{DATA}}", date.today().isoformat())


PAGINA = r"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<meta http-equiv="Content-Security-Policy"
      content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; form-action 'none'; base-uri 'none'">
<title>◉</title>
<style>
:root{--sf:#070a0f;--pan:#0d141d;--bor:#1e2a38;--txt:#d7e3ef;--dim:#7d93a8;--cia:#22d3ee;--ver:#2ee6a6;--gia:#f6c453;--ros:#ff6b6b}
*{box-sizing:border-box}
body{margin:0;background:var(--sf);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:15px;line-height:1.6}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace}

/* ── la porta ── */
#porta{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px;gap:22px}
#porta .marchio{font-family:ui-monospace,Menlo,monospace;font-size:30px;letter-spacing:.3em;color:var(--cia);text-indent:.3em}
#porta .sotto{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--dim);text-align:center}
#modulo{display:flex;flex-direction:column;gap:10px;width:100%;max-width:330px}
#frase{width:100%;background:var(--pan);border:1px solid var(--bor);border-radius:7px;padding:13px 15px;color:var(--txt);font-family:ui-monospace,Menlo,monospace;font-size:15px;text-align:center;letter-spacing:.04em}
#frase:focus{outline:none;border-color:var(--cia);box-shadow:0 0 0 3px rgba(34,211,238,.1)}
#apri{background:transparent;border:1px solid var(--cia);color:var(--cia);font-family:ui-monospace,Menlo,monospace;font-size:11.5px;letter-spacing:.18em;text-transform:uppercase;padding:12px;border-radius:7px;cursor:pointer}
#apri:hover:not(:disabled){background:var(--cia);color:var(--sf)}
#apri:disabled{opacity:.5;cursor:wait}
#esito{min-height:19px;font-family:ui-monospace,Menlo,monospace;font-size:11.5px;text-align:center;color:var(--ros)}
#esito.lavora{color:var(--dim)}

/* ── il banco ── */
#banco{max-width:820px;margin:0 auto;padding:20px 16px 40px}
.testa{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;border-bottom:1px solid var(--bor);padding-bottom:11px;margin-bottom:8px}
.testa h1{font-family:ui-monospace,Menlo,monospace;font-size:15px;letter-spacing:.16em;color:var(--cia);margin:0;text-transform:uppercase}
#chiudi{background:transparent;border:1px solid var(--bor);color:var(--dim);font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.14em;text-transform:uppercase;padding:5px 11px;border-radius:5px;cursor:pointer}
#chiudi:hover{border-color:var(--ros);color:var(--ros)}
h2{font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--dim);margin:30px 0 10px;border-bottom:1px solid var(--bor);padding-bottom:5px}
a{color:var(--cia);text-decoration:none;border-bottom:1px solid rgba(34,211,238,.25)}
a:hover{border-bottom-color:var(--cia)}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}
.att{background:var(--pan);border:1px solid var(--bor);border-radius:9px;padding:13px 15px}
.att .n{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;letter-spacing:.06em;color:var(--cia);margin-bottom:5px}
.att .c{font-size:13px;color:var(--dim);line-height:1.5}
.riga{display:flex;gap:11px;align-items:baseline;padding:7px 0;border-bottom:1px solid rgba(30,42,56,.55);font-size:13.5px;flex-wrap:wrap}
.riga:last-child{border-bottom:none}
.id{font-family:ui-monospace,Menlo,monospace;color:var(--cia);font-size:12px;min-width:34px}
.eta{font-family:ui-monospace,Menlo,monospace;font-size:11px;margin-left:auto;white-space:nowrap}
.fresco{color:var(--ver)}.medio{color:var(--gia)}.vecchio{color:var(--ros)}
.cif{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:12px 0}
.cif div{background:var(--pan);border:1px solid var(--bor);border-radius:9px;padding:12px 14px}
.cif b{display:block;font-family:ui-monospace,Menlo,monospace;font-size:23px;color:var(--cia);line-height:1.2}
.cif span{font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--dim)}
.avv{border-left:2px solid var(--gia);background:rgba(246,196,83,.06);padding:10px 14px;margin:12px 0;border-radius:0 8px 8px 0;font-size:13.5px}
.cmd{background:var(--pan);border:1px solid var(--bor);border-radius:8px;padding:10px 13px;margin:8px 0}
.cmd .q{font-size:12.5px;color:var(--dim);margin-bottom:5px}
.cmd code{display:block;font-family:ui-monospace,Menlo,monospace;font-size:12.5px;color:var(--ver);word-break:break-all}
/* Misurato il 30/08 a 390px: il ruolino della squadra sfondava di 92px e
   faceva scorrere TUTTA la pagina di lato — sul telefono del Direttore
   ogni riga finiva storta. La tabella scorre dentro il suo riquadro. */
.scorre{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:10px 0}
.scorre table{margin:0;min-width:520px}
table{border-collapse:collapse;width:100%;font-size:13px;margin:10px 0}
th,td{border:1px solid var(--bor);padding:7px 9px;text-align:left;vertical-align:top}
th{color:var(--cia);font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase;font-weight:400}
.pie{margin-top:32px;padding-top:12px;border-top:1px solid var(--bor);font-family:ui-monospace,Menlo,monospace;font-size:9.5px;color:#4a5a6b;letter-spacing:.09em;line-height:1.8}
</style>
</head>
<body>

<div id="porta">
  <div class="marchio">◉</div>
  <div class="sotto">banco di lavoro · accesso riservato</div>
  <div id="modulo">
    <input id="frase" type="password" autocomplete="off" autocapitalize="off"
           autocorrect="off" spellcheck="false" placeholder="frase di sblocco" aria-label="frase di sblocco">
    <button id="apri" type="button">apri</button>
    <div id="esito" role="status" aria-live="polite"></div>
  </div>
</div>

<div id="banco" hidden></div>

<script type="application/json" id="PORTA_PAYLOAD">
{{PAYLOAD}}
</script>

<script>
/*
  COSA FA — chiede la frase, deriva la chiave (PBKDF2-SHA256, 210.000 giri) e
    decifra i blocchi AES-GCM incorporati qui sopra. Se la frase è sbagliata,
    GCM non autentica e non esce niente: non c'è un «quasi giusto».
  FIN DOVE ARRIVA — protegge QUESTO contenuto. Non protegge le pagine che
    elenca: quelle restano raggiungibili da chi ne indovina l'indirizzo finché
    il repo è pubblico. Serratura qui, tenda là — ed è scritto anche in pagina.
  ZERO RETE — la CSP vieta ogni connessione. Niente esce da questa pagina.
*/
(function () {
  'use strict';
  var ITER_MINIME = 200000;   // un payload più debole è rotto o riscritto
  var $ = function (id) { return document.getElementById(id); };
  var porta = $('porta'), banco = $('banco'), campo = $('frase'),
      bottone = $('apri'), esito = $('esito');

  function b64(s) {
    var g = atob(s), a = new Uint8Array(g.length);
    for (var i = 0; i < g.length; i++) a[i] = g.charCodeAt(i);
    return a;
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  var payload = null;
  try {
    var tag = document.getElementById('PORTA_PAYLOAD');
    payload = tag ? JSON.parse(tag.textContent) : null;
  } catch (e) { payload = null; }

  function guasto(m) { esito.className = ''; esito.textContent = m; }

  if (!payload || payload.v !== 1 || !payload.blocchi || !payload.blocchi.length) {
    guasto('porta non generata: manca il contenuto cifrato');
    bottone.disabled = true;
  } else if (!(payload.iter >= ITER_MINIME)) {
    guasto('derivazione troppo debole: payload non attendibile');
    bottone.disabled = true;
  }

  async function apri() {
    var frase = campo.value;
    if (!frase) { guasto('serve la frase'); campo.focus(); return; }
    bottone.disabled = true;
    esito.className = 'lavora';
    esito.textContent = 'apro…';
    await new Promise(function (r) { setTimeout(r, 20); });   // lascia dipingere

    try {
      var base = await crypto.subtle.importKey('raw', new TextEncoder().encode(frase),
                                               'PBKDF2', false, ['deriveKey']);
      var chiave = await crypto.subtle.deriveKey(
        { name: 'PBKDF2', salt: b64(payload.salt), iterations: payload.iter, hash: 'SHA-256' },
        base, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);

      var dati = {};
      for (var i = 0; i < payload.blocchi.length; i++) {
        var b = payload.blocchi[i];
        var chiaro = await crypto.subtle.decrypt(
          { name: 'AES-GCM', iv: b64(b.iv) }, chiave, b64(b.d));
        var o = JSON.parse(new TextDecoder().decode(chiaro));
        dati[o.nome] = o.dati;
      }
      campo.value = '';
      mostra(dati);
    } catch (e) {
      // Messaggio unico: frase sbagliata e payload manomesso danno lo stesso
      // esito, e distinguerli in pagina aiuterebbe solo chi prova a indovinare.
      guasto('non si apre');
      bottone.disabled = false;
      campo.focus();
      campo.select();
    }
  }

  function classeEta(g) { return g == null ? '' : g > 21 ? 'vecchio' : g > 7 ? 'medio' : 'fresco'; }

  function mostra(d) {
    var h = '';
    h += '<div class="testa"><h1>◉ banco di lavoro</h1>'
       + '<button id="chiudi" type="button">chiudi</button></div>';

    var s = d.stato || {};
    // Numeri E etichette vengono dal cifrato: il modello di pagina non nomina
    // nulla del sistema, così a lucchetto chiuso non c'è niente da leggere.
    h += '<div class="cif">';
    (s.cifre || []).forEach(function (c) {
      h += '<div><b>' + esc(c.n) + '</b><span>' + esc(c.etichetta) + '</span></div>';
    });
    h += '</div>';

    if ((s.da_riverificare || []).length) {
      h += '<div class="avv"><b>Invecchiati oltre tre settimane.</b> Dodici giorni sono bastati, '
         + 'una volta, a rendere da correggere due verdetti su tre.<br>'
         + s.da_riverificare.map(esc).join('<br>') + '</div>';
    }

    h += '<h2>Strumenti</h2><div class="griglia">';
    ((d.strumenti || {}).voci || []).forEach(function (v) {
      h += '<div class="att"><div class="n"><a href="' + esc(v.dove) + '">' + esc(v.nome) + ' →</a></div>'
         + '<div class="c">' + esc(v.cosa) + '</div></div>';
    });
    h += '</div>';

    h += '<h2>Verdetti pubblicati</h2>';
    (s.elenco || []).forEach(function (v) {
      h += '<div class="riga"><span class="id">' + esc(v.id) + '</span>'
         + '<span>' + esc(v.titolo) + '</span>'
         + '<span class="eta ' + classeEta(v.eta) + '">'
         + esc(v.data) + (v.eta == null ? '' : ' · ' + v.eta + 'g') + '</span></div>';
    });

    var k = d.chiavi || {};
    h += '<h2>Chiavi</h2>';
    h += '<div class="avv">' + esc(k.regola) + '</div>';
    h += '<div class="scorre">';
    h += '<table><tr><th>Chiave</th><th>A cosa serve</th><th>Dove vive</th><th>Stato</th></tr>';
    (k.voci || []).forEach(function (v) {
      h += '<tr><td class="mono">' + esc(v.nome) + '</td><td>' + esc(v.serve)
         + '</td><td>' + esc(v.vive) + '</td><td>' + esc(v.stato) + '</td></tr>';
    });
    h += '</table></div>';
    (k.comandi || []).forEach(function (c) {
      h += '<div class="cmd"><div class="q">' + esc(c.cosa) + '</div><code>' + esc(c.come) + '</code></div>';
    });

    // CHI FA COSA — due colonne che non vanno confuse: chi esiste come agente
    // chiamabile, e chi è solo una mansione scritta su una pagina.
    var q = d.squadra || {};
    h += '<h2>Chi fa cosa</h2>';
    h += '<div class="cif">';
    (q.cifre || []).forEach(function (c) {
      h += '<div><b>' + esc(c.n) + '</b><span>' + esc(c.etichetta) + '</span></div>';
    });
    h += '</div>';
    h += '<div class="scorre">';
    h += '<table><tr><th>Agente</th><th>Mestiere</th><th>Risponde a</th><th>Modello</th><th>Dal</th></tr>';
    (q.veri || []).forEach(function (a) {
      h += '<tr><td class="mono">' + esc(a.sigla) + '</td><td>' + esc(a.mestiere)
         + '</td><td>' + esc(a.capo) + '</td><td class="mono">' + esc(a.modello)
         + '</td><td class="mono">' + esc(a.nato) + '</td></tr>';
    });
    h += '</table></div>';
    if ((q.carta || []).length) {
      h += '<div class="avv"><b>Posti sulla carta.</b> Mansioni descritte in una pagina '
         + 'di competenze e mai diventate un agente: non sono fermi, non sono mai partiti. '
         + 'Diventano veri solo con un file in .claude/agents/.</div>';
      h += '<div class="scorre">';
      h += '<table><tr><th>Posto</th><th>Mansione</th><th>Dove è scritto</th></tr>';
      (q.carta || []).forEach(function (a) {
        h += '<tr><td class="mono">' + esc(a.nome) + '</td><td>' + esc(a.posto)
           + '</td><td class="mono">' + esc(a.fonte) + '</td></tr>';
      });
      h += '</table></div>';
    }
    h += '<div class="avv">' + esc(q.nota) + '</div>';

    h += '<h2>Da ricordare</h2>';
    ((d.note || {}).voci || []).forEach(function (n) { h += '<div class="avv">' + esc(n) + '</div>'; });

    h += '<div class="pie">stato generato il ' + esc(s.generato) + ' da scripts/build_porta.py<br>'
       + 'la porta cifra questo contenuto; le pagine che elenca restano raggiungibili<br>'
       + 'da chi ne indovina l\'indirizzo finché il repo è pubblico</div>';

    banco.innerHTML = h;
    porta.hidden = true;
    banco.hidden = false;
    document.getElementById('chiudi').addEventListener('click', chiudi);
    window.scrollTo(0, 0);
  }

  function chiudi() {
    // Chiudere deve svuotare davvero: il DOM decifrato non resta in memoria.
    banco.innerHTML = '';
    banco.hidden = true;
    porta.hidden = false;
    esito.textContent = '';
    bottone.disabled = false;
    campo.value = '';
    campo.focus();
  }

  // Il click E l'Invio: la CSP vieta l'azione di un <form>, e il browser
  // blocca l'invio prima dell'evento — quindi il gesto passa da qui.
  bottone.addEventListener('click', apri);
  campo.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); apri(); }
  });
  campo.focus();
})();
</script>
</body>
</html>
"""


def main() -> None:
    salt_nuovo = "--salt-nuovo" in sys.argv
    frase = passphrase()

    verdetti = leggi_verdetti()
    blocchi = {
        "stato": blocco_stato(verdetti),
        "strumenti": blocco_strumenti(),
        "chiavi": blocco_chiavi(),
        "squadra": blocco_squadra(),
        "note": blocco_note(),
    }

    vecchio = None
    if os.path.exists(USCITA):
        with open(USCITA, encoding="utf-8") as f:
            vecchio = payload_esistente(f.read())

    payload = costruisci_payload(blocchi, frase, vecchio, salt_nuovo)

    # Guardia: a lucchetto chiuso nessuna parola del contenuto deve essere
    # leggibile. Si toglie dalla pagina il blocco cifrato e si cerca nel resto:
    # se una spia compare lì, sta in chiaro e non si pubblica.
    html = pagina(payload)
    spie = ["fake-checker", "braindance", "systema77.regia", "ANTHROPIC_API_KEY", "Portachiavi",
        # Dal 30/08 la porta porta anche il ruolino della squadra: le sigle
        # degli agenti sono nomi interni e non stanno in piazza (CLAUDE.md:
        # «nessun nome di agente in vetrina»).
        "SQUELCH", "KIROSHI", "collaudo-superfici", "provino"]
    visibili = [s for s in spie if s in re.sub(
        rf'<script[^>]*id="{SEGNO}"[^>]*>.*?</script>', "", html, flags=re.S)]
    if visibili:
        raise SystemExit(f"✗ a lucchetto chiuso si leggono ancora: {visibili}. Non pubblico.")

    with open(USCITA, "w", encoding="utf-8") as f:
        f.write(html)

    vecchi = len(blocchi["stato"]["da_riverificare"])
    print(f"✓ {os.path.relpath(USCITA, ROOT)} — {len(payload['blocchi'])} blocchi cifrati, "
          f"{len(html)} byte")
    print(f"  {len(verdetti)} verdetti · {vecchi} da riverificare · "
          f"{ITERAZIONI:,} iterazioni PBKDF2".replace(",", "."))
    sq = blocchi["squadra"]
    print(f"  {len(sq['veri'])} agenti veri · {len(sq['carta'])} posti sulla carta")
    print("  nessuna parola spia visibile a lucchetto chiuso (controllato)")


if __name__ == "__main__":
    main()
