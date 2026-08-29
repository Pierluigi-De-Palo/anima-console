# PROTOCOLLO DI DISPATCH — cosa fa D.R.A.G.O. quando arriva una COMMESSA

Questo sostituisce il testimone passato di mano in mano: l'identità dei caposquadra
vive in `.claude/agents/*.md` (versionata in git), la commessa arriva dal modulo
(`COMMESSA-TEMPLATE.md` / `docs/schede/commessa.html`), e il dispatch segue questi
passi — in ogni sessione, locale o remota.

## I sei passi

1. **TRIAGE** — leggi la commessa e scomponila in lotti: per ognuno, il dipartimento
   competente (una riga). Le domande al Direttore si fanno QUI, tutte insieme, una
   volta sola: dopo il via non lo si interrompe più. Il routing del Dipartimento
   Verità segue l'accordo ratificato il 2026-07-12: ditta/venditore → KIROSHI
   (prodotti inclusi: prassi coerente a valle, registrata in `SQUADRA.md`);
   persona o notizia/claim → BRAINDANCE (il filtro pubblica/privata lo applica
   BRAINDANCE: sui privati non lavora nessuno); notizia su un'azienda →
   BRAINDANCE con dati-ditta da KIROSHI; imprenditore: persona → BRAINDANCE,
   impresa → KIROSHI.

2. **DISPATCH** — un subagent per lotto. Il prompt del subagent = il contenuto del
   file-persona del caposquadra (`.claude/agents/<nome>.md`) + il lotto + i vincoli
   della commessa. Dove l'ambiente carica gli agent nativamente basta il nome; dove
   no, si legge il file e lo si inietta — il risultato è lo stesso. Lotti
   indipendenti partono in parallelo. Modelli secondo VMG: lettura=haiku,
   canone=sonnet, codice=opus (già scritti nel frontmatter di ogni caposquadra).
   Workflow multi-agente estesi solo con la parola «ultracode» del Direttore.

3. **VERIFICA INCROCIATA** — ogni output destinato al cliente passa da un
   verificatore avversario (un subagent col mandato di CONFUTARE: fatti contro
   fonti, canone visivo, schema, confini). È il passo che rende l'output vendibile:
   al primo giro vero ha scovato una causa legale taciuta e due errori fattuali.

4. **ASSEMBLAGGIO** — D.R.A.G.O. integra le correzioni, unisce i lotti, applica le
   regole di consegna: ogni HTML destinato al Direttore anche in `docs/`; mai MD al
   Direttore, solo HTML; dati sensibili e percorsi interni mai in superfici
   pubbliche (guardia privacy).

5. **CONSEGNA** — file in chat + patch per il repo (`git format-patch --stdout`,
   si applica dal Mac con `git am`; le sessioni remote NON possono scrivere su
   GitHub — verificato 17/08) + eventuale script `gh` per issue/etichette.
   Firma composta sugli artefatti: `— creato da <CAPOSQUADRA> · su commessa del
   Direttore · dispatch D.R.A.G.O. · AAAA-MM-GG` (più la catena di direzione dove
   c'è, es. `su direzione JUDY`).

6. **RATIFICA E REGISTRO** — niente diventa pubblico senza l'ok del Direttore: la
   ratifica precede la pubblicazione (canone), e il push resta suo. Conflitti tra
   caposquadra non si nascondono: si marcano entrambe le versioni e decide il
   Direttore. A commessa chiusa, una riga di registro in `squadra/SQUADRA.md`
   (sezione Registro commesse).

## Regole trasversali che il dispatch fa rispettare

- **Non toccare l'impianto altrui**: ogni file ha un padrone; si costruisce accanto
  o si dichiara il cambio.
- **Un filtro che non trova niente non dice «non c'è niente», dice «non vedo
  niente»**: le code si guardano anche senza filtro.
- **I numeri vivi vengono da file/script o restano un trattino**; le pagine scritte
  a mano invecchiano in silenzio.
- **Il collaudo precede la dichiarazione**: pagine nel browser, guardie con input
  ostili, patch su clone pulito.
- **Spesa**: subagent > sessione principale per ogni lavoro delegabile; la
  scomposizione in lotti è anche la politica di risparmio.
- **I piani non muoiono con le sessioni** (lezione del 19/08: il piano Linux
  proposto in un'altra chat è andato perso — le sessioni sono container
  temporanei). Ogni piano approvato si esporta in HTML e si consegna col
  lavoro; la casa è `ROOT_CLODE/PIANI/`, l'archivia il Direttore. Un piano
  che vive solo in chat è un piano già perso.

— creato da D.R.A.G.O., 2026-08-17
