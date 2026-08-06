/* IL SIGILLO — logica della pagina di verifica.
   L'ID arriva da body[data-card-id] (cartella per card, es. /anima/verifica/SYS-01/)
   oppure dalla query string (?id=SYS-01) sulla pagina generica.
   Legge un JSON pubblico per card. Nel JSON pubblico NON ci sono dati personali,
   né seriale né impronta: quelli restano nel backend, dietro consenso. */
(function () {
  var body = document.body;
  var base = body.getAttribute('data-base') || '';
  var id = body.getAttribute('data-card-id') ||
           new URLSearchParams(location.search).get('id') || '';
  id = id.trim().toUpperCase();

  var vEsito = document.getElementById('esito');
  var vPill = document.getElementById('pill');
  var vId = document.getElementById('id');
  var vNum = document.getElementById('num');
  var vData = document.getElementById('data');
  var pannello = document.getElementById('pannello');
  var entra = document.getElementById('entra');
  var collaudo = document.getElementById('collaudo');

  function mostra(stato, esito, dati) {
    pannello.classList.remove('ko', 'attesa');
    if (stato) pannello.classList.add(stato);
    vEsito.textContent = esito;
    vPill.textContent = dati.stato || '—';
    vId.textContent = dati.card_id || id || '—';
    // La carta 0 esiste (è quella dell'Overlord) e in JavaScript lo zero è "falso":
    // con un controllo di verità mostrava '—' proprio sulla prima card che verrà
    // scansionata. Si controlla l'assenza del dato, non il suo valore.
    vNum.textContent = (dati.numero === null || dati.numero === undefined)
      ? '—'
      : String(dati.numero).padStart(2, '0') + '/' + (dati.totale || '—');
    vData.textContent = dati.emessa || '—';
    // L'area personale deve sapere quale card ha aperto la porta. Percorso assoluto:
    // questa stessa pagina è servita da due indirizzi (/v/<ID>/ stampato sulla card
    // e /anima/verifica/<ID>/ storico), e un relativo darebbe due risultati diversi.
    if (dati.card_id || id) {
      entra.href = '/anima/dashboard/?id=' + encodeURIComponent(dati.card_id || id);
    }
    entra.hidden = stato !== null;
    if (dati.collaudo) collaudo.hidden = false;
  }

  if (!id || !/^[A-Z0-9-]{3,20}$/.test(id)) {
    mostra('attesa', 'NESSUN ID', { stato: 'in attesa di un ID' });
    return;
  }

  fetch(base + 'dati/' + id + '.json', { cache: 'no-store' })
    .then(function (r) {
      if (!r.ok) throw new Error('404');
      return r.json();
    })
    .then(function (d) {
      if (d.stato === 'VERIFICATA') mostra(null, 'AUTENTICA', d);
      else mostra('ko', 'NON AUTENTICA', d);
    })
    .catch(function () {
      mostra('ko', 'NON AUTENTICA', { card_id: id, stato: 'card non riconosciuta' });
    });
})();
