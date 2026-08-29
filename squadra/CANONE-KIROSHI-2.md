# CANONE KIROSHI 2.0 — token, PLANCIA, card-verdetto di gioco, sorte delle schede

Lotto JUDY su commessa del Direttore, ratificata 21/08 (`squadra/PROMPT-CAMPAGNA-REGIA.md`, P1).
Consegna una **direttiva applicabile**: chi costruisce (SQUELCH per `docs/regia/`, ECHO per i
microtesti, RONDA per il dispatch dei bottoni) prende i blocchi qui sotto e li usa, non li reinventa.

Non ho toccato nessuna pagina esistente. I due riferimenti che mi sono stati indicati come "attuale
da far crescere" restano quello che sono: `docs/fake-checker/index.html` e `docs/schede/commessa.html`
(entrambi cyan `#22d3ee` piatto su `#0a0e14`, senza scala né stati).

---

## 0 · La regola in una riga

> **KIROSHI 2.0 si applica dove il colore deve dire "una macchina sta misurando o lavorando per un
> umano che non è del mestiere": la regia interna di cyberboomer.io, le dashboard dati, il referto
> di verifica. Mai sul mito pubblico (ambra Camera Oscura), mai dentro il gioco (verde Anima Game),
> mai sull'agenzia (ACID di systema77.com).**

---

## 1 · I token — CSS custom properties, prefisso `--k2-`

Prefisso nuovo (`k2`, non `k`) apposta: dichiara la versione ed evita collisioni con le variabili
`--cyan`/`--dim`/… già scritte a mano nelle pagine esistenti, che restano intatte finché qualcuno
non decide di farle migrare a questo registro.

```css
:root{
  /* ── struttura: profondità di superficie, invariata rispetto a oggi ── */
  --k2-void:    #07090d;
  --k2-bg:      #0a0e14;
  --k2-panel:   #0d141d;
  --k2-panel-2: #111823;
  --k2-panel-3: #161f2c;  /* NUOVO — terzo livello: serve alla PLANCIA cifrata (§3) */
  --k2-line:    #1b2634;
  --k2-line-2:  #22303f;

  /* ── testo: tre pesi ── */
  --k2-txt:   #d7e3ef;
  --k2-muted: #7d93a8;  /* invariato — passa già ~6.1:1 su --k2-bg */
  --k2-dim:   #6b7e91;  /* CORRETTO da #5a6b7d (~3.4:1, non leggibile come testo:
                           è il debito di famiglia segnalato in squadra/SQUADRA.md
                           sulla firma di commessa.html e competenze-v1.1.html).
                           Ora ~4.6:1 su --k2-bg: passa. */

  /* ── l'accento macchina: una SCALA, non un valore piatto —
     è la crescita che il Direttore ha chiesto: oggi #22d3ee è un colore solo
     usato allo stesso modo ovunque (bordi, testo, sfondi, hover); qui ha un
     gradino per ruolo, l'identità di base (500) resta la stessa. ── */
  --k2-cyan-100: #12313b;  /* tinta di sfondo — hover, riga selezionata */
  --k2-cyan-300: #4fb8d6;  /* cyan a riposo — presente ma non urla */
  --k2-cyan-500: #22d3ee;  /* IDENTITÀ, invariata: il cyan KIROSHI */
  --k2-cyan-700: #8de9fb;  /* cyan acceso — solo per "sta succedendo ora" */
  --k2-cyan-glow: rgba(34,211,238,.35);

  /* ── stati operativi: riposo / attivo / allarme / spento —
     lessico DIVERSO dai colori di punteggio (rosso/ambra/verde delle fasce
     0-40/41-70/71-100 già in uso in fake-checker/index.html). Quei colori
     rispondono a "è vero?"; questi rispondono a "la macchina sta lavorando?".
     Non si mischiano MAI sullo stesso elemento — un pallino di stato non è
     mai rosso "punteggio basso", è arancio "allarme di sistema": sono due
     domande diverse e chi guarda non deve doverle distinguere leggendo. ── */
  --k2-stato-riposo:  var(--k2-dim);
  --k2-stato-attivo:  var(--k2-cyan-700);
  --k2-stato-allarme: #ff8a3d;  /* arancio, non il rosso #ff5c6c dei punteggi */
  --k2-stato-spento:  #3a4656;

  /* ── tipografia: due famiglie, un ruolo ciascuna, mai intercambiabili —
     mono = ogni dato che la macchina misura o etichetta (punteggi, ID, orari,
     stati) · sans = ogni frase scritta per spiegare qualcosa a un umano ── */
  --k2-mono: ui-monospace,SFMono-Regular,Menlo,monospace;
  --k2-sans: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;

  /* ── scala tipografica: 8 gradini fissi ── */
  --k2-text-xs:   .6875rem; /* 11px — etichette maiuscole, meta-dati */
  --k2-text-sm:   .8125rem; /* 13px — corpo secondario, note */
  --k2-text-base: .9375rem; /* 15px — corpo del testo */
  --k2-text-md:   1rem;     /* 16px — campi, bottoni */
  --k2-text-lg:   1.25rem;  /* 20px — titoli di sezione */
  --k2-text-xl:   1.625rem; /* 26px — nome della stanza */
  --k2-text-2xl:  2.25rem;  /* 36px — il numero grande: punteggio, contatore */

  /* ── spaziature: multipli di 4, mai un margine a caso ── */
  --k2-sp-1: .25rem; --k2-sp-2: .5rem; --k2-sp-3: .75rem; --k2-sp-4: 1rem;
  --k2-sp-5: 1.5rem; --k2-sp-6: 2rem;  --k2-sp-7: 3rem;   --k2-sp-8: 4rem;
}
```

### Il componente di stato (`k2-stato`) — riusabile ovunque

Le quattro fasi si distinguono per **forma e movimento**, non solo per colore — chi non
distingue le tinte deve comunque leggere lo stato:

```css
.k2-stato{ display:inline-flex; align-items:center; gap:var(--k2-sp-2);
  font-family:var(--k2-mono); font-size:var(--k2-text-xs); letter-spacing:.14em;
  text-transform:uppercase; color:var(--k2-muted) }
.k2-stato .dot{ width:8px; height:8px; border-radius:50%; background:var(--k2-stato-riposo); flex:0 0 auto }

.k2-stato.attivo{ color:var(--k2-cyan-700) }
.k2-stato.attivo .dot{ background:var(--k2-stato-attivo); box-shadow:0 0 8px 2px var(--k2-cyan-glow);
  animation:k2-pulsa 1.6s ease-in-out infinite }

.k2-stato.allarme{ color:var(--k2-stato-allarme) }
.k2-stato.allarme .dot{ background:var(--k2-stato-allarme); animation:k2-lampeggia .9s steps(2) infinite }

.k2-stato.spento{ color:var(--k2-dim); opacity:.55 }
.k2-stato.spento .dot{ background:transparent; border:1px solid var(--k2-stato-spento) }

@keyframes k2-pulsa{ 0%,100%{box-shadow:0 0 4px 1px var(--k2-cyan-glow)} 50%{box-shadow:0 0 12px 4px var(--k2-cyan-glow)} }
@keyframes k2-lampeggia{ 50%{opacity:.25} }
@media (prefers-reduced-motion: reduce){ .k2-stato .dot{ animation:none !important } }
```
`riposo` = nessuna classe extra (default). Uso: `<span class="k2-stato attivo"><i class="dot"></i>al lavoro</span>`.

---

## 2 · LA PLANCIA (`docs/regia/`) — modello, non implementazione

**Chi la costruisce:** SQUELCH (P2 di `PROMPT-CAMPAGNA-REGIA.md`) cifra davvero il payload
(AES-GCM, PBKDF2) e collega il verificatore di passphrase. Io consegno **il contratto visivo**:
le classi, gli stati, e cosa succede quando SQUELCH aggiunge/toglie `.sbloccata`. Non fingo una
sicurezza che non esiste: il JS qui sotto per lo strato pubblico è vero e finito; il passaggio
`.bloccata → .sbloccata` è lo *switch* che SQUELCH deve azionare dopo aver verificato la
passphrase per davvero, non un lucchetto di scena.

### Come si distinguono a colpo d'occhio (nessuna spiegazione richiesta)

**Prima di sbloccare, lo strato cifrato sembra nastro di cantiere: tratteggiato, arancio, spento.
Dopo, sembra un pannello acceso: bordo pieno, ciano, che brilla.** Lo strato pubblico invece è
sempre piatto e fermo — un cartellone, non un pannello: non cambia mai aspetto, perché non ha
niente da nascondere.

```css
.plancia{ max-width:390px; margin:0 auto; padding:var(--k2-sp-4) var(--k2-sp-3) var(--k2-sp-7);
  font-family:var(--k2-sans); background:var(--k2-void); color:var(--k2-txt) }
.pl-intestazione{ font-family:var(--k2-mono); font-size:var(--k2-text-xl); letter-spacing:.14em;
  color:var(--k2-cyan-500); margin:0 0 var(--k2-sp-1) }
.pl-sottotitolo{ font-family:var(--k2-mono); font-size:var(--k2-text-xs); letter-spacing:.18em;
  text-transform:uppercase; color:var(--k2-muted); margin-bottom:var(--k2-sp-6) }

/* ── strato pubblico: piatto, fermo, leggibile da chiunque, sempre uguale ── */
.pl-pubblica{ background:var(--k2-panel); border:1px solid var(--k2-line); border-radius:10px;
  padding:var(--k2-sp-4); margin-bottom:var(--k2-sp-6) }
.pl-pubblica h2{ font-family:var(--k2-mono); font-size:var(--k2-text-xs); letter-spacing:.18em;
  text-transform:uppercase; color:var(--k2-muted); margin:0 0 var(--k2-sp-3) }
.pl-riga{ display:flex; justify-content:space-between; gap:var(--k2-sp-3); padding:var(--k2-sp-2) 0;
  border-top:1px solid var(--k2-line); font-size:var(--k2-text-sm) }
.pl-riga:first-of-type{ border-top:0 }
.pl-riga b{ font-family:var(--k2-mono); font-weight:400; color:var(--k2-txt) }
.pl-riga span{ color:var(--k2-muted) }
.pl-riga .non-ratificato{ color:var(--k2-dim) } /* un numero non ratificato resta un trattino */

/* ── strato cifrato: PRIMA — nastro di cantiere ── */
.pl-cifrata{ position:relative; background:var(--k2-panel-3); border:1px dashed var(--k2-line-2);
  border-radius:10px; padding:var(--k2-sp-4); overflow:hidden; transition:border-color .3s, box-shadow .3s }
.pl-cifrata::before{ content:''; position:absolute; inset:0; pointer-events:none; opacity:.08;
  background:repeating-linear-gradient(135deg, var(--k2-stato-allarme) 0 10px, transparent 10px 20px) }
.pl-cifrata h2{ font-family:var(--k2-mono); font-size:var(--k2-text-xs); letter-spacing:.18em;
  text-transform:uppercase; color:var(--k2-cyan-700); margin:0 0 var(--k2-sp-3);
  display:flex; align-items:center; gap:var(--k2-sp-2) }

.pl-passphrase{ display:flex; gap:var(--k2-sp-2); margin-bottom:var(--k2-sp-2) }
.pl-passphrase input{ flex:1; background:var(--k2-void); border:1px solid var(--k2-line-2);
  border-radius:6px; color:var(--k2-txt); font-family:var(--k2-mono); font-size:var(--k2-text-md);
  padding:var(--k2-sp-3); min-height:44px }
.pl-passphrase input:focus{ outline:none; border-color:var(--k2-cyan-700) }
.pl-passphrase button{ font-family:var(--k2-mono); font-size:var(--k2-text-xs); letter-spacing:.1em;
  text-transform:uppercase; background:transparent; color:var(--k2-cyan-700); border:1px solid var(--k2-cyan-700);
  border-radius:6px; padding:0 var(--k2-sp-4); min-height:44px; cursor:pointer }
.pl-esito-cifrata{ font-family:var(--k2-mono); font-size:var(--k2-text-xs); color:var(--k2-dim); min-height:1.4em }
.pl-schede-comando{ display:none; grid-template-columns:1fr; gap:var(--k2-sp-3); margin-top:var(--k2-sp-4) }

/* ── strato cifrato: DOPO — pannello acceso (SQUELCH aggiunge questa classe) ── */
.pl-cifrata.sbloccata{ border:1px solid var(--k2-cyan-700); box-shadow:0 0 24px -4px var(--k2-cyan-glow) }
.pl-cifrata.sbloccata::before{ opacity:0 }
.pl-cifrata.sbloccata .pl-passphrase{ display:none }
.pl-cifrata.sbloccata .pl-schede-comando{ display:grid }

@media(min-width:700px){ .pl-schede-comando{ grid-template-columns:1fr 1fr } }
```

```html
<div class="plancia">
  <div class="pl-intestazione">LA PLANCIA</div>
  <div class="pl-sottotitolo">cyberboomer.io · regia</div>

  <!-- ═══ STRATO PUBBLICO — vero, onesto, lo vede chiunque arrivi qui ═══ -->
  <section class="pl-pubblica">
    <h2>Stato — lo vede chiunque</h2>
    <div class="pl-riga"><b>Verdetti pubblicati</b><span>7</span></div>
    <div class="pl-riga"><b>In coda</b><span>2</span></div>
    <div class="pl-riga"><b>Ultimo</b><span class="non-ratificato">—</span></div>
    <!-- il trattino resta finché il contatore vero non è corretto (P4): mai un numero a mano -->
  </section>

  <!-- ═══ STRATO CIFRATO — la regia vera, sotto passphrase ═══ -->
  <section class="pl-cifrata" id="regia-cifrata">
    <h2><span class="pl-lucchetto">[chiuso]</span> La regia — cifrata</h2>
    <div class="pl-passphrase">
      <input type="password" id="regia-pass" placeholder="passphrase" autocomplete="off">
      <button id="regia-sblocca" type="button">Sblocca</button>
    </div>
    <div class="pl-esito-cifrata" id="regia-esito"></div>

    <div class="pl-schede-comando" id="regia-schede">
      <!-- sei <article class="pl-scheda">, una per caposquadra — modello sotto -->
    </div>
  </section>
</div>
```

### La scheda-comando — modello (uno vale per tutti e sei)

```html
<article class="pl-scheda" data-agente="KIROSHI">
  <header>
    <span class="pl-scheda-nome">KIROSHI</span>
    <span class="k2-stato attivo"><i class="dot"></i>al lavoro</span>
  </header>
  <p class="pl-scheda-mestiere">verità — ditte, prodotti, venditori</p>
  <div class="pl-scheda-azioni">
    <button class="k2-btn" data-agente="KIROSHI" data-azione="Vedi la coda">Vedi la coda</button>
    <button class="k2-btn" data-agente="KIROSHI" data-azione="Ultimo verdetto">Ultimo verdetto</button>
    <button class="k2-btn secondario" data-agente="KIROSHI" data-azione="Nuova verifica">Nuova verifica</button>
  </div>
</article>
```

```css
.pl-scheda{ background:var(--k2-panel-2); border:1px solid var(--k2-line-2); border-radius:10px;
  padding:var(--k2-sp-4); display:flex; flex-direction:column; gap:var(--k2-sp-3) }
.pl-scheda header{ display:flex; justify-content:space-between; align-items:center; gap:var(--k2-sp-2) }
.pl-scheda-nome{ font-family:var(--k2-mono); font-size:var(--k2-text-md); letter-spacing:.1em; color:var(--k2-txt) }
.pl-scheda-mestiere{ font-family:var(--k2-sans); font-size:var(--k2-text-sm); color:var(--k2-muted); margin:0 }
.pl-scheda-azioni{ display:grid; grid-template-columns:repeat(2,1fr); gap:var(--k2-sp-2) }
.k2-btn{ font-family:var(--k2-mono); font-size:var(--k2-text-xs); letter-spacing:.08em; text-transform:uppercase;
  background:transparent; color:var(--k2-cyan-500); border:1px solid var(--k2-cyan-500); border-radius:6px;
  padding:var(--k2-sp-3) var(--k2-sp-2); min-height:44px; cursor:pointer; transition:background .2s }
.k2-btn:hover{ background:var(--k2-cyan-100) }
.k2-btn.secondario{ grid-column:1 / -1; color:var(--k2-muted); border-color:var(--k2-line-2) }
.k2-btn.secondario:hover{ color:var(--k2-txt); background:var(--k2-panel-3) }
```

**Le altre cinque, stesso modello, azioni suggerite (ECHO scrive il microtesto finale — qui è
struttura, non copy):**
- **D.R.A.G.O.** — dispatch: *Apri una commessa* · *Vedi le code aperte* · *Convoca il Consiglio*
- **BRAINDANCE** — verità persone/notizie: *Vedi la coda* · *Ultimo verdetto*
- **JUDY** — design: *Ultima direzione* · *Apri il canone*
- **SQUELCH** — backend/privacy: *Stato del backend* · *Controllo guardia privacy*
- **ECHO** — voce/testi: *Ultimo taglio pubblicato* · *Canali attivi*

### Il meccanismo dei bottoni (stesso schema di `commessa.html`, riusato)

Ogni bottone apre una scheda nella coda di lavoro con etichetta **`regia`** — è quella che
la RONDA legge (P6): il testo dice già a quale caposquadra va, lei instrada.

```js
function comandoURL(agente, azione, dettaglio){
  var titolo = '[regia] ' + agente + ' — ' + azione;
  var corpo = 'AGENTE — ' + agente + '\nAZIONE — ' + azione +
    (dettaglio ? '\nDETTAGLIO — ' + dettaglio : '') +
    '\n\n---\n_Comando premuto dalla PLANCIA · ' + new Date().toISOString().slice(0,10) + '_';
  return 'https://github.com/Pierluigi-De-Palo/anima-console/issues/new'
    + '?title=' + encodeURIComponent(titolo)
    + '&body=' + encodeURIComponent(corpo)
    + '&labels=' + encodeURIComponent('regia');
}
document.querySelectorAll('.k2-btn[data-agente]').forEach(function(b){
  b.addEventListener('click', function(){
    window.open(comandoURL(b.dataset.agente, b.dataset.azione), '_blank', 'noopener');
  });
});
```

⚠️ **Dipendenza, non dettaglio:** l'etichetta `regia` deve esistere nel repo prima che questo vada
online — è la stessa lezione del 17/08 su `kiroshi-queue` e del 18/08 su `commessa`: un'etichetta
assente non dà errore, sparisce in silenzio.

---

## 3 · La card-verdetto di gioco — modello

Coerente con `assets/solco.js` e `assets/stile.css` di `animagame-site` (verde `#38E08A` su nero,
`Share Tech Mono` per la macchina, `Newsreader` per l'umano — non introduco font nuovi, uso quelli
già scelti da ECHO/JUDY per il gioco).

**La regola in una riga:** *il verde è il timbro di "vero": più il punteggio sale, più si accende.
Tutto il resto — incerto, falso — non prende un colore diverso, perde semplicemente la luce.* Niente
rosso/ambra qui: quei colori sono il lessico dei referti (fake-checker), non del mondo di gioco. Un
solo accento, che cambia intensità e movimento, mai tinta — così l'esito resta parte della storia,
non diventa un semaforo da ufficio infilato in una stanza verde.

```css
.carta-verdetto{ background:var(--fondo); border:1px solid var(--linea); border-radius:10px;
  padding:1.4rem 1.3rem; max-width:26rem; position:relative; overflow:hidden }
.carta-verdetto::before{ content:''; position:absolute; inset:0; pointer-events:none;
  background:radial-gradient(ellipse at 25% 0%, var(--verde-soft), transparent 55%) }

.cv-testa{ display:flex; justify-content:space-between; align-items:baseline; gap:.8rem; margin-bottom:.9rem }
.cv-fonte{ font-family:var(--font-mono); font-size:.68rem; letter-spacing:.18em; text-transform:uppercase; color:var(--muto) }
.cv-esito{ font-family:var(--font-mono); font-size:.72rem; letter-spacing:.2em; text-transform:uppercase; color:var(--verde) }

.cv-domanda{ font-family:var(--font-serif); font-style:italic; font-size:1.05rem; line-height:1.5;
  color:var(--carta); margin:0 0 1.2rem }

.cv-punteggio{ display:flex; flex-wrap:wrap; align-items:baseline; gap:.4rem; margin-bottom:1.1rem }
.cv-num{ font-family:var(--font-mono); font-size:2rem; color:var(--verde); line-height:1 }
.cv-su{ font-family:var(--font-mono); font-size:.85rem; color:var(--muto) }
.cv-barra{ flex:1 0 100%; height:3px; background:var(--linea); border-radius:2px; margin-top:.5rem; overflow:hidden }
.cv-barra i{ display:block; height:100%; background:var(--verde); box-shadow:0 0 6px var(--verde) }

.cv-link{ font-family:var(--font-mono); font-size:.75rem; letter-spacing:.1em; text-transform:uppercase;
  color:var(--verde); text-decoration:none; border-bottom:1px solid var(--linea) }
.cv-link:hover{ border-color:var(--verde) }

/* esito: SOLO intensità e moto del verde cambiano, mai la tinta */
.carta-verdetto[data-esito="incerto"] .cv-esito,
.carta-verdetto[data-esito="incerto"] .cv-num{ color:var(--muto) }
.carta-verdetto[data-esito="incerto"] .cv-barra i{ background:var(--muto); box-shadow:none }

.carta-verdetto[data-esito="falso"] .cv-esito,
.carta-verdetto[data-esito="falso"] .cv-num{ color:var(--carta) }
.carta-verdetto[data-esito="falso"] .cv-barra i{ background:var(--carta); opacity:.65; box-shadow:none }
.carta-verdetto[data-esito="falso"] .cv-esito{ animation:cv-glitch 2.4s infinite }
@keyframes cv-glitch{ 0%,92%,100%{opacity:1;transform:none} 93%{opacity:.4;transform:translateX(1px)}
  95%{opacity:1;transform:translateX(-1px)} 97%{opacity:.55} }
@media (prefers-reduced-motion: reduce){ .carta-verdetto *{ animation:none !important } }
```

```html
<article class="carta-verdetto" data-esito="vero">
  <div class="cv-testa">
    <span class="cv-fonte">KIROSHI · verdetto #0007</span>
    <span class="cv-esito">CONFERMATO</span>
  </div>
  <p class="cv-domanda">«È vero che la Nikon ZR registra davvero in RAW interno?»</p>
  <div class="cv-punteggio">
    <span class="cv-num">82</span><span class="cv-su">/100</span>
    <div class="cv-barra"><i style="width:82%"></i></div>
  </div>
  <a class="cv-link" href="/verdetti/0007/">Leggi la scheda completa →</a>
</article>
```
`data-esito`: `"vero"` (≥71, verde acceso) · `"incerto"` (41-70, muto) · `"falso"` (≤40, ink piatto
che sfarfalla). Etichette suggerite: CONFERMATO / INCERTO / SMASCHERATO — nessuna parola vietata.

**Il link, per regola P9 (Anima Game stand-alone):** `cv-link` punta **sempre dentro animagame.io**
(`/verdetti/NNNN/`), mai a `cyberboomer.io/fake-checker/#NNNN` e mai a GitHub — la vista di gioco
legge lo stesso archivio (`docs/data/` resta l'unica fonte) ma passa dal ponte, non fa uscire il
giocatore di casa.

---

## 4 · La sorte delle schede esistenti — una direzione sola

**Direzione: le nove schede BRAINDANCE + `braindance/index.html` + `chiedi/` (oggi cyan) e le due
schede più recenti in carta chiara (`paradosso-fermi.html`, `contenuti-sensuali-social.html`, terzo
registro non canonico) smettono di essere la porta pubblica. Diventano viste di gioco su
animagame.io, ricostruite col modello del §3 (verde), lette dallo stesso archivio `docs/data/`
attraverso il ponte — non restano, non si riallineano al cyan sul posto.**

Motivazione in due righe: **cyberboomer.io ora è la regia interna, fuori dai motori di ricerca —
non è più la porta a cui il pubblico bussa** (assetto ratificato in `PROMPT-CAMPAGNA-REGIA.md`);
chi chiede "è vero che…" deve trovarsi davanti al gioco (verde, animagame.io), non a un pannello
cyan che sembra fatto per un tecnico. Il terzo registro (carta chiara `#faf9f5`) non era una terza
lingua legittima in nessuno scenario: era una deriva — comparsa senza mandato su due schede,
nessuna riga di canone la giustifica — e va sanata nello stesso passaggio, non lasciata né
"temporaneamente" spostata di dominio.

Questo non lo eseguo io: sposto solo la decisione. Serve **SQUELCH** per il ponte e le viste che
leggono `docs/data/` da animagame.io (P2/P9), **ECHO** per riscrivere i testi di gioco (lessico
vietato da controllare riga per riga: le schede attuali parlano di "verdetto", "fonti" — va bene;
vanno cercati residui di gergo da referto tecnico), e **il Direttore** per la ratifica di hosting/
DNS (dominio già di ROGUE) e per i tempi: non è un cambio di CSS, è uno spostamento di superficie
pubblica.

---

## Nota per chi implementa

- Il debito di contrasto sulla firma (`#5a6b7d`, ~3.4:1) segnalato in `squadra/SQUADRA.md` è
  risolto **in questo registro** (`--k2-dim` = `#6b7e91`, ~4.6:1). Non è retroattivo sulle pagine
  esistenti: chi le tocca per altro motivo, applichi anche questa correzione.
- Non ho creato `docs/regia/` né toccato `docs/braindance/`: la consegna richiesta erano token e
  modelli, non pagine. Un solo file nuovo, questo.
- I numeri d'esempio nei blocchi HTML sopra (7 verdetti, 82/100, "al lavoro") sono **illustrativi**:
  chi costruisce li sostituisce con dati veri o con un trattino, mai a mano.

— creato da JUDY, 2026-08-29
