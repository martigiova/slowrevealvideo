# Slow Reveal Video Batch Tool

App desktop per Windows e macOS che applica automaticamente un effetto “slow reveal” dal basso verso l’alto su interi batch di video verticali. Carica tutte le clip, scegli la cartella di export e lascia che l’app aggiusti il movimento di camera con zoom progressivo ed easing controllato.

---

## Step 1 – Scarica il build pronto
1. Apri l’ultima esecuzione riuscita del workflow *Build SlowRevealApp* su GitHub Actions: https://github.com/martigiova/slowrevealvideo/actions
2. Accedi con il tuo account GitHub (gli artifact richiedono una sessione autenticata).
3. Nella sezione **Artifacts** scarica il pacchetto adatto:
   - `SlowRevealVideo_windows.zip` per Windows
   - `SlowRevealVideo_macOS.zip` per macOS (se disponibile)

## Step 2 – Estrai lo ZIP
1. Vai nella cartella dei download e trova il file ZIP appena scaricato.
2. Estrai tutto il contenuto (su alcuni browser potresti dover estrarre due volte se il ZIP contiene una cartella annidata).
3. All’interno troverai:
   - `SlowRevealVideo.exe` (oppure `SlowRevealVideo.app` su Mac)
   - `ffmpeg`/`ffprobe` già inclusi
   - `README.txt` con scorciatoie e FAQ
   - Cartella `exports/` vuota dove finiscono i video elaborati
   - Eventuali clip di esempio nella cartella `samples/`

## Step 3 – Avvia l’applicazione
1. Su Windows fai doppio clic su `SlowRevealVideo.exe`.
2. Se SmartScreen o Gatekeeper mostrano un avviso, clicca **More info → Run anyway** (o *Apri comunque* su macOS). Il binario non è firmato, quindi l’avviso è normale.
3. Mantieni aperta la cartella dell’app mentre lavori: il programma ha bisogno dei file `ffmpeg` affiancati.

## Step 4 – Carica i video verticali
1. Premi **Aggiungi video…** e seleziona tutte le clip `.mp4`, `.mov`, `.mkv`, ecc. che vuoi elaborare (anche 20+ alla volta).
2. Rimuovi eventuali clip errate con **Rimuovi selezionati** oppure **Svuota lista** per ripartire da zero.
3. Il log segnalerà se una clip non è verticale; viene comunque elaborata ma riceverai un ⚠️ di promemoria.

## Step 5 – Imposta cartella di export e parametri
- **Cartella di destinazione**: di default è la cartella dell’app. Clicca **Scegli cartella…** per esportare su un SSD veloce o su una cartella condivisa.
- **Zoom factor (>= 1.1)**: quanto “stringe” il crop nel tempo. Valori tra 1.6 e 2.2 funzionano per la maggior parte dei Reels/TikTok.
- **Easing power**: controlla la curva di animazione (0.8–1.0 per reveal graduale; < 0.8 per partenza veloce).
- **Suffisso output**: testo aggiunto al nome file, es. `_slowreveal` o `_zoom`.

## Step 6 – Avvia la conversione
1. Clicca **Avvia elaborazione**.
2. Segui la barra di avanzamento e il log per ogni clip (`✅ clip.mov → clip_slowreveal.mp4`).
3. Al termine apri la cartella di export: troverai i nuovi video già pronti per Premiere/CapCut.

## Suggerimenti & Troubleshooting
- **Batch grandi (50+ clip)**: spezzali in blocchi da 20–25 se lavori su laptop.
- **Clip con bande nere**: aumenta lo `Zoom factor` o rifinisci successivamente in editing.
- **ffmpeg non trovato**: non spostare gli eseguibili inclusi; tieni tutto nella stessa cartella estratta.
- **Prestazioni migliori**: lavori più veloci su SSD NVMe e con alimentazione collegata.

---

## Modalità sviluppatore

### Requisiti
- Python 3.10+
- `ffmpeg` presente nel `PATH`

### Setup locale
```bash
python -m venv .venv
source .venv/bin/activate        # su Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m slowreveal
```

### Creare build distribuibili
Esegui i comandi sul sistema di destinazione (Windows per `.exe`, macOS per `.app`).

```bash
python -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --windowed --onefile \
  --name SlowRevealVideo \
  src/slowreveal/app.py
```

Output in `dist/SlowRevealVideo*`. Comprimi la cartella insieme agli eseguibili `ffmpeg`/`ffprobe` se vuoi fornire un pacchetto plug-and-play.

### Struttura principale
```
src/slowreveal/
├── __main__.py      # entry point `python -m slowreveal`
├── app.py           # interfaccia Tkinter con batch UI
└── processor.py     # logica di zoom progressivo + MoviePy
```

Per un effetto più marcato aumenta `Zoom factor`; per reveal rapidi imposta `Easing power < 1`. I video orizzontali vengono comunque processati, ma il log avvisa così puoi decidere se scartarli.