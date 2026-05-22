# CoreTune v2.0.0

**CoreTune** è una suite di ottimizzazione per Windows potente e intuitiva, sviluppata da **Aura**. Scritta in Python con un'interfaccia moderna basata su Tkinter, permette di monitorare le prestazioni del sistema in tempo reale ed eseguire script PowerShell per mantenere il PC veloce e pulito.

![Licenza](https://img.shields.io/badge/license-AGPL-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## 🚀 Caratteristiche Principali

*   **Dashboard Panoramica**: Visualizzazione immediata dell'uso di CPU, RAM e Disco con azioni rapide per la manutenzione.
*   **Ottimizzazione Avanzata**: Esecuzione di script per la pulizia dei file temporanei, della cache di Discord e attivazione della Modalità Prestazioni.
*   **Monitoraggio Real-Time**: Grafici della cronologia CPU e indicatori live per monitorare l'hardware.
*   **Diagnostica di Sistema**: Controlli di integrità per verificare la presenza di PowerShell, lo spazio su disco e lo stato dei moduli di monitoraggio.
*   **Consigli Intelligenti**: Una raccolta di guide e suggerimenti esperti per migliorare le prestazioni del PC.
*   **Registro Attività**: Log dettagliato di ogni operazione eseguita per la massima trasparenza.

## 🛠️ Tecnologie Utilizzate

*   **Linguaggio**: Python 3.x
*   **Interfaccia Grafica**: Tkinter (con supporto DPI Aware per schermi moderni)
*   **Monitoraggio Hardware**: `psutil` (opzionale, consigliato)
*   **Automazione**: PowerShell (tramite subprocess)

## 📥 Installazione

1.  **Installa il .zip**
    Installa il file .zip dalle release. Ti consigliamo di installare l'ultima versione disponibile.

2. **Estrarre il .zip**
    Estrai il .zip in una directory a piacere.

3. **Avvia "CoreTube.exe"**
    Avvia il file CoreTune.exe per l'uso.

## 📦 Compila
Per ottenere il codice sorgente in locale e farlo funzionare correttamente.

1.  **Clona il repository**:
    ```bash
    git clone https://github.com/madebyanto/coretune.git
    cd CoreTune
    ```

2.  **Installa le dipendenze**:
    CoreTune può funzionare in modalità simulata, ma per dati reali è necessario `psutil`:
    ```bash
    pip install psutil
    ```

3.  **Configura gli script**:
    Assicurati che i file `.ps1` siano presenti nella cartella `scripts/` nella root del progetto.

4.  **Avvia l'applicazione**:
    ```bash
    python main.py
    ```

## 📂 Struttura del Progetto

```text
CoreTune/
├── main.py              # Punto di ingresso dell'applicazione
├── scripts/             # Directory contenente gli script PowerShell (.ps1)
│   ├── clean_temp.ps1
│   ├── discord.ps1
│   └── performance_mode.ps1
└── README.md            # Documentazione del progetto
```

## 📝 Script di Ottimizzazione

CoreTune si appoggia a script PowerShell esterni per le operazioni di sistema:
*   **Pulisci File Temporanei**: Svuota le cartelle Temp e Prefetch di Windows.
*   **Pulizia Discord**: Rimuove cache e file inutilizzati per velocizzare l'app Discord.
*   **Modalità Prestazioni**: Regola i piani energetici e gli effetti visivi di Windows.

## ⚠️ Requisiti di Sistema

*   Windows 10 o Windows 11.
*   Python 3.10 o superiore.
*   Permessi di amministratore (necessari per alcuni script di ottimizzazione).

## 🤝 Contribuire

I contributi sono benvenuti! Se hai suggerimenti, nuovi script o bug da segnalare, visita https://support.aurastudioitalia.it

---

**Sviluppato con amore da Aura**

*Nota: Questo strumento è fornito "così com'è". Sebbene gli script siano progettati per essere sicuri, si consiglia sempre di effettuare un backup o un punto di ripristino prima di eseguire ottimizzazioni profonde del sistema.*