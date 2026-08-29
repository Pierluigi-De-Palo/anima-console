# PROMPT DI SVILUPPO — uno per agente (dal 2026-08-29)

I prompt della campagna che segue LA REGIA. Doppio aggancio come vuole il
Direttore: versionati qui, incollabili dove servono. Le identità permanenti
stanno in `.claude/agents/*.md` e in `squadra/DRAGO-CLIENT.md`; questi sono i
**lotti di lavoro**, aggiornati allo stato verificato del 29/08.

**L'assetto** (deciso il 29/08, non ridiscutere leggendo un prompt singolo):

| Dominio | Ruolo | Registro | Motori |
|---|---|---|---|
| cyberboomer.io | regia + archivio dati | KIROSHI 2.0 (cyan) | stanze di lavoro fuori |
| animagame.io | agenti per terze parti, viste di gioco | Anima Game (`#38E08A`) | dentro |
| systema77.com | solo output, nessun nome di agente | ACID | dentro |
| cyberboomer.ninja | la voce, divulgazione | blu `#5C7CFF` | dentro |

Un solo archivio (`docs/data/`), tre facciate. **I giocatori non devono mai
incontrare GitHub.**

---

## S1 · SQUELCH — IL PONTE (priorità massima: sblocca tre cose insieme)

```
Lotto SQUELCH — IL PONTE. È la commessa più importante aperta: costruita una
volta, serve tre canali (il gioco, la plancia, il futuro bot).

PERCHÉ ORA: oggi ogni richiesta dal web diventa una issue GitHub aperta
dall'utente stesso. Per il Direttore va bene; per un giocatore no — ordine
esplicito: «se i giocatori arrivano e trovano link che li portano su GitHub,
non è possibile». Serve un servizio che riceva la richiesta e apra lui la voce
in coda, così GitHub sparisce dalla vista.

COSTRUISCI un Worker Cloudflare su api.cyberboomer.io (il dominio è già acceso
per le card: NON toccare quella parte, aggiungi una rotta):
1. POST /richiesta — riceve {tipo, oggetto, domanda, canale} e apre l'issue con
   l'etichetta giusta (ditta/prodotto → kiroshi-queue; notizia/persona pubblica
   → braindance-queue; comando dalla plancia → regia; commessa → commessa).
   Risponde con l'esito, mai con l'URL di GitHub.
2. GUARDIA in ingresso, prima di tutto: la stessa dottrina di
   scripts/guardia_privacy.py — se il testo contiene un'intenzione riservata o
   un dato che non deve finire in pubblico, la richiesta viene RESPINTA con una
   spiegazione, non pubblicata. È l'incidente del form che ha creato la guardia:
   non ripeterlo dal lato server.
3. Limite di frequenza per indirizzo, e nessun dato personale conservato: il
   Worker è un passaggio, non un archivio.
4. Il token GitHub vive nell'ambiente del Worker. Nel codice non compare mai.
   Se manca, il servizio deve dire «non configurato» e non fingere.

CONSEGNA: codice del Worker, istruzioni di deploy passo per passo per il Mac,
e l'elenco esatto di cosa serve dal Direttore (quale token, con quali permessi
minimi — non chiedere più di quanto serve). Più il collaudo: una richiesta vera
che diventa una voce in coda, una richiesta ostile che viene respinta.

Nota: questa è la stessa infrastruttura della «verifica dal vivo» (fase 3 del
manuale) e del bot Slack L1. Costruiscila pensando a tutte e tre, esponi solo
quella che serve oggi.
```

## S2 · JUDY + ECHO — ANIMA GAME stand-alone

```
Lotto ANIMA GAME. Il gioco deve reggersi da solo: nessun link che porti fuori
casa, e i verdetti mostrati come parte del mondo, non come referti tecnici.

JUDY ha già consegnato il modello della card-verdetto di gioco in
squadra/CANONE-KIROSHI-2.md (sezione 3): verde su nero, mono=macchina,
serif=umano, un solo accento che cambia intensità e movimento — mai tinta —
per vero/incerto/falso. Partite da lì.

1. CENSIMENTO: ogni punto in cui animagame.io porta l'utente su GitHub, raw,
   issue o repo. Per ciascuno, la sostituzione (il ponte di S1 dove serve una
   richiesta, un link interno altrove).
2. LE VISTE: le pagine che mostrano i verdetti KIROSHI e BRAINDANCE ai
   giocatori, leggendo l'archivio che resta su cyberboomer.io. Un solo
   archivio, facciate diverse: non copiare i dati.
3. DEGRADAZIONE ONESTA: se l'archivio non risponde, cosa vede il giocatore?
   Mai una pagina rotta, mai un numero inventato: una frase che dice la verità.
4. ECHO scrive i testi. Vietate le parole del mestiere (issue, repo, commit,
   GitHub) e quelle già bandite nel gioco (forum, thread, feed, post, social,
   moderatori). Il lessico è quello del mondo: stanze, cerchio, referto.

Il repo è animagame-site, branch di lavoro designato. Collaudo nel browser
prima di dichiarare.
```

## S3 · ECHO — SYSTEMA 77, solo output

```
Lotto SYSTEMA 77. Decisione del Direttore: su questo dominio vanno SOLO output,
e in vetrina non compare nessun nome di agente.

Scrivi la sezione che mostra il lavoro fatto — verdetti pubblicati, schede,
strumenti costruiti — raccontando il METODO senza nominare chi lo esegue:
si parla di cosa è stato prodotto, con quale disciplina (fonti sempre citate,
incertezza dichiarata, ratifica umana prima della pubblicazione), e per chi.
Niente nomi in codice, niente prezzi, niente percorsi interni, nessun cliente.

Per chi usa l'AI «come una ricerca su Google»: niente gergo non spiegato.
Chiudi con una riga sola che dice come si comincia.

Repo systema77-site. I numeri vivi vengono dall'archivio, mai scritti a mano.
```

## S4 · KIROSHI — dai 7 verdetti ai 10-12

```
Lotto KIROSHI — massa critica. Il manuale dice che servono 10-12 verdetti
perché l'archivio abbia senso come prodotto: oggi sono 7 e le due code aperte
hanno già il loro verdetto pronto.

1. Proponi 5 candidati nuovi da verificare, scegliendo dove il fake-checking
   vale davvero: ditte e prodotti su cui una persona sta per spendere soldi e
   trova solo la voce del venditore. Per ognuno: perché vale la pena, quali
   fonti indipendenti esistono, quanto lavoro serve (rapida o scava).
2. Aspetta la scelta del Direttore, poi lavorali uno alla volta con lo Standard
   KIROSHI v1. Un verdetto senza fonti non si pubblica.
3. Ogni volta che pubblichi, rigenera db.js con lo script — mai a mano.

Regola nuova, imparata il 29/08: un verdetto scritto e non pubblicato invecchia.
Se resta in canna più di una settimana, riverificalo prima di farlo uscire —
l'ultima volta due su tre erano da correggere.
```

## S5 · BRAINDANCE — igiene dell'archivio

```
Lotto BRAINDANCE. Tre cose sulle tue schede pubbliche.
1. Almeno tre non portano firma (paradosso-fermi, topi-mantova-pavia,
   pensioni-2035): completale secondo il formato di casa.
2. Qualcuna mostra all'utente un percorso interno in un messaggio d'errore:
   trovali e riscrivili in modo che parlino a una persona.
3. Quali delle tue schede reggono il passaggio alla vista di gioco su
   animagame.io (lotto S2) così come sono, e quali no? Elenca e motiva.
Nessuna persona privata, fonti sempre linkate, incertezza dichiarata.
```

## S6 · RONDA — il prompt della Routine, aggiornato

```
[da aggiungere al prompt esistente, dopo il punto 1:]
1-bis. Leggi anche l'etichetta `regia`: sono i comandi che il Direttore ha
premuto dalla plancia (docs/regia/). Ognuno dice già a quale caposquadra va:
instradalo e lavoralo come una commessa normale.

[al punto 4, dopo il push:]
Rigenera la plancia con `python3 scripts/build_regia.py` (la passphrase arriva
dall'ambiente: se manca, salta questo passo e dillo nel report, non fallire).
Così lo stato che il Direttore legge dal telefono è sempre quello vero.

[da aggiungere alle regole dure:]
Un verdetto fermo da più di una settimana va riverificato prima di pubblicarlo.
```

## S7 · D.R.A.G.O.//CLIENT — chiudere C-01

```
Da D.R.A.G.O.//INTERNO. Hai l'offerta C-01 v2.0 pronta da giorni: consegnala al
Direttore per la ratifica nella forma prevista — verdetto di fattibilità
privato, preventivo con sforzi per voce e importi «— da ratificare», riga
REGISTRO in coda. Il prompt JUDY per logo/claim che avevi bozzato non lo esegui
tu: passalo al Direttore come richiesta, la casa lo dispaccia.

Contesto utile per il preventivo: quello che C-01 chiede — agenti autonomi con
confini scritti, un modulo che diventa lavoro, una ronda che gira da sola, la
ratifica umana prima di ogni pubblicazione — la casa lo ha costruito per sé e
lo può mostrare funzionante. È la referenza più forte che hai.

Perimetro invariato: niente push sul repo, clienti solo per sigla.
```

## S8 · SQUELCH — LA PLANCIA VIVA (dopo il ponte, con la chiave)

```
Lotto SQUELCH — plancia viva. Solo quando il ponte (S1) è in piedi e il
Direttore ha messo la chiave dell'API.

Aggiungi al Worker una rotta che riceve una domanda dalla plancia, la manda al
caposquadra giusto con il suo prompt (i file .claude/agents/*.md sono la fonte:
leggili, non riscriverli) e risponde in diretta al browser.

Vincoli: la chiave vive solo nell'ambiente del Worker; un limite di spesa
dichiarato e verificabile (quante richieste al giorno, cosa succede al
superamento); la risposta arriva SEMPRE come bozza, mai come cosa pubblicata —
la ratifica del Direttore resta il cancello, anche quando la macchina è veloce.
Se la chiave manca, la plancia continua a funzionare in modalità coda: la
degradazione è onesta, non un errore.
```

---

## I due gesti che non sono di nessun agente

Restano al Direttore, e ognuno costa un minuto:
1. **Creare le etichette `regia` e `commessa`** — nessuna delle due esiste
   ancora nel repo (verificato il 29/08). Senza, i comandi della plancia e il
   modulo commessa aprono richieste **nude**: nessuno le trova filtrando, e
   spariscono in silenzio. È la lezione del 17/08, che è costata cinque giorni
   a uno sconosciuto.
2. **Il secret `ANTHROPIC_API_KEY`** — l'automazione dei verdetti è ferma dal
   16/08 per questo.

— creato da D.R.A.G.O., 2026-08-29 · su commessa del Direttore
