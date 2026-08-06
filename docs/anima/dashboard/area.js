/* AREA PERSONALE — la porta che si apre da soli, con la card in mano.

   IL PROBLEMA CHE RISOLVE
   Il QR sulla card e' pubblico: chi ne fotografa uno vede che la card e'
   autentica. Va bene, quella e' la verifica. Ma non puo' bastare per ENTRARE,
   altrimenti chiunque fotografi la card di un altro prende il suo posto.
   Quello che solo il titolare ha e' il codice STAMPATO SUL RETRO. Digitarlo e'
   la prova di avere l'oggetto in mano.

   COME FUNZIONA
   Il JSON pubblico della card porta `verifica_ingresso`, cioe'
   sha256("carta|<ID>|<seriale>"). Qui si rifa' lo stesso conto sul codice
   digitato: se combacia, la card e' quella. Il seriale non e' in rete e non ci
   va mai — viaggia solo dalle dita di chi ce l'ha alla memoria del suo telefono.

   FIN DOVE ARRIVA (dichiarato, non nascosto)
   Questo e' un controllo che gira nel browser, su un sito statico: dimostra il
   possesso della card, NON nasconde niente. Tutto cio' che sta in questa pagina
   e' comunque pubblico. Va bene cosi': dietro questa porta non c'e' un segreto,
   c'e' un posto nel cerchio. Il giorno in cui ci finiranno dati veri di una
   persona, quel giorno serve un server — non una riga in piu' di JavaScript.
   Regge perche' il seriale e' HMAC troncato a 12 caratteri base32 = 60 bit —
   ~57,7 dopo l'accorpamento dei caratteri confondibili qui sotto. Non e' una
   password scelta da qualcuno: non sta in nessun dizionario, non si indovina.

— creato da SQUELCH, 2026-08-06 */
(function () {
  var CHIAVE = 's77.carta';
  var BASE = '/anima/verifica/';

  var porta = document.getElementById('porta');
  var dentro = document.getElementById('dentro');
  var campoId = document.getElementById('campo-id');
  var rigaId = document.getElementById('riga-id');
  var campoCodice = document.getElementById('campo-codice');
  var bottone = document.getElementById('apri');
  var errore = document.getElementById('errore');
  var vCarta = document.getElementById('carta');
  var vId = document.getElementById('id');
  var vNum = document.getElementById('num');
  var vData = document.getElementById('data');
  var vCodice = document.getElementById('codice');
  var copia = document.getElementById('copia');
  var esci = document.getElementById('esci');

  function ricordata() {
    try { return (JSON.parse(localStorage.getItem(CHIAVE) || '{}') || {}).card_id || ''; }
    catch (e) { return ''; }
  }

  var id = (new URLSearchParams(location.search).get('id') || ricordata() || '')
             .trim().toUpperCase();

  // Caratteri che una persona confonde leggendo il retro. Ognuno viene ricondotto a
  // UNO solo prima del confronto, cosi' «Z» e «2» aprono la stessa porta.
  //   - 0 1 8 9 non esistono in base32: chi li digita ha letto male di sicuro.
  //   - Z/2, S/5, G/6 esistono entrambi ed erano la trappola vera: il codice della
  //     carta 0 contiene sia G sia Z (trovato da SHUTTER il 06/08).
  //   - I/L/1 si confondono fra loro e non c'e' modo di indovinare: si accorpano.
  // ⚠️ Questa tabella e' gemella di CONFONDIBILI in scripts/build_card_pubblica.py.
  // Se cambia una, cambiano tutte e due, e i JSON pubblici vanno rigenerati.
  var CONFONDIBILI = { '0': 'O', '1': 'I', 'L': 'I', '8': 'B',
                       '9': 'G', '6': 'G', '2': 'Z', '5': 'S' };

  // Due normalizzazioni, e vanno tenute separate.
  // Sull'ID NON si applica la tabella: «SYS-00» diventerebbe «SYSOO» e la card
  // non si troverebbe piu'. L'ID e' scritto grande sul fronte, non si sbaglia.
  function normalizzaId(t) { return (t || '').toUpperCase().replace(/[^A-Z0-9]/g, ''); }

  // Il codice del retro invece si puo' scrivere come viene: minuscolo, senza
  // trattini, con spazi, e con i caratteri confusi.
  function normalizzaCodice(t) {
    return normalizzaId(t).replace(/[01L89625]/g, function (c) { return CONFONDIBILI[c]; });
  }

  function sha256(testo) {
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(testo))
      .then(function (buf) {
        return Array.prototype.map.call(new Uint8Array(buf), function (b) {
          return ('0' + b.toString(16)).slice(-2);
        }).join('');
      });
  }

  function dillo(messaggio) {
    errore.textContent = messaggio;
    errore.hidden = !messaggio;
  }

  function apriStanza(dati, codice) {
    vCarta.textContent = dati.card_id;
    vId.textContent = dati.card_id;
    // «00/10 · cerchio 1» — decisione del Direttore, 06/08. Stessa forma della
    // pagina di verifica: il numero dice anche a quale cerchio appartiene.
    vNum.textContent = (dati.numero === null || dati.numero === undefined)
      ? '—'
      : String(dati.numero).padStart(2, '0') + '/' + (dati.totale || '—') +
        (dati.cerchio ? ' · cerchio ' + dati.cerchio : '');
    vData.textContent = dati.emessa || '—';
    vCodice.textContent = codice;
    porta.hidden = true;
    dentro.hidden = false;
  }

  function entra(dati, seriale) {
    return sha256('carta|' + dati.card_id + '|' + seriale).then(function (prova) {
      if (prova !== dati.verifica_ingresso) {
        dillo('Il codice non corrisponde a questa carta. Ricontrolla il retro: '
              + 'sono dodici caratteri, fra lettere e numeri, in tre gruppi.');
        return false;
      }
      // Il codice di ingresso e' un'impronta DIVERSA da quella pubblicata: chi legge
      // il JSON non puo' ricavarlo, quindi vale come prova di possesso.
      return sha256('ingresso|' + dati.card_id + '|' + seriale).then(function (h) {
        var c = h.slice(0, 8).toUpperCase();
        var codice = c.slice(0, 4) + '-' + c.slice(4);
        // In memoria resta l'ID della card, mai il codice del retro.
        try { localStorage.setItem(CHIAVE, JSON.stringify({ card_id: dati.card_id })); }
        catch (e) { /* navigazione privata: si entra lo stesso, non si ricorda */ }
        apriStanza(dati, codice);
        return true;
      });
    });
  }

  function prova() {
    dillo('');
    var quale = normalizzaId(campoId.value || id);
    var seriale = normalizzaCodice(campoCodice.value);

    if (!quale) { dillo('Scrivi il numero della carta, per esempio SYS-02.'); return; }
    if (!seriale) { dillo('Scrivi il codice stampato sul retro della carta.'); return; }
    if (!window.crypto || !crypto.subtle) {
      dillo('Questo browser non riesce a fare il controllo. Apri la pagina in Chrome, '
            + 'Safari o Brave aggiornati.');
      return;
    }

    // SYS02 digitato senza trattino deve trovare la card SYS-02.
    var idCard = /^SYS\d{2}$/.test(quale) ? 'SYS-' + quale.slice(3) : quale;

    bottone.disabled = true;
    fetch(BASE + 'dati/' + idCard + '.json', { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error('404'); return r.json(); })
      .then(function (d) {
        if (d.stato !== 'VERIFICATA') {
          dillo('Questa carta risulta non verificata. Scrivi a chi te l\'ha data.');
          return;
        }
        if (!d.verifica_ingresso) {
          dillo('Questa carta non è ancora abilitata all\'ingresso. Scrivi a chi te l\'ha data.');
          return;
        }
        return entra(d, seriale);
      })
      .catch(function () {
        dillo('Non trovo la carta «' + idCard + '». Controlla il numero sul fronte.');
      })
      .then(function () { bottone.disabled = false; });
  }

  if (id) {
    vCarta.textContent = id;
    campoId.value = id;
    rigaId.hidden = true;   // arriva dal QR: il numero della card lo sappiamo già
  }

  bottone.addEventListener('click', prova);
  campoCodice.addEventListener('keydown', function (e) { if (e.key === 'Enter') prova(); });

  copia.addEventListener('click', function () {
    var testo = vCarta.textContent + ' · codice di ingresso ' + vCodice.textContent;
    navigator.clipboard.writeText(testo).then(function () {
      copia.textContent = 'copiato';
      setTimeout(function () { copia.textContent = 'copia'; }, 2000);
    }, function () {
      copia.textContent = 'copialo a mano';
    });
  });

  esci.addEventListener('click', function (e) {
    e.preventDefault();
    try { localStorage.removeItem(CHIAVE); } catch (err) { /* niente da togliere */ }
    location.href = '/anima/dashboard/';
  });
})();
