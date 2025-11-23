# Slow Reveal Video Batch Tool

Applicazione desktop cross-platform (macOS e Windows) che permette di caricare più video verticali e applicare un effetto “slow reveal” dal basso verso l’alto, simulando un movimento di camera progressivo con zoom controllato.

## Requisiti

- Python 3.10 o superiore
- `ffmpeg` installato e disponibile nel `PATH` (MoviePy ne fa uso dietro le quinte)

## Installazione rapida

```bash
python -m venv .venv
source .venv/bin/activate  # su Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Avvio dell’interfaccia grafica

```bash
python -m slowreveal
```

### Funzionalità principali

- Caricamento multiplo di file video (`.mp4`, `.mov`, `.mkv`, ecc.)
- Selezione della cartella di destinazione degli export
- Parametri regolabili:
  - `Zoom factor`: controlla quanto stringere l’inquadratura (valori > 1)
  - `Easing power`: gestisce la curva di movimento (valori < 1 velocizzano l’inizio)
  - `Suffisso output`: testo aggiunto al nome file esportato
- Log in tempo reale, con segnalazione di eventuali clip non verticali

## Creare un eseguibile scaricabile

> Nota: per distribuire file “scaricabili” è consigliato generare gli eseguibili con [PyInstaller](https://pyinstaller.org/). I passaggi devono essere ripetuti separatamente su macOS e Windows, così da produrre binari nativi per ciascuna piattaforma.

### macOS (.app o binario)

```bash
python -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --windowed --onefile \
  --name SlowRevealApp \
  src/slowreveal/app.py
```

- Il risultato si trova in `dist/SlowRevealApp`. Potrai zipparlo e condividerlo.
- Per una classica app bundle (`.app`) ometti `--onefile`.

### Windows (.exe)

Esegui dal prompt con ambiente virtuale attivo:

```powershell
python -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --windowed --onefile `
  --name SlowRevealApp `
  src/slowreveal/app.py
```

- Il file finale `SlowRevealApp.exe` sarà in `dist\`.
- Distribuiscilo insieme alla cartella `ffmpeg` se gli utenti non hanno ffmpeg installato.

## Struttura del progetto

```
src/slowreveal/
├── __init__.py              # metadata del pacchetto
├── __main__.py              # entry point `python -m slowreveal`
├── app.py                   # interfaccia Tkinter
└── processor.py             # logica di crop dinamico con MoviePy
```

## Suggerimenti

- Per ottenere un effetto più drammatico aumenta `Zoom factor` (es. 2.0).
- Usa `Easing power < 1` per far partire più velocemente il movimento (stile reveal).
- I video orizzontali vengono comunque elaborati ma riceverai un avviso nel log.