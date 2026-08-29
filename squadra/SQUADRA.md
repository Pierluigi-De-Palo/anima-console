# LA SQUADRA — organigramma operativo di SYSTEMA 77

L'identità dei caposquadra vive in **file versionati** (`.claude/agents/*.md`), non
nella memoria delle chat: è questo che pensiona il testimone. Ogni riga qui sotto è
citata dai file dei 5 repo (ricognizione del 2026-08-17); dove i file canonici del
Mac non sono visibili, lo si dice.

## Caposquadra attivi (roster v1 — decisione del Direttore, 17/08)

| Caposquadra | Dipartimento | File-persona | Modello |
|---|---|---|---|
| **JUDY** | Comunicazione / Design — Camera Oscura, SOLCO, «il colore segue il mestiere della stanza» (`CLAUDE.md:75`) | `.claude/agents/judy.md` | sonnet |
| **KIROSHI//OR** | Verità — ditte / prodotti / venditori (Standard KIROSHI v1; arcano VIII · La Giustizia, `systema77-site/bilancia.html:67`) | `.claude/agents/kiroshi.md` | sonnet |
| **BRAINDANCE//CODE** | Verità — persone + notizie/claim (accordo di confine 2026-07-12: proposta `DA-BRAINDANCE-accordo-confine.md`, ratifica registrata in `CLAUDE.md`) | `.claude/agents/braindance.md` | sonnet |
| **SQUELCH** | Tecnica / Backend — backend e guardia privacy (`animagame-site/README.md:17-20`); Worker (`animagame-site/assets/config.js:6`) | `.claude/agents/squelch.md` | opus |
| **ECHO** | Ripresa / Output — voce e testi, tagli per canale (`competenze-v1.1.html:95-99`, dove il dept si chiama «Output / Dispatch») | `.claude/agents/echo.md` | sonnet |

Il Dipartimento Verità ha **due** caposquadra (KIROSHI e BRAINDANCE) perché il
confine è per **oggetto**, non per gerarchia: ditta/venditore → KIROSHI
(«prodotti» inclusi: prassi coerente a valle dell'accordo, registrata qui da
D.R.A.G.O. il 2026-08-18); persona o notizia/claim → BRAINDANCE (il filtro
pubblica/privata lo applica BRAINDANCE: sui privati non lavora nessuno);
notizia su un'azienda → BRAINDANCE con dati-ditta da KIROSHI; imprenditore:
persona → BRAINDANCE, impresa → KIROSHI (accordo ratificato 2026-07-12).

**Porta d'ingresso: sempre D.R.A.G.O.** (decisione del Direttore, 17/08). La
commessa arriva a lui, il dispatch segue `squadra/PROTOCOLLO-DISPATCH.md`.

## Vertice e dispatch

- **IL DIRETTORE** (carta 0 · OVERLORD) — ordina, ratifica, decide colori e
  lessico; non gioca (`animagame-site/index.html:380-383`). Niente diventa
  pubblico senza la sua ratifica; il push resta suo, dal Mac.
- **IL RE** — emette missioni (`docs/braindance/schede/piante-sofferenza-sillogismo.html:56`);
  il rapporto RE↔Direttore non è chiarito da nessun file (dichiarato, non dedotto).
- **D.R.A.G.O.** — dispatch e fixer: instrada, registra gli accordi
  (`DA-BRAINDANCE-accordo-confine.md:27`), convoca il Consiglio, tiene questo registro.

## Censiti, non ancora attivabili (posti veri, tool assenti in sandbox)

| Agente | Posto | Fonte |
|---|---|---|
| **CHRONO** | capo video (Veo · Kling · Runway · HeyGen) | `competenze-v1.1.html:70-73` |
| **SHUTTER** | fotografia fine-art + pipeline stampa (Printful); autorità su naming/cache | `competenze-v1.1.html:63-66`; `area2.js:7` |
| **FLUX** | fix images / time developer; casa `cyberboomer.ninja` | `competenze-v1.1.html:57-62`; la casa: commit `18df488` di cyberboomer-ninja-site («casa di FLUX») |
| **ROGUE** | domini e DNS, redirect col Direttore | `consiglio-animagame-2026-07-17.html:138`; `animagame-site/index.html:487` |
| **TBFIND** ×3 | montatore · VFX/motion · fonico (candidato TECHIE) | `competenze-v1.1.html:74-93` |

Citati una volta, ruolo non documentato: EDDIE, LED, A.R.K. (capi squadra al
Consiglio), SUONO (dottrina `.gitignore`), TRACE→CHROME (dedica-canzone, posto
prenotato). Non si inventano ruoli: quando il Direttore li definisce, entrano qui.

## Come si aggiunge un caposquadra (checklist)

1. Il Direttore ratifica nome, mestiere e confini (una riga per ciascuno).
2. Si scrive `.claude/agents/<nome>.md`: frontmatter (name, description con quando
   invocarlo, model secondo VMG, tools) + regole non negoziabili **citate dai canoni**, formato output, firma, checklist.
3. Riga nella tabella del roster qui sopra, con le fonti.
4. Smoke test: un subagent con quella persona su un compito piccolo e vero del suo mestiere.
5. Patch nel repo + registrazione di D.R.A.G.O. (questo file è il registro).

## Registro commesse

| # | Data | Commessa | Lotti / caposquadra | Esito |
|---|---|---|---|---|
| 0 | 2026-08-18 | Collaudo del sistema LA COMMESSA (cliente interno: il Direttore) | JUDY (canone su commessa.html) · KIROSHI (fact-check di questo file) · BRAINDANCE (confine nel protocollo) · SQUELCH (JS e guardia privacy) · ECHO (testo d'uso della scheda) | chiusa 18/08 — 5/5 in-persona, con prese vere: TRIAGE corretto (BRAINDANCE: «persone», non «persone pubbliche», + rotta imprenditore), denylist pubblica bonificata (SQUELCH: i nomi interni non stanno più nel sorgente), 3 citazioni integrate (KIROSHI, 93/100), testo d'uso riscritto (ECHO), canone conforme (JUDY) |

| 1 | 2026-08-18 | Automazione della catena (ordine diretto del Direttore): RONDA autonoma · filiera fascicoli NotebookLM · inventario ROOT_CLODE | D.R.A.G.O. (RONDA + modulo) · SQUELCH-stile (build_fascicolo.py, inventario_root_clode.sh) | consegnata 18/08 — Routine «RONDA D.R.A.G.O.» creata (spenta fino a push + etichetta `commessa`), bottone «Invia alla RONDA» sul modulo (guardia che respinge collaudata), fascicolo pilota trappole-digitali generato, script inventario collaudato su albero finto senza leak |

| 2 | 2026-08-19 | Console v2 del Direttore + casa delle chiavi + igiene segreti (ordine diretto) | D.R.A.G.O. (console, registro) · SQUELCH-stile (chiavi.sh, .gitignore ×3) | consegnata 19/08 — console v2 (telefono-first, code vive da API, zoo agenti pensionato) e REGISTRO-CHIAVI consegnati come file per il Mac (mai in repo); chiavi.sh collaudato con casi ostili; sezione Segreti chiusa su anima-console e .gitignore nuovi su ninja e solar. Censimento 5 repo: nessun valore segreto mai entrato in git |

## Registro commesse cliente (via D.R.A.G.O.//CLIENT — sigle, mai nomi)

| Sigla | Data | Traguardo | Stato | Prossimo passo |
|---|---|---|---|---|
| C-01 | 2026-08-19 | commessa ricevuta dal modulo | in triage presso //CLIENT | verdetto di fattibilità + preventivo al Direttore |

Segnalazioni aperte dalla commessa 0 (decide il Direttore):
- **Debito visivo di famiglia** (JUDY): la firma `.foot` in `#5a6b7d` (~3.4:1 di
  contrasto) sta sia in `commessa.html` sia in `competenze-v1.1.html` — o si
  corregge in tutta la famiglia con mandato, o resta debito dichiarato qui.
- **`docs/schede/consiglio-animagame-2026-07-17.html:131,135`** (SQUELCH): il
  verbale nomina in chiaro un nome di dato sensibile su superficie pubblica.
  Impianto altrui: segnalato, non toccato.

— creato da D.R.A.G.O., 2026-08-18
