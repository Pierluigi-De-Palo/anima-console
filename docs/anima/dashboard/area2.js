/* AREA PERSONALE — la porta vera, quella che risponde da fuori dal browser.

   PERCHE' UN FILE NUOVO E NON UNA MODIFICA DI area.js
   `area.js` e' servito con cache normale. Se cambiasse sotto un browser che ha
   ancora in cache il vecchio JSON, la pagina direbbe «questa carta non e' ancora
   abilitata» — e sembrerebbe rotta LA CARTA, non la pagina. Un nome nuovo non puo'
   essere in cache. (Istruzione di SHUTTER, 09/08.) `area.js` resta dov'e' e continua
   a funzionare per chi ha la pagina vecchia in cache: non va cancellato.

   COSA CAMBIA RISPETTO A PRIMA, ED E' TUTTO
   Prima: il codice si confrontava QUI, nel browser, contro un'impronta pubblicata
   nello stesso JSON. Dimostrava il possesso e non apriva niente: per entrare
   davvero bisognava mandare un codice a chi ti aveva dato la carta e ASPETTARE che
   ti registrasse. Cioe' qualcuno doveva aprirti la porta.
   Adesso: il codice va al Worker, che ricalcola HMAC(segreto, carta) e apre una
   sessione da 30 giorni. Il segreto non e' in rete e qui non arriva mai.
   ⭐ Chi ha la carta entra da solo. Non serve che esista un JSON pubblico per la
   sua carta, non serve che qualcuno la registri prima: la registrazione, se serve,
   viene DOPO.

   ⭐ LA CHIAVE E' LA CARTA, NON CHI LA TIENE
   Le prime due carte vanno allo stesso indirizzo e non sono la stessa persona:
   la 0 conduce il mondo e non gioca, la 1 gioca. Il ruolo lo dice il Worker DOPO
   che la carta ha aperto — non sta nel JSON pubblico e non si indovina da qui.

   FIN DOVE ARRIVA (dichiarato, non nascosto)
   La sessione vive in localStorage: chi ti prende il telefono sbloccato entra.
   E' la stessa fiducia che dai a un'app di posta. Chi perde la carta la spegne
   da solo — «ho perso la carta» qui sotto — e da quel momento non apre piu',
   comprese le sessioni gia' aperte.

— creato da SQUELCH, 2026-08-10 */
(function () {
  // La casa del Worker. Il giorno che ROGUE accende api.cyberboomer.io, cambia
  // QUESTA riga e nient'altro.
  var API = 'https://punti-anima.insieme.workers.dev';
  var CHIAVE = 's77.sessione';

  var $ = function (id) { return document.getElementById(id); };
  var porta = $('porta'), errore = $('errore'), bottone = $('apri');
  var campoId = $('campo-id'), campoCodice = $('campo-codice'), rigaId = $('riga-id');
  var vCarta = $('carta');
  var stanzaG = $('dentro-giocatore'), stanzaO = $('dentro-overlord');

  function dillo(m) { errore.textContent = m || ''; errore.hidden = !m; }

  function ricorda(s) {
    try { localStorage.setItem(CHIAVE, JSON.stringify(s)); } catch (e) { /* navigazione privata */ }
  }
  function ricordata() {
    try { return JSON.parse(localStorage.getItem(CHIAVE) || 'null'); } catch (e) { return null; }
  }
  function scorda() {
    try { localStorage.removeItem(CHIAVE); } catch (e) { /* niente da togliere */ }
  }

  // Una risposta del Worker porta gia' `messaggio` scritto in italiano per chi
  // legge: si mostra quello, non si traduce un codice.
  function chiedi(via, opzioni) {
    opzioni = opzioni || {};
    var testa = { 'content-type': 'application/json' };
    var s = ricordata();
    if (s && s.token) testa.authorization = 'Bearer ' + s.token;
    return fetch(API + via, {
      method: opzioni.metodo || 'GET', headers: testa,
      body: opzioni.corpo ? JSON.stringify(opzioni.corpo) : undefined,
      cache: 'no-store'
    }).then(function (r) {
      return r.json().catch(function () { return {}; })
        .then(function (d) { return { ok: r.ok, stato: r.status, dati: d }; });
    });
  }

  function scrivi(id, testo) { var n = $(id); if (n) n.textContent = testo; }

  // Una riga «etichetta → valore», nella stessa forma di .dati che la pagina usa
  // gia' ovunque. Niente classi nuove: un foglio di stile in piu' e' un posto in
  // piu' dove il colore della casa privata puo' finire in un repo pubblico.
  function riga(dove, etichetta, valore) {
    var d = document.createElement('div');
    var s = document.createElement('span'); s.textContent = etichetta;
    var b = document.createElement('b');    b.textContent = valore;
    d.appendChild(s); d.appendChild(b); dove.appendChild(d);
  }

  /* ── la stanza del giocatore ─────────────────────────────────────────────── */
  function apriGiocatore(d) {
    scrivi('g-carta', d.carta);
    scrivi('g-arcano', d.arcano || '—');
    scrivi('g-punti', String(d.punti));
    scrivi('g-stato', d.stato === 'registrata' ? 'registrata' : 'in attesa di registrazione');

    var lista = $('g-referti');
    lista.innerHTML = '';
    if (!d.referti || !d.referti.length) {
      riga(lista, 'niente ancora', '—');
    } else {
      d.referti.forEach(function (r) {
        riga(lista, r.titolo,
             (r.stato === 'pubblico' ? 'pubblico' : 'tenuto per te') +
             ' · ' + r.punti + ' punti · letto da ' + r.letto_da);
      });
    }
    porta.hidden = true; stanzaO.hidden = true; stanzaG.hidden = false;
  }

  /* ── la stanza dell'Overlord ─────────────────────────────────────────────
     Non e' la stessa pagina con qualcosa in piu': e' un altro mestiere.
     Niente punti, niente referti, niente gioco.                              */
  function apriOverlord(d) {
    scrivi('o-carta', d.carta);
    scrivi('o-arcano', d.arcano || '—');
    var m = d.mazzo || { conto: {} };
    scrivi('o-registrate', String(m.conto.registrate || 0));
    scrivi('o-attesa', String(m.conto['in-attesa'] || 0));
    scrivi('o-smarrite', String(m.conto.smarrite || 0));
    scrivi('o-cerchio', (m.conto.registrate || 0) + '/' + (m.totale || '—'));

    var lista = $('o-carte');
    lista.innerHTML = '';
    if (!d.carte || !d.carte.length) riga(lista, 'nessuna carta ha ancora aperto', '—');
    else d.carte.forEach(function (c) {
      riga(lista, c.carta, c.stato + ' · ' + c.punti + ' punti');
    });
    porta.hidden = true; stanzaG.hidden = true; stanzaO.hidden = false;
  }

  function mostra(d) {
    if (d.ruolo === 'overlord') apriOverlord(d); else apriGiocatore(d);
  }

  /* ── entrare ─────────────────────────────────────────────────────────────── */
  function entra() {
    dillo('');
    var quale = (campoId.value || '').trim();
    var codice = (campoCodice.value || '').trim();
    if (!quale) { dillo('Scrivi il numero della carta, quello grande sul fronte.'); return; }
    if (!codice) { dillo('Scrivi il codice stampato sul retro della carta.'); return; }

    bottone.disabled = true;
    // Il codice si manda GREZZO: normalizzare e' compito del Worker, e vive in un
    // posto solo. Due copie della stessa regola prima o poi divergono.
    chiedi('/sessione', { metodo: 'POST', corpo: { carta: quale, codice: codice } })
      .then(function (r) {
        if (!r.ok) { dillo(r.dati.messaggio || 'Non sono riuscito ad aprire. Riprova.'); return; }
        ricorda({ token: r.dati.sessione, scade: r.dati.scade, carta: r.dati.carta });
        return dentro();
      })
      .catch(function () {
        dillo('Non riesco a raggiungere la porta. Controlla la connessione e riprova.');
      })
      .then(function () { bottone.disabled = false; });
  }

  function dentro() {
    return chiedi('/io').then(function (r) {
      if (!r.ok) {
        // Sessione scaduta o carta spenta: si torna alla porta, e si dice perche'.
        scorda();
        porta.hidden = false; stanzaG.hidden = true; stanzaO.hidden = true;
        if (r.stato !== 401) dillo(r.dati.messaggio || '');
        return;
      }
      mostra(r.dati);
    });
  }

  /* ── ho perso la carta ───────────────────────────────────────────────────── */
  function perduta() {
    var s = ricordata();
    if (!s) return;
    if (!confirm('Disattivo la carta ' + s.carta + '.\n\n'
                 + 'Da subito non apre più niente, nemmeno da questo telefono. '
                 + 'I punti restano tuoi. Serve una carta nuova per rientrare.\n\nProcedo?')) return;
    chiedi('/carta/smarrita', { metodo: 'POST', corpo: { carta: s.carta } })
      .then(function (r) {
        scorda();
        porta.hidden = false; stanzaG.hidden = true; stanzaO.hidden = true;
        dillo(r.dati.messaggio || 'Carta disattivata.');
      });
  }

  /* ── avvio ───────────────────────────────────────────────────────────────── */
  var idDaQR = (new URLSearchParams(location.search).get('id') || '').trim().toUpperCase();
  var sessione = ricordata();

  if (idDaQR) {
    campoId.value = idDaQR;
    if (vCarta) vCarta.textContent = idDaQR;
    rigaId.hidden = true;          // arriva dal QR: il numero lo sappiamo gia'
  } else if (sessione && sessione.carta) {
    campoId.value = sessione.carta;
    if (vCarta) vCarta.textContent = sessione.carta;
  }

  bottone.addEventListener('click', entra);
  campoCodice.addEventListener('keydown', function (e) { if (e.key === 'Enter') entra(); });
  [$('g-esci'), $('o-esci')].forEach(function (n) {
    if (n) n.addEventListener('click', function (e) {
      e.preventDefault(); scorda(); location.href = location.pathname;
    });
  });
  var perso = $('g-perduta');
  if (perso) perso.addEventListener('click', function (e) { e.preventDefault(); perduta(); });

  // Chi e' gia' entrato non ridigita niente: la sessione dura 30 giorni.
  if (sessione && sessione.token) dentro();
})();
