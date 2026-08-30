# IL RITO — come si entra in ANIMA GAME

> ⚠️ **Perché questo file nasce il 30/08, tardi.** Il rito è il gesto più importante del
> gioco: senza, non entra nessuno. Ed era scritto **da nessuna parte**. Cercato il 30/08 in
> tutti e cinque i repo: l'unica traccia era una riga in `animagame-site/assets/scheda.js`
> — `arcano: null, // il tarocco arriva a settembre, con la Porta` — e un accenno nel
> README. Tutto il resto viveva nella testa del Direttore e in chat perdute.
> 📜 **Regola che ne esce:** se una cosa la sa solo una persona, non è una decisione presa —
> è una decisione a rischio. Il momento di scriverla è quando la si dice ad alta voce.

## Il rito, dalla voce del Direttore (30/08)

1. Il giocatore riceve **a casa** un tarocco personalizzato, con sopra un **adesivo speciale**.
2. Ci si **incontra di persona**.
3. Il Direttore **spiega a voce le finalità del gioco**.
4. Se tutto va bene, **attiva il tarocco** con un **anello smart** (o strumento simile).
5. Da quel momento il giocatore accede alla propria pagina e può usare le stanze.

**Scelta già fatta e motivata:** all'inizio si era pensato a un **chip installato**; l'anello
si è rivelato migliore. Non si torna al chip senza una ragione nuova.

## Cosa fa cadere questo rito

Il rito **sostituisce** l'impianto di verifica costruito ad agosto (`docs/v/<ID>/`,
`build_card_pubblica.py`, le due impronte SHA-256). Quell'impianto faceva due mestieri:

| Mestiere | Come funzionava | Perché cade |
|---|---|---|
| **La porta** | Il portatore digitava a mano il codice a 12 caratteri stampato sul retro | L'adesivo si appoggia al telefono. Niente da digitare, niente da sbagliare — e il codice digitato *aveva già* prodotto un guasto: il 09/08 è servita una tabella di caratteri confondibili perché chi leggeva «2» dove c'era «Z» veniva respinto |
| **La prova** | Una pagina pubblica dichiarava «questa tessera è autentica» | La prova ora sei **tu**, di persona, mentre guardi in faccia il giocatore. Più forte di una pagina web — e in un gioco a invito nessuno deve verificare la tessera di un altro |

📌 **Conseguenza operativa:** le pagine `/v/SYS-xx` e il QR stampato **non hanno più un
mestiere**. Si spengono. E con loro cade l'unica obiezione tecnica a mettere Cloudflare
Access uniforme davanti a cyberboomer.io.

## La domanda aperta che il rito porta con sé — materia SQUELCH

Un adesivo NFC contiene **un indirizzo**. Chi appoggia il telefono apre quell'indirizzo.
Se l'indirizzo basta per entrare, allora **chiunque trovi il tarocco entra**: il tarocco
diventa una chiave di casa.

Non è un difetto del piano: è una scelta di progetto, e va fatta con gli occhi aperti.

- **A · Il tarocco è la chiave.** Semplice, rituale, coerente con l'oggetto. Chi lo perde
  perde l'accesso finché il Direttore non lo revoca.
- **B · Tarocco + qualcosa che sa solo lui** (una parola scelta durante il rito). Due
  fattori: chi trova il tarocco non entra. Costa un passaggio in più al momento del rito.

**Raccomandazione di D.R.A.G.O., non ancora ratificata:** partire con **A** — dieci
giocatori, il Direttore li conosce tutti di persona, può revocare a mano — **e progettare
la revoca fin dal primo giorno**. Il primo tarocco perso arriverà; senza revoca l'unica
risposta sarebbe «rifacciamo tutto».

## Cosa resta da decidere

1. **A o B** (sopra).
2. **Come si revoca** un tarocco perso, e chi può farlo.
3. **Cosa contiene esattamente l'adesivo** — un indirizzo con dentro un identificativo? un
   segreto? Cambia tutto il resto, ed è la prima cosa da fissare.
4. Se il tarocco sia **anche** l'oggetto che porta l'arcano del giocatore (`scheda.js`
   prevede già un campo `arcano`, oggi `null`), o se le due cose siano separate.

— scritto da D.R.A.G.O. il 2026-08-30, dalla voce del Direttore, alla prima occasione in
cui è stato detto ad alta voce
