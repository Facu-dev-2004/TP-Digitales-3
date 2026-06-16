"""
reproductor.py — Receptor continuo y reproductor de audio para LPC1769
=======================================================================
Protocolo (de sendSamplesUART en main.c):
  - LISTSIZE = 12000 muestras
  - 2 bytes por muestra, big-endian:
      buf[0] = (sample >> 8) & 0x03   → 2 bits altos (bits 9:8)
      buf[1] =  sample       & 0xFF   → 8 bits bajos (bits 7:0)
  - sample es 10 bits (0..1023)
  - ADC_RATE = 8000 Hz
  - Baud rate UART2 = 115200

Pitch shift (solo numpy):
  Se aplica resampleo: se interpolan N*factor muestras y se recortan a N.
  Subir el tono = factor > 1.0  →  el audio suena más agudo y levemente
  más corto (proporcional al factor). Sin dependencias extra.

Uso:
  python reproductor.py                    # auto-detecta puerto, abre GUI
  python reproductor.py COM3               # Windows
  python reproductor.py /dev/ttyUSB0       # Linux/Mac
  python reproductor.py --demo             # señal sintética sin hardware
"""

import sys
import time
import struct
import argparse
import threading
import queue
import os
from datetime import datetime

# ── dependencias ─────────────────────────────────────────────────────────────
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("[ERROR] pyserial no instalado.  pip install pyserial")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("[ERROR] numpy no instalado.  pip install numpy")
    sys.exit(1)

try:
    import sounddevice as sd
except ImportError:
    print("[ERROR] sounddevice no instalado.  pip install sounddevice")
    sys.exit(1)

import tkinter as tk
from tkinter import filedialog

# ── constantes (deben coincidir con el .c) ────────────────────────────────────
BAUD_RATE    = 115200
LISTSIZE     = 12000
BYTES_TOTAL  = LISTSIZE * 2   # 24000 bytes
ADC_RATE     = 8000
ADC_MAX      = 255.0          # centro de escala 10-bit

# ── pitch shift ───────────────────────────────────────────────────────────────
# Factor > 1.0 → sube el tono (1.5 = una quinta musical, ~7 semitonos)
# Cambiar este valor para ajustar cuánto sube el tono.
PITCH_FACTOR = 1.5

# ── paleta de colores ─────────────────────────────────────────────────────────
C_BG      = "#0D0F14"
C_PANEL   = "#13161E"
C_BORDER  = "#1E2230"
C_ACCENT  = "#00C8A0"
C_ACCENT2 = "#0088FF"
C_WARN    = "#FF6B35"
C_TEXT    = "#E8EAF0"
C_MUTED   = "#5A6070"
C_SUCCESS = "#00C8A0"
C_ERROR   = "#FF4560"

FONT_TITLE  = ("Consolas", 11, "bold")
FONT_STATUS = ("Consolas", 10)
FONT_LOG    = ("Consolas", 9)
FONT_BIG    = ("Consolas", 28, "bold")
FONT_LABEL  = ("Consolas", 8)


# ══════════════════════════════════════════════════════════════════════════════
#  UTILIDADES DE PUERTO
# ══════════════════════════════════════════════════════════════════════════════

_USB_KEYWORDS = ("cp210", "silicon lab", "ch340", "ch341", "uart",
                 "usb serial", "prolific", "ftdi", "ft232")


def find_serial_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if any(k in p.description.lower() for k in _USB_KEYWORDS):
            return p.device
    return ports[0].device if ports else None


# ══════════════════════════════════════════════════════════════════════════════
#  PITCH SHIFT (solo numpy)
# ══════════════════════════════════════════════════════════════════════════════

def pitch_shift(audio: np.ndarray, factor: float) -> np.ndarray:
    """
    Sube el tono del audio sin dependencias externas.

    Técnica: resampleo por interpolación lineal.
    ─────────────────────────────────────────────
    El audio original tiene N muestras a 8000 Hz.
    Queremos que suene como si hubiera sido grabado
    a 8000 Hz pero con las frecuencias multiplicadas
    por `factor`.

    Pasos:
      1. Generar N*factor muestras interpoladas del
         audio original (como si lo "estiráramos").
      2. Tomar solo las primeras N muestras.

    Resultado: el mismo contenido cabe en menos tiempo
    → al reproducirlo a 8000 Hz suena más agudo.
    El audio queda levemente más corto (N / factor segundos).

    factor = 1.0  → sin cambio
    factor = 1.5  → sube ~7 semitonos (quinta musical)
    factor = 2.0  → sube una octava completa
    """
    if factor == 1.0:
        return audio

    n_orig    = len(audio)
    # índices de las N*factor muestras interpoladas
    n_stretched = int(n_orig * factor)
    idx_orig  = np.linspace(0, n_orig - 1, n_stretched)
    # interpolación lineal entre muestras contiguas
    idx_lo    = np.floor(idx_orig).astype(np.int32)
    idx_hi    = np.clip(idx_lo + 1, 0, n_orig - 1)
    frac      = (idx_orig - idx_lo).astype(np.float32)
    stretched = audio[idx_lo] + frac * (audio[idx_hi] - audio[idx_lo])
    # recortar a N muestras → mismo largo, tono más agudo
    return stretched[:n_orig].astype(np.float32)


# ══════════════════════════════════════════════════════════════════════════════
#  DECODIFICACIÓN Y AUDIO
# ══════════════════════════════════════════════════════════════════════════════

def decodificar(raw: bytes) -> np.ndarray:
    if len(raw) % 2 != 0:
        raw = raw[:-1]
    muestras = []
    for i in range(0, len(raw), 2):
        sample = ((raw[i] & 0x03) << 8) | raw[i + 1]
        muestras.append(sample)
    arr = np.array(muestras, dtype=np.float32)
    arr = (arr / ADC_MAX - 0.5) * 2.0
    return arr


def reproducir_async(muestras: np.ndarray):
    """Reproducción en hilo aparte para no bloquear la GUI."""
    def _play():
        try:
            sd.play(muestras, samplerate=ADC_RATE)
            sd.wait()
        except Exception as e:
            print(f"[AUDIO] Error: {e}")
    threading.Thread(target=_play, daemon=True).start()


def guardar_wav(muestras: np.ndarray, nombre: str, rate: int = ADC_RATE):
    pcm        = (muestras * 32767).astype(np.int16)
    data_bytes = pcm.tobytes()
    n          = len(pcm)
    bps        = 16
    byte_rate  = rate * bps // 8
    data_size  = n * bps // 8

    with open(nombre, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))
        f.write(struct.pack("<H", 1))        # PCM
        f.write(struct.pack("<H", 1))        # mono
        f.write(struct.pack("<I", rate))
        f.write(struct.pack("<I", byte_rate))
        f.write(struct.pack("<H", bps // 8))
        f.write(struct.pack("<H", bps))
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(data_bytes)
    return n / rate


def generar_demo() -> np.ndarray:
    t     = np.linspace(0, LISTSIZE / ADC_RATE, LISTSIZE, dtype=np.float32)
    chirp = np.sin(2 * np.pi * (200 + (3000 * t / t[-1])) * t)
    s10   = np.clip(((chirp * 0.45 + 0.5) * ADC_MAX).astype(np.uint16), 0, int(ADC_MAX))
    raw   = bytearray()
    for s in s10:
        raw.append((s >> 8) & 0x03)
        raw.append(s & 0xFF)
    return decodificar(bytes(raw))


# ══════════════════════════════════════════════════════════════════════════════
#  HILO RECEPTOR UART
# ══════════════════════════════════════════════════════════════════════════════

class ReceiverThread(threading.Thread):
    def __init__(self, port: str, out_queue: queue.Queue, log_queue: queue.Queue):
        super().__init__(daemon=True)
        self.port      = port
        self.out_queue = out_queue
        self.log_queue = log_queue
        self._stop_evt = threading.Event()
        self.ser       = None

    def log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{ts}] {msg}")

    def stop(self):
        self._stop_evt.set()
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass

    def run(self):
        self.log(f"Abriendo {self.port} @ {BAUD_RATE} baud…")
        try:
            self.ser = serial.Serial(
                port     = self.port,
                baudrate = BAUD_RATE,
                bytesize = serial.EIGHTBITS,
                parity   = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                timeout  = 0.1,
            )
        except serial.SerialException as e:
            self.log(f"ERROR al abrir puerto: {e}")
            self.out_queue.put(("error", str(e)))
            return

        self.log("Puerto abierto. Esperando grabaciones del LPC1769…")
        self.out_queue.put(("ready", None))

        grabacion_num = 0

        while not self._stop_evt.is_set():
            raw             = bytearray()
            bytes_esperados = BYTES_TOTAL

            while len(raw) < bytes_esperados and not self._stop_evt.is_set():
                try:
                    chunk = self.ser.read(min(256, bytes_esperados - len(raw)))
                except serial.SerialException as e:
                    self.log(f"ERROR de lectura: {e}")
                    self._stop_evt.set()
                    break

                if chunk:
                    if len(raw) == 0:
                        grabacion_num += 1
                        self.log(f"Recibiendo grabación #{grabacion_num}…")
                        self.out_queue.put(("receiving", grabacion_num))
                    raw.extend(chunk)
                    pct = int(len(raw) / bytes_esperados * 100)
                    self.out_queue.put(("progress", pct))

            if len(raw) >= bytes_esperados:
                muestras = decodificar(bytes(raw[:bytes_esperados]))
                rms      = float(np.sqrt(np.mean(muestras**2)))
                peak     = float(np.max(np.abs(muestras)))
                self.log(f"Grabación #{grabacion_num} lista — RMS={rms:.3f}  PEAK={peak:.3f}")
                self.out_queue.put(("done", (grabacion_num, muestras)))

        self.log("Receptor detenido.")
        if self.ser and self.ser.is_open:
            self.ser.close()


# ══════════════════════════════════════════════════════════════════════════════
#  GUI PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self, port: str | None, demo: bool = False):
        super().__init__()
        self.title("LPC1769 Audio Receiver")
        self.configure(bg=C_BG)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._port       = port
        self._demo       = demo
        self._last_audio = None   # audio original (sin efecto)
        self._last_num   = 0
        self._receiver   = None
        self._out_queue  = queue.Queue()
        self._log_queue  = queue.Queue()
        self._grab_count = 0

        # estado del pitch shift (botón toggle)
        self._pitch_on   = tk.BooleanVar(value=False)

        self._build_ui()
        self.after(100, self._start)
        self.after(50,  self._poll)

    # ── construcción de la UI ──────────────────────────────────────────────

    def _build_ui(self):
        # ── título ──────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=C_BG, padx=20, pady=14)
        hdr.pack(fill="x")

        tk.Label(hdr, text="◈ LPC1769", font=("Consolas", 13, "bold"),
                 bg=C_BG, fg=C_ACCENT).pack(side="left")
        tk.Label(hdr, text=" Audio Receiver", font=("Consolas", 13),
                 bg=C_BG, fg=C_TEXT).pack(side="left")

        self._lbl_port = tk.Label(hdr, text="", font=FONT_LABEL,
                                  bg=C_BG, fg=C_MUTED)
        self._lbl_port.pack(side="right")

        tk.Frame(self, bg=C_BORDER, height=1).pack(fill="x")

        # ── panel central: contador + estado ────────────────────────────
        mid = tk.Frame(self, bg=C_PANEL, padx=24, pady=20)
        mid.pack(fill="x")

        left = tk.Frame(mid, bg=C_PANEL)
        left.pack(side="left")

        tk.Label(left, text="GRABACIONES", font=FONT_LABEL,
                 bg=C_PANEL, fg=C_MUTED).pack(anchor="w")
        self._lbl_count = tk.Label(left, text="0", font=FONT_BIG,
                                   bg=C_PANEL, fg=C_ACCENT)
        self._lbl_count.pack(anchor="w")

        tk.Frame(mid, bg=C_BORDER, width=1).pack(side="left", fill="y", padx=20)

        right = tk.Frame(mid, bg=C_PANEL)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="ESTADO", font=FONT_LABEL,
                 bg=C_PANEL, fg=C_MUTED).pack(anchor="w")
        self._lbl_status = tk.Label(right, text="Iniciando…",
                                    font=FONT_STATUS, bg=C_PANEL, fg=C_TEXT,
                                    wraplength=280, justify="left")
        self._lbl_status.pack(anchor="w", pady=(4, 8))

        tk.Label(right, text="RECEPCIÓN", font=FONT_LABEL,
                 bg=C_PANEL, fg=C_MUTED).pack(anchor="w")
        prog_bg = tk.Frame(right, bg=C_BORDER, height=6, width=280)
        prog_bg.pack(anchor="w", pady=(2, 0))
        prog_bg.pack_propagate(False)

        self._prog_bar = tk.Frame(prog_bg, bg=C_MUTED, height=6, width=0)
        self._prog_bar.place(x=0, y=0, height=6)

        tk.Frame(self, bg=C_BORDER, height=1).pack(fill="x")

        # ── botones ──────────────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=C_BG, padx=20, pady=14)
        btn_frame.pack(fill="x")

        self._btn_save = tk.Button(
            btn_frame, text="▼  Guardar WAV",
            font=FONT_STATUS, bg=C_PANEL, fg=C_ACCENT,
            activebackground=C_BORDER, activeforeground=C_ACCENT,
            relief="flat", bd=0, padx=14, pady=7,
            cursor="hand2", state="disabled",
            command=self._save_wav,
        )
        self._btn_save.pack(side="left", padx=(0, 8))

        self._btn_replay = tk.Button(
            btn_frame, text="▶  Reproducir",
            font=FONT_STATUS, bg=C_PANEL, fg=C_ACCENT2,
            activebackground=C_BORDER, activeforeground=C_ACCENT2,
            relief="flat", bd=0, padx=14, pady=7,
            cursor="hand2", state="disabled",
            command=self._replay,
        )
        self._btn_replay.pack(side="left", padx=(0, 8))

        # ── botón pitch toggle ───────────────────────────────────────────
        # Se dibuja como un Checkbutton con apariencia de botón plano.
        # Cuando está activo cambia de color para indicar el estado.
        self._btn_pitch = tk.Checkbutton(
            btn_frame,
            text="▲  Voz Grave",
            font=FONT_STATUS,
            variable=self._pitch_on,
            # colores cuando está DESACTIVADO
            bg=C_PANEL, fg=C_MUTED,
            # colores cuando está ACTIVADO (selectcolor = fondo del check)
            selectcolor=C_PANEL,
            activebackground=C_PANEL, activeforeground=C_WARN,
            relief="flat", bd=0, padx=14, pady=7,
            cursor="hand2",
            indicatoron=False,   # ocultar el cuadrito de checkbox
            command=self._on_pitch_toggle,
        )
        self._btn_pitch.pack(side="left")

        tk.Frame(self, bg=C_BORDER, height=1).pack(fill="x")

        # ── log ──────────────────────────────────────────────────────────
        log_frame = tk.Frame(self, bg=C_BG, padx=12, pady=10)
        log_frame.pack(fill="both", expand=True)

        tk.Label(log_frame, text="LOG", font=FONT_LABEL,
                 bg=C_BG, fg=C_MUTED).pack(anchor="w", pady=(0, 4))

        self._log_text = tk.Text(
            log_frame, height=10, width=62,
            bg=C_PANEL, fg=C_MUTED,
            font=FONT_LOG, relief="flat", bd=0,
            state="disabled", wrap="word",
            insertbackground=C_ACCENT,
        )
        self._log_text.pack(fill="both", expand=True)

        self._log_text.tag_config("accent",  foreground=C_ACCENT)
        self._log_text.tag_config("warn",    foreground=C_WARN)
        self._log_text.tag_config("error",   foreground=C_ERROR)
        self._log_text.tag_config("muted",   foreground=C_MUTED)

        # ── pie ──────────────────────────────────────────────────────────
        tk.Frame(self, bg=C_BORDER, height=1).pack(fill="x")
        foot = tk.Frame(self, bg=C_BG, pady=6)
        foot.pack(fill="x")
        tk.Label(foot,
                 text=f"8000 Hz · 10-bit · mono · {BYTES_TOTAL} bytes/trama",
                 font=FONT_LABEL, bg=C_BG, fg=C_MUTED).pack()

    # ── toggle pitch ───────────────────────────────────────────────────────

    def _on_pitch_toggle(self):
        """Actualiza el color del botón y loguea el cambio de estado."""
        if self._pitch_on.get():
            self._btn_pitch.config(fg=C_WARN)
            self._log_append(
                f"▲ Pitch shift ACTIVADO  (factor ×{PITCH_FACTOR})", "warn"
            )
        else:
            self._btn_pitch.config(fg=C_MUTED)
            self._log_append("◇ Pitch shift desactivado", "muted")

    def _get_audio_para_reproducir(self) -> np.ndarray:
        """
        Devuelve el audio listo para reproducir:
        original o con pitch shift según el estado del toggle.
        """
        if self._last_audio is None:
            return np.zeros(LISTSIZE, dtype=np.float32)

        if self._pitch_on.get():
            return pitch_shift(self._last_audio, PITCH_FACTOR)
        return self._last_audio

    # ── arranque ───────────────────────────────────────────────────────────

    def _start(self):
        if self._demo:
            self._log_append("Modo DEMO — generando señal sintética…", "warn")
            self._set_status("Modo demo activo", C_WARN)
            muestras = generar_demo()
            self._on_audio_ready(0, muestras)
            return

        if self._port is None:
            self._port = find_serial_port()

        if self._port is None:
            self._log_append("No se encontró ningún puerto serie.", "error")
            self._set_status("Sin puerto — pasá el puerto como argumento", C_ERROR)
            return

        self._launch_receiver(self._port)

    def _launch_receiver(self, port: str):
        if self._receiver and self._receiver.is_alive():
            self._receiver.stop()

        self._port = port
        self._lbl_port.config(text=port)
        self._log_append(f"Conectando a {port}…", "muted")
        self._set_status("Conectando…", C_MUTED)
        self._set_progress(0)

        self._receiver = ReceiverThread(port, self._out_queue, self._log_queue)
        self._receiver.start()

    # ── polling de colas ──────────────────────────────────────────────────

    def _poll(self):
        try:
            while True:
                msg = self._log_queue.get_nowait()
                self._log_append(msg)
        except queue.Empty:
            pass

        try:
            while True:
                event, data = self._out_queue.get_nowait()

                if event == "ready":
                    self._set_status("Esperando grabación — presioná EINT0", C_TEXT)
                    self._set_progress(0)

                elif event == "receiving":
                    self._set_status(f"Recibiendo grabación #{data}…", C_WARN)

                elif event == "progress":
                    self._set_progress(data)

                elif event == "done":
                    num, muestras = data
                    self._on_audio_ready(num, muestras)

                elif event == "error":
                    self._set_status(f"Error: {data}", C_ERROR)

        except queue.Empty:
            pass

        self.after(50, self._poll)

    # ── audio listo ────────────────────────────────────────────────────────

    def _on_audio_ready(self, num: int, muestras: np.ndarray):
        self._last_audio = muestras           # guardar siempre el original
        self._last_num   = num
        self._grab_count = num if num > 0 else (self._grab_count + 1)

        self._lbl_count.config(text=str(self._grab_count))
        self._set_progress(100)

        audio_out = self._get_audio_para_reproducir()

        if self._pitch_on.get():
            self._set_status(
                f"Reproduciendo #{self._grab_count} — voz grave ▲", C_WARN
            )
            self._log_append(
                f"▶ Reproduciendo #{self._grab_count} (pitch ×{PITCH_FACTOR})", "warn"
            )
        else:
            self._set_status(
                f"Reproduciendo grabación #{self._grab_count}…", C_ACCENT
            )
            self._log_append(f"▶ Reproduciendo #{self._grab_count}", "accent")

        self._btn_save.config(state="normal")
        self._btn_replay.config(state="normal")

        reproducir_async(audio_out)
        self.after(1700, self._back_to_waiting)

    def _back_to_waiting(self):
        if self._receiver and self._receiver.is_alive():
            self._set_status("Esperando grabación — presioná EINT0", C_TEXT)
            self._set_progress(0)

    # ── acciones de botones ────────────────────────────────────────────────

    def _save_wav(self):
        """
        Guarda el WAV con el efecto aplicado si el pitch está activo,
        o el audio original si está desactivado.
        """
        if self._last_audio is None:
            return
        ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
        sufijo  = f"_pitch{PITCH_FACTOR}" if self._pitch_on.get() else ""
        default = f"grabacion_{ts}{sufijo}.wav"
        path    = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV audio", "*.wav")],
            initialfile=default,
            title="Guardar grabación",
        )
        if not path:
            return
        audio_out = self._get_audio_para_reproducir()
        dur = guardar_wav(audio_out, path)
        self._log_append(
            f"WAV guardado: {os.path.basename(path)}  ({dur:.2f}s)", "accent"
        )

    def _replay(self):
        if self._last_audio is None:
            return
        audio_out = self._get_audio_para_reproducir()
        efecto    = f" (pitch ×{PITCH_FACTOR})" if self._pitch_on.get() else ""
        self._log_append(
            f"▶ Reproduciendo #{self._last_num} (manual){efecto}", "accent"
        )
        if self._pitch_on.get():
            self._set_status(
                f"Reproduciendo #{self._last_num} — voz graves ▲", C_WARN
            )
        else:
            self._set_status(
                f"Reproduciendo grabación #{self._last_num}…", C_ACCENT
            )
        reproducir_async(audio_out)
        self.after(1700, self._back_to_waiting)

    # ── helpers UI ─────────────────────────────────────────────────────────

    def _set_status(self, msg: str, color: str = C_TEXT):
        self._lbl_status.config(text=msg, fg=color)

    def _set_progress(self, pct: int):
        w     = int(280 * pct / 100)
        color = C_ACCENT if pct < 100 else C_SUCCESS
        self._prog_bar.config(width=w, bg=color)

    def _log_append(self, msg: str, tag: str = ""):
        self._log_text.config(state="normal")
        self._log_text.insert("end", msg + "\n", tag or "muted")
        self._log_text.see("end")
        self._log_text.config(state="disabled")

    # ── cierre ─────────────────────────────────────────────────────────────

    def _on_close(self):
        if self._receiver:
            self._receiver.stop()
        sd.stop()
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Receptor continuo de audio LPC1769 con GUI",
    )
    parser.add_argument("port", nargs="?", default=None,
                        help="Puerto serie (ej: COM3 o /dev/ttyUSB0)")
    parser.add_argument("--demo", action="store_true",
                        help="Modo demo sin hardware")
    args = parser.parse_args()

    app = App(port=args.port, demo=args.demo)
    app.mainloop()


if __name__ == "__main__":
    main()