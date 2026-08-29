# PROMPT DI CAMPAGNA — REGIA (dal 2026-08-21)

Tutti i prompt operativi della campagna che trasforma `cyberboomer.io` nella
sala di regia del sistema. Doppio aggancio, come vuole il Direttore: ogni
prompt vive **qui** (versionato, non si perde con la chat) e si **incolla**
dove serve. Le identità permanenti stanno altrove: i caposquadra in
`.claude/agents/*.md`, il gemello commerciale in `squadra/DRAGO-CLIENT.md`.

**L'assetto deciso il 21/08** — da tenere presente leggendo ogni prompt:

| Dominio | Ruolo | Registro | Motori |
|---|---|---|---|
| cyberboomer.io | regia + archivio dati | KIROSHI 2.0 (cyan macchina) | stanze di lavoro fuori |
| animagame.io | agenti per terze parti, viste di gioco | Anima Game (verde `#38E08A`) | dentro |
| systema77.com | solo output, nessun nome di agente | ACID | dentro |
| cyberboomer.ninja | la voce, divulgazione | blu link `#5C7CFF` | dentro |

Un solo archivio (`docs/data/` su cyberboomer.io), tre facciate. I giocatori non
devono mai incontrare GitHub: le richieste passano dal ponte (Worker).

---

## P1 · JUDY — KIROSHI 2.0 e i quattro registri
Consegna: token CSS riusabili + modelli (plancia, scheda-comando, card-verdetto
di gioco) + la decisione sulle schede che oggi parlano tre lingue.
Vive in: `squadra/CANONE-KIROSHI-2.md`.

## P2 · SQUELCH — cifratura, generatore, ponte, guardie
1. `docs/regia/index.html`: payload AES-GCM 256, PBKDF2 ≥200k, salt per build,
   IV per messaggio, sblocco ricordabile e dimenticabile. Passphrase mai in un
   file, in un commit, in un log.
2. `scripts/build_regia.py`: legge i file veri, scrive payload cifrato + dati
   pubblici. Passphrase da ambiente o da `chiavi.sh`, mai da riga di comando.
3. Il ponte (Worker su `api.cyberboomer.io`): riceve la richiesta e apre lui la
   voce in coda — GitHub sparisce dalla vista di giocatori e ospiti. Guardia
   privacy in ingresso, limite di frequenza, nessun dato personale conservato.
4. Guardie: `guardia_privacy.py` oltre `docs/`; chiudere le due fughe note
   (`area2.js` nomina il sottodominio nel commento che spiega di non farlo;
   `braindance/index.html:117` mostra un percorso interno all'utente).
5. Igiene: `.nojekyll`, `robots.txt`. *(fatto il 21/08)*

## P3 · ECHO — le parole della regia e del gioco
Strato pubblico della plancia · la porta cifrata · sei schede-comando con
microtesti di conferma · la riga di stato onesta. Nelle viste di gioco sono
vietate: forum, thread, feed, commenti, post, social, moderatori — e anche
issue, repo, commit, GitHub. Nessun numero non ratificato, nessuna promessa di
tempi.

## P4 · KIROSHI — arretrato, code, contatore
Verificare che 0005/0006/0007 siano ancora veri oggi (fonti raggiungibili, fatti
non invecchiati) · testi di chiusura per #13 e #15 col permalink · causa esatta
del contatore «Ultimo» fermo a «—» e correzione minima, senza numeri a mano.

## P5 · BRAINDANCE — archivio e coerenza
`archivio.js` rigenerato *(fatto il 21/08: 19 voci)* · schede senza firma, con
percorsi interni o orfane · quali reggono il passaggio alla vista di gioco.

## P6 · RONDA — aggiunte al prompt della Routine
> 1-bis. Leggi anche l'etichetta `regia`: sono i comandi premuti dalla plancia.
> Ognuno dice già a quale caposquadra va: instradalo e lavoralo come una
> commessa normale.
> [al punto 4] Dopo il push rigenera la plancia con
> `python3 scripts/build_regia.py` (passphrase dall'ambiente: se manca, salta e
> dillo nel report, non fallire), così lo stato che il Direttore legge dal
> telefono è sempre quello vero.

## P7 · D.R.A.G.O.//CLIENT — handoff C-01
Consegnare l'offerta C-01 v2.0 per la ratifica: verdetto di fattibilità privato,
preventivo con sforzi per voce e importi «— da ratificare», riga REGISTRO in
coda. Il prompt JUDY per logo/claim non lo esegue lui: JUDY è della casa.
Perimetro invariato: niente push, clienti per sigla.

## P8 · IGIENE del sito *(fatto il 21/08, commit `a2971bd`)*
Home → termini v1 · indice schede non più orfano · `archivio.js` rigenerato ·
ponte `/anima/` → animagame.io · `.nojekyll` · `robots.txt`.
Nota di ricognizione: le rotte storiche `/anima/verifica/<ID>/` esistono **solo**
per le carte stampate prima del cambio (SYS-00, SYS-01). Per SYS-02 e SYS-03 non
vanno create: lo script genera la rotta corta `/v/<ID>/`, ed è quella sul QR.

## P9 · ANIMA GAME stand-alone
Censire ogni punto in cui il gioco porta l'utente fuori casa (GitHub, raw,
issue) e sostituirlo col ponte · viste dei verdetti in stile gioco sui dati che
restano su cyberboomer.io · degradazione onesta se l'archivio è irraggiungibile:
mai una pagina rotta.

---

— creato da D.R.A.G.O., 2026-08-21 · su commessa del Direttore
