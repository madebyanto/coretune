import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import os
import platform
import datetime
import queue
import sys

APP_NAME = "CoreTune"
APP_VERSION = "2.0.0"
APP_SUBTITLE = "Suite di Ottimizzazione Sistema — Aura Studio"
SCRIPTS_PATH = "scripts"

# ─── Color Palette ────────────────────────────────────────────────────────────
BG_BASE        = "#f3f3f3"
BG_PANEL       = "#ffffff"
BG_SIDEBAR     = "#202020"
BG_SIDEBAR_HV  = "#2d2d2d"
BG_HEADER      = "#0067c0"
BG_CARD        = "#fafafa"
BG_CARD_DARK   = "#efefef"
ACCENT         = "#0067c0"
ACCENT_HOVER   = "#0078d4"
ACCENT_LIGHT   = "#cce4f7"
DANGER         = "#c42b1c"
DANGER_HOVER   = "#d13438"
SUCCESS        = "#107c10"
WARNING        = "#ca5010"
TEXT_PRIMARY   = "#1a1a1a"
TEXT_SECONDARY = "#5c5c5c"
TEXT_TERTIARY  = "#999999"
TEXT_ON_DARK   = "#ffffff"
TEXT_ON_DARK2  = "#cccccc"
BORDER         = "#e0e0e0"
BORDER_DARK    = "#c8c8c8"
STATUSBAR_BG   = "#f0f0f0"

FONT_HEADING = ("Segoe UI", 10, "bold")
FONT_BODY    = ("Segoe UI", 9)
FONT_SMALL   = ("Segoe UI", 8)
FONT_MONO    = ("Consolas", 8)

# ─── Performance Tips ─────────────────────────────────────────────────────────
PERFORMANCE_TIPS = [
    ("CPU",      "Disabilita i programmi di avvio non necessari tramite Gestione attività → scheda Avvio per ridurre il tempo di avvio e il carico della CPU."),
    ("RAM",      "Imposta manualmente la memoria virtuale: Sistema → Avanzate → Impostazioni prestazioni → Avanzate → Cambia. Consigliato: 1.5× la tua RAM."),
    ("Disco",    "Mantieni almeno il 15% del tuo disco di sistema libero. Windows ha bisogno di questo spazio per la memoria virtuale e gli aggiornamenti."),
    ("Rete",     "Disabilita gli aggiornamenti automatici durante le ore di punta tramite Windows Update → Ore attive."),
    ("Sicurezza", "Esegui una scansione rapida di Windows Defender settimanalmente. La protezione in tempo reale dovrebbe essere sempre ATTIVA."),
    ("CPU",      "Imposta il piano energetico su 'Bilanciato' sui laptop, 'Prestazioni elevate' sui desktop collegati."),
    ("RAM",      "Chiudi le schede del browser che non ti servono — ogni scheda di Chrome/Edge utilizza 50–150 MB di RAM."),
    ("Disco",    "Esegui Pulizia disco mensilmente. Rimuove in sicurezza file di sistema, cache degli aggiornamenti e miniature."),
    ("Generale", "Riavvia il PC almeno una volta a settimana. Cancella le perdite di memoria e applica gli aggiornamenti in sospeso."),
    ("GPU",      "Aggiorna i driver della GPU trimestralmente tramite NVIDIA GeForce Experience o AMD Adrenalin."),
    ("Rete",     "Usa una connessione cablata per giochi o videochiamate. Ethernet è 10 volte più stabile del WiFi."),
    ("Generale", "Disabilita gli effetti visivi per le prestazioni: Sistema → Avanzate → Prestazioni → Regola per le migliori prestazioni."),
    ("Disco",    "Deframmenta gli HDD mensilmente; non deframmentare mai gli SSD — Windows gestisce gli SSD automaticamente."),
    ("CPU",      "Monitora la temperatura della CPU. Temperature sostenute sopra i 90°C indicano un raffreddamento insufficiente o un carico eccessivo."),
    ("RAM",      "16 GB è il punto ideale per i carichi di lavoro del 2024. 8 GB causa uno swapping costante su Windows moderno."),
    ("Sicurezza", "Abilita BitLocker sui dispositivi portatili. La perdita di dati per furto è molto più comune del guasto hardware."),
    ("Generale", "Usa Gestione attività (Ctrl+Maiusc+Esc) → scheda Prestazioni per identificare il tuo collo di bottiglia in tempo reale."),
    ("Rete",     "Il DNS può influenzare la velocità di navigazione. Prova Cloudflare (1.1.1.1) o Google (8.8.8.8) per ricerche più veloci."),
    ("Disco",    "Sposta giochi e app di grandi dimensioni su un'unità secondaria per mantenere il tuo SSD di sistema veloce e sano."),
    ("CPU",      "Se non stai giocando, imposta lo stato massimo del processore al 99% — questo previene il calore inutile del turbo boost."),
]

# ─── Script Runner ────────────────────────────────────────────────────────────
def run_script(script_name, log_callback=None):
    path = os.path.join(SCRIPTS_PATH, script_name)
    if not os.path.exists(path):
        msg = f"[ATTENZIONE] Script non trovato: {path}"
        if log_callback:
            log_callback(msg, "warn")
        return False, msg
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", path],
            capture_output=True, text=True, timeout=120
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if log_callback:
            for line in out.splitlines():
                log_callback(f"  {line}", "info")
            for line in err.splitlines():
                log_callback(f"  {line}", "warn")
        return result.returncode == 0, out
    except FileNotFoundError:
        msg = "[ERRORE] PowerShell non trovato."
        if log_callback:
            log_callback(msg, "error")
        return False, msg
    except subprocess.TimeoutExpired:
        msg = f"[ERRORE] Script scaduto: {script_name}"
        if log_callback:
            log_callback(msg, "error")
        return False, msg
    except Exception as e:
        msg = f"[ERRORE] {e}"
        if log_callback:
            log_callback(msg, "error")
        return False, msg


# ─── System Monitor ───────────────────────────────────────────────────────────
class SystemMonitor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.data = {
            "cpu": 0.0, "ram": 0.0, "ram_used": 0.0, "ram_total": 0.0,
            "disk": 0.0, "disk_used": 0.0, "disk_total": 0.0,
            "cpu_temp": None, "uptime": "", "processes": 0,
            "cpu_name": platform.processor() or "Unknown CPU",
        } # "CPU Sconosciuta"
        self._callbacks = []
        self._psutil_available = False
        self._try_import_psutil()

    def _try_import_psutil(self):
        try:
            import psutil
            self._psutil = psutil
            self._psutil_available = True
        except ImportError:
            self._psutil_available = False

    def add_callback(self, fn):
        self._callbacks.append(fn)

    def _notify(self):
        for cb in self._callbacks:
            try:
                cb(self.data.copy())
            except Exception:
                pass

    def _collect(self):
        if not self._psutil_available:
            import random
            self.data["cpu"]       = round(random.uniform(5, 45), 1)
            self.data["ram"]       = round(random.uniform(40, 80), 1)
            self.data["ram_used"]  = round(random.uniform(4, 12), 2)
            self.data["ram_total"] = 16.0
            self.data["disk"]      = round(random.uniform(30, 70), 1)
            self.data["disk_used"] = round(random.uniform(100, 400), 0)
            self.data["disk_total"]= 512.0
            self.data["processes"] = random.randint(120, 250)
            self.data["uptime"]    = self._uptime_str()
            return

        p = self._psutil
        self.data["cpu"] = p.cpu_percent(interval=None)
        vm = p.virtual_memory()
        self.data["ram"]       = vm.percent
        self.data["ram_used"]  = round(vm.used / 1e9, 2)
        self.data["ram_total"] = round(vm.total / 1e9, 2)
        try:
            du = p.disk_usage("C:\\")
            self.data["disk"]       = du.percent
            self.data["disk_used"]  = round(du.used / 1e9, 1)
            self.data["disk_total"] = round(du.total / 1e9, 1)
        except Exception:
            pass
        try:
            self.data["processes"] = len(p.pids())
        except Exception:
            pass
        self.data["uptime"] = self._uptime_str()
        try:
            temps = p.sensors_temperatures()
            if temps:
                for key in ["coretemp", "k10temp", "cpu_thermal"]:
                    if key in temps and temps[key]:
                        self.data["cpu_temp"] = round(temps[key][0].current, 1)
                        break
        except Exception:
            pass

    def _uptime_str(self):
        try:
            if self._psutil_available:
                sec = time.time() - self._psutil.boot_time()
            else:
                sec = time.time() % 86400
            return f"{int(sec//3600)}h {int((sec%3600)//60)}m"
        except Exception:
            return "N/A"

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        if self._psutil_available:
            self._psutil.cpu_percent(interval=None)
        time.sleep(1)
        while self.running:
            self._collect()
            self._notify()
            time.sleep(2)


# ─── Main App ─────────────────────────────────────────────────────────────────
class CoreTuneApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION} — {APP_SUBTITLE}")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG_SIDEBAR)

        self.current_tab      = tk.StringVar(value="dashboard")
        self.status_var       = tk.StringVar(value="Pronto")
        self.log_queue        = queue.Queue()
        self.tip_index        = 0
        self.operation_running= False
        self._cpu_history     = []

        self.monitor = SystemMonitor()
        self.monitor.add_callback(self._on_monitor_update)
        self._build_ui()

        self.monitor.start()
        self._process_log_queue()
        self._rotate_tip()
        self._update_clock()

        self._log(f"CoreTune {APP_VERSION} initialized — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")
        self._log(f"System: {platform.system()} {platform.release()} | Host: {platform.node()}", "info")
        if not self.monitor._psutil_available: # "psutil non installato — dati simulati attivi. Esegui: pip install psutil"
            self._log("psutil not installed — simulated data active. Run: pip install psutil", "warn")

    # ── Root layout ───────────────────────────────────────────────────────────
    def _build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = tk.Frame(self.root, bg=BG_SIDEBAR, width=210)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.columnconfigure(0, weight=1)
        sb.rowconfigure(1, weight=1)

        # Logo
        logo = tk.Frame(sb, bg=BG_HEADER, height=64)
        logo.grid(row=0, column=0, sticky="ew")
        logo.grid_propagate(False)
        tk.Label(logo, text="CoreTune", font=("Segoe UI", 16, "bold"),
                 bg=BG_HEADER, fg=TEXT_ON_DARK).place(x=16, y=10)
        tk.Label(logo, text="Aura Studio", font=FONT_SMALL,
                 bg=BG_HEADER, fg="#9fd6f7").place(x=18, y=36)

        # Nav
        nav = tk.Frame(sb, bg=BG_SIDEBAR)
        nav.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        self._nav_buttons = {}
        for tab_id, label in [
            ("dashboard",   "  Dashboard"),
            ("optimize",    "  Ottimizza"),
            ("monitor",     "  Monitor"),
            ("diagnostics", "  Diagnostica"),
            ("tips",        "  Consigli e Guide"),
            ("log",         "  Registro Attività"),
            ("settings",    "  Impostazioni"),
        ]:
            self._nav_buttons[tab_id] = self._nav_btn(nav, tab_id, label)

        # Footer
        foot = tk.Frame(sb, bg=BG_SIDEBAR)
        foot.grid(row=2, column=0, sticky="ew")
        tk.Label(foot, text=f"v{APP_VERSION}", font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg="#555555").pack(side="left", padx=14, pady=8)
        self._clock_lbl = tk.Label(foot, text="", font=FONT_SMALL,
                                   bg=BG_SIDEBAR, fg="#555555")
        self._clock_lbl.pack(side="right", padx=14, pady=8)

    def _nav_btn(self, parent, tab_id, label):
        btn = tk.Frame(parent, bg=BG_SIDEBAR, cursor="hand2", height=36)
        btn.pack(fill="x")
        btn.pack_propagate(False)

        ind = tk.Frame(btn, width=3, bg=BG_SIDEBAR)
        ind.pack(side="left", fill="y")

        lbl = tk.Label(btn, text=label, font=("Segoe UI", 9),
                       bg=BG_SIDEBAR, fg=TEXT_ON_DARK2, anchor="w")
        lbl.pack(side="left", fill="both", expand=True, padx=8)

        def click(e=None): self._switch_tab(tab_id)
        def enter(e):
            if self.current_tab.get() != tab_id:
                btn.configure(bg=BG_SIDEBAR_HV); lbl.configure(bg=BG_SIDEBAR_HV); ind.configure(bg=BG_SIDEBAR_HV)
        def leave(e):
            if self.current_tab.get() != tab_id:
                btn.configure(bg=BG_SIDEBAR); lbl.configure(bg=BG_SIDEBAR); ind.configure(bg=BG_SIDEBAR)

        for w in (btn, lbl, ind):
            w.bind("<Button-1>", click)
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)

        btn._ind = ind
        btn._lbl = lbl
        return btn

    def _switch_tab(self, tab_id):
        old = self.current_tab.get()
        if old == tab_id:
            return
        if old in self._nav_buttons:
            b = self._nav_buttons[old]
            b.configure(bg=BG_SIDEBAR)
            b._lbl.configure(bg=BG_SIDEBAR, fg=TEXT_ON_DARK2, font=("Segoe UI", 9))
            b._ind.configure(bg=BG_SIDEBAR)
        self.current_tab.set(tab_id)
        b = self._nav_buttons[tab_id]
        b.configure(bg=BG_SIDEBAR_HV)
        b._lbl.configure(bg=BG_SIDEBAR_HV, fg=TEXT_ON_DARK, font=("Segoe UI", 9, "bold"))
        b._ind.configure(bg=ACCENT)
        for tid, fr in self._tab_frames.items():
            if tid == tab_id:
                fr.grid(row=0, column=0, sticky="nsew")
            else:
                fr.grid_remove()

    # ── Main area ─────────────────────────────────────────────────────────────
    def _build_main(self):
        main = tk.Frame(self.root, bg=BG_BASE)
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)
        main.rowconfigure(1, weight=0)

        content = tk.Frame(main, bg=BG_BASE)
        content.grid(row=0, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        self._tab_frames = {}
        for tab_id, builder in [
            ("dashboard",   self._tab_dashboard),
            ("optimize",    self._tab_optimize),
            ("monitor",     self._tab_monitor),
            ("diagnostics", self._tab_diagnostics),
            ("tips",        self._tab_tips),
            ("log",         self._tab_log),
            ("settings",    self._tab_settings),
        ]:
            fr = tk.Frame(content, bg=BG_BASE)
            fr.columnconfigure(0, weight=1)
            fr.rowconfigure(0, weight=1)
            self._tab_frames[tab_id] = fr
            builder(fr)

        # Status bar
        bar = tk.Frame(main, bg=STATUSBAR_BG, height=24,
                       highlightthickness=1, highlightbackground=BORDER)
        bar.grid(row=1, column=0, sticky="ew")
        bar.grid_propagate(False)
        tk.Label(bar, textvariable=self.status_var, font=FONT_SMALL,
                 bg=STATUSBAR_BG, fg=TEXT_SECONDARY, anchor="w").pack(side="left", padx=10)
        self._sb_mon = tk.Label(bar, text="", font=FONT_SMALL,
                                bg=STATUSBAR_BG, fg=TEXT_SECONDARY)
        self._sb_mon.pack(side="right", padx=10)

        self._switch_tab("dashboard")

    # ── Shared helpers ────────────────────────────────────────────────────────
    def _page_header(self, parent, title, subtitle):
        """Blue header row. Uses pack inside itself; grid-places into parent row=0."""
        hdr = tk.Frame(parent, bg=BG_HEADER, height=56)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        tk.Label(hdr, text=title, font=("Segoe UI", 14, "bold"),
                 bg=BG_HEADER, fg=TEXT_ON_DARK, anchor="w").place(x=18, y=8)
        tk.Label(hdr, text=subtitle, font=FONT_SMALL,
                 bg=BG_HEADER, fg="#9fd6f7", anchor="w").place(x=20, y=32)
        parent.rowconfigure(0, weight=0)
        parent.rowconfigure(1, weight=1)

    def _scrollable(self, parent):
        """
        Returns a padded inner Frame suitable for grid children.
        The canvas sits at parent row=1, column=0.
        """
        canvas = tk.Canvas(parent, bg=BG_BASE, highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)

        inner = tk.Frame(canvas, bg=BG_BASE)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas(e):
            canvas.itemconfigure(win_id, width=e.width)
        def _on_wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        inner.bind("<Configure>", _on_inner)
        canvas.bind("<Configure>", _on_canvas)
        canvas.bind_all("<MouseWheel>", _on_wheel)

        padded = tk.Frame(inner, bg=BG_BASE)
        padded.pack(fill="both", expand=True, padx=16, pady=12)
        padded.columnconfigure(0, weight=1)
        return padded

    def _section(self, parent, title):
        """
        Returns (outer_frame, body_frame).
        outer uses pack for its header + body; body is pure grid-ready.
        Caller places outer with .grid() into the scrollable frame.
        """
        outer = tk.Frame(parent, bg=BG_PANEL,
                         highlightthickness=1, highlightbackground=BORDER)
        # header row — pack only inside outer
        hdr = tk.Frame(outer, bg=BG_CARD_DARK, height=30)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=title, font=FONT_HEADING,
                 bg=BG_CARD_DARK, fg=TEXT_PRIMARY).pack(side="left", padx=12, pady=6)
        # body frame — children will use grid
        body = tk.Frame(outer, bg=BG_PANEL)
        body.pack(fill="both", expand=True)
        return outer, body

    def _btn(self, parent, text, cmd, bg=BG_CARD_DARK, fg=TEXT_PRIMARY):
        """Clickable label button."""
        b = tk.Label(parent, text=text, font=FONT_BODY, bg=bg, fg=fg,
                     padx=14, pady=6, cursor="hand2", relief="flat", bd=0)
        hover_bg = ACCENT_HOVER if bg == ACCENT else (DANGER_HOVER if bg == DANGER else BORDER_DARK)
        b.bind("<Enter>", lambda e: b.configure(bg=hover_bg))
        b.bind("<Leave>", lambda e: b.configure(bg=bg))
        b.bind("<Button-1>", lambda e: cmd())
        return b

    # ── Metric card ───────────────────────────────────────────────────────────
    def _metric_card(self, parent, title, unit, color):
        card = tk.Frame(parent, bg=BG_PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
        card._val_var = tk.StringVar(value="—")
        # Everything inside card uses pack — card itself is placed by caller
        tk.Label(card, text=title, font=FONT_BODY, bg=BG_PANEL,
                 fg=TEXT_SECONDARY).pack(anchor="w", padx=14, pady=(12, 0))
        vf = tk.Frame(card, bg=BG_PANEL)
        vf.pack(fill="x", padx=14, pady=4)
        card._val_lbl = tk.Label(vf, textvariable=card._val_var,
                                 font=("Segoe UI", 28, "bold"), bg=BG_PANEL, fg=color)
        card._val_lbl.pack(side="left")
        tk.Label(vf, text=unit, font=("Segoe UI", 14),
                 bg=BG_PANEL, fg=TEXT_SECONDARY).pack(side="left", anchor="s", pady=6)
        bar_bg = tk.Frame(card, bg=BORDER, height=4)
        bar_bg.pack(fill="x", padx=14, pady=(0, 12))
        bar_bg.pack_propagate(False)
        card._bar    = tk.Frame(bar_bg, bg=color, height=4)
        card._bar.place(x=0, y=0, relheight=1, relwidth=0)
        card._color  = color
        card._bar_bg = bar_bg
        return card

    def _update_metric_card(self, card, val):
        card._val_var.set(f"{val:.1f}")
        pct = max(0.0, min(1.0, val / 100.0))
        card._bar.place_configure(relwidth=pct)
        color = DANGER if val >= 85 else (WARNING if val >= 65 else card._color)
        card._val_lbl.configure(fg=color)
        card._bar.configure(bg=color)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Dashboard
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_dashboard(self, parent):
        self._page_header(parent, "Dashboard", "Panoramica del sistema e azioni rapide")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)
        sf.columnconfigure(1, weight=1)
        sf.columnconfigure(2, weight=1)

        # ── Metric cards (row 0) ──
        self._dash_cards = {}
        for col, (key, title, unit, color) in enumerate([
            ("cpu",  "Utilizzo CPU",  "%", ACCENT),
            ("ram",  "Utilizzo RAM",  "%", SUCCESS),
            ("disk", "Utilizzo Disco", "%", WARNING),
        ]):
            c = self._metric_card(sf, title, unit, color)
            px = (0, 6) if col == 0 else (6, 6) if col == 1 else (6, 0)
            c.grid(row=0, column=col, padx=px, pady=(0, 12), sticky="ew")
            self._dash_cards[key] = c

        # ── System info + Quick actions (row 1) ──
        si_outer, si_body = self._section(sf, "Informazioni di Sistema")
        si_outer.grid(row=1, column=0, columnspan=2, padx=(0, 6), pady=(0, 12), sticky="nsew")
        si_body.columnconfigure(1, weight=1)
        
        self._si_lbls = {}
        for r, (key, label, val) in enumerate([
            ("os",     "Sistema Operativo", platform.system() + " " + platform.release()),
            ("host",   "Nome Host",         platform.node()),
            ("cpu",    "Processore",        (platform.processor() or "Sconosciuto")[:60]),
            ("arch",   "Architettura",     platform.machine()),
            ("python", "Versione Python",   platform.python_version()),
            ("uptime", "Tempo di Attività",           "—"),
            ("procs",  "Processi",        "—"),
            ("temp",   "Temperatura CPU",  "—"),
        ]):
            tk.Label(si_body, text=label + ":", font=FONT_BODY,
                     bg=BG_PANEL, fg=TEXT_SECONDARY, anchor="w").grid(
                row=r, column=0, sticky="w", padx=(14, 6), pady=3)
            lbl = tk.Label(si_body, text=val, font=("Segoe UI", 9, "bold"),
                           bg=BG_PANEL, fg=TEXT_PRIMARY, anchor="w")
            lbl.grid(row=r, column=1, sticky="w", padx=(0, 14), pady=3)
            self._si_lbls[key] = lbl
        tk.Frame(si_body, bg=BG_PANEL, height=6).grid(row=8, column=0)
        
        qa_outer, qa_body = self._section(sf, "Azioni Rapide")
        qa_outer.grid(row=1, column=2, pady=(0, 12), sticky="nsew")
        for label, cmd, bg, fg in [
            ("Ottimizza Tutto",         self._do_boost_all,    ACCENT,    TEXT_ON_DARK),
            ("Pulisci File Temporanei",  self._do_clean_temp,   BG_CARD,   TEXT_PRIMARY),
            ("Pulizia Discord",   self._do_discord,      BG_CARD,   TEXT_PRIMARY),
            ("Modalità Prestazioni",  self._do_perf_mode,    BG_CARD,   TEXT_PRIMARY),
            ("Apri Gestione Attività", self._open_taskmgr,    BG_CARD,   TEXT_PRIMARY),
        ]:
            self._btn(qa_body, label, cmd, bg, fg).pack(fill="x", padx=12, pady=3)
        tk.Frame(qa_body, bg=BG_PANEL, height=6).pack()
        
        # ── Tip of the Day (row 2) ── # "Consiglio del Giorno"
        tip_outer, tip_body = self._section(sf, "Consiglio del Giorno")
        tip_outer.grid(row=2, column=0, columnspan=3, pady=(0, 12), sticky="ew")
        self._tip_cat_lbl = tk.Label(tip_body, text="", font=FONT_SMALL,
                                     bg=BG_PANEL, fg=ACCENT)
        self._tip_cat_lbl.pack(anchor="w", padx=14, pady=(8, 2))
        self._tip_txt_lbl = tk.Label(tip_body, text="", font=FONT_BODY,
                                     bg=BG_PANEL, fg=TEXT_PRIMARY,
                                     wraplength=700, justify="left", anchor="w")
        self._tip_txt_lbl.pack(anchor="w", padx=14, pady=(0, 10))

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Optimize
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_optimize(self, parent):
        self._page_header(parent, "Ottimizza", "Esegui script di ottimizzazione per migliorare le prestazioni del sistema")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)
        sf.columnconfigure(1, weight=1)

        opts = [
            dict(id="boost_all",   title="Ottimizzazione Completa del Sistema",
                 desc="Esegue tutti gli script di ottimizzazione in sequenza: pulizia temporanei, pulizia Discord e attivazione della modalità prestazioni. Consigliato per una messa a punto completa.",
                 badge="CONSIGLIATO", badge_color=ACCENT, action=self._do_boost_all,
                 col=0, row=0, cs=2),
            dict(id="clean_temp",  title="Pulisci File Temporanei",
                 desc="Rimuove i file temporanei da %TEMP%, Windows Temp e dalle directory Prefetch. Libera spazio su disco e può ridurre il tempo di avvio.",
                 badge="SICURO", badge_color=SUCCESS, action=self._do_clean_temp,
                 col=0, row=1, cs=1),
            dict(id="discord",     title="Pulizia Cache Discord",
                 desc="Cancella la cache locale di Discord, la cache GPU e i dump degli errori. Risolve lag e utilizzo elevato della memoria. Discord deve essere chiuso prima.",
                 badge="CACHE APP", badge_color="#5865f2", action=self._do_discord,
                 col=1, row=1, cs=1),
            dict(id="performance", title="Modalità Prestazioni",
                 desc="Passa il piano energetico di Windows a Prestazioni elevate, disabilita gli effetti visivi e regola le impostazioni di sistema per la massima reattività.",
                 badge="ENERGIA", badge_color=WARNING, action=self._do_perf_mode,
                 col=0, row=2, cs=1),
            dict(id="taskmgr",     title="Apri Gestione Attività",
                 desc="Avvia Gestione attività di Windows per ispezionare i processi in esecuzione, l'utilizzo di CPU/RAM/Disco/Rete e i programmi di avvio.",
                 badge="WINDOWS", badge_color=TEXT_SECONDARY, action=self._open_taskmgr,
                 col=1, row=2, cs=1),
        ]

        for o in opts:
            card = self._opt_card(sf, o)
            px = (0, 6) if o["col"] == 0 and o["cs"] == 1 else \
                 (6, 0) if o["col"] == 1 else (0, 0)
            card.grid(row=o["row"], column=o["col"], columnspan=o["cs"], # "Registro Ottimizzazione"
                      padx=px, pady=(0, 10), sticky="nsew")

        # Log panel
        log_outer, log_body = self._section(sf, "Optimization Log")
        log_outer.grid(row=10, column=0, columnspan=2, pady=(6, 0), sticky="nsew")
        sf.rowconfigure(10, weight=1)

        self._opt_log = scrolledtext.ScrolledText(
            log_body, font=FONT_MONO, height=8,
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="white",
            relief="flat", bd=0, state="disabled")
        self._opt_log.pack(fill="both", expand=True)
        for tag, fg in [("info","#9cdcfe"),("warn","#ce9178"),("error","#f48771"),
                        ("ok","#4ec9b0"),("ts","#608b4e")]:
            self._opt_log.tag_config(tag, foreground=fg)

    def _opt_card(self, parent, o):
        card = tk.Frame(parent, bg=BG_PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
        # Title row — pack inside card
        top = tk.Frame(card, bg=BG_PANEL)
        top.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(top, text=o["badge"], font=("Segoe UI", 7, "bold"),
                 bg=o["badge_color"], fg="white", padx=5, pady=1).pack(side="right")
        tk.Label(top, text=o["title"], font=FONT_HEADING,
                 bg=BG_PANEL, fg=TEXT_PRIMARY).pack(side="left")
        tk.Label(card, text=o["desc"], font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SECONDARY,
                 wraplength=380, justify="left", anchor="nw").pack(
            anchor="w", padx=14, pady=(0, 8))
        btn_bg = ACCENT if o["id"] == "boost_all" else BG_CARD_DARK # "Esegui"
        btn_fg = TEXT_ON_DARK if o["id"] == "boost_all" else TEXT_PRIMARY
        self._btn(card, "Run", o["action"], btn_bg, btn_fg).pack(
            anchor="w", padx=14, pady=(0, 12))
        return card

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Monitor
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_monitor(self, parent):
        self._page_header(parent, "Monitor di Sistema", "Monitoraggio hardware e prestazioni in tempo reale")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)

        # Live gauges
        g_outer, g_body = self._section(sf, "Metriche in Tempo Reale")
        g_outer.grid(row=0, column=0, pady=(0, 12), sticky="ew")
        for i in range(4):
            g_body.columnconfigure(i, weight=1)

        self._mon_gauges = {}
        for col, (key, lbl, unit, color) in enumerate([
            ("cpu",  "CPU",       "%",  ACCENT), # "Disco (C:)"
            ("ram",  "RAM",       "%",  SUCCESS),
            ("disk", "Disk (C:)", "%",  WARNING),
            ("temp", "CPU Temp",  "°C", DANGER),
        ]):
            self._mon_gauges[key] = self._gauge(g_body, lbl, unit, color, col)

        # Component details
        d_outer, d_body = self._section(sf, "Dettagli Componenti") # "Temp CPU"
        d_outer.grid(row=1, column=0, pady=(0, 12), sticky="ew") # "Utilizzo CPU"
        d_body.columnconfigure(0, weight=1)
        d_body.columnconfigure(1, weight=1)

        left  = tk.Frame(d_body, bg=BG_PANEL)
        right = tk.Frame(d_body, bg=BG_PANEL)
        left.grid(row=0, column=0, sticky="nsew", padx=(14, 7), pady=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(7, 14), pady=10)
        left.columnconfigure(1, weight=1)
        right.columnconfigure(1, weight=1)

        self._mon_det = {}
        left_rows = [
            ("cpu_pct",  "Utilizzo CPU"),
            ("cpu_name", "Modello CPU"),
            ("cpu_temp", "Temperatura CPU"),
            ("procs",    "Processi"),
        ]
        right_rows = [
            ("ram_pct",    "Utilizzo RAM"),
            ("ram_det",    "RAM Usata/Totale"),
            ("disk_pct",   "Utilizzo Disco"),
            ("disk_det",   "Disco Usato/Totale"),
            ("uptime",     "Tempo di Attività"),
        ]
        for frame, rows in [(left, left_rows), (right, right_rows)]:
            for r, (key, label) in enumerate(rows):
                tk.Label(frame, text=label + ":", font=FONT_BODY,
                         bg=BG_PANEL, fg=TEXT_SECONDARY).grid(row=r, column=0, sticky="w", pady=3)
                lbl = tk.Label(frame, text="—", font=("Segoe UI", 9, "bold"),
                               bg=BG_PANEL, fg=TEXT_PRIMARY)
                lbl.grid(row=r, column=1, sticky="w", padx=10, pady=3)
                self._mon_det[key] = lbl

        # CPU history
        h_outer, h_body = self._section(sf, "Cronologia CPU (finestra 2 min)")
        h_outer.grid(row=2, column=0, pady=(0, 12), sticky="ew")
        self._cpu_canvas = tk.Canvas(h_body, height=80, bg="#1e1e1e", highlightthickness=0)
        self._cpu_canvas.pack(fill="x", padx=14, pady=10)

    def _gauge(self, parent, label, unit, color, col):
        fr = tk.Frame(parent, bg=BG_PANEL)
        fr.grid(row=0, column=col, padx=14, pady=10, sticky="ew")
        tk.Label(fr, text=label, font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_SECONDARY).pack() # "N/D"
        vl = tk.Label(fr, text="—", font=("Segoe UI", 20, "bold"), bg=BG_PANEL, fg=color)
        vl.pack()
        tk.Label(fr, text=unit, font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_TERTIARY).pack()
        bar_bg = tk.Frame(fr, bg=BORDER, height=6)
        bar_bg.pack(fill="x", pady=(4, 0))
        bar    = tk.Frame(bar_bg, bg=color, height=6)
        bar.place(x=0, y=0, relheight=1, relwidth=0)
        fr._vl = vl; fr._bar = bar; fr._bar_bg = bar_bg; fr._color = color
        return fr

    def _update_gauge(self, g, val, is_pct=True):
        if val is None:
            g._vl.configure(text="N/A"); return
        g._vl.configure(text=f"{val:.1f}")
        if is_pct:
            g._bar.place_configure(relwidth=max(0.0, min(1.0, val / 100.0)))
            color = DANGER if val >= 85 else (WARNING if val >= 65 else g._color)
            g._vl.configure(fg=color); g._bar.configure(bg=color)

    def _draw_history(self):
        c = self._cpu_canvas
        c.update_idletasks()
        w, h = c.winfo_width(), c.winfo_height()
        if w <= 1: return
        c.delete("all")
        data = self._cpu_history[-60:]
        if len(data) < 2: return
        step = w / (len(data) - 1)
        pts = []
        for i, v in enumerate(data):
            pts.extend([i * step, h - (v / 100.0) * (h - 4) - 2])
        if len(pts) >= 4:
            c.create_line(*pts, fill=ACCENT, width=1.5, smooth=True)
        for pct, clr in [(50, "#444"), (80, "#663")]:
            y = h - (pct / 100.0) * (h - 4) - 2
            c.create_line(0, y, w, y, fill=clr, dash=(3, 4))
            c.create_text(4, y - 6, text=f"{pct}%", fill="#666", anchor="w",
                          font=("Consolas", 7))

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Diagnostics
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_diagnostics(self, parent):
        self._page_header(parent, "Diagnostica", "Ispeziona lo stato del sistema ed esegui controlli diagnostici")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)

        c_outer, c_body = self._section(sf, "Controlli di Integrità del Sistema")
        c_outer.grid(row=0, column=0, pady=(0, 12), sticky="ew")
        c_body.columnconfigure(0, weight=1)

        self._diag_rows = {}
        checks = [
            ("powershell", "PowerShell Disponibile",  self._chk_powershell),
            ("scripts",    "Directory Script",      self._chk_scripts),
            ("psutil",     "Monitoraggio psutil",      self._chk_psutil),
            ("winver",     "Versione Windows",        self._chk_winver),
            ("diskspace",  "Spazio su Disco (C:)",        self._chk_diskspace),
            ("tempsize",   "Dimensione Directory Temp",    self._chk_tempsize),
        ]
        for r, (key, label, fn) in enumerate(checks):
            row = tk.Frame(c_body, bg=BG_PANEL)
            row.grid(row=r, column=0, sticky="ew", padx=14, pady=3)
            row.columnconfigure(1, weight=1)
            dot = tk.Label(row, text="●", font=("Segoe UI", 10),
                           bg=BG_PANEL, fg=TEXT_TERTIARY)
            dot.grid(row=0, column=0, padx=(0, 8))
            tk.Label(row, text=label, font=FONT_BODY,
                     bg=BG_PANEL, fg=TEXT_PRIMARY, anchor="w").grid(row=0, column=1, sticky="w")
            det = tk.Label(row, text="Not checked", font=FONT_SMALL,
                           bg=BG_PANEL, fg=TEXT_TERTIARY, anchor="e") # "Non controllato"
            det.grid(row=0, column=2, sticky="e")
            self._diag_rows[key] = (dot, det, fn)

        tk.Frame(c_body, bg=BG_PANEL, height=8).grid(row=len(checks), column=0)
        bf = tk.Frame(c_body, bg=BG_PANEL)
        bf.grid(row=len(checks)+1, column=0, sticky="w", padx=14, pady=(0, 12)) # "Esegui Tutti i Controlli"
        self._btn(bf, "Run All Checks", self._run_diag, ACCENT, TEXT_ON_DARK).pack(side="left")

        o_outer, o_body = self._section(sf, "Diagnostic Output")
        o_outer.grid(row=1, column=0, pady=(0, 12), sticky="nsew")
        sf.rowconfigure(1, weight=1)
        self._diag_out = scrolledtext.ScrolledText(
            o_body, font=FONT_MONO, height=12,
            bg="#1e1e1e", fg="#d4d4d4", relief="flat", bd=0, state="disabled")
        self._diag_out.pack(fill="both", expand=True)

    def _run_diag(self):
        self._dlog("─" * 60)
        self._dlog(f"Esecuzione diagnostica — {datetime.datetime.now().strftime('%H:%M:%S')}") # "Diagnostica completata."
        threading.Thread(target=self._diag_thread, daemon=True).start() # "✓"

    def _diag_thread(self):
        for key, (dot, det, fn) in self._diag_rows.items():
            self.root.after(0, dot.configure, {"fg": WARNING})
            ok, msg = fn()
            color = SUCCESS if ok else DANGER
            self.root.after(0, dot.configure, {"fg": color})
            self.root.after(0, det.configure, {"text": msg, "fg": color})
            self._dlog(f"{'✓' if ok else '✗'} {msg}") # "✗"
            time.sleep(0.2)
        self._dlog("Diagnostic complete.")

    def _dlog(self, msg):
        def _do():
            self._diag_out.configure(state="normal")
            self._diag_out.insert("end", msg + "\n")
            self._diag_out.see("end")
            self._diag_out.configure(state="disabled")
        self.root.after(0, _do)

    def _chk_powershell(self):
        try:
            r = subprocess.run(["powershell", "-Command", "echo ok"],
                               capture_output=True, text=True, timeout=5)
            if r.returncode == 0: return True, "PowerShell è disponibile"
        except Exception: pass
        return False, "PowerShell non trovato"

    def _chk_scripts(self):
        if os.path.isdir(SCRIPTS_PATH):
            files = [f for f in os.listdir(SCRIPTS_PATH) if f.endswith(".ps1")]
            return (True, f"Trovato/i {len(files)} script") if files else (False, "Nessuno script .ps1 trovato")
        return False, f"Directory '{SCRIPTS_PATH}' non trovata"

    def _chk_psutil(self):
        if self.monitor._psutil_available:
            v = ".".join(str(x) for x in self.monitor._psutil.version_info)
            return True, f"psutil {v} installato"
        return False, "psutil non installato (pip install psutil)"

    def _chk_winver(self):
        s = platform.system()
        if s == "Windows":
            return True, f"Windows {platform.release()} (build {platform.version()})"
        return False, f"Non Windows: {s} {platform.release()}"

    def _chk_diskspace(self):
        try:
            if self.monitor._psutil_available:
                du = self.monitor._psutil.disk_usage("C:\\")
                free = du.free / 1e9
                ok = free > 10 # "BASSO"
                return ok, f"{free:.1f} GB liberi su C:\\ ({'OK' if ok else 'BASSO'})"
        except Exception: pass
        return False, "Impossibile leggere le informazioni del disco"

    def _chk_tempsize(self):
        try:
            tmp = os.environ.get("TEMP", "C:\\Windows\\Temp")
            total = 0; count = 0
            for root_, _, files in os.walk(tmp):
                for f in files:
                    try: total += os.path.getsize(os.path.join(root_, f)); count += 1
                    except Exception: pass # "Errore: {e}"
            mb = total / 1e6
            return mb < 500, f"{mb:.0f} MB in temp ({count} file)"
        except Exception as e:
            return False, f"Error: {e}"

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Tips # "Consigli sulle Prestazioni"
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_tips(self, parent):
        self._page_header(parent, "Consigli sulle Prestazioni", "Guida esperta per mantenere il tuo sistema veloce e sano")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)

        # Filter bar # "Filtra:"
        fbar = tk.Frame(sf, bg=BG_BASE)
        fbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(fbar, text="Filter:", font=FONT_BODY,
                 bg=BG_BASE, fg=TEXT_SECONDARY).pack(side="left", padx=(0, 8))
        self._tip_filter = tk.StringVar(value="Tutti")
        for cat in ["Tutti","CPU","RAM","Disco","Rete","GPU","Sicurezza","Generale"]:
            tk.Radiobutton(fbar, text=cat, variable=self._tip_filter, value=cat,
                           font=FONT_SMALL, bg=BG_BASE, fg=TEXT_PRIMARY,
                           selectcolor=ACCENT_LIGHT, activebackground=BG_BASE,
                           command=self._render_tips).pack(side="left", padx=4)

        self._tips_box = tk.Frame(sf, bg=BG_BASE)
        self._tips_box.grid(row=1, column=0, sticky="ew")
        self._tips_box.columnconfigure(0, weight=1)
        self._render_tips()

    def _render_tips(self):
        for w in self._tips_box.winfo_children():
            w.destroy()
        cat_filter = self._tip_filter.get() # "Disco"
        cat_colors = {"CPU":ACCENT,"RAM":SUCCESS,"Disk":WARNING,"Network":"#007ea7",
                      "GPU":"#7b2fbe","Security":DANGER,"General":TEXT_SECONDARY}
        filtered = [(c,t) for c,t in PERFORMANCE_TIPS if cat_filter == "All" or c == cat_filter]
        for r, (cat, tip) in enumerate(filtered):
            card = tk.Frame(self._tips_box, bg=BG_PANEL,
                            highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=r, column=0, sticky="ew", pady=(0, 6))
            card.columnconfigure(1, weight=1)
            color = cat_colors.get(cat, TEXT_SECONDARY)
            tk.Label(card, text=f"  {cat}  ", font=("Segoe UI", 7, "bold"),
                     bg=color, fg="white").grid(row=0, column=0, padx=(14,10), pady=10, sticky="n")
            tk.Label(card, text=tip, font=FONT_BODY, bg=BG_PANEL, fg=TEXT_PRIMARY,
                     wraplength=600, justify="left", anchor="nw").grid(
                row=0, column=1, sticky="ew", padx=(0,14), pady=10)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Log
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_log(self, parent):
        self._page_header(parent, "Registro Attività", "Cronologia completa di tutte le operazioni di CoreTune")
        content = tk.Frame(parent, bg=BG_BASE)
        content.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)
        parent.rowconfigure(1, weight=1)

        tb = tk.Frame(content, bg=BG_BASE)
        tb.grid(row=0, column=0, sticky="ew", pady=(0, 6)) # "Cancella Registro"
        self._btn(tb, "Clear Log", self._clear_log, BG_CARD_DARK, TEXT_PRIMARY).pack(side="right")

        self._main_log = scrolledtext.ScrolledText(
            content, font=FONT_MONO, bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white", relief="flat", bd=1,
            highlightthickness=1, highlightbackground=BORDER, state="disabled")
        self._main_log.grid(row=1, column=0, sticky="nsew")
        for tag, fg in [("info","#9cdcfe"),("warn","#ce9178"),("error","#f48771"),
                        ("ok","#4ec9b0"),("ts","#608b4e"),("head","#dcdcaa")]:
            self._main_log.tag_config(tag, foreground=fg)

    def _clear_log(self):
        self._main_log.configure(state="normal")
        self._main_log.delete("1.0", "end")
        self._main_log.configure(state="disabled")
        self._log("Log cleared.", "info")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Settings
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_settings(self, parent):
        self._page_header(parent, "Settings", "Configure CoreTune preferences")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)

        s_outer, s_body = self._section(sf, "Scripts Configuration")
        s_outer.grid(row=0, column=0, pady=(0, 12), sticky="ew")
        s_body.columnconfigure(1, weight=1)
        tk.Label(s_body, text="Scripts Directory:", font=FONT_BODY,
                 bg=BG_PANEL, fg=TEXT_SECONDARY).grid(row=0, column=0, padx=14, pady=10, sticky="w")
        self._scripts_path_var = tk.StringVar(value=SCRIPTS_PATH)
        tk.Entry(s_body, textvariable=self._scripts_path_var,
                 font=FONT_BODY, relief="solid", bd=1).grid(
            row=0, column=1, padx=(0, 14), pady=10, sticky="ew")
        tk.Label(s_body, text="Path relative to the app directory (.ps1 scripts).",
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_TERTIARY).grid(
            row=1, column=0, columnspan=2, padx=14, pady=(0, 10), sticky="w")

        m_outer, m_body = self._section(sf, "Monitoring")
        m_outer.grid(row=1, column=0, pady=(0, 12), sticky="ew")
        tk.Label(m_body, text="Background monitoring active — refresh every 2 seconds.",
                 font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SECONDARY).pack(
            anchor="w", padx=14, pady=10)

        a_outer, a_body = self._section(sf, "About CoreTune")
        a_outer.grid(row=2, column=0, pady=(0, 12), sticky="ew")
        a_body.columnconfigure(1, weight=1)
        for r, (k, v) in enumerate([
            ("Application", f"CoreTune {APP_VERSION}"),
            ("Developer",   "Aura Studio"),
            ("Platform",    f"{platform.system()} {platform.release()}"),
            ("Python",      sys.version.split()[0]),
        ]):
            tk.Label(a_body, text=k+":", font=FONT_BODY,
                     bg=BG_PANEL, fg=TEXT_SECONDARY).grid(row=r, column=0, padx=14, pady=4, sticky="w")
            tk.Label(a_body, text=v, font=("Segoe UI", 9, "bold"),
                     bg=BG_PANEL, fg=TEXT_PRIMARY).grid(row=r, column=1, padx=8, pady=4, sticky="w")
        tk.Frame(a_body, bg=BG_PANEL, height=8).grid(row=4, column=0)

    # ─────────────────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────────────────
    def _run_action(self, name, scripts):
        if self.operation_running: # "Occupato"
            messagebox.showwarning("Occupato", "Un'altra operazione è già in esecuzione.")
            return
        self.operation_running = True
        self.status_var.set(f"In esecuzione: {name}...")
        self._log("─" * 50, "head")
        self._log(f"Avvio: {name}", "head")
        threading.Thread(target=self._action_thread, args=(name, scripts), daemon=True).start()

    def _action_thread(self, name, scripts):
        ok_count = 0
        for s in scripts:
            self._log(f"Esecuzione: {s}", "info")
            ok, _ = run_script(s, log_callback=self._log)
            if ok:
                self._log(f"Completato: {s}", "ok"); ok_count += 1
            else:
                self._log(f"Problema con: {s}", "warn")
        self._log(f"Completato: {name} ({ok_count}/{len(scripts)} OK)", "ok")
        self.root.after(0, self.status_var.set, "Pronto")
        self.root.after(0, setattr, self, "operation_running", False)

    def _do_boost_all(self):
        self._run_action("Ottimizzazione Completa del Sistema", ["clean_temp.ps1","discord.ps1","performance_mode.ps1"])
    def _do_clean_temp(self):
        self._run_action("Clean Temp Files", ["clean_temp.ps1"])
    def _do_discord(self):
        self._run_action("Discord Cleanup", ["discord.ps1"])
    def _do_perf_mode(self):
        self._run_action("Performance Mode", ["performance_mode.ps1"])
    def _open_taskmgr(self):
        try: # "Gestione Attività avviata"
            subprocess.Popen("taskmgr")
            self._log("Gestione Attività avviata", "ok")
        except Exception as e:
            self._log(f"Could not open Task Manager: {e}", "error")

    # ─────────────────────────────────────────────────────────────────────────
    # Logging
    # ─────────────────────────────────────────────────────────────────────────
    def _log(self, msg, level="info"):
        self.log_queue.put((datetime.datetime.now().strftime("%H:%M:%S"), msg, level))

    def _process_log_queue(self):
        try:
            while True:
                ts, msg, level = self.log_queue.get_nowait()
                self._wlog(self._main_log, ts, msg, level)
                if hasattr(self, "_opt_log"):
                    self._wlog(self._opt_log, ts, msg, level)
        except queue.Empty:
            pass
        self.root.after(100, self._process_log_queue)

    def _wlog(self, widget, ts, msg, level):
        try:
            widget.configure(state="normal")
            widget.insert("end", f"[{ts}] ", "ts")
            widget.insert("end", msg + "\n", level)
            widget.see("end")
            widget.configure(state="disabled")
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────────────────────
    # Monitor callback
    # ─────────────────────────────────────────────────────────────────────────
    def _on_monitor_update(self, data):
        self.root.after(0, self._apply_data, data)

    def _apply_data(self, data):
        cpu  = data.get("cpu", 0)
        ram  = data.get("ram", 0)
        disk = data.get("disk", 0)
        temp = data.get("cpu_temp")

        # Dashboard cards
        if hasattr(self, "_dash_cards"):
            self._update_metric_card(self._dash_cards["cpu"],  cpu)
            self._update_metric_card(self._dash_cards["ram"],  ram)
            self._update_metric_card(self._dash_cards["disk"], disk)

        # Dashboard sysinfo
        if hasattr(self, "_si_lbls"):
            self._si_lbls["uptime"].configure(text=data.get("uptime", "—"))
            self._si_lbls["procs"].configure(text=str(data.get("processes", "—"))) # "N/D"
            self._si_lbls["temp"].configure(
                text=f"{temp}°C" if temp is not None else "N/A")

        # Monitor gauges
        if hasattr(self, "_mon_gauges"):
            self._update_gauge(self._mon_gauges["cpu"],  cpu)
            self._update_gauge(self._mon_gauges["ram"],  ram)
            self._update_gauge(self._mon_gauges["disk"], disk)
            if temp is not None:
                g = self._mon_gauges["temp"]
                g._vl.configure(text=f"{temp:.1f}")
                g._bar.place_configure(relwidth=min(1.0, temp / 100.0)) # "N/D"

        # Monitor details
        if hasattr(self, "_mon_det"):
            d = self._mon_det
            d["cpu_pct"].configure(text=f"{cpu:.1f}%")
            d["cpu_name"].configure(text=data.get("cpu_name","Unknown")[:50])
            d["cpu_temp"].configure(text=f"{temp}°C" if temp else "N/A")
            d["procs"].configure(text=str(data.get("processes","—")))
            d["ram_pct"].configure(text=f"{ram:.1f}%")
            d["ram_det"].configure(text=f"{data.get('ram_used',0):.2f} / {data.get('ram_total',0):.1f} GB")
            d["disk_pct"].configure(text=f"{disk:.1f}%")
            d["disk_det"].configure(text=f"{data.get('disk_used',0):.0f} / {data.get('disk_total',0):.0f} GB")
            d["uptime"].configure(text=data.get("uptime","—"))

        # CPU history + graph
        self._cpu_history.append(cpu)
        if len(self._cpu_history) > 120:
            self._cpu_history.pop(0)
        if hasattr(self, "_cpu_canvas"):
            self._draw_history()

        # Status bar
        self._sb_mon.configure(
            text=f"CPU {cpu:.0f}%  RAM {ram:.0f}%  Disco {disk:.0f}%"
                 + (f"  Temp {temp:.0f}°C" if temp else ""))

    # ─────────────────────────────────────────────────────────────────────────
    # Utility
    # ─────────────────────────────────────────────────────────────────────────
    def _rotate_tip(self):
        if hasattr(self, "_tip_txt_lbl"):
            cat, tip = PERFORMANCE_TIPS[self.tip_index % len(PERFORMANCE_TIPS)]
            self._tip_cat_lbl.configure(text=f"▸ {cat}")
            self._tip_txt_lbl.configure(text=tip)
            self.tip_index += 1
        self.root.after(15000, self._rotate_tip)

    def _update_clock(self):
        if hasattr(self, "_clock_lbl"):
            self._clock_lbl.configure(text=datetime.datetime.now().strftime("%H:%M"))
        self.root.after(30000, self._update_clock)

    def on_close(self):
        self.monitor.stop()
        self.root.destroy()


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg=BG_SIDEBAR)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Vertical.TScrollbar",
                    background=BG_CARD_DARK, troughcolor=BG_BASE,
                    bordercolor=BORDER, arrowcolor=TEXT_SECONDARY, relief="flat")
    app = CoreTuneApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()