# KIROSHI — fake checker

> "Scansiona una cosa e ti dice se è vera o è una minaccia."
> Nome dagli impianti oculari di Cyberpunk 2077 (contesto metaforico di ROOT_CLODE).
> Agente figlio di D.R.A.G.O. (dispatch). Scopato a questa cartella.

Mandi un **link** o **scrivi una voce** dal telefono, KIROSHI ricerca sul web e
ti risponde: **è vero o è falso? Ci si può fidare?** — con un punteggio di
affidabilità **0-100** e le fonti che lo giustificano.

---

## Come funziona (architettura v0.1)

```
  Telefono                GitHub                          Claude API
 ┌─────────┐   apri     ┌──────────────────┐   trigger  ┌──────────────┐
 │ app     │  issue     │ GitHub Actions   │──────────▶ │ Claude +     │
 │ GitHub  │──────────▶ │ (kiroshi.yml)    │            │ web_search   │
 └─────────┘            └──────────────────┘            └──────┬───────┘
      ▲                        │  scrive                       │ verdetto
      │  commento con          │  docs/data/NNNN.json          │ (JSON)
      │  il verdetto  ◀────────┴───────────────────────────────┘
      │
 ┌─────────────────────────────────────────┐
 │ Dashboard (GitHub Pages, /docs)          │
 │ gauge · grafo delle fonti · timeline     │
 └─────────────────────────────────────────┘
```

Nessun server sempre acceso. Tutto vive nel repo: gratis nei limiti di GitHub
Actions + il costo delle chiamate API di Claude (poche frazioni di dollaro a
verifica).

### Le due modalità
- **rapida** (default): 1-2 minuti, fonti principali.
- **scava**: indagine profonda (fonti primarie, cross-check, reputazione del
  venditore). Attivala scrivendo `scava` nel corpo della issue, o mettendo
  l'etichetta `scava`.

### Il verdetto
Punteggio **0-100** + motivazione + **red/green flags** + fonti linkate.
Onesto per costruzione: quasi nulla è 100% vero o 100% falso.

---

## Setup su GitHub (una volta sola)

1. **Crea il repo** e caricaci questa cartella (`kiroshi-fake-checker`).
2. **Aggiungi il segreto** `ANTHROPIC_API_KEY`
   in *Settings → Secrets and variables → Actions → New repository secret*.
   (La chiave si genera su console.anthropic.com — è l'unica cosa che serve.)
3. **Attiva GitHub Pages** su *Settings → Pages → Source: Deploy from a branch →
   `main` / `/docs`*. La dashboard sarà su `https://<utente>.github.io/<repo>/`.
4. **Dai i permessi di scrittura alle Action**:
   *Settings → Actions → General → Workflow permissions → Read and write*.

Fatto. Da qui in poi funziona da solo.

## Come si usa (dal telefono)

1. App GitHub → questo repo → **Issues → New issue** → template *"Verifica KIROSHI"*.
2. Incolli il link o scrivi la voce da controllare. (Aggiungi `scava` per la modalità profonda.)
3. Aspetti ~1-2 minuti: KIROSHI risponde nel commento e aggiorna la dashboard.

> ⚠️ **Sicurezza malware:** KIROSHI non apre, non scarica e non esegue mai i
> link. Li tratta solo come testo da analizzare. Un link malevolo per lui è
> inerte. Sei protetto per costruzione, non per fortuna.

---

## Struttura del progetto

| Percorso | Cosa contiene |
|---|---|
| `.github/workflows/kiroshi.yml` | La GitHub Action che orchestra tutto |
| `.github/ISSUE_TEMPLATE/verifica.md` | Il modulo della issue dal telefono |
| `scripts/kiroshi_check.py` | Il motore: chiama Claude+web_search, produce il verdetto |
| `prompts/kiroshi-verifica.md` | Le istruzioni che il motore passa a Claude |
| `docs/index.html` | La dashboard (gauge, grafo fonti, timeline) |
| `docs/data/NNNN-*.json` | I verdetti salvati (uno per verifica, record leggibile) |
| `docs/data/db.js` | Bundle rigenerato a ogni verifica; la dashboard lo carica via `<script>` (niente fetch, si apre anche in locale) |
| `report/` | I report di chiusura leggibili dall'umano |

---

*Questo è uno scheletro v0.1 pensato per essere iterato con Claude. Vedi
`report/0001-sway-audima.md` per il primo caso reale. La dashboard si apre
anche con doppio clic (`docs/index.html`); per riprodurre l'ambiente Pages usa
`python3 -m http.server` dentro `docs/`.*

— creato da KIROSHI, 2026-07-09
