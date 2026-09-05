"""Collaudo della porta: si apre davvero, e mostra «Chi fa cosa»?
Nessun numero dichiarato: si legge quello che il browser ha davvero reso."""
import os, sys, re
from playwright.sync_api import sync_playwright

FRASE = open(os.environ["REGIA_FILE"], encoding="utf-8").read().splitlines()[0].strip()
PAG = "file:///home/user/anima-console/docs/index.html"
esiti = []

def prova(nome, cond, dettaglio=""):
    esiti.append((cond, nome, dettaglio))
    print(("✓ " if cond else "✗ ") + nome + ((" — " + dettaglio) if dettaglio else ""))

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    for larghezza in (390, 1280):
        p = b.new_page(viewport={"width": larghezza, "height": 900})
        errori = []
        p.on("pageerror", lambda e: errori.append(str(e)))
        p.goto(PAG)

        # 1. a lucchetto chiuso non si legge niente della squadra
        chiuso = p.inner_text("body")
        spie = [s for s in ("SQUELCH", "KIROSHI", "JUDY", "CHRONO", "caposquadra", "provino") if s.lower() in chiuso.lower()]
        prova(f"[{larghezza}] a lucchetto chiuso nessuna sigla visibile", not spie, str(spie))

        # 2. frase sbagliata non apre
        p.fill("input", "frase-sbagliata-lunga")
        p.keyboard.press("Enter")
        p.wait_for_timeout(2500)
        prova(f"[{larghezza}] frase sbagliata NON apre", "chi fa cosa" not in p.inner_text("body").lower())

        # 3. frase giusta apre
        p.fill("input", FRASE)
        p.keyboard.press("Enter")
        p.wait_for_selector("#chiudi", state="visible", timeout=30000)
        testo = p.inner_text("body")
        prova(f"[{larghezza}] frase giusta apre", p.is_visible("#banco"))
        prova(f"[{larghezza}] c'è la sezione «Chi fa cosa»", "chi fa cosa" in testo.lower())

        # 4. il ruolino c'è per intero — 7 agenti veri, 5 posti sulla carta
        righe_veri = p.eval_on_selector_all(
            "table", "ts => ts.map(t => t.rows.length)")
        prova(f"[{larghezza}] tabelle rese: {righe_veri}", len(righe_veri) >= 3, str(righe_veri))
        for sigla in ("JUDY", "SQUELCH", "ECHO", "KIROSHI", "BRAINDANCE", "PROVINO", "COLLAUDO-SUPERFICI"):
            prova(f"[{larghezza}] {sigla} in tabella", sigla in testo)
        # Dal 31/08 la porta mostra le CASE DI LAVORO vere di ROOT_CLODE al posto
        # dei «posti sulla carta»: la prova va aggiornata, perche' pretendeva il
        # comportamento vecchio — che era sbagliato.
        for casa in ("SUONO", "FLUX", "SHUTTER", "CHRONO", "ROGUE", "kiroshi-interno"):
            prova(f"[{larghezza}] casa di lavoro {casa}", casa in testo)
        prova(f"[{larghezza}] i «posti sulla carta» non compaiono piu'", "TBFIND" not in testo)
        prova(f"[{larghezza}] le case portano una data di STATO", "2026-08-" in testo)

        # 5. niente scroll orizzontale: la tabella non deve sfondare il telefono
        sfonda = p.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
        prova(f"[{larghezza}] nessuno scorrimento orizzontale", not sfonda,
              p.evaluate("document.documentElement.scrollWidth + 'px vs ' + document.documentElement.clientWidth + 'px'"))

        prova(f"[{larghezza}] nessun errore JS", not errori, "; ".join(errori)[:200])
        p.screenshot(path=f"/tmp/claude-0/-home-user/3981b954-c276-5a58-bc91-a130aa9128c4/scratchpad/porta-{larghezza}.png", full_page=True)
        p.close()
    b.close()

falliti = [e for e in esiti if not e[0]]
print(f"\n{len(esiti)-len(falliti)}/{len(esiti)} passati")
sys.exit(1 if falliti else 0)
