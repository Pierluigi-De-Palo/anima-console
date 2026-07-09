"""KIROSHI — motore di verifica.

Legge la issue (da variabili d'ambiente), chiama Claude con la ricerca web,
ottiene un verdetto JSON, lo salva in docs/data/ e prepara il commento per la
issue. Scheletro v0: minimale di proposito, da iterare.
"""

import json
import os
import re
import pathlib
import datetime
import anthropic

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data"
PROMPT = (ROOT / "prompts" / "kiroshi-verifica.md").read_text(encoding="utf-8")

issue_num = os.environ.get("ISSUE_NUMBER", "0")
issue_body = os.environ.get("ISSUE_BODY", "") or ""
issue_labels = os.environ.get("ISSUE_LABELS", "") or ""

# Modalità: "scava" se scritto nel corpo o presente come etichetta.
modalita = "scava" if ("scava" in issue_body.lower() or "scava" in issue_labels.lower()) else "rapida"

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

resp = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=4000,
    system=PROMPT,
    tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8 if modalita == "scava" else 4}],
    messages=[{
        "role": "user",
        "content": f"Modalità: {modalita}\n\nDa verificare:\n{issue_body}",
    }],
)

# Concateno il testo finale del modello ed estraggo il blocco JSON.
text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
match = re.search(r"\{.*\}", text, re.DOTALL)
if not match:
    raise SystemExit(f"Nessun JSON nel verdetto. Output:\n{text}")
verdetto = json.loads(match.group(0))
verdetto["issue"] = int(issue_num)
verdetto["data_verifica"] = datetime.date.today().isoformat()

# --- salvataggio: docs/data/NNNN.json (record) + rigenerazione bundle db.js ---
DATA.mkdir(parents=True, exist_ok=True)
slug = re.sub(r"[^a-z0-9]+", "-", verdetto.get("titolo", f"check-{issue_num}").lower()).strip("-")
fname = f"{int(issue_num):04d}-{slug}.json"
(DATA / fname).write_text(json.dumps(verdetto, ensure_ascii=False, indent=2), encoding="utf-8")

# Rigenero un unico bundle da tutti i verdetti salvati. La dashboard lo carica
# via <script> (niente fetch), così funziona anche aperta in locale.
checks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(DATA.glob("[0-9]*.json"))]
checks.sort(key=lambda c: c.get("issue", 0))
(DATA / "db.js").write_text(
    "window.KIROSHI_DB = " + json.dumps(checks, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)

# --- commento per la issue ---
emoji = {"affidabile": "🟢", "dubbio": "🟡", "falso": "🔴"}.get(verdetto.get("etichetta"), "⚪")
righe = [
    f"## {emoji} KIROSHI — {verdetto.get('punteggio')}/100 ({verdetto.get('etichetta')})",
    "",
    verdetto.get("verdetto", ""),
    "",
    "**A favore:** " + "; ".join(verdetto.get("green_flags", []) or ["—"]),
    "",
    "**Da tenere d'occhio:** " + "; ".join(verdetto.get("red_flags", []) or ["—"]),
    "",
    "**Fonti:**",
]
righe += [f"- [{f['titolo']}]({f['url']})" for f in verdetto.get("fonti", [])]
righe += ["", f"_Sicurezza:_ {verdetto.get('nota_sicurezza', 'n/d')}  ·  modalità: {modalita}", "", "— KIROSHI"]
(ROOT / "kiroshi_comment.md").write_text("\n".join(righe), encoding="utf-8")

print(f"OK: {fname} — {verdetto.get('punteggio')}/100")
