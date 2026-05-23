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
import math
from PIL import Image, ImageTk, ImageDraw, ImageFilter

APP_NAME    = "CoreTune"
APP_VERSION = "2.0.0"
APP_SUBTITLE = "Suite di Ottimizzazione Sistema"
SCRIPTS_PATH = "scripts"

# ─── Wintoys-inspired dark glass palette ──────────────────────────────────────
BG_ROOT         = "#0d0d0d"
BG_SIDEBAR      = "#111111"
BG_SIDEBAR_ITEM = "#1a1a1a"
BG_SIDEBAR_SEL  = "#1f1f1f"
BG_MAIN         = "#141414"
BG_CARD         = "#1c1c1c"
BG_CARD_HOVER   = "#232323"
BG_CARD_BORDER  = "#2a2a2a"
BG_HEADER_CARD  = "#181818"
GLASS_BG        = "#1a1a1a"
GLASS_BORDER    = "#333333"

ACCENT          = "#0078d4"
ACCENT2         = "#60cdff"
ACCENT_GLOW     = "#0067c0"
ACCENT_LIGHT    = "#1e3a5f"
ACCENT_HOVER    = "#106ebe"
DANGER          = "#c42b1c"
DANGER_SOFT     = "#3d1210"
SUCCESS         = "#0f7b0f"
SUCCESS_SOFT    = "#0c2e0c"
SUCCESS_TEXT    = "#6ccb5f"
WARNING         = "#9d5d00"
WARNING_TEXT    = "#f0a742"
INFO_TEXT       = "#60cdff"

TEXT_PRIMARY    = "#ffffff"
TEXT_SECONDARY  = "#9d9d9d"
TEXT_TERTIARY   = "#666666"
TEXT_ACCENT     = "#60cdff"
TEXT_ON_ACCENT  = "#ffffff"

BORDER          = "#2a2a2a"
BORDER_LIGHT    = "#3a3a3a"
SEPARATOR       = "#222222"

RADIUS = 15

FONT_TITLE   = ("Segoe UI", 11, "bold")
FONT_HEADING = ("Segoe UI", 9, "bold")
FONT_BODY    = ("Segoe UI", 9)
FONT_SMALL   = ("Segoe UI", 8)
FONT_TINY    = ("Segoe UI", 7)
FONT_LARGE   = ("Segoe UI", 22, "bold")
FONT_XLARGE  = ("Segoe UI", 28, "bold")
FONT_MONO    = ("Consolas", 8)
FONT_ICON    = ("Segoe UI", 14)

# ─── Icons (Unicode) ──────────────────────────────────────────────────────────
ICONS = {
    "dashboard":   "⌂",
    "optimize":    "⚡",
    "monitor":     "📊",
    "diagnostics": "🔍",
    "tips":        "💡",
    "log":         "📋",
    "settings":    "⚙",
    "cpu":         "🔲",
    "ram":         "🧠",
    "disk":        "💾",
    "network":     "🌐",
    "gpu":         "🖥",
    "temp":        "🌡",
    "process":     "⚙",
    "uptime":      "⏱",
    "app":         "📦",
    "service":     "🔧",
    "clean":       "🧹",
    "boost":       "🚀",
    "task":        "📋",
    "perf":        "⚡",
    "discord":     "💬",
    "restart":     "🔄",
    "feedback":    "💬",
    "power":       "⏻",
    "delete":      "🗑️",
    "download":    "📥",
}

PERFORMANCE_TIPS = [
    ("CPU",      "Disabilita i programmi di avvio non necessari tramite Gestione attività → scheda Avvio per ridurre il tempo di avvio e il carico della CPU."),
    ("RAM",      "Imposta manualmente la memoria virtuale: Sistema → Avanzate → Impostazioni prestazioni → Avanzate → Cambia. Consigliato: 1.5× la tua RAM."),
    ("Disco",    "Mantieni almeno il 15% del tuo disco di sistema libero. Windows ha bisogno di questo spazio per la memoria virtuale e gli aggiornamenti."),
    ("Rete",     "Disabilita gli aggiornamenti automatici durante le ore di punta tramite Windows Update → Ore attive."),
    ("Sicurezza","Esegui una scansione rapida di Windows Defender settimanalmente. La protezione in tempo reale dovrebbe essere sempre ATTIVA."),
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
    ("Sicurezza","Abilita BitLocker sui dispositivi portatili. La perdita di dati per furto è molto più comune del guasto hardware."),
    ("Generale", "Usa Gestione attività (Ctrl+Maiusc+Esc) → scheda Prestazioni per identificare il tuo collo di bottiglia in tempo reale."),
    ("Rete",     "Il DNS può influenzare la velocità di navigazione. Prova Cloudflare (1.1.1.1) o Google (8.8.8.8) per ricerche più veloci."),
    ("Disco",    "Sposta giochi e app di grandi dimensioni su un'unità secondaria per mantenere il tuo SSD di sistema veloce e sano."),
    ("CPU",      "Se non stai giocando, imposta lo stato massimo del processore al 99% — questo previene il calore inutile del turbo boost."),
]

APP_CATALOG = {
    "🌐 Browser": [
        ("Chrome", "Google.Chrome"), ("Firefox", "Mozilla.Firefox"), ("Brave", "BraveSoftware.BraveBrowser"),
        ("Edge", "Microsoft.Edge"), ("Opera", "Opera.Opera"), ("Vivaldi", "VivaldiTechnologies.Vivaldi"),
        ("Tor Browser", "TorProject.TorBrowser"), ("LibreWolf", "LibreWolf.LibreWolf")
    ],
    "💻 Sviluppo": [
        ("VS Code", "Microsoft.VisualStudioCode"), ("Git", "Git.Git"), ("Python 3", "Python.Python.3.12"),
        ("Node.js", "OpenJS.NodeJS"), ("Docker", "Docker.DockerDesktop"), ("Notepad++", "Notepad++.Notepad++"),
        ("WinSCP", "WinSCP.WinSCP"), ("Putty", "PuTTY.PuTTY"), ("IntelliJ IDEA", "JetBrains.IntelliJIDEA.Community"),
        ("PyCharm", "JetBrains.PyCharm.Community"), ("Sublime Text", "SublimeHQ.SublimeText.4")
    ],
    "🎬 Media": [
        ("VLC", "VideoLAN.VLC"), ("Spotify", "Spotify.Spotify"), ("Handbrake", "Handbrake.Handbrake"),
        ("Audacity", "Audacity.Audacity"), ("OBS Studio", "obsproject.obs-studio"), ("Plex", "Plex.PlexDesktop")
    ],
    "🎮 Gaming": [
        ("Steam", "Valve.Steam"), ("Epic Games", "EpicGames.EpicGamesLauncher"), ("GOG Galaxy", "GOG.Galaxy"),
        ("Ubisoft", "Ubisoft.Connect"), ("EA App", "ElectronicArts.EADesktop"), ("Battle.net", "Blizzard.BattleNet"),
        ("Discord", "Discord.Discord"), ("CurseForge", "Overwolf.CurseForge"), ("Discord PTB", "Discord.Discord.PTB")
    ],
    "💬 Social": [
        ("Telegram", "Telegram.TelegramDesktop"), ("WhatsApp", "WhatsApp.WhatsApp"),
        ("Slack", "Slack.Slack"), ("Zoom", "Zoom.Zoom"), ("Teams", "Microsoft.Teams"),
        ("Skype", "Microsoft.Skype"), ("Signal", "OpenWhisperSystems.Signal")
    ],
    "🛠 Utility": [
        ("7-Zip", "7zip.7zip"), ("PowerToys", "Microsoft.PowerToys"), ("WinRAR", "RARLab.WinRAR"),
        ("Lightshot", "Skillbrains.Lightshot"), ("CPU-Z", "CPUID.CPU-Z"), ("Rufus", "Akeo.Rufus"),
        ("Everything", "voidtools.Everything"), ("BleachBit", "BleachBit.BleachBit"), ("qBittorrent", "qBittorrent.qBittorrent")
    ]
}


# ─── Script Runner ────────────────────────────────────────────────────────────
def run_script(script_name, args=None, log_callback=None):
    path = os.path.join(SCRIPTS_PATH, script_name)
    if not os.path.exists(path):
        msg = f"[ATTENZIONE] Script non trovato: {path}"
        if log_callback: log_callback(msg, "warn")
        return False, msg
    try:
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", path]
        if args:
            cmd.extend(args)
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=120, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
        out = result.stdout.strip(); err = result.stderr.strip()
        if log_callback:
            for line in out.splitlines(): log_callback(f"  {line}", "info")
            for line in err.splitlines(): log_callback(f"  {line}", "warn")
        return result.returncode == 0, out
    except FileNotFoundError:
        msg = "[ERRORE] PowerShell non trovato."
        if log_callback: log_callback(msg, "error")
        return False, msg
    except subprocess.TimeoutExpired:
        msg = f"[ERRORE] Script scaduto: {script_name}"
        if log_callback: log_callback(msg, "error")
        return False, msg
    except Exception as e:
        msg = f"[ERRORE] {e}"
        if log_callback: log_callback(msg, "error")
        return False, msg


# ─── System Monitor ───────────────────────────────────────────────────────────
class SystemMonitor:
    def __init__(self):
        self.running = False
        self.thread  = None
        self.data    = {
            "cpu": 0.0, "ram": 0.0, "ram_used": 0.0, "ram_total": 0.0,
            "disk": 0.0, "disk_used": 0.0, "disk_total": 0.0,
            "cpu_temp": None, "uptime": "", "processes": 0,
            "cpu_name": platform.processor() or "Unknown CPU",
            "gpu": 0.0,
        }
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

    def add_callback(self, fn): self._callbacks.append(fn)

    def _notify(self):
        for cb in self._callbacks:
            try: cb(self.data.copy())
            except Exception: pass

    def _collect(self):
        if not self._psutil_available:
            import random
            self.data["cpu"]        = round(random.uniform(5, 65), 1)
            self.data["ram"]        = round(random.uniform(40, 80), 1)
            self.data["ram_used"]   = round(random.uniform(4, 12), 2)
            self.data["ram_total"]  = 16.0
            self.data["disk"]       = round(random.uniform(30, 70), 1)
            self.data["disk_used"]  = round(random.uniform(100, 400), 0)
            self.data["disk_total"] = 512.0
            self.data["processes"]  = random.randint(120, 250)
            self.data["gpu"]        = round(random.uniform(5, 50), 1)
            self.data["uptime"]     = self._uptime_str()
            return
        p = self._psutil
        self.data["cpu"] = p.cpu_percent(interval=None)
        vm = p.virtual_memory()
        self.data["ram"]      = vm.percent
        self.data["ram_used"] = round(vm.used / 1e9, 2)
        self.data["ram_total"]= round(vm.total / 1e9, 2)
        try:
            du = p.disk_usage("C:\\")
            self.data["disk"]       = du.percent
            self.data["disk_used"]  = round(du.used / 1e9, 1)
            self.data["disk_total"] = round(du.total / 1e9, 1)
        except Exception: pass
        try: self.data["processes"] = len(p.pids())
        except Exception: pass
        self.data["uptime"] = self._uptime_str()
        try:
            temps = p.sensors_temperatures()
            if temps:
                for key in ["coretemp","k10temp","cpu_thermal"]:
                    if key in temps and temps[key]:
                        self.data["cpu_temp"] = round(temps[key][0].current, 1)
                        break
        except Exception: pass

    def _uptime_str(self):
        try:
            sec = time.time() - (self._psutil.boot_time() if self._psutil_available else time.time() % 86400)
            h = int(sec // 3600); m = int((sec % 3600) // 60); s = int(sec % 60)
            return f"{h:02d}:{m:02d}:{s:02d}"
        except Exception: return "N/A"

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self): self.running = False

    def _loop(self):
        if self._psutil_available: self._psutil.cpu_percent(interval=None)
        time.sleep(1)
        while self.running:
            self._collect(); self._notify(); time.sleep(2)


# ─── Rounded-rectangle helper (PIL) ──────────────────────────────────────────
def make_rounded_image(w, h, radius, fill, border=None, border_width=1):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = min(radius, w // 2, h // 2)
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=fill,
                           outline=border, width=border_width if border else 0)
    return img


def hex_to_rgba(hex_color, alpha=255):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, alpha)


# ─── Wintoys-style glass card frame ──────────────────────────────────────────
class GlassCard(tk.Frame):
    """A frame that looks like a Wintoys dark glass card with rounded corners."""
    def __init__(self, parent, radius=RADIUS, bg_color=BG_CARD, border_color=BG_CARD_BORDER,
                 alpha=220, **kwargs):
        super().__init__(parent, bg=parent.cget("bg"), **kwargs)
        self._radius = radius
        self._bg_color = bg_color
        self._border_color = border_color
        self._alpha = alpha
        self._img = None
        self._canvas = tk.Canvas(self, highlightthickness=0, bg=parent.cget("bg"))
        self._canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._inner = tk.Frame(self._canvas, bg=bg_color)
        self._canvas.create_window(0, 0, anchor="nw", window=self._inner,
                                   tags="inner_win")
        self.bind("<Configure>", self._redraw)
        self._inner.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        w = self.winfo_width(); h = self.winfo_height()
        if w < 2 or h < 2: return
        self._canvas.config(width=w, height=h)
        self._canvas.itemconfigure("inner_win", width=w-2, height=h-2)
        self._canvas.coords("inner_win", 1, 1)
        # Draw rounded background
        self._canvas.delete("bg_rect")
        self._canvas.create_rounded_rectangle = getattr(
            self._canvas, "create_rounded_rectangle", None)
        r = RADIUS
        # Draw via polygon
        self._draw_rounded_rect(w, h, r)

    def _draw_rounded_rect(self, w, h, r):
        self._canvas.delete("bg_rect", "bg_border")
        bg = self._bg_color; bd = self._border_color
        c = self._canvas
        # Background
        pts = self._rounded_pts(2, 2, w-2, h-2, r)
        c.create_polygon(pts, fill=bg, outline="", tags="bg_rect", smooth=False)
        # Border
        c.create_polygon(pts, fill="", outline=bd, width=1, tags="bg_border", smooth=False)

    @staticmethod
    def _rounded_pts(x1, y1, x2, y2, r):
        r = min(r, (x2-x1)//2, (y2-y1)//2)
        pts = []
        steps = 8
        for cx, cy, sa, ea in [
            (x1+r, y1+r, 180, 270),
            (x2-r, y1+r,  270, 360),
            (x2-r, y2-r,   0, 90),
            (x1+r, y2-r,  90, 180),
        ]:
            for i in range(steps+1):
                angle = math.radians(sa + (ea - sa) * i / steps)
                pts.append(cx + r * math.cos(angle))
                pts.append(cy + r * math.sin(angle))
        return pts

    def inner(self):
        return self._inner


# ─── Circular gauge (canvas) ─────────────────────────────────────────────────
class ArcGauge(tk.Canvas):
    def __init__(self, parent, size=90, color=ACCENT, bg=BG_CARD, **kwargs):
        super().__init__(parent, width=size, height=size, bg=bg,
                         highlightthickness=0, **kwargs)
        self._size = size
        self._color = color
        self._bg_color = bg
        self._value = 0.0
        self._val_var = tk.StringVar(value="0")
        self._draw()

    def _draw(self):
        s = self._size; m = 8; c = s // 2
        self.delete("all")
        # Track
        self.create_arc(m, m, s-m, s-m, start=220, extent=-260,
                        outline=BG_CARD_BORDER, width=6, style="arc")
        # Value arc
        extent = -260 * (self._value / 100.0)
        if abs(extent) > 0.5:
            self.create_arc(m, m, s-m, s-m, start=220, extent=extent,
                            outline=self._color, width=6, style="arc")
        # Center text
        self.create_text(c, c-4, text=f"{self._value:.0f}",
                         font=("Segoe UI", int(s*0.2), "bold"),
                         fill=TEXT_PRIMARY)
        self.create_text(c, c+10, text="%",
                         font=("Segoe UI", int(s*0.1)),
                         fill=TEXT_SECONDARY)

    def set_value(self, val):
        self._value = max(0.0, min(100.0, val))
        color = DANGER if self._value >= 85 else (WARNING_TEXT if self._value >= 65 else self._color)
        self._color_current = color
        self._draw_colored(color)

    def _draw_colored(self, color):
        s = self._size; m = 8; c = s // 2
        self.delete("all")
        self.create_arc(m, m, s-m, s-m, start=220, extent=-260,
                        outline=BG_CARD_BORDER, width=6, style="arc")
        extent = -260 * (self._value / 100.0)
        if abs(extent) > 0.5:
            self.create_arc(m, m, s-m, s-m, start=220, extent=extent,
                            outline=color, width=6, style="arc")
        self.create_text(c, c-4, text=f"{self._value:.0f}",
                         font=("Segoe UI", int(s*0.2), "bold"), fill=TEXT_PRIMARY)
        self.create_text(c, c+10, text="%",
                         font=("Segoe UI", int(s*0.1)), fill=TEXT_SECONDARY)


# ─── Mini spark line ──────────────────────────────────────────────────────────
class SparkLine(tk.Canvas):
    def __init__(self, parent, width=80, height=30, color=ACCENT, bg=BG_CARD, **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=0, **kwargs)
        self._color = color
        self._data = []
        self._w = width; self._h = height

    def push(self, val):
        self._data.append(val)
        if len(self._data) > 30: self._data.pop(0)
        self._redraw()

    def _redraw(self):
        self.delete("all")
        if len(self._data) < 2: return
        w, h = self._w, self._h
        step = w / (len(self._data) - 1)
        pts = []
        for i, v in enumerate(self._data):
            x = i * step
            y = h - (v / 100.0) * (h - 4) - 2
            pts.extend([x, y])
        if len(pts) >= 4:
            self.create_line(*pts, fill=self._color, width=1.5, smooth=True)


# ─── Flat dark button ─────────────────────────────────────────────────────────
class DarkButton(tk.Label):
    def __init__(self, parent, text, command, style="normal", **kwargs):
        self._radius = RADIUS
        if style == "accent":
            bg, fg, hbg = ACCENT, TEXT_ON_ACCENT, ACCENT_HOVER
        elif style == "danger":
            bg, fg, hbg = "#3d1210", DANGER, "#5a1a17"
        else:
            bg, fg, hbg = BG_CARD_BORDER, TEXT_SECONDARY, "#333333"
        
        # Usiamo un canvas per bottoni arrotondati veri
        self._container = tk.Canvas(parent, height=34, bg=parent.cget("bg"), 
                                   highlightthickness=0, cursor="hand2")
        super().__init__(self._container, text=text, bg=bg, fg=fg,
                        font=FONT_BODY, padx=14, pady=4,
                        cursor="hand2", relief="flat")
        
        # Nota: Per semplicità in questo refactor manteniamo la Label ma con stile flat
        # In una versione PRO useremmo create_polygon anche qui.
        # Applichiamo un padding interno simulato
        kwargs.pop('padx', None)
        kwargs.pop('pady', None)
        super().__init__(parent, text=text, bg=bg, fg=fg,
                         font=FONT_BODY, padx=14, pady=6,
                         cursor="hand2", relief="flat", **kwargs)
        
        self._bg = bg; self._hbg = hbg
        self.bind("<Enter>", lambda e: self.configure(bg=hbg))
        self.bind("<Leave>", lambda e: self.configure(bg=bg))
        self.bind("<Button-1>", lambda e: command())


# ─── Sidebar nav item ─────────────────────────────────────────────────────────
class NavItem(tk.Frame):
    def __init__(self, parent, icon, label, tab_id, on_click, **kwargs):
        super().__init__(parent, bg=BG_SIDEBAR, height=40, cursor="hand2", **kwargs)
        self.pack_propagate(False)
        self._tab_id = tab_id
        self._on_click = on_click
        self._active = False

        # Left indicator bar
        self._ind = tk.Frame(self, bg=BG_SIDEBAR, width=3)
        self._ind.pack(side="left", fill="y")

        # Icon
        self._icon_lbl = tk.Label(self, text=icon, font=("Segoe UI", 12),
                                   bg=BG_SIDEBAR, fg=TEXT_TERTIARY, width=2)
        self._icon_lbl.pack(side="left", padx=(8, 4))

        # Label
        self._text_lbl = tk.Label(self, text=label, font=FONT_BODY,
                                   bg=BG_SIDEBAR, fg=TEXT_SECONDARY, anchor="w")
        self._text_lbl.pack(side="left", fill="both", expand=True)

        for w in (self, self._icon_lbl, self._text_lbl, self._ind):
            w.bind("<Button-1>", self._click)
            w.bind("<Enter>", self._hover)
            w.bind("<Leave>", self._unhover)

    def _click(self, e=None): self._on_click(self._tab_id)

    def _hover(self, e=None):
        if not self._active:
            for w in (self, self._icon_lbl, self._text_lbl):
                w.configure(bg=BG_SIDEBAR_ITEM)

    def _unhover(self, e=None):
        if not self._active:
            for w in (self, self._icon_lbl, self._text_lbl):
                w.configure(bg=BG_SIDEBAR)

    def set_active(self, active):
        self._active = active
        if active:
            self._ind.configure(bg=ACCENT)
            for w in (self, self._icon_lbl, self._text_lbl):
                w.configure(bg=BG_SIDEBAR_SEL)
            self._text_lbl.configure(fg=TEXT_PRIMARY, font=FONT_HEADING)
            self._icon_lbl.configure(fg=ACCENT2)
        else:
            self._ind.configure(bg=BG_SIDEBAR)
            for w in (self, self._icon_lbl, self._text_lbl):
                w.configure(bg=BG_SIDEBAR)
            self._text_lbl.configure(fg=TEXT_SECONDARY, font=FONT_BODY)
            self._icon_lbl.configure(fg=TEXT_TERTIARY)


# ─── Info tile (like Wintoys grid card) ───────────────────────────────────────
class InfoTile(GlassCard):
    """Wintoys-style dark grid tile with icon, label, value."""
    def __init__(self, parent, icon, label, value="—", accent=ACCENT, **kwargs):
        super().__init__(parent, radius=RADIUS, bg_color=BG_CARD, border_color=BG_CARD_BORDER, **kwargs)
        target = self.inner()
        self._accent = accent
        top = tk.Frame(target, bg=BG_CARD)
        top.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(top, text=icon, font=("Segoe UI", 13), bg=BG_CARD,
                 fg=TEXT_SECONDARY).pack(side="left")
        self._val = tk.Label(top, text="", font=FONT_TINY,
                             bg=BG_CARD, fg=TEXT_TERTIARY)
        self._val.pack(side="right")
        tk.Label(target, text=label, font=FONT_SMALL, bg=BG_CARD,
                 fg=TEXT_SECONDARY).pack(anchor="w", padx=12)
        self._big = tk.Label(target, text=value, font=("Segoe UI", 14, "bold"),
                             bg=BG_CARD, fg=TEXT_PRIMARY)
        self._big.pack(anchor="w", padx=12, pady=(0, 4))
        # Progress bar
        bar_bg = tk.Frame(target, bg=BG_CARD_BORDER, height=3)
        bar_bg.pack(fill="x", padx=12, pady=(0, 10))
        bar_bg.pack_propagate(False)
        self._bar = tk.Frame(bar_bg, bg=accent, height=3)
        self._bar.place(x=0, y=0, relheight=1, relwidth=0)

    def update_val(self, val_str, pct=None, accent=None):
        self._big.configure(text=val_str)
        if pct is not None:
            a = accent or self._accent
            if pct >= 85: a = DANGER
            elif pct >= 65: a = WARNING_TEXT
            self._bar.configure(bg=a)
            self._bar.place_configure(relwidth=max(0, min(1, pct / 100)))

    def set_sub(self, txt):
        self._val.configure(text=txt)


# ─── Main Application ─────────────────────────────────────────────────────────
class CoreTuneApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION} — {APP_SUBTITLE}")
        self.root.geometry("1120x700")
        self.root.minsize(900, 580)
        self.root.configure(bg=BG_ROOT)

        self.current_tab       = tk.StringVar(value="dashboard")
        self.status_var        = tk.StringVar(value="Pronto")
        self.log_queue         = queue.Queue()
        self.tip_index         = 0
        self.operation_running = False
        self._cpu_history      = []
        self._installed_apps   = [] # Cache per app installate

        self.monitor = SystemMonitor()
        self.monitor.add_callback(self._on_monitor_update)

        self._setup_styles()
        self._build_ui()
        self.monitor.start()
        self._process_log_queue()
        self._rotate_tip()
        self._update_clock()

        # Assicura che la home sia mostrata correttamente all'avvio
        self.root.after(100, lambda: self._switch_tab("dashboard"))

        self._log(f"CoreTune {APP_VERSION} avviato — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")
        self._log(f"Sistema: {platform.system()} {platform.release()} | Host: {platform.node()}", "info")
        if not self.monitor._psutil_available:
            self._log("psutil non installato — dati simulati. Esegui: pip install psutil", "warn")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Vertical.TScrollbar",
                        background=BG_CARD_BORDER, troughcolor=BG_CARD,
                        bordercolor=BG_CARD, arrowcolor=TEXT_TERTIARY, relief="flat",
                        width=8)
        style.map("Dark.Vertical.TScrollbar",
                  background=[("active", GLASS_BORDER)])

    # ── Root layout ───────────────────────────────────────────────────────────
    def _build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = tk.Frame(self.root, bg=BG_SIDEBAR, width=200)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.columnconfigure(0, weight=1)
        sb.rowconfigure(1, weight=1)

        # Logo area
        logo = tk.Frame(sb, bg=BG_SIDEBAR, height=60)
        logo.grid(row=0, column=0, sticky="ew")
        logo.grid_propagate(False)
        # Hamburger-style menu icon area
        top_bar = tk.Frame(logo, bg=BG_SIDEBAR)
        top_bar.pack(fill="x", padx=16, pady=(12, 0))
        tk.Label(top_bar, text="≡", font=("Segoe UI", 14), bg=BG_SIDEBAR,
                 fg=TEXT_SECONDARY).pack(side="left")
        # App name
        name_fr = tk.Frame(logo, bg=BG_SIDEBAR)
        name_fr.pack(fill="x", padx=16)
        tk.Label(name_fr, text=APP_NAME, font=("Segoe UI", 13, "bold"),
                 bg=BG_SIDEBAR, fg=TEXT_PRIMARY).pack(side="left")

        # Thin separator
        tk.Frame(sb, bg=SEPARATOR, height=1).grid(row=0, column=0, sticky="sew")

        # Nav items
        nav = tk.Frame(sb, bg=BG_SIDEBAR)
        nav.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        nav.columnconfigure(0, weight=1)

        self._nav_items = {}
        for tab_id, icon, label in [
            ("dashboard",   "⌂",  "Home"),
            ("optimize",    "⚡", "Ottimizzazione"),
            ("apps",        "📥", "App Manager"),
            ("debloat",     "🧹", "Debloat"),
            ("monitor",     "📊", "Prestazioni"),
            ("diagnostics", "🔍", "Diagnostica"),
            ("tips",        "💡", "Consigli"),
            ("log",         "📋", "Registro"),
            ("settings",    "⚙",  "Settaggi"),
        ]:
            item = NavItem(nav, icon, label, tab_id, self._switch_tab)
            item.pack(fill="x", padx=4, pady=1)
            self._nav_items[tab_id] = item

        # Footer
        tk.Frame(sb, bg=SEPARATOR, height=1).grid(row=2, column=0, sticky="ew")
        foot = tk.Frame(sb, bg=BG_SIDEBAR)
        foot.grid(row=3, column=0, sticky="ew")

        for icon, label in [("🔄", "Riavvio"), ("💬", "Feedback"), ("⚙", "Impostazioni")]:
            fr = tk.Frame(foot, bg=BG_SIDEBAR, height=36, cursor="hand2")
            fr.pack(fill="x")
            fr.pack_propagate(False)
            tk.Label(fr, text=icon, font=("Segoe UI", 10), bg=BG_SIDEBAR,
                     fg=TEXT_TERTIARY).pack(side="left", padx=(16, 6), pady=8)
            tk.Label(fr, text=label, font=FONT_SMALL, bg=BG_SIDEBAR,
                     fg=TEXT_TERTIARY).pack(side="left")

        self._clock_lbl = tk.Label(foot, text="", font=FONT_SMALL,
                                   bg=BG_SIDEBAR, fg=TEXT_TERTIARY)
        self._clock_lbl.pack(side="bottom", pady=6)

    def _switch_tab(self, tab_id):
        old = self.current_tab.get()
        if old == tab_id: return
        if old in self._nav_items: self._nav_items[old].set_active(False)
        self.current_tab.set(tab_id)
        self._nav_items[tab_id].set_active(True)
        for tid, fr in self._tab_frames.items():
            if tid == tab_id: fr.grid(row=0, column=0, sticky="nsew")
            else: fr.grid_remove()

    # ── Main area ─────────────────────────────────────────────────────────────
    def _build_main(self):
        main = tk.Frame(self.root, bg=BG_MAIN)
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)
        main.rowconfigure(1, weight=0)

        content = tk.Frame(main, bg=BG_MAIN)
        content.grid(row=0, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        self._tab_frames = {}
        for tab_id, builder in [
            ("dashboard",   self._tab_dashboard),
            ("optimize",    self._tab_optimize),
            ("apps",        self._tab_apps),
            ("debloat",     self._tab_debloat),
            ("monitor",     self._tab_monitor),
            ("diagnostics", self._tab_diagnostics),
            ("tips",        self._tab_tips),
            ("log",         self._tab_log),
            ("settings",    self._tab_settings),
        ]:
            fr = tk.Frame(content, bg=BG_MAIN)
            fr.columnconfigure(0, weight=1)
            fr.rowconfigure(0, weight=1)
            self._tab_frames[tab_id] = fr
            builder(fr)

        # Status bar
        bar = tk.Frame(main, bg=BG_SIDEBAR, height=26)
        bar.grid(row=1, column=0, sticky="ew")
        bar.grid_propagate(False)
        tk.Frame(bar, bg=SEPARATOR, height=1).place(x=0, y=0, relwidth=1)
        tk.Label(bar, textvariable=self.status_var, font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg=TEXT_TERTIARY, anchor="w").pack(side="left", padx=14)
        self._sb_mon = tk.Label(bar, text="", font=FONT_SMALL,
                                bg=BG_SIDEBAR, fg=TEXT_TERTIARY)
        self._sb_mon.pack(side="right", padx=14)
        self._switch_tab("dashboard")

    # ── Scrollable canvas ─────────────────────────────────────────────────────
    def _scrollable(self, parent, row=1):
        canvas = tk.Canvas(parent, bg=BG_MAIN, highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview,
                            style="Dark.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.grid(row=row, column=0, sticky="nsew")
        vsb.grid(row=row, column=1, sticky="ns")
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)
        parent.rowconfigure(row, weight=1)

        inner = tk.Frame(canvas, bg=BG_MAIN)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize_inner(e): 
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _resize_canvas(e): canvas.itemconfigure(win_id, width=e.width)

        # Variabili per lo scorrimento fluido (Smooth Scrolling)
        canvas._target_pos = 0.0
        canvas._is_scrolling = False

        def _smooth_scroll_task():
            if not canvas._is_scrolling: return
            curr = canvas.yview()[0]
            diff = canvas._target_pos - curr
            if abs(diff) < 0.0001:
                canvas.yview_moveto(canvas._target_pos)
                canvas._is_scrolling = False
            else:
                # 0.25 determina la "morbidezza": più basso è, più è lento/fluido
                canvas.yview_moveto(curr + diff * 0.25)
                canvas.after(10, _smooth_scroll_task)

        def _on_mousewheel(event):
            # 1. Verifica se il canvas è visibile (non siamo in un'altra tab)
            if not canvas.winfo_viewable():
                return

            # 2. Verifica se il mouse è fisicamente sopra il canvas
            # Usiamo le coordinate assolute per bypassare i widget figli che "rubano" l'evento
            mx = canvas.winfo_pointerx() - canvas.winfo_rootx()
            my = canvas.winfo_pointery() - canvas.winfo_rooty()
            
            if not (0 <= mx <= canvas.winfo_width() and 0 <= my <= canvas.winfo_height()):
                return

            # 3. Se siamo sopra un'area di testo (log), lasciamo che lo scroll lo gestisca il widget stesso
            if "scrolledtext" in str(event.widget).lower():
                return
            
            # 4. Calcolo dimensioni contenuto
            canvas.update_idletasks() # Assicura che le dimensioni siano aggiornate
            region = canvas.cget("scrollregion")
            if not region: 
                canvas.configure(scrollregion=canvas.bbox("all"))
                region = canvas.cget("scrollregion")

            try:
                content_h = float(region.split()[-1])
                visible_h = canvas.winfo_height()
                if content_h <= visible_h: return
                
                if not canvas._is_scrolling:
                    canvas._target_pos = canvas.yview()[0]
                    canvas._is_scrolling = True
                    canvas.after(1, _smooth_scroll_task)
                
                # Sensibilità: 180 pixel per scatto, più veloce e reattivo
                delta = (180 / content_h) * (-event.delta / 120)
                canvas._target_pos = max(0.0, min(1.0, canvas._target_pos + delta))
            except: pass

        # Usiamo bind_all sul root per catturare TUTTI gli eventi rotellina
        # ma la logica sopra filtra solo quelli validi per questo canvas
        self.root.bind_all("<MouseWheel>", _on_mousewheel, add="+")

        inner.bind("<Configure>", _resize_inner)
        canvas.bind("<Configure>", _resize_canvas)

        padded = tk.Frame(inner, bg=BG_MAIN)
        padded.pack(fill="both", expand=True, padx=20, pady=16)
        padded.columnconfigure(0, weight=1)
        return padded

    # ── Page header ───────────────────────────────────────────────────────────
    def _page_header(self, parent, title, subtitle=""):
        hdr = tk.Frame(parent, bg=BG_SIDEBAR, height=52)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        hdr.grid_propagate(False)
        tk.Frame(hdr, bg=SEPARATOR, height=1).place(x=0, rely=1.0, anchor="sw", relwidth=1)
        tk.Label(hdr, text=title, font=("Segoe UI", 13, "bold"),
                 bg=BG_SIDEBAR, fg=TEXT_PRIMARY).place(x=20, y=8)
        if subtitle:
            tk.Label(hdr, text=subtitle, font=FONT_SMALL,
                     bg=BG_SIDEBAR, fg=TEXT_TERTIARY).place(x=22, y=31)
        parent.rowconfigure(0, weight=0)
        parent.rowconfigure(1, weight=1)

    # ── Dark card ─────────────────────────────────────────────────────────────
    def _card(self, parent, title=None):
        outer = tk.Frame(parent, bg=BG_CARD,
                         highlightbackground=BG_CARD_BORDER, highlightthickness=1)
        if title:
            hdr = tk.Frame(outer, bg=BG_CARD)
            hdr.pack(fill="x", padx=14, pady=(12, 6))
            tk.Label(hdr, text=title, font=FONT_HEADING,
                     bg=BG_CARD, fg=TEXT_PRIMARY).pack(side="left")
            tk.Frame(outer, bg=SEPARATOR, height=1).pack(fill="x")
        body = tk.Frame(outer, bg=BG_CARD)
        body.pack(fill="both", expand=True)
        return outer, body

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Dashboard
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_dashboard(self, parent):
        self._page_header(parent, "Home", f"CoreTune {APP_VERSION} — Panoramica del sistema")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)

        # ── Top: System info tiles (4 per row, like Wintoys) ──
        top_fr = tk.Frame(sf, bg=BG_MAIN)
        top_fr.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        for i in range(4): top_fr.columnconfigure(i, weight=1)

        cpu_short = (platform.processor() or "Unknown")[:24]
        os_name = f"{platform.system()} {platform.release()}"

        sysinfo = [
            ("🖥", "Sistema",     platform.node()[:20],    ACCENT),
            ("🔲", "Processore",  cpu_short,               "#9b59b6"),
            ("🎮", "Grafica",     "GPU Integrata",         "#e74c3c"),
            ("🧠", "Memoria",     "—",                     SUCCESS_TEXT),
            ("💾", "Archiviazione","—",                    WARNING_TEXT),
            ("🪟", "Windows",     platform.release(),      ACCENT2),
            ("⏱", "Uptime",      "—",                     "#1abc9c"),
            ("📊", "Prestazioni", "—",                     "#f39c12"),
        ]
        self._si_tiles = {}
        for i, (icon, label, val, color) in enumerate(sysinfo):
            col = i % 4; row_num = i // 4
            tile = InfoTile(top_fr, icon, label, val, accent=color)
            px = (0, 6) if col == 0 else (3, 3) if col < 3 else (6, 0)
            tile.grid(row=row_num, column=col, padx=px, pady=(0, 6), sticky="ew")
            self._si_tiles[label] = tile

        # ── Middle: metrics + quick actions ──
        mid_fr = tk.Frame(sf, bg=BG_MAIN)
        mid_fr.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        mid_fr.columnconfigure(0, weight=1)
        mid_fr.columnconfigure(1, weight=0)

        # Usage gauges row
        gauge_fr = tk.Frame(mid_fr, bg=BG_CARD,
                           highlightbackground=BG_CARD_BORDER, highlightthickness=1)
        gauge_fr.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        for i in range(4): gauge_fr.columnconfigure(i, weight=1)
        tk.Label(gauge_fr, text="Monitoraggio in tempo reale", font=FONT_HEADING,
                 bg=BG_CARD, fg=TEXT_PRIMARY).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(12, 6))
        tk.Frame(gauge_fr, bg=SEPARATOR, height=1).grid(
            row=1, column=0, columnspan=4, sticky="ew")

        self._gauges = {}
        for col, (key, label, color) in enumerate([
            ("cpu",  "Processore", ACCENT),
            ("ram",  "Memoria",    SUCCESS_TEXT),
            ("disk", "Disco",      WARNING_TEXT),
            ("gpu",  "Scheda video", "#9b59b6"),
        ]):
            gf = tk.Frame(gauge_fr, bg=BG_CARD)
            gf.grid(row=2, column=col, padx=10, pady=12)
            g = ArcGauge(gf, size=80, color=color, bg=BG_CARD)
            g.pack()
            tk.Label(gf, text=label, font=FONT_SMALL, bg=BG_CARD,
                     fg=TEXT_SECONDARY).pack(pady=(4, 0))
            self._gauges[key] = g

        # Quick actions
        qa_fr = tk.Frame(mid_fr, bg=BG_CARD,
                         highlightbackground=BG_CARD_BORDER, highlightthickness=1,
                         width=180)
        qa_fr.grid(row=0, column=1, sticky="nsew")
        qa_fr.grid_propagate(False)
        tk.Label(qa_fr, text="Azioni Rapide", font=FONT_HEADING,
                 bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(12, 6))
        tk.Frame(qa_fr, bg=SEPARATOR, height=1).pack(fill="x")

        for label, cmd, style in [
            ("🚀  Ottimizza Tutto",       self._do_boost_all,  "accent"),
            ("🧹  Pulisci Temp",          self._do_clean_temp, "normal"),
            ("💬  Svuota Discord",       self._do_discord,    "normal"),
            ("⚡  Modalità Prestazioni",  self._do_perf_mode,  "normal"),
            ("📋  Gestione Attività",     self._open_taskmgr,  "normal"),
        ]:
            DarkButton(qa_fr, label, cmd, style=style).pack(
                fill="x", padx=10, pady=(4, 0))
        tk.Frame(qa_fr, bg=BG_CARD, height=8).pack()

        # ── Bottom: stat tiles ──
        bot_fr = tk.Frame(sf, bg=BG_MAIN)
        bot_fr.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        for i in range(4): bot_fr.columnconfigure(i, weight=1)

        self._stat_tiles = {}
        stat_defs = [
            ("📦", "Applicazioni", "—",  ACCENT),
            ("⚙",  "Processi",    "—",  TEXT_SECONDARY),
            ("🔧", "Servizi",     "—",  "#1abc9c"),
            ("🧹", "Spazio pulito","0 B", SUCCESS_TEXT),
        ]
        for i, (icon, label, val, color) in enumerate(stat_defs):
            px = (0, 6) if i == 0 else (3, 3) if i < 3 else (6, 0)
            tile = InfoTile(bot_fr, icon, label, val, accent=color)
            tile.grid(row=0, column=i, padx=px, sticky="ew")
            self._stat_tiles[label] = tile

        # ── Tip of the day ──
        tip_outer, tip_body = self._card(sf, "💡  Consiglio del Giorno")
        tip_outer.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        self._tip_cat_lbl = tk.Label(tip_body, text="", font=("Segoe UI", 8, "bold"),
                                     bg=BG_CARD, fg=ACCENT2)
        self._tip_cat_lbl.pack(anchor="w", padx=14, pady=(8, 2))
        self._tip_txt_lbl = tk.Label(tip_body, text="", font=FONT_BODY,
                                     bg=BG_CARD, fg=TEXT_SECONDARY,
                                     wraplength=700, justify="left")
        self._tip_txt_lbl.pack(anchor="w", padx=14, pady=(0, 12))

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Optimize
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_optimize(self, parent):
        self._page_header(parent, "Ottimizza", "Esegui script di ottimizzazione per migliorare le prestazioni")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)
        sf.columnconfigure(1, weight=1)

        opts = [
            dict(id="boost_all", icon="🚀", title="Ottimizzazione Completa",
                 desc="Esegue tutti gli script in sequenza: pulizia temporanei, Discord e modalità prestazioni.",
                 badge="CONSIGLIATO", badge_color=ACCENT, action=self._do_boost_all,
                 col=0, row=0, cs=2),
            dict(id="clean_temp", icon="🧹", title="Pulisci File Temporanei",
                 desc="Rimuove file temporanei da %TEMP%, Windows Temp e Prefetch. Libera spazio su disco.",
                 badge="SICURO", badge_color=SUCCESS, action=self._do_clean_temp,
                 col=0, row=1, cs=1),
            dict(id="discord", icon="💬", title="Pulizia Cache Discord",
                 desc="Cancella cache locale di Discord, GPU e dump errori. Discord deve essere chiuso prima.",
                 badge="CACHE APP", badge_color="#5865f2", action=self._do_discord,
                 col=1, row=1, cs=1),
            dict(id="performance", icon="⚡", title="Modalità Prestazioni",
                 desc="Passa il piano energetico a Prestazioni elevate e disabilita effetti visivi.",
                 badge="ENERGIA", badge_color=WARNING_TEXT, action=self._do_perf_mode,
                 col=0, row=2, cs=1),
            dict(id="taskmgr", icon="📋", title="Gestione Attività",
                 desc="Avvia Gestione attività per ispezionare processi e utilizzo risorse.",
                 badge="WINDOWS", badge_color=TEXT_TERTIARY, action=self._open_taskmgr,
                 col=1, row=2, cs=1),
        ]

        for o in opts:
            card = self._opt_card(sf, o)
            px = (0, 6) if o["col"] == 0 and o["cs"] == 1 else \
                 (6, 0) if o["col"] == 1 else (0, 0)
            card.grid(row=o["row"], column=o["col"], columnspan=o["cs"],
                      padx=px, pady=(0, 10), sticky="nsew")

        log_out, log_body = self._card(sf, "📋  Registro Ottimizzazione")
        log_out.grid(row=10, column=0, columnspan=2, pady=(6, 0), sticky="nsew")
        sf.rowconfigure(10, weight=1)
        self._opt_log = scrolledtext.ScrolledText(
            log_body, font=FONT_MONO, height=8,
            bg="#0d0d0d", fg="#d4d4d4", insertbackground="white",
            relief="flat", bd=0, state="disabled")
        self._opt_log.pack(fill="both", expand=True, padx=1, pady=1)
        for tag, fg in [("info",INFO_TEXT),("warn",WARNING_TEXT),
                        ("error",DANGER),("ok",SUCCESS_TEXT),("ts",TEXT_TERTIARY)]:
            self._opt_log.tag_config(tag, foreground=fg)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: App Manager
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_apps(self, parent):
        self._page_header(parent, "App Manager", "Gestione centralizzata software (Winget)")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)
        
        # 1. Installazione Rapida (Categorie)
        inst_out, inst_body = self._card(sf, "📥  Catalogo Applicazioni")
        inst_out.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        for cat_name, apps in APP_CATALOG.items():
            cat_fr = tk.Frame(inst_body, bg=BG_CARD)
            cat_fr.pack(fill="x", padx=14, pady=(10, 5))
            tk.Label(cat_fr, text=cat_name, font=FONT_HEADING, bg=BG_CARD, fg=ACCENT2).pack(anchor="w")
            
            grid = tk.Frame(inst_body, bg=BG_CARD)
            grid.pack(fill="x", padx=14, pady=(0, 10))
            for i, (name, app_id) in enumerate(apps):
                btn_fr = tk.Frame(grid, bg=BG_CARD_BORDER, padx=8, pady=4)
                btn_fr.grid(row=i//3, column=i%3, padx=4, pady=4, sticky="ew")
                grid.columnconfigure(i%3, weight=1)
                
                tk.Label(btn_fr, text=name, font=FONT_SMALL, bg=BG_CARD_BORDER, fg=TEXT_PRIMARY).pack(side="left")
                DarkButton(btn_fr, "Install", lambda id=app_id: self._run_action(f"Install {name}", ["install_app.ps1", id]), 
                           style="accent").pack(side="right")

        # 2. Disinstallazione in tempo reale
        uninst_out, uninst_body = self._card(sf, "🗑️  App Installate sul PC")
        uninst_out.grid(row=1, column=0, sticky="ew")
        
        # Toolbar disinstallazione
        tools = tk.Frame(uninst_body, bg=BG_CARD, padx=14, pady=10)
        tools.pack(fill="x")
        
        self._app_search_var = tk.StringVar()
        self._app_search_var.trace_add("write", lambda *a: self._render_installed_list())
        tk.Label(tools, text="🔍", bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left")
        search = tk.Entry(tools, textvariable=self._app_search_var, font=FONT_BODY, bg=BG_CARD_BORDER, 
                          fg=TEXT_PRIMARY, relief="flat", insertbackground="white", width=30)
        search.pack(side="left", padx=10, ipady=3)
        
        DarkButton(tools, "🔄 Aggiorna Elenco", self._refresh_installed_apps, style="normal").pack(side="right")

        self._uninst_list_fr = tk.Frame(uninst_body, bg=BG_CARD)
        self._uninst_list_fr.pack(fill="x", padx=14, pady=(0, 15))
        
        # Carica automaticamente al primo accesso
        self.root.after(500, self._refresh_installed_apps)

    def _refresh_installed_apps(self):
        if self.operation_running: return
        self.status_var.set("Scansione app in corso...")
        self._log("Avvio scansione applicazioni installate...", "info")
        
        def _task():
            # Aumentiamo la tolleranza: a volte winget è lento a rispondere
            self.root.after(0, self.status_var.set, "Interrogazione Winget in corso...")
            ok, out = run_script("get_installed_apps.ps1")
            
            apps = []
            if out:
                for line in out.splitlines():
                    if "|" in line:
                        name, pkg_id = line.split("|", 1)
                        apps.append({"name": name.strip(), "id": pkg_id.strip()})
            
            self._installed_apps = sorted(apps, key=lambda x: x["name"].lower())
            self.root.after(0, self._render_installed_list)

            if not apps:
                self._log("Scansione completata: nessuna app rilevata tramite Winget. Prova ad aggiornare manualmente.", "warn")
            self.root.after(0, self.status_var.set, "Pronto")
        threading.Thread(target=_task, daemon=True).start()

    def _render_installed_list(self):
        for w in self._uninst_list_fr.winfo_children(): w.destroy()
        search_term = self._app_search_var.get().lower()
        
        count = 0
        for app in self._installed_apps:
            if search_term and search_term not in app["name"].lower() and search_term not in app["id"].lower():
                continue
            
            row = tk.Frame(self._uninst_list_fr, bg=BG_CARD, pady=4)
            row.pack(fill="x")
            tk.Label(row, text="• " + app["name"], font=FONT_BODY, bg=BG_CARD, fg=TEXT_PRIMARY, anchor="w").pack(side="left", fill="x", expand=True)
            tk.Label(row, text=app["id"], font=FONT_TINY, bg=BG_CARD, fg=TEXT_TERTIARY).pack(side="left", padx=10)
            DarkButton(row, "Disinstalla", lambda a=app: self._run_action(f"Rimozione {a['name']}", ["uninstall_app.ps1", a['id']]), 
                       style="danger").pack(side="right")
            tk.Frame(self._uninst_list_fr, bg=SEPARATOR, height=1).pack(fill="x")
            
            count += 1
            if count > 50: # Limite per performance, usa la ricerca per trovarne altre
                tk.Label(self._uninst_list_fr, text="...usa la ricerca per vedere altre app...", 
                         font=FONT_SMALL, bg=BG_CARD, fg=TEXT_TERTIARY).pack(pady=5)
                break

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Debloat
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_debloat(self, parent):
        self._page_header(parent, "Windows Debloat", "Rimuovi app preinstallate e telemetria inutile")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)
        
        # Sidebar vars per debloat
        self._debloat_vars = {}
        
        db_out, db_body = self._card(sf, "🚀  Ottimizzazione Sistema")
        db_out.grid(row=0, column=0, sticky="ew")
        
        actions = [
            ("Rimuovi Bloatware Windows", "Disinstalla app come Candy Crush, Xbox (se inutilizzato), e app meteo.", "debloat_system.ps1"),
            ("Disabilita Telemetria", "Blocca l'invio di dati diagnostici a Microsoft per privacy e velocità.", "disable_telemetry.ps1"),
            ("Rimuovi OneDrive", "Disinstalla completamente OneDrive se non lo usi.", "remove_onedrive.ps1")
        ]
        
        for title, desc, script in actions:
            f = tk.Frame(db_body, bg=BG_CARD, pady=10)
            f.pack(fill="x", padx=14)
            tk.Label(f, text=title, font=FONT_HEADING, bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w")
            tk.Label(f, text=desc, font=FONT_SMALL, bg=BG_CARD, fg=TEXT_SECONDARY, wraplength=600, justify="left").pack(anchor="w")
            DarkButton(f, "Esegui", lambda s=script: self._run_action(title, [s])).pack(anchor="w", pady=(5,0))
            tk.Frame(db_body, bg=SEPARATOR, height=1).pack(fill="x", pady=5)

        # Selective Debloat Card
        sel_out, sel_body = self._card(sf, "📦  Rimozione Selettiva App")
        sel_out.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        
        tk.Label(sel_body, text="Seleziona le app di sistema che desideri rimuovere:", 
                 font=FONT_BODY, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w", padx=14, pady=10)
        
        apps_frame = tk.Frame(sel_body, bg=BG_CARD)
        apps_frame.pack(fill="x", padx=14)
        
        debloat_list = [
            ("Meteo", "Microsoft.BingWeather"), ("Notizie", "Microsoft.BingNews"),
            ("Mappe", "Microsoft.WindowsMaps"), ("Xbox App", "Microsoft.XboxApp"),
            ("Solitario", "Microsoft.MicrosoftSolitaireCollection"), ("Skype", "Microsoft.SkypeApp"),
            ("Office Hub", "Microsoft.MicrosoftOfficeHub"), ("Film e TV", "Microsoft.ZuneVideo"),
            ("Musica Groove", "Microsoft.ZuneMusic"), ("Suggerimenti", "Microsoft.GetStarted"),
            ("Il tuo Telefono", "Microsoft.YourPhone"), ("Feedback Hub", "Microsoft.WindowsFeedbackHub")
        ]
        
        for i, (name, pkg) in enumerate(debloat_list):
            var = tk.BooleanVar()
            self._debloat_vars[pkg] = var
            col = i % 2
            row = i // 2
            cb = tk.Checkbutton(apps_frame, text=name, variable=var, font=FONT_SMALL,
                                bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_ROOT,
                                activebackground=BG_CARD, activeforeground=TEXT_PRIMARY,
                                highlightthickness=0, bd=0)
            cb.grid(row=row, column=col, sticky="w", padx=10, pady=2)

        btn_fr = tk.Frame(sel_body, bg=BG_CARD)
        btn_fr.pack(fill="x", padx=14, pady=15)
        DarkButton(btn_fr, "🗑️  Disinstalla App Selezionate", self._do_selective_debloat, style="danger").pack(side="left")

    def _do_selective_debloat(self):
        selected = [pkg for pkg, var in self._debloat_vars.items() if var.get()]
        if not selected:
            messagebox.showinfo("Info", "Seleziona almeno un'app da rimuovere.")
            return
        if messagebox.askyesno("Conferma", f"Sei sicuro di voler rimuovere {len(selected)} applicazioni di sistema?"):
            # Passiamo l'elenco dei pacchetti come argomenti allo script
            self._run_action("Rimozione Selettiva Bloatware", ["remove_selected_apps.ps1"] + selected)

    def _opt_card(self, parent, o):
        card = tk.Frame(parent, bg=BG_CARD,
                        highlightbackground=BG_CARD_BORDER, highlightthickness=1)
        top = tk.Frame(card, bg=BG_CARD)
        top.pack(fill="x", padx=14, pady=(14, 6))
        # Badge
        badge_fr = tk.Frame(top, bg=o["badge_color"])
        badge_fr.pack(side="right")
        tk.Label(badge_fr, text=o["badge"], font=FONT_TINY,
                 bg=o["badge_color"], fg="white", padx=6, pady=2).pack()
        # Icon + title
        tk.Label(top, text=o["icon"], font=("Segoe UI", 14), bg=BG_CARD,
                 fg=TEXT_PRIMARY).pack(side="left", padx=(0, 8))
        tk.Label(top, text=o["title"], font=FONT_HEADING,
                 bg=BG_CARD, fg=TEXT_PRIMARY).pack(side="left")
        tk.Frame(card, bg=SEPARATOR, height=1).pack(fill="x")
        tk.Label(card, text=o["desc"], font=FONT_BODY, bg=BG_CARD,
                 fg=TEXT_SECONDARY, wraplength=370, justify="left").pack(
            anchor="w", padx=14, pady=10)
        style = "accent" if o["id"] == "boost_all" else "normal"
        DarkButton(card, "▶  Esegui", o["action"], style=style).pack(
            anchor="w", padx=14, pady=(0, 12))
        return card

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Monitor
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_monitor(self, parent):
        self._page_header(parent, "Prestazioni", "Monitoraggio hardware in tempo reale")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)

        # ── Live metric tiles ──
        live_fr = tk.Frame(sf, bg=BG_MAIN)
        live_fr.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        for i in range(4): live_fr.columnconfigure(i, weight=1)

        self._mon_tiles = {}
        tile_defs = [
            ("🔲", "Processore",  "—", ACCENT,      "cpu"),
            ("🎮", "Scheda video","—", "#9b59b6",   "gpu"),
            ("🧠", "Memoria",     "—", SUCCESS_TEXT,"ram"),
            ("🌡", "Temperatura", "—", DANGER,      "temp"),
        ]
        for i, (icon, label, val, color, key) in enumerate(tile_defs):
            px = (0, 6) if i == 0 else (3, 3) if i < 3 else (6, 0)
            t = InfoTile(live_fr, icon, label, val, accent=color)
            t.grid(row=0, column=i, padx=px, sticky="ew")
            self._mon_tiles[key] = t

        # ── CPU history graph ──
        hist_out, hist_body = self._card(sf, "📈  Cronologia CPU (finestra 2 min)")
        hist_out.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self._cpu_canvas = tk.Canvas(hist_body, height=90, bg="#0d0d0d",
                                     highlightthickness=0)
        self._cpu_canvas.pack(fill="x", padx=14, pady=12)

        # ── Component details ──
        det_out, det_body = self._card(sf, "🔧  Dettagli Componenti")
        det_out.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        det_body.columnconfigure(0, weight=1)
        det_body.columnconfigure(1, weight=1)

        left  = tk.Frame(det_body, bg=BG_CARD)
        right = tk.Frame(det_body, bg=BG_CARD)
        left.grid(row=0, column=0, sticky="nsew", padx=(14, 7), pady=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(7, 14), pady=10)

        self._mon_det = {}
        left_rows  = [("cpu_pct","Utilizzo CPU"),("cpu_name","Modello CPU"),
                      ("cpu_temp","Temperatura CPU"),("procs","Processi attivi")]
        right_rows = [("ram_pct","Utilizzo RAM"),("ram_det","RAM Usata/Totale"),
                      ("disk_pct","Utilizzo Disco"),("disk_det","Disco Usato/Totale"),
                      ("uptime","Uptime")]
        for frame, rows in [(left, left_rows), (right, right_rows)]:
            frame.columnconfigure(1, weight=1)
            for r, (key, lbl) in enumerate(rows):
                tk.Label(frame, text=lbl + ":", font=FONT_SMALL, bg=BG_CARD,
                         fg=TEXT_TERTIARY).grid(row=r, column=0, sticky="w", pady=4, padx=(0,8))
                v = tk.Label(frame, text="—", font=("Segoe UI", 9, "bold"),
                             bg=BG_CARD, fg=TEXT_PRIMARY)
                v.grid(row=r, column=1, sticky="w", pady=4)
                self._mon_det[key] = v

    def _draw_history(self):
        c = self._cpu_canvas; c.update_idletasks()
        w, h = c.winfo_width(), c.winfo_height()
        if w <= 1: return
        c.delete("all")
        data = self._cpu_history[-60:]
        if len(data) < 2: return
        step = w / (len(data) - 1)
        pts = []
        for i, v in enumerate(data):
            pts.extend([i * step, h - (v / 100.0) * (h - 8) - 4])
        if len(pts) >= 4:
            # Fill under curve
            fill_pts = [0, h] + pts + [w, h]
            c.create_polygon(*fill_pts, fill="#0d2a45", outline="")
            c.create_line(*pts, fill=ACCENT, width=2, smooth=True)
        for pct, clr in [(50, "#1a3a4a"), (80, "#3a2a1a")]:
            y = h - (pct / 100.0) * (h - 8) - 4
            c.create_line(0, y, w, y, fill=clr, dash=(4, 4))
            c.create_text(6, y - 7, text=f"{pct}%", fill=TEXT_TERTIARY,
                          anchor="w", font=("Consolas", 7))

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Diagnostics
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_diagnostics(self, parent):
        self._page_header(parent, "Diagnostica", "Controlli integrità del sistema")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)

        c_out, c_body = self._card(sf, "🔍  Controlli di Integrità")
        c_out.grid(row=0, column=0, pady=(0, 12), sticky="ew")

        self._diag_rows = {}
        checks = [
            ("powershell", "PowerShell Disponibile", self._chk_powershell),
            ("scripts",    "Directory Script",        self._chk_scripts),
            ("psutil",     "Monitoraggio psutil",     self._chk_psutil),
            ("winver",     "Versione Windows",        self._chk_winver),
            ("diskspace",  "Spazio su Disco (C:)",    self._chk_diskspace),
            ("tempsize",   "Dimensione Directory Temp",self._chk_tempsize),
        ]
        for r, (key, label, fn) in enumerate(checks):
            row = tk.Frame(c_body, bg=BG_CARD,
                           highlightbackground=SEPARATOR, highlightthickness=1)
            row.pack(fill="x", padx=14, pady=2)
            row.columnconfigure(2, weight=1)
            # Status dot
            dot = tk.Label(row, text="●", font=("Segoe UI", 9),
                           bg=BG_CARD, fg=TEXT_TERTIARY, width=2)
            dot.pack(side="left", padx=(10, 4), pady=8)
            tk.Label(row, text=label, font=FONT_BODY,
                     bg=BG_CARD, fg=TEXT_PRIMARY).pack(side="left", pady=8)
            det = tk.Label(row, text="Non controllato", font=FONT_SMALL,
                           bg=BG_CARD, fg=TEXT_TERTIARY)
            det.pack(side="right", padx=12, pady=8)
            self._diag_rows[key] = (dot, det, fn)

        tk.Frame(c_body, bg=BG_CARD, height=8).pack()
        btn_fr = tk.Frame(c_body, bg=BG_CARD)
        btn_fr.pack(anchor="w", padx=14, pady=(0, 12))
        DarkButton(btn_fr, "▶  Esegui Tutti i Controlli", self._run_diag,
                   style="accent").pack(side="left")
        
        # Quick Fix Section
        fix_out, fix_body = self._card(sf, "🛠️  Riparazione Rapida")
        fix_out.grid(row=2, column=0, pady=(12, 0), sticky="ew")
        DarkButton(fix_body, "🔧 Ripara File di Sistema (SFC/DISM)", lambda: self._run_action("Riparazione", ["system_fix.ps1"]), style="normal").pack(padx=14, pady=12)

        o_out, o_body = self._card(sf, "📋  Output Diagnostica")
        o_out.grid(row=1, column=0, pady=(0, 12), sticky="nsew")
        sf.rowconfigure(1, weight=1)
        self._diag_out = scrolledtext.ScrolledText(
            o_body, font=FONT_MONO, height=12,
            bg="#0d0d0d", fg="#d4d4d4", relief="flat", bd=0, state="disabled")
        self._diag_out.pack(fill="both", expand=True, padx=1, pady=1)

    def _run_diag(self):
        self._dlog("─" * 60)
        self._dlog(f"Diagnostica — {datetime.datetime.now().strftime('%H:%M:%S')}")
        threading.Thread(target=self._diag_thread, daemon=True).start()

    def _diag_thread(self):
        for key, (dot, det, fn) in self._diag_rows.items():
            self.root.after(0, dot.configure, {"fg": WARNING_TEXT})
            ok, msg = fn()
            color = SUCCESS_TEXT if ok else DANGER
            self.root.after(0, dot.configure, {"fg": color})
            self.root.after(0, det.configure, {"text": msg, "fg": color})
            self._dlog(f"{'✓' if ok else '✗'} {msg}")
            time.sleep(0.2)
        self._dlog("Diagnostica completata.")

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
            if r.returncode == 0: return True, "PowerShell disponibile"
        except Exception: pass
        return False, "PowerShell non trovato"

    def _chk_scripts(self):
        if os.path.isdir(SCRIPTS_PATH):
            files = [f for f in os.listdir(SCRIPTS_PATH) if f.endswith(".ps1")]
            return (True, f"Trovati {len(files)} script") if files else (False, "Nessuno script .ps1")
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
                ok = free > 10
                return ok, f"{free:.1f} GB liberi su C:\\ ({'OK' if ok else 'BASSO'})"
        except Exception: pass
        return False, "Impossibile leggere info disco"

    def _chk_tempsize(self):
        try:
            tmp = os.environ.get("TEMP", "C:\\Windows\\Temp")
            total = 0; count = 0
            for root_, _, files in os.walk(tmp):
                for f in files:
                    try: total += os.path.getsize(os.path.join(root_, f)); count += 1
                    except Exception: pass
            mb = total / 1e6
            return mb < 500, f"{mb:.0f} MB in temp ({count} file)"
        except Exception as e:
            return False, f"Errore: {e}"

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Tips
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_tips(self, parent):
        self._page_header(parent, "Consigli sulle Prestazioni",
                          "Guida esperta per mantenere il sistema veloce e sano")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)

        # Filter bar
        fbar = tk.Frame(sf, bg=BG_CARD,
                        highlightbackground=BG_CARD_BORDER, highlightthickness=1)
        fbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        tk.Label(fbar, text="  Filtra per categoria:", font=FONT_SMALL,
                 bg=BG_CARD, fg=TEXT_SECONDARY).pack(side="left", padx=(8, 4), pady=10)
        self._tip_filter = tk.StringVar(value="Tutti")
        for cat in ["Tutti","CPU","RAM","Disco","Rete","GPU","Sicurezza","Generale"]:
            rb = tk.Radiobutton(fbar, text=cat, variable=self._tip_filter, value=cat,
                                font=FONT_SMALL, bg=BG_CARD, fg=TEXT_SECONDARY,
                                selectcolor=BG_CARD_BORDER, activebackground=BG_CARD,
                                activeforeground=TEXT_PRIMARY,
                                command=self._render_tips)
            rb.pack(side="left", padx=4, pady=8)

        self._tips_box = tk.Frame(sf, bg=BG_MAIN)
        self._tips_box.grid(row=1, column=0, sticky="ew")
        self._tips_box.columnconfigure(0, weight=1)
        self._render_tips()

    def _render_tips(self):
        for w in self._tips_box.winfo_children(): w.destroy()
        cat_filter = self._tip_filter.get()
        cat_colors = {"CPU": ACCENT, "RAM": SUCCESS_TEXT, "Disco": WARNING_TEXT,
                      "Rete": ACCENT2, "GPU": "#9b59b6", "Sicurezza": DANGER,
                      "Generale": TEXT_SECONDARY}
        filtered = [(c, t) for c, t in PERFORMANCE_TIPS
                    if cat_filter in ("Tutti", "All") or c == cat_filter]
        for r, (cat, tip) in enumerate(filtered):
            color = cat_colors.get(cat, TEXT_SECONDARY)
            card = tk.Frame(self._tips_box, bg=BG_CARD,
                            highlightbackground=BG_CARD_BORDER, highlightthickness=1)
            card.grid(row=r, column=0, sticky="ew", pady=(0, 6))
            card.columnconfigure(1, weight=1)
            # Left color bar
            accent_bar = tk.Frame(card, bg=color, width=3)
            accent_bar.grid(row=0, column=0, sticky="ns")
            # Badge
            badge = tk.Frame(card, bg=color)
            badge.grid(row=0, column=0, padx=(10, 8), pady=10, sticky="n")
            tk.Label(badge, text=f" {cat} ", font=FONT_TINY,
                     bg=color, fg="white").pack()
            # Tip text
            tk.Label(card, text=tip, font=FONT_BODY, bg=BG_CARD, fg=TEXT_SECONDARY,
                     wraplength=620, justify="left").grid(
                row=0, column=1, sticky="ew", padx=(0, 14), pady=10)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Log
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_log(self, parent):
        self._page_header(parent, "Registro Attività", "Cronologia completa di tutte le operazioni")
        content = tk.Frame(parent, bg=BG_MAIN)
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 16))
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)
        parent.rowconfigure(1, weight=1)

        tb = tk.Frame(content, bg=BG_MAIN)
        tb.grid(row=0, column=0, sticky="ew", pady=(12, 8))
        DarkButton(tb, "🗑  Cancella Registro", self._clear_log).pack(side="right")

        log_fr = tk.Frame(content, bg=BG_CARD,
                          highlightbackground=BG_CARD_BORDER, highlightthickness=1)
        log_fr.grid(row=1, column=0, sticky="nsew")
        log_fr.columnconfigure(0, weight=1)
        log_fr.rowconfigure(0, weight=1)

        self._main_log = scrolledtext.ScrolledText(
            log_fr, font=FONT_MONO, bg="#0d0d0d", fg="#d4d4d4",
            insertbackground="white", relief="flat", bd=0, state="disabled")
        self._main_log.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        for tag, fg in [("info", INFO_TEXT), ("warn", WARNING_TEXT),
                        ("error", DANGER), ("ok", SUCCESS_TEXT),
                        ("ts", TEXT_TERTIARY), ("head", "#dcdcaa")]:
            self._main_log.tag_config(tag, foreground=fg)

    def _clear_log(self):
        self._main_log.configure(state="normal")
        self._main_log.delete("1.0", "end")
        self._main_log.configure(state="disabled")
        self._log("Registro cancellato.", "info")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB: Settings
    # ─────────────────────────────────────────────────────────────────────────
    def _tab_settings(self, parent):
        self._page_header(parent, "Impostazioni", "Configura le preferenze di CoreTune")
        sf = self._scrollable(parent)
        sf.columnconfigure(0, weight=1)

        s_out, s_body = self._card(sf, "📁  Configurazione Script")
        s_out.grid(row=0, column=0, pady=(0, 12), sticky="ew")
        s_body.columnconfigure(1, weight=1)
        tk.Label(s_body, text="Directory Script:", font=FONT_BODY,
                 bg=BG_CARD, fg=TEXT_SECONDARY).grid(row=0, column=0, padx=14, pady=12, sticky="w")
        self._scripts_path_var = tk.StringVar(value=SCRIPTS_PATH)
        entry = tk.Entry(s_body, textvariable=self._scripts_path_var,
                         font=FONT_BODY, relief="flat", bd=1,
                         bg=BG_CARD_BORDER, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        entry.grid(row=0, column=1, padx=(0, 14), pady=12, sticky="ew",
                   ipady=6)
        tk.Label(s_body, text="Percorso relativo alla directory dell'app (.ps1).",
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_TERTIARY).grid(
            row=1, column=0, columnspan=2, padx=14, pady=(0, 12), sticky="w")

        m_out, m_body = self._card(sf, "📊  Monitoraggio")
        m_out.grid(row=1, column=0, pady=(0, 12), sticky="ew")
        tk.Label(m_body, text="Monitoraggio in background attivo — aggiornamento ogni 2 secondi.",
                 font=FONT_BODY, bg=BG_CARD, fg=TEXT_SECONDARY).pack(
            anchor="w", padx=14, pady=12)

        a_out, a_body = self._card(sf, "ℹ  Informazioni su CoreTune")
        a_out.grid(row=2, column=0, pady=(0, 12), sticky="ew")
        a_body.columnconfigure(1, weight=1)
        for r, (k, v) in enumerate([
            ("Applicazione", f"CoreTune {APP_VERSION}"),
            ("Sviluppatore", "Aura Studio"),
            ("Piattaforma",  f"{platform.system()} {platform.release()}"),
            ("Python",       sys.version.split()[0]),
        ]):
            tk.Label(a_body, text=k + ":", font=FONT_BODY,
                     bg=BG_CARD, fg=TEXT_SECONDARY).grid(row=r, column=0, padx=14, pady=5, sticky="w")
            tk.Label(a_body, text=v, font=FONT_HEADING,
                     bg=BG_CARD, fg=TEXT_PRIMARY).grid(row=r, column=1, padx=8, pady=5, sticky="w")
        tk.Frame(a_body, bg=BG_CARD, height=8).grid(row=4, column=0)

    # ─────────────────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────────────────
    def _run_action(self, name, script_list):
        if self.operation_running:
            messagebox.showwarning("Occupato", "Un'altra operazione è già in esecuzione.")
            return
        self.operation_running = True
        self.status_var.set(f"Esecuzione: {name}...")
        self._log("─" * 50, "head")
        self._log(f"▶ Avvio: {name}", "head")
        threading.Thread(target=self._action_thread, args=(name, script_list), daemon=True).start()

    def _action_thread(self, name, script_list):
        ok_count = 0
        # Determina se è un singolo script con argomenti o una lista di script diversi
        # Se ci sono più elementi e il secondo NON termina con .ps1, sono argomenti per il primo
        is_args = len(script_list) > 1 and not script_list[1].lower().endswith(".ps1")
        
        if is_args:
            base = script_list[0]
            args = script_list[1:]
            self._log(f"  Esecuzione script: {base}", "info")
            ok, _ = run_script(base, args=args, log_callback=self._log)
            if ok: ok_count = 1
            total = 1
        else:
            total = len(script_list)
            for s in script_list:
                self._log(f"  Esecuzione: {s}", "info")
                ok, _ = run_script(s, log_callback=self._log)
                if ok: ok_count += 1
        
        if ok_count == total:
            self._log(f"✓ Completato: {name}", "ok")
        else:
            self._log(f"⚠ Operazione terminata con {total - ok_count} errori", "warn")

        self._log(f"Fine sessione: {name}", "info")
        self.root.after(0, self.status_var.set, "Pronto")
        self.root.after(0, setattr, self, "operation_running", False)

    def _do_boost_all(self):
        self._run_action("Ottimizzazione Completa", ["clean_temp.ps1","discord.ps1","performance_mode.ps1"])
    def _do_clean_temp(self):
        self._run_action("Pulisci File Temporanei", ["clean_temp.ps1"])
    def _do_discord(self):
        self._run_action("Pulizia Discord", ["discord.ps1"])
    def _do_perf_mode(self):
        self._run_action("Modalità Prestazioni", ["performance_mode.ps1"])
    def _open_taskmgr(self):
        try:
            subprocess.Popen("taskmgr")
            self._log("✓ Gestione Attività avviata", "ok")
        except Exception as e:
            self._log(f"Impossibile aprire Gestione Attività: {e}", "error")

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
        except Exception: pass

    # ─────────────────────────────────────────────────────────────────────────
    # Monitor callback
    # ─────────────────────────────────────────────────────────────────────────
    def _on_monitor_update(self, data):
        self.root.after(0, self._apply_data, data)

    def _apply_data(self, data):
        cpu  = data.get("cpu",  0)
        ram  = data.get("ram",  0)
        disk = data.get("disk", 0)
        gpu  = data.get("gpu",  0)
        temp = data.get("cpu_temp")
        procs= data.get("processes", 0)

        # Dashboard gauges
        if hasattr(self, "_gauges"):
            self._gauges["cpu"].set_value(cpu)
            self._gauges["ram"].set_value(ram)
            self._gauges["disk"].set_value(disk)
            self._gauges["gpu"].set_value(gpu)

        # Dashboard system info tiles
        if hasattr(self, "_si_tiles"):
            ram_gb = data.get("ram_total", 0)
            self._si_tiles["Memoria"].update_val(f"{ram_gb:.0f} GB", ram, SUCCESS_TEXT)
            disk_t = data.get("disk_total", 0)
            self._si_tiles["Archiviazione"].update_val(f"{disk_t:.0f} GB", disk, WARNING_TEXT)
            self._si_tiles["Uptime"].update_val(data.get("uptime", "—"))
            self._si_tiles["Prestazioni"].update_val(f"{(100-cpu):.0f}/100")

        # Dashboard stat tiles
        if hasattr(self, "_stat_tiles"):
            self._stat_tiles["Processi"].update_val(str(procs))

        # Monitor tiles
        if hasattr(self, "_mon_tiles"):
            self._mon_tiles["cpu"].update_val(f"{cpu:.0f}%",  cpu,  ACCENT)
            self._mon_tiles["ram"].update_val(f"{ram:.0f}%",  ram,  SUCCESS_TEXT)
            self._mon_tiles["gpu"].update_val(f"{gpu:.0f}%",  gpu,  "#9b59b6")
            temp_str = f"{temp:.0f}°C" if temp else "N/A"
            self._mon_tiles["temp"].update_val(temp_str)
            if temp:
                self._mon_tiles["temp"].update_val(temp_str, min(100, temp), DANGER)

        # Monitor details
        if hasattr(self, "_mon_det"):
            d = self._mon_det
            d["cpu_pct"].configure(text=f"{cpu:.1f}%")
            d["cpu_name"].configure(text=data.get("cpu_name","Unknown")[:50])
            d["cpu_temp"].configure(text=f"{temp}°C" if temp else "N/A")
            d["procs"].configure(text=str(procs))
            d["ram_pct"].configure(text=f"{ram:.1f}%")
            d["ram_det"].configure(
                text=f"{data.get('ram_used',0):.2f} / {data.get('ram_total',0):.1f} GB")
            d["disk_pct"].configure(text=f"{disk:.1f}%")
            d["disk_det"].configure(
                text=f"{data.get('disk_used',0):.0f} / {data.get('disk_total',0):.0f} GB")
            d["uptime"].configure(text=data.get("uptime","—"))

        # CPU history
        self._cpu_history.append(cpu)
        if len(self._cpu_history) > 120: self._cpu_history.pop(0)
        if hasattr(self, "_cpu_canvas"): self._draw_history()

        # Status bar
        temp_part = f"  🌡 {temp:.0f}°C" if temp else ""
        self._sb_mon.configure(
            text=f"CPU {cpu:.0f}%   RAM {ram:.0f}%   Disco {disk:.0f}%{temp_part}")

    # ─────────────────────────────────────────────────────────────────────────
    # Utility
    # ─────────────────────────────────────────────────────────────────────────
    def _rotate_tip(self):
        if hasattr(self, "_tip_txt_lbl"):
            cat, tip = PERFORMANCE_TIPS[self.tip_index % len(PERFORMANCE_TIPS)]
            self._tip_cat_lbl.configure(text=f"▸  {cat}")
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
    root.configure(bg=BG_ROOT)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
        # Enable dark title bar on Windows 11
        try:
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            windll.dwmapi.DwmSetWindowAttribute(
                windll.user32.GetForegroundWindow(),
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                byref(c_int(1)), sizeof(c_int))
        except Exception: pass
    except Exception: pass

    app = CoreTuneApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()