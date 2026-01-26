#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silaba Registrilo — 32 kHz / 32-bit Float
Riparita por Linux (Ubuntu): evitas PortAudio-fadenajn erarojn.
"""
import numpy as np
import sounddevice as sd
import soundfile as sf
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import os
import json
import traceback

from scipy import signal
from time import sleep

# -------------------------------------------------
# KONSTANTOJ
# -------------------------------------------------
samplerate = 32000
DAŬRO_REGISTRO = 3.0
TIPO_DATUMO = 'float32'
DOSIERO_AGORDOJ = "recorder_32bit_settings.json"

# -------------------------------------------------
# HELP-FUNKCIOJ (RIPARITAJ POR LINUX)
# -------------------------------------------------
def ludi_aŭdion(aŭdio, sr):
    """Ludas sonon sen blokado kaj kun antaŭa ĉesigo."""
    try:
        sd.stop()  # Ĉesigu ĉiujn antaŭajn operaciojn
        sd.play(aŭdio, sr, blocking=False)
    except Exception as e:
        print(f"Lud-eraro: {e}")

def konservi_kiel_32bit_wav(dosiernomo, aŭdio, sr):
    if aŭdio.ndim == 2 and aŭdio.shape[1] == 1:
        aŭdio = aŭdio[:, 0]
    sf.write(dosiernomo, aŭdio, sr, subtype='FLOAT')

def sekura_dosiernomo(vorto):
    return "".join(c if c.isalnum() or c in "ĉĝĥĵŝŭĈĜĤĴŜŬ_" else "_" for c in vorto)

def forigi_silenton_ultraprecize(aŭdio, sr, sojlo_db=10.9, aldono_komenca_ms=0, aldono_fina_ms=3):
    if aŭdio.size == 0:
        return aŭdio
    if aŭdio.ndim == 2:
        mono = np.mean(aŭdio, axis=1)
    else:
        mono = aŭdio.copy()
    eps = 1e-9
    bruo_specimenoj = min(int(0.4 * sr), len(mono) // 2)
    if bruo_specimenoj > 100:
        bruo_rms = np.sqrt(np.mean(mono[:bruo_specimenoj] ** 2))
    else:
        bruo_rms = np.sqrt(np.mean(mono ** 2))
    if bruo_rms < eps:
        bruo_rms = eps
    sojlo_rms = bruo_rms * (10 ** (sojlo_db / 20))
    longeco_tramo = max(1, int(sr * 0.002))
    salto_tramo = max(1, int(sr * 0.001))
    if longeco_tramo >= len(mono):
        return aŭdio
    rms = []
    komencoj = []
    for i in range(0, len(mono) - longeco_tramo, salto_tramo):
        tramo_rms = np.sqrt(np.mean(mono[i:i+longeco_tramo] ** 2))
        rms.append(tramo_rms)
        komencoj.append(i)
    rms = np.array(rms)
    komencoj = np.array(komencoj)
    if len(rms) == 0:
        return aŭdio
    aktiva = rms > sojlo_rms
    if not np.any(aktiva):
        return np.array([])
    unua = np.argmax(aktiva)
    lasta = len(aktiva) - np.argmax(aktiva[::-1]) - 1
    komenca_specimeno = komencoj[unua]
    fina_specimeno = komencoj[lasta] + longeco_tramo
    komenca_specimeno = max(0, komenca_specimeno - int(aldono_komenca_ms / 1000 * sr))
    fina_specimeno = min(len(aŭdio), fina_specimeno + int(aldono_fina_ms / 1000 * sr))
    return aŭdio[komenca_specimeno:fina_specimeno]

# -------------------------------------------------
# SIGNAL-PRILABORADO
# -------------------------------------------------
def normalizi_rms(aŭdio, celo_rms=0.25):
    nuna_rms = np.sqrt(np.mean(aŭdio**2))
    if nuna_rms > 1e-20:
        skalo = celo_rms / nuna_rms
    else:
        skalo = 1.0
    return aŭdio * skalo

def normalizi_pintvaloron(aŭdio, celo=0.98):
    maks = np.max(np.abs(aŭdio))
    if maks > 1e-20:
        return aŭdio * (celo / maks)
    return aŭdio

def apliki_kompreson(aŭdio, celo_lufteco=-12, maksimumo_db=-0.5):
    aŭdio_db = 20 * np.log10(np.abs(aŭdio) + 1e-20)
    ne_silentaj = aŭdio_db > -70
    aktuala_lufteco = np.mean(aŭdio_db[ne_silentaj]) if np.any(ne_silentaj) else -40
    gajno_db = celo_lufteco - aktuala_lufteco
    aŭdio_kompresita_db = np.clip(aŭdio_db + gajno_db, -70, maksimumo_db)
    return 10**(aŭdio_kompresita_db / 20) * np.sign(aŭdio)

# -------------------------------------------------
# ĈEFA APLIKAĴO
# -------------------------------------------------
class SilabaRegistriloApliko:
    def __init__(self, radiko):
        self.radiko = radiko
        self.radiko.title("Silaba Registrilo — 32 kHz / 32-bit Float")
        self.radiko.geometry("1050x920")
        self.radiko.minsize(1000, 850)
        self.radiko.grid_columnconfigure(0, weight=1)

        self.agordoj = self.ŝargi_agordojn()
        self.eliga_dosierujo = self.agordoj.get("eliga_dosierujo", "clopeau/lingvaprogramado/fonemoj")
        os.makedirs(self.eliga_dosierujo, exist_ok=True)
        self.vortoj = self.agordoj.get("listo_de_silaboj", ["ĉirkaŭ", "ĝardeno", "ŝuo"])
        #print(self.vortoj)
        self.lasta_indekso=0
        self.nuna_indekso = self.trovi_lastan_ne_registritan_indekson()

        self.start_var = tk.IntVar(value=0)
        self.end_var = tk.IntVar(value=0)
        self.nuna_originala_bazo = None
        self.nuna_bazo = None
        self.nuna_prilaborita = None
        self.elektita_start = None
        self.elektita_end = None
        self.nuna_longeco = 0
        self.prilaboraj_butoj = {}

        self.krei_fenestraĵojn()
        self.ĝisdatigi_montron_de_vorto()
        self.start_var.trace("w", self._ĝisdatigi_start_etikedon)
        self.end_var.trace("w", self._ĝisdatigi_end_etikedon)

    def ŝargi_agordojn(self):
        if os.path.exists(DOSIERO_AGORDOJ):
            try:
                with open(DOSIERO_AGORDOJ, "r", encoding="utf-8") as f:
                    #print(json.load(f))
                    return json.load(f)
            except:
                pass
        return {}

    def konservi_agordojn(self):
        self.agordoj.update({
            "eliga_dosierujo": self.eliga_dosierujo,
            "listo_de_silaboj": self.vortoj
        })
        with open(DOSIERO_AGORDOJ, "w", encoding="utf-8") as f:
            json.dump(self.agordoj, f, ensure_ascii=False, indent=2)

    def trovi_lastan_ne_registritan_indekson(self):
        if not self.vortoj:
            return 0
        eliga_dosierujo_abs = os.path.abspath(self.eliga_dosierujo)
        i=self.lasta_indekso
        print("lasta_indekso",self.lasta_indekso)
        while i<len(self.vortoj)-1:
            vorto=self.vortoj[i]
            dosiernomo = os.path.join(eliga_dosierujo_abs, sekura_dosiernomo(vorto) + ".wav")
            #print(vorto)
            if not os.path.exists(dosiernomo):
                print(vorto)
                self.lasta_indekso=i+1
                return i
            i=i+1
        return 0

    def krei_fenestraĵojn(self):
        r = 0
        eniga_frame = ttk.LabelFrame(self.radiko, text="Silaboj por Registri")
        eniga_frame.grid(row=r, column=0, sticky="ew", padx=8, pady=3)
        r += 1
        btn_frame = ttk.Frame(eniga_frame)
        btn_frame.pack(fill=tk.X, padx=3, pady=3)
        ttk.Button(btn_frame, text="Elŝuti el Dosiero", command=self.ŝargi_vortojn_el_dosiero).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Apliki Tajpadon", command=self.apliki_tajpadon).pack(side=tk.RIGHT)
        self.vorto_teksto = tk.Text(eniga_frame, height=2, width=60)
        self.vorto_teksto.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.vorto_teksto.insert("1.0", "\n".join(self.vortoj))
        dosierujo_frame = ttk.Frame(self.radiko)
        dosierujo_frame.grid(row=r, column=0, sticky="ew", padx=8, pady=3)
        r += 1
        ttk.Button(dosierujo_frame, text="Elekti Sav-Dosierujon", command=self.elekti_eligan_dosierujon).pack(side=tk.LEFT)
        self.dosierujo_etikedo = ttk.Label(dosierujo_frame, text=self.eliga_dosierujo, foreground="gray")
        self.dosierujo_etikedo.pack(side=tk.LEFT, padx=8)
        self.vorto_montro = ttk.Label(self.radiko, text="", font=("Arial", 12, "bold"))
        self.vorto_montro.grid(row=r, column=0, pady=5)
        r += 1
        ctrl_frame = ttk.Frame(self.radiko)
        ctrl_frame.grid(row=r, column=0, pady=5)
        r += 1
        ttk.Button(ctrl_frame, text="⏮️ Reveni", command=self.daŭrigi_de_lasta, width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text="⏭️ Sekva", command=self.iri_al_sekva_silabo, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text="⏺️ Registri & Konservi", command=self.trakti_registro_aŭ_konservo, width=18).pack(side=tk.LEFT, padx=2)
        self.ripeti_btn = ttk.Button(ctrl_frame, text="🔁 Ripeti", state="disabled", command=self.ripeti_nunan, width=10)
        self.ripeti_btn.pack(side=tk.LEFT, padx=2)
        self.ludi_btn = ttk.Button(ctrl_frame, text="▶️ Aŭskulti", state="disabled", command=self.ludi_nunan, width=10)
        self.ludi_btn.pack(side=tk.LEFT, padx=2)
        self.stato_etikedo = ttk.Label(self.radiko, text="", foreground="gray")
        self.stato_etikedo.grid(row=r, column=0, pady=2)
        r += 1
        self.fig, self.ax = plt.subplots(1, 1, figsize=(9, 1.4))
        self.tegmento = FigureCanvasTkAgg(self.fig, master=self.radiko)
        self.tegmento.get_tk_widget().grid(row=r, column=0, sticky="ew", padx=8, pady=5)
        r += 1
        tranĉo_frame = ttk.LabelFrame(self.radiko, text="Elektu regionon por prilabori kaj konservi")
        tranĉo_frame.grid(row=r, column=0, sticky="ew", padx=8, pady=3)
        r += 1
        ttk.Label(tranĉo_frame, text="Komenca:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.start_slider = ttk.Scale(tranĉo_frame, from_=0, to=1, variable=self.start_var, orient=tk.HORIZONTAL)
        self.start_slider.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.start_label = ttk.Label(tranĉo_frame, text="0")
        self.start_label.grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(tranĉo_frame, text="Fina:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.end_slider = ttk.Scale(tranĉo_frame, from_=0, to=1, variable=self.end_var, orient=tk.HORIZONTAL)
        self.end_slider.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.end_label = ttk.Label(tranĉo_frame, text="0")
        self.end_label.grid(row=1, column=2, padx=5, pady=2)
        tranĉo_frame.grid_columnconfigure(1, weight=1)
        prilaboro_frame = ttk.LabelFrame(self.radiko, text="Provu diversajn prilaborojn sur la sama elektitaĵo")
        prilaboro_frame.grid(row=r, column=0, sticky="ew", padx=8, pady=3)
        r += 1
        metodoj = [
            ("Kruda", self.apliki_kruda),
            ("RMS", self.apliki_rms),
            ("Pinta valoro (MEZ)", self.apliki_pintvaloron),
            ("Kompresigo", self.apliki_kompreson),
        ]
        for i, (nomo, funkcio) in enumerate(metodoj):
            btn = ttk.Button(prilaboro_frame, text=nomo, command=funkcio, state="disabled")
            btn.grid(row=i//2, column=i%2, padx=3, pady=2, sticky="ew")
            self.prilaboraj_butoj[nomo] = btn
        prilaboro_frame.grid_columnconfigure(0, weight=1)
        prilaboro_frame.grid_columnconfigure(1, weight=1)

    def elekti_eligan_dosierujon(self):
        dosierujo = filedialog.askdirectory(initialdir=self.eliga_dosierujo)
        if dosierujo:
            self.eliga_dosierujo = dosierujo
            self.dosierujo_etikedo.config(text=self.eliga_dosierujo)

    def ŝargi_vortojn_el_dosiero(self):
        dosiero_pado = filedialog.askopenfilename(filetypes=[("Tekstaj dosieroj", "*.txt")])
        if dosiero_pado:
            try:
                with open(dosiero_pado, "r", encoding="utf-8") as f:
                    vortoj = [line.strip() for line in f if line.strip()]
                self.vortoj = vortoj
                self.vorto_teksto.delete("1.0", tk.END)
                self.vorto_teksto.insert("1.0", "\n".join(vortoj))
                self.nuna_indekso = 0
                self.ĝisdatigi_montron_de_vorto()
            except Exception as e:
                messagebox.showerror("Eraro", f"Ne povis legi la dosieron:\n{str(e)}")

    def apliki_tajpadon(self):
        teksto = self.vorto_teksto.get("1.0", tk.END).strip()
        vortoj = [w.strip() for w in teksto.split("\n") if w.strip()]
        if vortoj:
            self.vortoj = vortoj
            self.nuna_indekso = 0
            self.ĝisdatigi_montron_de_vorto()

    def ĝisdatigi_montron_de_vorto(self):
        if self.vortoj:
            vorto = self.vortoj[self.nuna_indekso]
            print("ĝisdatigo", self.nuna_indekso,vorto)
            totalo = len(self.vortoj)
            self.vorto_montro.config(text=f"Silabo {self.nuna_indekso+1}/{totalo}: {vorto}")
        else:
            self.vorto_montro.config(text="Neniu silabo")

    def vakigi_grafikaĵon(self):
        self.ax.clear()
        self.ax.set_title("Sono")
        self.fig.tight_layout()
        self.tegmento.draw()

    def montri_sono(self):
        if self.nuna_bazo is None:
            self.vakigi_grafikaĵon()
            return
        self.ax.clear()
        p = self.nuna_bazo
        self.ax.plot(p, color='darkgreen')
        self.ax.set_title("Aktuala sono")
        self.fig.tight_layout()
        self.tegmento.draw()

    def trakti_registro_aŭ_konservo(self):
        if self.nuna_bazo is not None:
            self.konservi_kaj_venonta()
        else:
            self.registri_nunan()

    def registri_nunan(self):
        if not self.vortoj:
            messagebox.showwarning("Averto", "Neniu silabo!")
            return
        self.stato_etikedo.config(text="Registrado...")
        self.radiko.update()
        thread = threading.Thread(target=self._fari_registro)
        thread.daemon = True
        thread.start()

    def _fari_registro(self):
        try:
            sd.stop()  # ← ĈI TIU LINIO PREVENTAS LA ERARON
            aŭdio_registro = sd.rec(int(DAŬRO_REGISTRO * samplerate), samplerate=samplerate, channels=1, dtype=TIPO_DATUMO)
            sd.wait()
            aŭdio_trancxita = forigi_silenton_ultraprecize(aŭdio_registro.copy(), samplerate)
            if aŭdio_trancxita.size == 0:
                self.radiko.after(0, lambda: self.stato_etikedo.config(text="⚠️ Neniu sono trovita!"))
                return
            self.nuna_originala_bazo = aŭdio_trancxita.copy().astype(np.float32)
            self.nuna_bazo = self.nuna_originala_bazo.copy()
            self.nuna_prilaborita = self.nuna_bazo.copy()
            self.elektita_start = None
            self.elektita_end = None
            self.radiko.after(0, self._ĝisdatigi_post_registro)
        except Exception as e:
            self.radiko.after(0, lambda: messagebox.showerror("Eraro", str(e)))
            self.radiko.after(0, lambda: self.stato_etikedo.config(text="Eraro"))

    def _ĝisdatigi_post_registro(self):
        self.nuna_longeco = len(self.nuna_bazo)
        self.start_var.set(0)
        self.end_var.set(self.nuna_longeco)
        self.start_slider.config(to=self.nuna_longeco)
        self.end_slider.config(to=self.nuna_longeco)
        self.start_label.config(text="0")
        self.end_label.config(text=str(self.nuna_longeco))
        self.montri_sono()
        self.stato_etikedo.config(text="Registrita. Elektu regionon kaj provu prilaboron.")
        self.ripeti_btn.config(state="normal")
        self.ludi_btn.config(state="normal")
        for btn in self.prilaboraj_butoj.values():
            btn.config(state="normal")

    def _ĝisdatigi_start_etikedon(self, *args):
        self.start_label.config(text=str(self.start_var.get()))

    def _ĝisdatigi_end_etikedon(self, *args):
        self.end_label.config(text=str(self.end_var.get()))

    def ludi_nunan(self):
        if self.nuna_originala_bazo is None:
            return
        if self.elektita_start is not None and self.elektita_end is not None:
            start = self.elektita_start
            end = self.elektita_end
        else:
            start = self.start_var.get()
            end = self.end_var.get()
        if start >= end:
            messagebox.showwarning("Averto", "Elektu validan regionon por aŭskulti.")
            return
        por_ludi = self.nuna_originala_bazo[start:end]
        self.nuna_bazo=self.nuna_originala_bazo[start:end]
        print("por ludi,",start, end )
        threading.Thread(target=ludi_aŭdion, args=(por_ludi, samplerate), daemon=True).start()

    def ripeti_nunan(self):
        # Sekurige rekomenci per 'after'
        self.nuna_originala_bazo = None
        self.nuna_bazo = None
        self.nuna_prilaborita = None
        self.elektita_start = None
        self.elektita_end = None
        self.vakigi_grafikaĵon()
        self.ripeti_btn.config(state="disabled")
        self.ludi_btn.config(state="disabled")
        for btn in self.prilaboraj_butoj.values():
            btn.config(state="disabled")
        self.stato_etikedo.config(text="Rekomencanta registradon...")
        self.nuna_indekson=self.trovi_lastan_ne_registritan_indekson()
        #self.radiko.after(100, self.registri_nunan)  # ← sekura transiro

    def apliki_kruda(self):
        if self.nuna_originala_bazo is not None:
            start = self.start_var.get()
            end = self.end_var.get()
            if start >= end:
                messagebox.showwarning("Averto", "Elektu validan regionon por prilabori.")
                return
            self.elektita_start = start
            self.elektita_end = end
            elektita = self.nuna_originala_bazo[start:end]
            self.nuna_bazo = elektita.copy()
            self.nuna_prilaborita = self.nuna_bazo.copy()
            self._ĝisdatigi_post_prilaboro()

    def apliki_rms(self):
        if self.nuna_originala_bazo is not None:
            start = self.start_var.get()
            end = self.end_var.get()
            if start >= end:
                messagebox.showwarning("Averto", "Elektu validan regionon por prilabori.")
                return
            self.elektita_start = start
            self.elektita_end = end
            elektita = self.nuna_originala_bazo[start:end]
            prilaborita = normalizi_rms(elektita, celo_rms=0.25)
            self.nuna_bazo = prilaborita
            self.nuna_prilaborita = prilaborita
            self._ĝisdatigi_post_prilaboro()

    def apliki_pintvaloron(self):
        if self.nuna_originala_bazo is not None:
            start = self.start_var.get()
            end = self.end_var.get()
            if start >= end:
                messagebox.showwarning("Averto", "Elektu validan regionon por prilabori.")
                return
            self.elektita_start = start
            self.elektita_end = end
            elektita = self.nuna_originala_bazo[start:end]
            prilaborita = normalizi_pintvaloron(elektita, celo=0.98)
            self.nuna_bazo = prilaborita
            self.nuna_prilaborita = prilaborita
            self._ĝisdatigi_post_prilaboro()

    def apliki_kompreson(self):
        if self.nuna_originala_bazo is not None:
            start = self.start_var.get()
            end = self.end_var.get()
            if start >= end:
                messagebox.showwarning("Averto", "Elektu validan regionon por prilabori.")
                return
            self.elektita_start = start
            self.elektita_end = end
            elektita = self.nuna_originala_bazo[start:end]
            prilaborita = apliki_kompreson(elektita, celo_lufteco=-12)
            self.nuna_bazo = prilaborita
            self.nuna_prilaborita = prilaborita
            self._ĝisdatigi_post_prilaboro()

    def _ĝisdatigi_post_prilaboro(self):
        self.nuna_longeco = len(self.nuna_bazo)
        self.start_var.set(0)
        self.end_var.set(self.nuna_longeco)
        self.start_slider.config(to=self.nuna_longeco)
        self.end_slider.config(to=self.nuna_longeco)
        self.start_label.config(text="0")
        self.end_label.config(text=str(self.nuna_longeco))
        self.montri_sono()
        self.stato_etikedo.config(text="Prilaboro aplikiĝis. Vi povas provi alian sur la sama elektitaĵo.")
        self.ripeti_btn.config(state="normal")
        self.ludi_btn.config(state="normal")

    def konservi_kaj_venonta(self):
        if self.nuna_bazo is None:
            messagebox.showwarning("Averto", "Neniu sono por konservi!")
            return
        konservota = self.nuna_bazo
        vorto = self.vortoj[self.nuna_indekso]
        eliga_dosierujo_abs = os.path.abspath(self.eliga_dosierujo)
        os.makedirs(eliga_dosierujo_abs, exist_ok=True)
        dosiernomo = os.path.join(eliga_dosierujo_abs, sekura_dosiernomo(vorto) + ".wav")
        print(f"Konservante: {dosiernomo}")
        konservi_kiel_32bit_wav(dosiernomo, konservota, samplerate)
        self.stato_etikedo.config(text=f"✅ Konservita: {os.path.basename(dosiernomo)}")
        self.nuna_indekso += 1
        if self.nuna_indekso >= len(self.vortoj):
            messagebox.showinfo("Finita!", "Ĉiuj silaboj estas registritaj!")
            self.lasta_indekso = 0
        else:
            self.nuna_indekso = self.trovi_lastan_ne_registritan_indekson()
            
        self.ĝisdatigi_montron_de_vorto()
        self.vakigi_grafikaĵon()
        self.nuna_originala_bazo = None
        self.nuna_bazo = None
        self.nuna_prilaborita = None
        self.elektita_start = None
        self.elektita_end = None
        self.ripeti_btn.config(state="disabled")
        self.ludi_btn.config(state="disabled")
        for btn in self.prilaboraj_butoj.values():
            btn.config(state="disabled")

    def iri_al_sekva_silabo(self):
        if not self.vortoj:
            return
        if self.nuna_bazo is not None:
            self.konservi_kaj_venonta()
        else:
            #self.nuna_indekso += 1
            if self.lasta_indekso >= len(self.vortoj):
                messagebox.showinfo("Finita!", "Ĉiuj silaboj estas traktitaj!")
                self.nuna_indekso = 0
            self.nuna_indekso = self.trovi_lastan_ne_registritan_indekson()
            self.ĝisdatigi_montron_de_vorto()
            self.vakigi_grafikaĵon()
            self.nuna_originala_bazo = None
            self.nuna_bazo = None
            self.nuna_prilaborita = None
            self.elektita_start = None
            self.elektita_end = None
            self.ripeti_btn.config(state="disabled")
            self.ludi_btn.config(state="disabled")
            for btn in self.prilaboraj_butoj.values():
                btn.config(state="disabled")
            self.stato_etikedo.config(text="Saltis al sekva silabo.")

    def daŭrigi_de_lasta(self):
        if self.nuna_indekso < len(self.vortoj):
            
            self.ĝisdatigi_montron_de_vorto()
            self.vakigi_grafikaĵon()
            self.nuna_originala_bazo = None
            self.nuna_bazo = None
            self.nuna_prilaborita = None
            self.elektita_start = None
            self.elektita_end = None
            self.ripeti_btn.config(state="disabled")
            self.ludi_btn.config(state="disabled")
            for btn in self.prilaboraj_butoj.values():
                btn.config(state="disabled")
            self.stato_etikedo.config(text=f"Rekomencanta ĉe silabo {self.nova_indekso + 1}")
        else:
            messagebox.showinfo("Informo", "Ĉiuj silaboj jam estas registritaj!")
            self.nuna_indekso = 0
            self.ĝisdatigi_montron_de_vorto()

# -------------------------------------------------
# RULIGO
# -------------------------------------------------
if __name__ == "__main__":
    try:
        # Opcie: elekti PulseAudio por eviti ALSA-problemojn
        # sd.default.device = 'pulse'
        radiko = tk.Tk()
        apliko = SilabaRegistriloApliko(radiko)
        radiko.mainloop()
    except Exception as e:
        print("\n" + "="*60)
        print("KRITIKA ERARO:")
        traceback.print_exc()
        print("="*60)
        input("\nPremu Enigon por eliri...")