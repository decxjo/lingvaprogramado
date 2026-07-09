#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ring-Buffer TTS kun Semaforo-Sinkronigo + Sku-Detekto + Lernanta reĝimo + Paŭzo
"""
disvolvo=False


import logging
logging.getLogger('numba').setLevel(logging.WARNING)
import librosa
import numpy as np
import os
import glob
import unicodedata
import tempfile
import shutil
import requests
import importlib
from kivy.uix.filechooser import FileChooserListView as Dosier_Elektejo
from kivy.uix.popup import Popup as Krom_Kadro
from kivy.uix.scrollview import ScrollView as VidRulejo
from kivy.utils import platform as platformo
from kivy.core.audio import SoundLoader as SonTraktilo
from kivy.clock import Clock as Kronometro
from kivy.uix.textinput import TextInput as Tekstejo
from kivy.uix.label import Label as Etikedo
from kivy.uix.button import Button as Butono
from kivy.uix.boxlayout import BoxLayout as KadroAranĝo
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
import threading
import time
import numpy as np
import wave
import librosa
from queue import Queue, Empty
from pathlib import Path as vojo
import pickle
import re
import json
#from readability import Document as mal_htmlo
import trafilatura

os.environ["KIVY_AUDIO"] = "sdl2"
if platformo != "android":
    os.environ["SDL_AUDIODRIVER"] = "alsa"

#*********************** ĝisdatigo **********

import zipfile
import os
import gdown
import shutil

# ------------------------------------------------------------
# KONSTANTOJ
# ------------------------------------------------------------
ZIP_ID = "1e_a0QJNAJ32VMYMmGYvY4zfqt7-F_q9O"      # ID de voĉigilo.zip
VERSIO_ID = "1npFl5hP2pwOXyWb_0iKJMJDd0iJBJX4y"                 # <--- Anstataŭigu per la ID de via versio.txt
ZIP_NOMO = "voĉigilo.zip"
VERSIO_DOSIERO = "versio.txt"
VERSIO_TEMP = "versio_temp.txt"
CEL_DOSIERUJO = "fonemojx"                         # La dosierujo, kiun ni atendas post malpakigo

# ------------------------------------------------------------
# HELPA FUNKCIO: elŝuti version
# ------------------------------------------------------------
def elŝuti_version():
    """
    Provoj elŝuti la version-dosieron el Google Drive.
    Revenas (sukceso, numero) aŭ (False, None) se malsukcesas.
    """
    try:
        gdown.download(
            id=VERSIO_ID,
            output=VERSIO_TEMP,
            quiet=True,          # malpli da bruo
            use_cookies=False,
            fuzzy=True
        )
    except Exception:
        # Se io misfunkcias, ni simple ignoras
        return False, None

    if not os.path.exists(VERSIO_TEMP):
        return False, None

    # Legu la numeron el la dosiero
    try:
        with open(VERSIO_TEMP, 'r') as f:
            enhavo = f.read().strip()
        numero = int(enhavo)
        os.remove(VERSIO_TEMP)   # forigu provizoran dosieron
        return True, numero
    except (ValueError, IOError):
        # Se la enhavo ne estas valida entjero
        if os.path.exists(VERSIO_TEMP):
            os.remove(VERSIO_TEMP)
        return False, None

# ------------------------------------------------------------
# ĈEFA FUNKCIO: prepari datumojn
# ------------------------------------------------------------
def prepari_datumojn():
    """
    Kontrolas la version kaj, se necese, elŝutas kaj malpakas la zip-on.
    """
    # 1) Kontrolu ĉu la celita dosierujo jam ekzistas
    if os.path.exists(CEL_DOSIERUJO) and os.path.isdir(CEL_DOSIERUJO):
        # Se ĝi ekzistas, ni kontrolu version (por eventuala ĝisdatigo)
        print("📁 Dosierujo jam ekzistas. Kontrolas version...")
    else:
        print("⏳ Dosierujo ne ekzistas. Ĝisdatigo nepra.")

    # 2) Elŝutu la foran version (se eble)
    sukceso, fora_numero = elŝuti_version()

    # 3) Legu lokan version (se ekzistas)
    loka_numero = 0
    if os.path.exists(VERSIO_DOSIERO):
        try:
            with open(VERSIO_DOSIERO, 'r') as f:
                loka_numero = int(f.read().strip())
        except (ValueError, IOError):
            loka_numero = 0   # se la dosiero estas difektita, traktu kiel 0

    # 4) Decido pri ĝisdatigo
    devas_ĝisdatigi = False

    if sukceso and fora_numero is not None:
        print(f"🔢 Fora versio: {fora_numero}, Loka versio: {loka_numero}")
        if fora_numero > loka_numero:
            devas_ĝisdatigi = True
            print("🔄 Nova versio havebla! Ĝisdatiganta...")
        else:
            print("✅ Jam havas la lastan version.")
            # Se la dosierujo mankas, tamen ni devas elŝuti (sed tiam loka_numero verŝajne estus 0)
            if not os.path.exists(CEL_DOSIERUJO):
                devas_ĝisdatigi = True
                print("⚠️ Dosierujo mankas, do ni elŝutos.")
    else:
        # Se la fora versio ne estas alirebla, ni ignoras kaj uzas la ekzistantan
        if os.path.exists(CEL_DOSIERUJO):
            print("⚠️ Ne povis kontakti Google Drive. Uzas ekzistantajn datumojn.")
            return True
        else:
            # Se la dosierujo mankas kaj ni ne povas kontroli, ni devas provi elŝuti
            print("⚠️ Ne povis kontakti Google Drive kaj dosierujo mankas. Provos elŝuti...")
            devas_ĝisdatigi = True

    # 5) Se necesas ĝisdatigi, elŝutu zip-on kaj malpaku
    if devas_ĝisdatigi:
        # Forigu la malnovan dosierujon se ĝi ekzistas
        if os.path.exists(CEL_DOSIERUJO):
            print(f"🗑️  Forigas malnovan dosierujon '{CEL_DOSIERUJO}'...")
            shutil.rmtree(CEL_DOSIERUJO)

        print(f"⏳ Elŝutas la zip-dosieron el Google Drive...")
        try:
            gdown.download(
                id=ZIP_ID,
                output=ZIP_NOMO,
                quiet=False,
                use_cookies=False,
                fuzzy=True
            )
        except Exception as e:
            print(f"❌ Malsukcesis elŝuti zip-on: {e}")
            return False

        if not os.path.exists(ZIP_NOMO):
            print("❌ Zip-dosiero ne troviĝas post elŝuto.")
            return False

        # Malpaku la zip-on (ĉiuj dosieroj)
        print(f"⏳ Malpakiganta '{ZIP_NOMO}'...")
        try:
            with zipfile.ZipFile(ZIP_NOMO, 'r') as zip_ref:
                zip_ref.extractall(".")
        except Exception as e:
            print(f"❌ Malsukcesis malpakigi: {e}")
            os.remove(ZIP_NOMO)
            return False

        os.remove(ZIP_NOMO)
        print("✅ Zip-forigita.")

        # Konservu la novan version numeron loke
        if sukceso and fora_numero is not None:
            with open(VERSIO_DOSIERO, 'w') as f:
                f.write(str(fora_numero))
            print(f"💾 Loka versio ĝisdatigita al {fora_numero}")

        # Kontrolu, ke la dosierujo nun ekzistas
        if os.path.exists(CEL_DOSIERUJO) and os.path.isdir(CEL_DOSIERUJO):
            print(f"✅ Dosierujo '{CEL_DOSIERUJO}' preta.")
            return True
        else:
            print("⚠️ Post malpakigo, la dosierujo ne troviĝas. Kontrolu la zip-enhavon.")
            return False

    # Se ne necesis ĝisdatigi, ni jam havas la dosierujon (aŭ ni ignoris)
    return True

# ------------------------------------------------------------
# ĈEFA PROGRAMO
# ------------------------------------------------------------
if __name__ == "__main__":
    sukceso = prepari_datumojn()
    if sukceso:
        print("🚀 Ĉio preta! Vi povas uzi la dosierojn.")
    else:
        print("🛑 Programo haltas pro manko de datumoj.")
#*******************************************

import sys
import os

def resource_path(relativa_vojo):
    try:
        bazvojo = sys._MEIPASS
        bazvojo = os.path.dirname(os.path.abspath(sys.executable))
    except AttributeError:
        bazvojo = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(bazvojo, relativa_vojo)

# def resource_path(relativa_vojo):
#     bazvojo = os.path.dirname(os.path.abspath(sys.executable))
#     #os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(bazvojo, relativa_vojo)

# Krei skribeblajn dosierujojn en la nuna labordosierujo
# os.makedirs(resource_path("legaĵo"), exist_ok=True)
# os.makedirs("legendaĵo", exist_ok=True)
# frazoj_bufro = resource_path("legaĵo")
# print("frazoj_bufro",frazoj_bufro)
# legendaĵoj = "legendaĵoj"

os.makedirs(resource_path("legaĵo"), exist_ok=True)
os.makedirs("legendaĵo", exist_ok=True)
frazoj_bufro = resource_path("legaĵo")
print("frazoj_bufro",frazoj_bufro)
legendaĵoj = "legendaĵoj"

# ========================
# KONSTANTOJ (elŝutado ktp.)
# ========================
def elŝuti_google_drive(dosiernomo, dosiera_id):
    url = f"https://drive.google.com/uc?export=download&id={dosiera_id}"
    session = requests.Session()
    response = session.get(url, stream=True)
    confirm_token = None
    match = re.search(r'confirm=([0-9A-Za-z_-]+)', response.text)
    if match:
        confirm_token = match.group(1)
    else:
        match = re.search(r'name="confirm" value="([0-9A-Za-z_-]+)"', response.text)
        if match:
            confirm_token = match.group(1)
    if confirm_token:
        download_url = f"https://drive.usercontent.google.com/download?export=download&confirm={confirm_token}&id={dosiera_id}"
    else:
        download_url = response.url
    response = session.get(download_url, stream=True)
    total_downloaded = 0
    with open(dosiernomo, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                total_downloaded += len(chunk)
                print(f"Elŝutita: {total_downloaded/(1024*1024):.2f} MB", end='\r')
    print(f"\nElŝuto finita: {dosiernomo}")

def malzipi_kaj_rearanĝi(zip_dosiero):
    print(f"Malzipas {zip_dosiero}...")
    with tempfile.TemporaryDirectory() as tempdir:
        with zipfile.ZipFile(zip_dosiero, 'r') as zip_ref:
            zip_ref.extractall(tempdir)
        src_dir = os.path.join(tempdir, 'parametroj')
        if not os.path.isdir(src_dir):
            src_dir = tempdir
        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(os.getcwd(), item)
            if os.path.exists(d):
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.remove(d)
            shutil.move(s, d)
            print(f"Movita: {item}")
        print("Malzipado kaj rearanĝo finita.")
    os.remove(zip_dosiero)
    print(f"Forigita {zip_dosiero}")

if not os.path.isdir(resource_path("fonemojx")):
    dosiera_id = '1fs50G_-fjZyYdKwpzwaUlOvbXFy5d5Vi'
    zip_nomo = 'parametroj.zip'
    elŝuti_google_drive(zip_nomo, dosiera_id)
    malzipi_kaj_rearanĝi(zip_nomo)

SAMPLE_RATE = 44100
MAX_FILES = 4           #nombro de eroj en son-bufro


try:
    import konfiguro
    KONFIGURO = konfiguro.KONFIGURO
    cifero = KONFIGURO.get("cifera_mapo", {})
except:
    cifero = {}
    KONFIGURO = {}

global PLYER_DISPONEBLA, ACCEL_DISPONEBLA
PLYER_DISPONEBLA = False
ACCEL_DISPONEBLA = False
if platformo == 'android':
    try:
        from plyer import filechooser, accelerometer, vibrator
        PLYER_DISPONEBLA = True
        ACCEL_DISPONEBLA = True
    except ImportError:
        PLYER_DISPONEBLA = False

def estas_pydroid3():
    try:
        import sys
        if 'pydroid' in sys.version.lower() or 'pydroid' in sys.executable.lower():
            return True
        if os.path.exists('/sdcard/Android/data/ru.iiec.pydroid3/'):
            return True
        return False
    except:
        return False

PYDROID3 = estas_pydroid3()

class AccelMezurilo:
    def __init__(self, sojlo=0.3, callback=None):
        self.soĵlo = sojlo
        self.callback = callback
        self._aktiva = False
        self._start_tempo = 0
        self._min = [None, None, None]
        self._max = [None, None, None]
        self._Kronometro_event = None
        self._validaj_valoroj = False
        self._provoj = 0

    def start_mezuro(self):
        print(f"🔍 start_mezuro: ACCEL={ACCEL_DISPONEBLA}, aktiva={self._aktiva}")
        if not ACCEL_DISPONEBLA or self._aktiva:
            return False
        try:
            if platformo == 'android' and hasattr(accelerometer, 'enable'):
                accelerometer.enable()
        except Exception as e:
            print(f"⚠ Eraro ebligante akcelometron: {e}")
        self._reset_minmax()
        self._start_tempo = Kronometro.get_time()
        self._aktiva = True
        self._validaj_valoroj = False
        self._provoj = 0
        self._Kronometro_event = Kronometro.schedule_interval(self._mezuri_pasxe, 0.05)
        return True

    def _reset_minmax(self):
        self._min = [None, None, None]
        self._max = [None, None, None]
        self._validaj_valoroj = False

    def _mezuri_pasxe(self, dt):
        try:
            val = accelerometer.acceleration
            if val is None or val == (None, None, None):
                self._provoj += 1
                if Kronometro.get_time() - self._start_tempo > 0.8:
                    print(f"⚠ Akcelometro ne respondas post {self._provoj} provoj")
                    self._fini_mezuron()
                return
            if isinstance(val, (tuple, list)) and len(val) >= 3:
                x, y, z = val[0], val[1], val[2]
            else:
                return
            if not self._validaj_valoroj:
                self._min = [x, y, z]
                self._max = [x, y, z]
                self._validaj_valoroj = True
                print(f"📊 Unuaj validaj valoroj: X={x:.2f}, Y={y:.2f}, Z={z:.2f}")
                return
            for i, valuo in enumerate([x, y, z]):
                if valuo < self._min[i]:
                    self._min[i] = valuo
                if valuo > self._max[i]:
                    self._max[i] = valuo
            if Kronometro.get_time() - self._start_tempo >= 1.0:
                self._fini_mezuron()
        except Exception as e:
            print(f"❌ Eraro en mezuro: {e}")
            self._fini_mezuron()

    def _fini_mezuron(self):
        if self._Kronometro_event:
            self._Kronometro_event.cancel()
            self._Kronometro_event = None
        try:
            if platformo == 'android' and hasattr(accelerometer, 'disable'):
                accelerometer.disable()
        except:
            pass
        if not self._aktiva:
            return
        self._aktiva = False
        if not self._validaj_valoroj:
            if self.callback:
                Kronometro.schedule_once(lambda dt: self.callback(False))
            return
        diff_x = abs(self._max[0] - self._min[0])
        diff_y = abs(self._max[1] - self._min[1])
        diff_z = abs(self._max[2] - self._min[2])
        max_diff = max(diff_x, diff_y, diff_z)
        detektita = max_diff > self.soĵlo
        if self.callback:
            Kronometro.schedule_once(lambda dt: self.callback(detektita))

    def haltigi(self):
        if self._Kronometro_event:
            self._Kronometro_event.cancel()
            self._Kronometro_event = None
        self._aktiva = False
        try:
            if platformo == 'android' and hasattr(accelerometer, 'disable'):
                accelerometer.disable()
        except:
            pass

class SonaPeto:
    def __init__(self, data, is_parolado):
        self.data = data
        self.is_parolado = is_parolado

class Esperanto_voĉigiloAudio:
    def __init__(self):
        self.files = [None] * MAX_FILES
        self.play_index = 0
        self.write_index = 0
        self.lock = threading.Lock()
        self.running = True
        self.current_sound = None
        self.request_queue = Queue()
        self.generita_count = 0
        self.ludita_count = 0
        self.semaphore = threading.Semaphore(MAX_FILES)
        self.buffer_Etikedo = None
        self.stats_Etikedo = None
        threading.Thread(target=self._produktanto, daemon=True).start()

    def reset(self):
        print("🔄 Resetado de Ringo-Buffer...")
        with self.lock:
            for i in range(MAX_FILES):
                if self.files[i] is not None:
                    try:
                        if os.path.exists(self.files[i]):
                            os.remove(self.files[i])
                    except: pass
                    self.files[i] = None
            self.play_index = 0
            self.write_index = 0
            self.request_queue = Queue()
            self.generita_count = 0
            self.ludita_count = 0
            self.semaphore = threading.Semaphore(MAX_FILES)
            self._montri_staton()

    def _produktanto(self):
        while self.running:
            try:
                peto = self.request_queue.get(timeout=0.5)
                with self.lock:
                    idx = self.write_index
                    start_time = time.time()
                    while self.files[idx] is not None:
                        if time.time() - start_time > 3.0:
                            idx = (idx + 1) % MAX_FILES
                            start_time = time.time()
                            if idx == self.write_index:
                                time.sleep(0.2)
                        time.sleep(0.05)
                    if self.files[idx] is not None:
                        try:
                            if os.path.exists(self.files[idx]):
                                os.remove(self.files[idx])
                        except: pass
                    self.generita_count += 1
                    if peto.is_parolado:
                        filename = f"{frazoj_bufro}/parolado_{idx+1:01d}.wav"
                    else:
                        filename = f"{frazoj_bufro}/testo_{idx+1:01d}.wav"
                    print("filename",filename)
                    with wave.open(filename, 'w') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(SAMPLE_RATE)
                        wf.writeframes(peto.data.tobytes())
                    self.files[idx] = filename
                    self.write_index = (idx + 1) % MAX_FILES
                    self._montri_staton()
            except Empty:
                pass
            time.sleep(0.05)

    def _montri_staton(self):
        if not self.buffer_Etikedo:
            return
        stato = []
        for i in range(MAX_FILES):
            if self.files[i] is not None:
                if i == self.play_index:
                    if "parolado" in self.files[i]:
                        stato.append("▶️🔵")
                    else:
                        stato.append("▶️🟢")
                else:
                    if "parolado" in self.files[i]:
                        stato.append("🔵")
                    else:
                        stato.append("🟢")
            else:
                stato.append("⬜")
        self.buffer_Etikedo.text = "[" + " ".join(stato) + "]"
        if self.stats_Etikedo:
            self.stats_Etikedo.text = f"Generitaj: {self.generita_count} | Luditaj: {self.ludita_count}"

    def peti_ludon(self, sono_array, is_parolado=True):
        if sono_array is not None and len(sono_array) > 0:
            self.request_queue.put(SonaPeto(sono_array, is_parolado))
            return True
        return False

    def sekva_por_ludi(self):
        with self.lock:
            if self.files[self.play_index] is not None:
                return self.files[self.play_index]
            return None

    def marki_kiel_ludita(self):
        with self.lock:
            if self.files[self.play_index] is not None:
                self.ludita_count += 1
                try:
                    if os.path.exists(self.files[self.play_index]):
                        os.remove(self.files[self.play_index])
                except: pass
                self.files[self.play_index] = None
                self._montri_staton()
                self.play_index = (self.play_index + 1) % MAX_FILES
                self.semaphore.release()

class ViaKompleksaParolilo:
    def __init__(self, ringo):
        self.ringo = ringo
        self.sample_rate = SAMPLE_RATE
        self.salti_intervalon = False
        self.jamcitilo = False
        self.finpunkto = False
        self.last_nombroflago = True
        self.neciferaj = 0
        self.nombroflago = False
        self.mankantaj = ""
        self.silab_memoro = {}
        self.vortaro = {}
        self.silaba_vortaro = {}
        self.silabaro = []
        self.senfinaĵaj = []
        self.finaĵoj = []
        self.prefiksoj = []
        self.sufiksoj =[]
        self.silento_komo = 0
        self.silento_punkto = 0
        self.silento_cifero = 0
        self.silento_akronimo = 0
        self.laŭteco_faktoro = 0
        self.pika_maks = 0
        self.lasta_malplifortigo = 0
        self.radikoj = []
        self.cifero = KONFIGURO.get("cifera_mapo", {})
        self.konsonantoj = KONFIGURO.get("konsonantoj", {})
        self.grekaj_literoj = KONFIGURO.get("grekaj_literoj", {})
        self.uz_maniero = "uzanto"
        self.silento_elemento = KONFIGURO.get("silento_elemento", 0.05)
        self._ŝargi_datumojn()

    def _legu_dosieron(self, dosiernomo):
        with open(dosiernomo, 'r', encoding='utf-8') as enigo:
            return enigo.read()

    def _ŝargi_vortaron(self, dosieronomo, formato='pickle'):
        try:
            if formato == 'json':
                with open(dosieronomo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif formato == 'pickle':
                with open(dosieronomo, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"Eraro dum ŝargado: {e}")
            return {}

    def _kalkuli_rms(self, data):
        return np.sqrt(np.mean(data**2))

    def _kombinu(self, x, y):
        return [v + w for v in x for w in y]

    def _nombru_silabojn(self, vorto):
        return sum([v in "aeiou" for v in vorto])



    def _silaboj(self, n):
        return [v for v in self.vortaro.keys() if self._nombru_silabojn(v) == n]

    def _akiru_kategoriojn(self, vorto):
        return [v for v in self.vortaro.keys() if self.vortaro[v][0] in vorto]



    def _ŝargi_datumojn(self):
        importlib.reload(konfiguro)
        KONFIGURO = konfiguro.KONFIGURO
        print (KONFIGURO)
        self.silento_komo = KONFIGURO.get("silento_komo")
        self.silento_punkto = KONFIGURO.get("silento_punkto")
        self.silento_cifero = KONFIGURO.get("silento_cifero")
        self.silento_akronimo = KONFIGURO.get("silento_akronimo")
        self.silento_intervalo = KONFIGURO.get("silento_intervalo")
        print("silento_intervalo",self.silento_intervalo)
        self.laŭteco_faktoro = KONFIGURO.get("laŭteco_faktoro")
        self.pika_maks = KONFIGURO.get("pika_maks")
        self.lasta_malplifortigo = KONFIGURO.get('lasta_malplifortigo')
        self.fade_proporcio = KONFIGURO.get("fade_proporcio")
        self.fade_fino = KONFIGURO.get("fade_fino")
        self.silento_sojlo = KONFIGURO.get("silento_sojlo")
        self.celo_rms = KONFIGURO.get("celo_rms")
        elekto = {1:0, 2:0.7, 5:1, 8:2, 12:2.5, 16:3, 22:3.5, 30:4}
        b = 1
        self.silento_progreso = []
        for i in range(30):
            a = elekto.get(i)
            if a is not None:
                b = a
            self.silento_progreso.append(b)
        print(self.silento_progreso)
        self.testo_po_litera = KONFIGURO.get('testo_po_litera')
        self.uzi_fontajn = KONFIGURO.get('uzi_fontajn')
        self.registri_finan_rezulton = KONFIGURO.get('registri_finan_rezulton')
        self.normaligisilaboj = KONFIGURO.get('normaligisilaboj')
        dosierujo = vojo(__file__).parent.absolute()
        os.chdir(dosierujo)
        self.dosierujo = str(dosierujo) + "/"
        vortarodosiero = KONFIGURO.get("vortarodosiero")
        vortarodosiero=resource_path(vortarodosiero)
        if os.path.exists(vortarodosiero):
            vortarolinioj = self._legu_dosieron(vortarodosiero).lower().split("\n")
            for linio in vortarolinioj:
                if len(linio) > 0 and "," in linio:
                    vorto, kategorio = linio.split(",")
                    self.vortaro[vorto] = kategorio
        self.senfinaĵaj = self._akiru_kategoriojn("znx")
        self.senfinaĵaj += self._kombinu(self._akiru_kategoriojn("qu"), ["", "n"])
        self.senfinaĵaj += self._kombinu(self._akiru_kategoriojn("v"), ["", "n", "j", "jn"])
        self.finaĵoj = self._akiru_kategoriojn("t")
        self.finaĵoj = [f for f in self.finaĵoj if f not in ['j', 'n']]
        self.finaĵoj += self._kombinu(["o", "a"], ["n", "j", "jn"])
        self.finaĵoj.append("en")
        self.prefiksoj = self._akiru_kategoriojn("pz")
        self.prefiksoj.append("ne")
        # Aldonu post kiam finaĵoj kaj sufiksoj estas difinitaj
        self.sufiksoj = self._akiru_kategoriojn("s")
        self.sufiksoj = sorted(self.sufiksoj, key=len, reverse=True)
        if KONFIGURO.get('uzi_fontajn', True):
            fonemujo = self.dosierujo + "fonemoj"
        else:
            fonemujo =resource_path("fonemojx")
            print(fonemujo)
            #fonemujo = self.dosierujo + "fonemojx"
        self._ŝargi_kaj_normaligi_silabojn(fonemujo, self.celo_rms)
        silaba_vortaro_dosiero = KONFIGURO.get("silaba_vortaro_dosiero", "")
        silaba_vortaro_dosiero=resource_path(silaba_vortaro_dosiero)
        self.silaba_vortaro = self._ŝargi_vortaron(silaba_vortaro_dosiero, formato="pickle")
        silabaro_dosiero = KONFIGURO.get("silabaro_dosiero", "")
        silabaro_dosiero = resource_path(silabaro_dosiero)
        self.silabaro = self._ŝargi_vortaron(silabaro_dosiero, formato="pickle")
        radikodosiero = KONFIGURO.get("radikodosiero", "")
        radikodosiero = resource_path(radikodosiero)
        if os.path.exists(radikodosiero):
            with open(radikodosiero, "r") as enigo:
                radikoj = enigo.read()
            radikoj = radikoj.split()
            radikoj = self._flatigi_liston(radikoj)
            self.radikoj = []
            for radiko in radikoj:
                radiko = radiko.strip("[]").strip(",").strip("'").strip("'")
                self.radikoj.append(radiko)



    def normalizi_32bit(self, aŭdio, celo_rms, eviti_kliradon=True):
        nuna_rms = np.sqrt(np.mean(aŭdio**2))
        skalo_rms = celo_rms / nuna_rms if nuna_rms > 1e-20 else 1.0

        if eviti_kliradon:
            maks_abs = np.max(np.abs(aŭdio))
            skalo_peka = 1.0 / maks_abs if maks_abs > 1e-20 else 1.0
            skalo = min(skalo_rms, skalo_peka)
        else:
            skalo = skalo_rms

        return aŭdio * skalo

    def _ŝargi_kaj_normaligi_silabojn(self, dosierujo, celo_rms):
        print( "doierujo de silaboj", dosierujo)
        if not os.path.isdir(dosierujo):
            raise FileNotFoundError(f"Dosierujo ne ekzistas: {dosierujo}")

        for dosiero in sorted(os.listdir(dosierujo)):
            # wave-modulo nur subtenas WAV. OGG postulas eksteran bibliotekon.
            if not dosiero.lower().endswith(".wav"):
                continue

            vojo = os.path.join(dosierujo, dosiero)
            silabo = os.path.splitext(dosiero)[0]
            #print("vojo,  silabo", vojo,silabo)

            try:
                with wave.open(vojo, 'rb') as wf:
                    sr_orig = wf.getframerate()
                    n_kanaloj = wf.getnchannels()
                    samplo_profundeco = wf.getsampwidth()  # bajtoj per specimeno
                    n_framoj = wf.getnframes()

                    if n_framoj == 0:
                        print(f"⚠️ {dosiero}: malplena dosiero, preterpasita.")
                        continue

                    if samplo_profundeco != 2:
                        print(f"⚠️ {dosiero}: Atendita 16-bit (2 bajtoj), sed trovis {samplo_profundeco*8}-bit.")

                    raw_data = wf.readframes(n_framoj)

                data = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0


                # Se plurkanala, rearanĝi kaj konverti al mono


                # Normaligi al float32 en [-1.0, 1.0]
                # 32768.0 estas norma divisoro por signed 16-bit PCM
                data = data.astype(np.float32) / 32768.0

            except Exception as e:
                print(f"⚠️ Ne eblas legi {dosiero}: {e}")
                continue



            # ⚠️ GRAVA: Asignu la rezulton al `data`! (via originala kodo ne faris ĉi tion)
            data = self.normalizi_32bit(data, celo_rms, eviti_kliradon=True)

            self.silab_memoro[silabo] = (sr_orig, data)




    def akcepti_vorton(self, vorto):
        apartigiloj = ".,-/*\" "
        majuskloj = "ABCDEFGHIJKLMNOPQRSTUVWXYZĈĜĤĴŜŬ"
        minuskloj = "abcdefghijklmnopqrstuvwxyzĉĝĥĵŝŭ"
        ciferoj = "0123456789"
        permesataj = majuskloj + minuskloj + ciferoj + apartigiloj
        for ch in vorto:
            if ch not in permesataj:
                return False
        restanta = ''.join(ch for ch in vorto if ch not in apartigiloj)
        if len(restanta) == len(vorto):
            if len(vorto) > 3:
                return False
            if len(vorto) < 3:
                return False
        if not restanta:
            return False
        if restanta[0] not in majuskloj:
            return False
        for ch in restanta:
            if not (ch in majuskloj or ch in ciferoj):
                return False
        return True

    def _testo_traduko_nombro(self, vorto):
        if bool(re.match(r"^\d+[.,+*/]?\d*$", vorto)):
            vortoj = self.nombro_al_vortoj(vorto)
            self.nombroflago = True
            self.last_nombroflago = False
            return self.nombroflago, vortoj
        else:
            self.nombroflago = False
            return self.nombroflago, None

    def nombro_al_vortoj(self, nombro_str):
        unuoj = ["nul", "unu", "du", "tri", "kvar", "kvin", "ses", "sep", "ok", "naŭ"]
        def konvertu_tri_ciferojn(n):
            if n == 0:
                return []
            partoj = []
            centoj = n // 100
            resto = n % 100
            if centoj > 0:
                if centoj == 1:
                    partoj.append("cent")
                else:
                    partoj.append(unuoj[centoj] + " cent")
            if resto > 0:
                if resto < 10:
                    partoj.append(unuoj[resto])
                elif resto == 10:
                    partoj.append("dek")
                elif 11 <= resto <= 19:
                    partoj.append("dek " + unuoj[resto-10])
                else:
                    dek = resto // 10
                    unu = resto % 10
                    partoj.append(unuoj[dek] + " dek")
                    if unu > 0:
                        partoj.append(unuoj[unu])
            return partoj
        def entjero_al_vortoj(n_str, sufiksoj=True):
            n_str = n_str.lstrip('0')
            if n_str == "":
                return ["nul"]
            grupetoj = []
            temp = n_str
            while temp:
                if len(temp) <= 3:
                    grupetoj.append(temp)
                    break
                grupetoj.append(temp[-3:])
                temp = temp[:-3]
            grupetoj.reverse()
            vortoj_partoj = []
            for i, grupo_str in enumerate(grupetoj):
                grupo_valoro = int(grupo_str)
                if grupo_valoro == 0:
                    continue
                grupo_vortoj = konvertu_tri_ciferojn(grupo_valoro)
                vortoj_partoj.extend(grupo_vortoj)
                pozicio = len(grupetoj) - i - 1
                if sufiksoj:
                    if pozicio == 1:
                        vortoj_partoj.append("mil")
                    elif pozicio == 2:
                        if grupo_valoro == 1:
                            vortoj_partoj.append("miliono")
                        else:
                            vortoj_partoj.append("milionoj")
                    elif pozicio == 3:
                        if grupo_valoro == 1:
                            vortoj_partoj.append("miliardo")
                        else:
                            vortoj_partoj.append("miliardoj")
            return vortoj_partoj
        signo = []
        if nombro_str and nombro_str[0] in "+-/*=":
            signo = [self.cifero.get(nombro_str[0], "")]
            nombro_str = nombro_str[1:]
        nombro_str = str(nombro_str).replace(',', '.')
        partoj = nombro_str.split('.')
        if len(partoj) == 1:
            tuta_parto = partoj[0]
            dekuma_parto = ""
        else:
            tuta_parto = partoj[0]
            dekuma_parto = partoj[1]
        if tuta_parto == "" or int(tuta_parto) == 0:
            tuta_vortoj = ["nul"]
        else:
            tuta_vortoj = entjero_al_vortoj(tuta_parto, sufiksoj=True)
        if dekuma_parto == "" or int(dekuma_parto) == 0:
            dekuma_vortoj = []
        else:
            dekuma_parto = dekuma_parto.lstrip('0')
            if dekuma_parto == "":
                dekuma_vortoj = []
            else:
                dekuma_vortoj = entjero_al_vortoj(dekuma_parto, sufiksoj=False)
        if dekuma_vortoj:
            rezulto_listo = tuta_vortoj + ["komo"] + dekuma_vortoj
        else:
            rezulto_listo = tuta_vortoj
        rezulto_listo = signo + rezulto_listo
        return " ".join(rezulto_listo)



    def _aldonu_elementon(self, listo, elemento):
        nova_listo = listo[:]
        nova_listo.append(elemento)
        return nova_listo



    def _post_korekti_izolitajn(self, rezulto):
        """Gluas sinsekvajn erojn por formi konatajn morfemojn, forigante 'y'."""
        print("rezulto1",rezulto)
        if len(rezulto) < 2:
            return rezulto
        morfemoj = rezulto[:-1]
        # Platigi la liston (ĉiu sublisto estas aŭ unu morfemo aŭ listo de sufiksoj; ni platigas nur la unuopajn)
        flat = []
        for ero in morfemoj:
            if isinstance(ero, list):
                flat.extend(ero)
            else:
                flat.append(ero)
        # Ripetita kunigo: provu ĉiujn subsegmentojn
        ŝanĝita = True
        while ŝanĝita:
            ŝanĝita = False
            i = 0
            while i < len(flat):
                # Provu kunigi de i ĝis j (de la plej longa subsegmento)
                for j in range(len(flat), i, -1):
                    if j - i <= 1:
                        continue
                    provo = ''.join(flat[i:j])
                    # Se la kunigo estas en vortaro kaj ĝia kategorio ne estas 'y' (aŭ eĉ se 'y' sed ni preferas ne)
                    if provo in self.vortaro and self.vortaro[provo] != 'y':
                        flat[i:j] = [provo]
                        ŝanĝita = True
                        break
                i += 1
        # Rekonstrui la rezulton: ĉiu ero en propran subliston
        novaj_morfemoj = [[m] for m in flat]
        nova_kodo = ''.join(self.vortaro.get(m, '?') for m in flat)
        novaj_morfemoj.append(nova_kodo)
        return novaj_morfemoj




    def algoritmo4(self, vorto):
        trovitaj = []
        pritraktotaj = [([], vorto)]
        while pritraktotaj:
            faritaj, restantaj = pritraktotaj.pop()
            if restantaj in self.vortaro:
                trovitaj.append(self._aldonu_elementon(faritaj, restantaj))
                pritraktotaj = trovitaj
                break
            for i in range(1, len(restantaj) - 1):
                if restantaj[:i] in self.vortaro:
                    pritraktotaj.append((self._aldonu_elementon(faritaj, restantaj[:i]), restantaj[i:]))
        return pritraktotaj

    def _fortranĉu_finaĵon_detale(self, vorto):
        for finaĵo in self.finaĵoj:
            if vorto.endswith(finaĵo):
                return vorto[:-len(finaĵo)], finaĵo
        return vorto, ""

    def analizu_prefiksojn_kaj_radikojn(self, resto):
        """Rekursie serĉu prefiksojn + radiko. Revenas (prefikso_listo, radiko) aŭ (None, None) se malsukcesas."""
        ord_prefiksoj = sorted(self.prefiksoj, key=len, reverse=True)

        def serĉu(s, akumulitaj):
            if s == "":
                return None
            if s in self.vortaro and self.vortaro.get(s) == 'r':
                return (akumulitaj, s)
            for p in ord_prefiksoj:
                if s.startswith(p):
                    rez = serĉu(s[len(p):], akumulitaj + [p])
                    if rez is not None:
                        return rez
            return None

        rez = serĉu(resto, [])
        if rez is None:
            return ([], None)
        return rez

    def radikanalizo(self, vorto):
        # 1. Apartigi finaĵon
        radiko, finaĵo = self._fortranĉu_finaĵon_detale(vorto)

        # 2. Provizore forpreni sufiksojn (avide de la fino)
        provizoraj_sufiksoj = []
        restanta = radiko
        ŝanĝita = True
        while ŝanĝita:
            ŝanĝita = False
            for suf in sorted(self.sufiksoj, key=len, reverse=True):
                if restanta.endswith(suf):
                    provizoraj_sufiksoj.insert(0, suf)
                    restanta = restanta[:-len(suf)]
                    ŝanĝita = True
                    break

        # 3. Regluado de sufiksoj ĝis la restanta parto estas analizebla per prefiksoj+radiko
        while True:
            prefiksoj_listo, radiko_rekta = self.analizu_prefiksojn_kaj_radikojn(restanta)
            if radiko_rekta is not None:
                break
            if not provizoraj_sufiksoj:
                prefiksoj_listo = []
                radiko_rekta = restanta
                break
            suf = provizoraj_sufiksoj.pop(0)
            restanta = restanta + suf

        # 4. Se la rezulto estas nedisigita (radiko_rekta == restanta) kaj tiu restanta
        #    ne estas valida radiko (ne en vortaro aŭ ĝia kategorio estas 'y'),
        #    tiam provu malkomponi per algoritmo4.
        print("****",radiko_rekta,self.vortaro.get(radiko_rekta))
        if radiko_rekta == restanta and (radiko_rekta not in self.vortaro or self.vortaro.get(radiko_rekta) == 'Y'):
            rez_algo4 = self.algoritmo4(restanta)
            if rez_algo4:
                plej_longaj = sorted(rez_algo4, key=len, reverse=True)
                morfemoj = plej_longaj[0]
                rezulto = []
                for m in morfemoj:
                    rezulto.append([m])
                if provizoraj_sufiksoj:
                    rezulto.append(provizoraj_sufiksoj)
                if finaĵo:
                    rezulto.append([finaĵo])
                kodo = "".join(self.vortaro.get(m, "?") for m in morfemoj)
                kodo += "s" * len(provizoraj_sufiksoj)
                if finaĵo:
                    kodo += "t"
                rezulto.append(kodo)
                return rezulto

        # 5. Normala kunmetado (prefiksoj + radiko)
        rezulto = []
        for p in prefiksoj_listo:
            rezulto.append([p])
        rezulto.append([radiko_rekta])
        if provizoraj_sufiksoj:
            rezulto.append(provizoraj_sufiksoj)
        if finaĵo:
            rezulto.append([finaĵo])

        kodo = "p" * len(prefiksoj_listo) + 'r' + "s" * len(provizoraj_sufiksoj)
        if finaĵo:
            kodo += "t"
        rezulto.append(kodo)
        return rezulto



    def _flatigi_liston(self, nesta_listo):
        simpla_listo = []
        for elemento in nesta_listo:
            if isinstance(elemento, list):
                simpla_listo.extend(self._flatigi_liston(elemento))
            else:
                simpla_listo.append(elemento)
        return simpla_listo



    def _kompletigo_por_legado(self, analizo):
        ikompletigo = 0
        analizo = self._flatigi_liston(analizo)
        silaboj = []
        ĉiujsilaboj = []
        while ikompletigo <= len(analizo[-1])-1:
            if analizo[-1][ikompletigo] == "r":
                if self.silaba_vortaro.get(analizo[ikompletigo]) is not None:
                    if str(analizo[ikompletigo]) in self.silab_memoro:
                        silaboj = [analizo[ikompletigo]]
                    else:
                        analizo[ikompletigo] = self.silaba_vortaro.get(analizo[ikompletigo])
                        silaboj = list(analizo[ikompletigo])
                else:
                    silaboj = [analizo[ikompletigo]]
            elif analizo[-1][ikompletigo] in "spqvzxynt":
                if self.silaba_vortaro.get(analizo[ikompletigo]) is not None:
                    analizo[ikompletigo] = self.silaba_vortaro.get(analizo[ikompletigo])
                    silaboj = list(analizo[ikompletigo])
                else:
                    silaboj = [analizo[ikompletigo]]
            elif analizo[-1][ikompletigo] == "?":
                silaboj = [analizo[ikompletigo]]
            ikompletigo += 1
            ĉiujsilaboj = ĉiujsilaboj + silaboj
            #print(analizo, ĉiujsilaboj,silaboj)
        return ĉiujsilaboj, analizo

    def _aldoni_silenton(self, aŭdio_segmentoj, sampla_rapido, silento_daŭro):
        if silento_daŭro > 0:
            silento_samples = int(silento_daŭro * sampla_rapido)
            aŭdio_segmentoj.append(np.zeros(silento_samples))

    def piĉo_laŭgrada_rapida(self, signal, sr, fino_faktoro, segment_duration=0.1):
        segment_len = int(segment_duration * sr)
        output_parts = []
        for start in range(0, len(signal), segment_len):
            seg = signal[start:start+segment_len]
            if len(seg) == 0:
                continue
            t = start / len(signal)
            faktoro = 1.0 + t * (fino_faktoro - 1.0)
            new_len = int(len(seg) / faktoro)
            if new_len < 1:
                new_len = 1
            from scipy import signal as scipy_signal
            seg_shifted = scipy_signal.resample(seg, new_len)
            output_parts.append(seg_shifted)
        result = np.concatenate(output_parts)
        if len(result) > len(signal):
            result = result[:len(signal)]
        else:
            result = np.pad(result, (0, len(signal)-len(result)))
        max_val = np.max(np.abs(result))
        if max_val > 0:
            result = result / max_val * np.max(np.abs(signal))
        return result

    def _ŝargu_sekure(self, ŝlosilo):
        if ŝlosilo in self.silab_memoro:
            if self.last_nombroflago == False:
                self.neciferaj = self.neciferaj + 1
                if self.neciferaj > 2:
                    self.neciferaj = 0
                    self.last_nombroflago = True
            sr, datumoj = self.silab_memoro[ŝlosilo]
            return sr, datumoj, self.jamcitilo
        else:
            if ŝlosilo in "1234567890+-/*()[]{}€.,=_><#&|^@$£µ%§€°:~?!":
                if ŝlosilo == "-" and self.last_nombroflago == True:
                    ŝlosilo = "streketo"
                else:
                    ŝ=ŝlosilo
                    ŝlosilo = self.cifero.get(ŝlosilo)
                    print(ŝ,"cifera ŝlosilo", ŝlosilo)
                    self.last_nombroflago = True
            elif ŝlosilo in "αβγδεζηθικλμνξοπρστυφχψω":
                ŝlosilo = self.grekaj_literoj.get(ŝlosilo)
            elif ŝlosilo in "\"\'":
                if ŝlosilo == "'":
                    ŝlosilo = "apostrofo"
                    sr, datumoj = self.silab_memoro[ŝlosilo]
                elif ŝlosilo == '"':
                    if self.jamcitilo == True:
                        ŝlosilo = "fincitilo"
                        self.jamcitilo = False
                    else:
                        ŝlosilo = "ekcitilo"
                        self.jamcitilo = True
                    sr, datumoj = self.silab_memoro[ŝlosilo]
            if ŝlosilo in self.silab_memoro:
                sr, datumoj = self.silab_memoro[ŝlosilo]
            else:
                print("ŝlosilo",ŝlosilo)
                if ŝlosilo == " ":
                    pass
                elif ŝlosilo == '\uE000':
                    self.salti_intervalon = True
                    sr, datumoj = 44100, np.zeros(int(0.05 * self.sample_rate), dtype=np.float32)
                elif ŝlosilo is not None and ŝlosilo in "\n\r":
                    sr, datumoj = self.silab_memoro['alineo']
                else:
                    print(str(ŝlosilo))
                    sr, datumoj = self.silab_memoro['bof']
                    self.mankantaj = self.mankantaj + str(ŝlosilo)
            datumoj = np.atleast_1d(datumoj).astype(np.float32)
            return sr, datumoj, self.jamcitilo

    def _ludu_vorton_el_memoro(self, aŭdio_segmentoj, jamcitilo, interpunkcio, silaboj,
                               silab_memoro, laŭteco_faktoro, lasta_malplifortigo,
                               pika_maks, fade_proporcio, fade_fino, silento_sojlo):
        datumaro = []
        n = len(silaboj)
        print("nombre de silaboj", n)
        lasta_i = n - 1
        antaŭlasta_i = n - 2 if n >= 2 else None
        uzi_inter_silenton = (self.uz_maniero != "uzanto")
        inter_silento = self.silento_elemento if uzi_inter_silenton else 0.0
        for i, sil in enumerate(silaboj):
            segmentoj = []
            temp_sil = sil
            if KONFIGURO.get("testo_po_litera") == True:
                while len(temp_sil) > 0:
                    fono = temp_sil[0]
                    _, fon_datumoj, jamcitilo = self._ŝargu_sekure(fono)
                    segmentoj.append(fon_datumoj)
                    temp_sil = temp_sil[1:]
            else:
                print("sil",sil)
                if sil in silab_memoro:
                    _, datumoj, jamcitilo = self._ŝargu_sekure(sil)
                    segmentoj.append(datumoj)
                else:
                    temp_sil = sil
                    while len(temp_sil) > 0:
                        print(temp_sil)
                        if len(temp_sil) >= 3 and temp_sil[:3] in silab_memoro:
                            _, fon_datumoj, jamcitilo = self._ŝargu_sekure(temp_sil[:3])
                            segmentoj.append(fon_datumoj)
                            temp_sil = temp_sil[3:]
                        elif len(temp_sil) >= 2 and temp_sil[:2] in silab_memoro:
                            _, fon_datumoj, jamcitilo = self._ŝargu_sekure(temp_sil[:2])
                            segmentoj.append(fon_datumoj)
                            temp_sil = temp_sil[2:]
                        else:
                            fono = temp_sil[0]
                            _, fon_datumoj, jamcitilo = self._ŝargu_sekure(fono)
                            #fon_datumoj = np.concatenate((fon_datumoj, np.zeros(int(0.05 * 44100))))
                            segmentoj.append(fon_datumoj)
                            temp_sil = temp_sil[1:]
            if segmentoj:
                silab_sono = np.concatenate(segmentoj)
            else:
                silab_sono = np.array([])
            datumaro.append(silab_sono)
        if antaŭlasta_i is not None:
            if self.uz_maniero =="lernanto":
                datumaro[antaŭlasta_i] = datumaro[antaŭlasta_i] * (laŭteco_faktoro+0.5)
            else:
                datumaro[antaŭlasta_i] = datumaro[antaŭlasta_i] * laŭteco_faktoro
        datumaro[lasta_i] = datumaro[lasta_i] * lasta_malplifortigo
        if n == 0:
            rezulto = np.array([])
        elif n == 1:
            rezulto = datumaro[0]
        else:
            rezulto = datumaro[0]
            for i in range(1, n):
                nuna = datumaro[i]
                if uzi_inter_silenton and inter_silento > 0:
                    silento = np.zeros(int(inter_silento * self.sample_rate))
                    rezulto = np.concatenate([rezulto, silento, nuna])
                else:
                    fade_len = int(min(len(rezulto), len(nuna)) * fade_proporcio)
                    if fade_len > 0:
                        fad_out = np.linspace(1.0, fade_fino, fade_len)
                        fad_in = np.linspace(fade_fino, 1.0, fade_len)
                        fino_rez = rezulto[-fade_len:] * fad_out
                        komenco_nuna = nuna[:fade_len] * fad_in
                        miksaĵo = fino_rez + komenco_nuna
                        rezulto = np.concatenate([
                            rezulto[:-fade_len] if len(rezulto) > fade_len else np.array([]),
                            miksaĵo,
                            nuna[fade_len:] if len(nuna) > fade_len else np.array([])
                        ])
                    else:
                        rezulto = np.concatenate([rezulto, nuna])
        rezulto = np.clip(rezulto, -pika_maks, pika_maks)
        aŭdio_segmentoj.append(rezulto)
        return jamcitilo

    def anstataŭigi_streketon(self, listo):
        for i in range(1, len(listo) - 1):
            if listo[i] == '-':
                antaŭa = listo[i-1]
                sekva = listo[i+1]
                if antaŭa not in ('-', '') and sekva not in ('-', ''):
                    if sekva[0] not in self.cifero:
                        listo[i] = '\uE000'
        return listo


# ========== METODOJ POR LERNANTA REĜIMO ==========
    def _generi_sonon_por_frazo_rekte(self, frazo, inter_vorta_silento=0.50):
        """
        Generas sonon por frazo, resendas (sono, indeksoj) kie indeksoj estas listo
        de la komencaj pozicioj (en specimenoj) de ĉiu vorto.
        """
        import re
        print(f"  🔨 Generas sonon por: '{frazo[:100]}...'")
        # 1. Disigu la frazon en vortojn (inkluzive interpunkciojn)
        vortoj = re.findall(r'\w+|[.,!?;:()"\'-]', frazo)
        print(vortoj)
        if not vortoj:
            return None, []

        # 2. Generu sonon por ĉiu vorto aparte (sen inter-vorta silento)
        sondatumoj = []
        for v in vortoj:
            # Por ĉiu vorto, ni kreas provizoran aŭdion
            temp_aŭdio = []
            self.jamcitilo = False
            v=v.lower()
            print("eldiro   ",v)
            if v in self.silab_memoro:
                sr, datumoj = self.silab_memoro[v]
                temp_aŭdio.append(datumoj)
            else:
                analizo = self.radikanalizo(v.lower())
                analizo = self._flatigi_liston(analizo)
                silaboj, _ = self._kompletigo_por_legado(analizo)
                self.jamcitilo = self._ludu_vorton_el_memoro(
                    temp_aŭdio, self.jamcitilo, "", silaboj,
                    self.silab_memoro, self.laŭteco_faktoro, self.lasta_malplifortigo,
                    self.pika_maks, self.fade_proporcio, self.fade_fino, self.silento_sojlo)
            if temp_aŭdio:
                sono_vorto = np.concatenate(temp_aŭdio)
                max_val = np.max(np.abs(sono_vorto))
                if max_val > 0:
                    sono_vorto = sono_vorto / max_val * 0.6
                sono_vorto = np.int16(sono_vorto * 32767)
                sondatumoj.append(sono_vorto)
            else:
                sondatumoj.append(np.zeros(int(0.05 * SAMPLE_RATE), dtype=np.int16))

        # 3. Kunigu la sondatumojn kun egala silento inter ili
        # if v=="punkto":
        #     silento = np.zeros(int(inter_vorta_silento * SAMPLE_RATE*3), d
        # else:type=np.int16)
        silento = np.zeros(int(inter_vorta_silento * SAMPLE_RATE), dtype=np.int16)
        tuto = []
        indeksoj = [0]  # unua vorto komenciĝas ĉe 0
        for i, snd in enumerate(sondatumoj):
            tuto.append(snd)
            if i < len(sondatumoj) - 1:
                tuto.append(silento)
                # post aldono de la nuna vorto kaj la silento, la sekva vorto komenciĝas
                indeksoj.append(len(np.concatenate(tuto)))
        # post la lasta vorto, aldoni la finon (indekso por tranĉi la lastan vorton)
        tuto = np.concatenate(tuto)
        indeksoj.append(len(tuto))
        return tuto, indeksoj

    def legi_lernanto_sinsekve(self, text, app):
        """Legas tekston po unu vorto, haltas je la fino de la nuna vorto, rekomencas de tiu sama."""
        print('TEXT',text)
        frazoj = [s.strip() for s in text.split('\n') if s.strip()]
        if not frazoj:
            frazoj = [text]
        for frazo in frazoj:
            if not app._legado_aktiva:
                break
            sono, indeksoj = self._generi_sonon_por_frazo_rekte(frazo)
            if sono is None:
                continue
            vorto_num = 0
            while vorto_num < len(indeksoj) - 1:
                # Atendu se paŭzita antaŭ ol ludi la sekvan vorton
                while app.paŭzita:
                    time.sleep(0.1)
                    if not app._legado_aktiva:
                        return
                start = indeksoj[vorto_num]
                end = indeksoj[vorto_num + 1]
                segmento = sono[start:end]
                temp_file = f"{frazoj_bufro}/lernanto_temp.wav"
                with wave.open(temp_file, 'w') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(segmento.tobytes())
                sound = SonTraktilo.load(temp_file)
                if sound:

                    sound.play()
                    while sound.state == 'play':
                        time.sleep(0.05)
                        if app.paŭzita:
                            sound.stop()
                            break
                    sound.unload()
                try:
                    os.remove(temp_file)
                except:
                    pass
                # Post kiam la sono finiĝis (nature aŭ haltigite), pluigu al sekva vorto
                # nur se NE estas paŭzita. Se paŭpzita, ni restas ĉe la sama vorto_num.
                if not app.paŭzita:
                    vorto_num += 1
            # Fino de frazo: se paŭzita, atendu por ke la rekomenco daŭrigu al sekva frazo
            while app.paŭzita:
                time.sleep(0.1)
                if not app._legado_aktiva:
                    return
        Kronometro.schedule_once(lambda dt: app._finu_legadon(), 0)



    def akiri_koloritan_tekston(self, frazo):
        import re
        try:
            parts=re.split(r'(["\';:+\-/*=_)({}\[\]&°#@£$µ§><^|~%¨\\ ]|\r?\n|\r)', frazo)

            parts = [p for p in parts if p != ' ']
            #parts = self.anstataŭigi_streketon(parts)
            vortoj = [r for r in parts if r != ""]
        except Exception as e:
            return frazo
        rezulto = []
        index=0
        print("vortoj",vortoj)
        for vorto in vortoj:
            print(vorto,"########")
            interpunkcio = ''
            kolora_vorto = []
            #vorto = original_vorto
            if vorto and vorto[-1] in '.,;:!?)]}\'"':
                interpunkcio = vorto[-1]
                vorto = vorto[:-1]
            if not vorto:
                rezulto.append(f'[color=000000]{interpunkcio}[/color]')
                rezulto.append('  ')
                continue
            if vorto in self.cifero:
                vortoj[index]=self.cifero.get(vorto)

                print("izolita cifero",vorto)
            print("nova vortoj",vortoj)

            try:
                self.nombroflago, tradukitanombro = self._testo_traduko_nombro(vorto)
                # Bluo - #0000FF
                # Lazuro - #007FFF
                # Cielbluo - #00BFFF
                # Ciano - #00FFFF
                # Verdo (transira) - #00FF80
                # Flavverdo - #80FF00
                # Flavo - #FFFF00
                # Oranĝo - #FF8000
                # Vermiljono - #FF4000
                # Ruĝo - #FF0000
                if self.nombroflago:
                    print(tradukitanombro)
                    nombrazono = tradukitanombro
                    print("nombrezono",nombrazono)
                    vortoj[index]=tradukitanombro
                    print("traduko de nombro",vortoj[index])
                    for nv in tradukitanombro.split():
                        print("nv",nv)
                        kolora_vorto.append(f'[color=000000]{nv}[/color]')
                elif self.akcepti_vorton(vorto):
                    #
                    print("pre akronimo",vorto)
                    #vorto = re.sub(r'[.\',/]', "", vorto)
                    akronimo = list(vorto)
                    print (akronimo)
                    akronimo = [elem for elem in akronimo if elem != '.']
                    print (akronimo)
                    n = 0
                    for vorto in akronimo:
                        vorto = vorto.lower()
                        print(vorto)
                        if vorto in self.konsonantoj:
                            vorto = vorto+"o"
                        akronimo[n] = vorto
                        kolora_vorto.append(f'[color=000000]{vorto}[/color]')
                        n = n+1
                    akronimo=" ".join(akronimo)
                    print ("akronimo",akronimo)
                    vortoj[index]= akronimo


                else:
                    vorto_low = vorto.lower()
                    print(vorto_low,"+++")
                    if vorto_low in self.vortaro:
                        print(vorto_low,"****+++")
                        print("tipo",self.vortaro.get(vorto_low))
                        tipo=self.vortaro.get(vorto_low).lower()
                        print(tipo)
                        if tipo=='v': #korelativo
                           kolora_vorto.append(f'[color=80FF00]{vorto_low}[/color]')
                        elif tipo == 'q': #pronomo
                            kolora_vorto.append(f'[color=0000FF]{vorto_low}[/color]')
                        elif tipo == 'z': # prepozicio
                            kolora_vorto.append(f'[color=00BFFF]{vorto_low}[/color]')
                        elif tipo == 'x': # konjunkcio
                            kolora_vorto.append(f'[color=007FFF]{vorto_low}[/color]')
                        else:
                            kolora_vorto.append(f'[color=000000]{vorto_low}[/color]')
                    else:
                        analizo = self.radikanalizo(vorto_low)
                        analizo = self._flatigi_liston(analizo)
                        print ("analizo", analizo)
                        if len(analizo) >= 2:
                            kodo = analizo[-1]
                            partoj = analizo[:-1]
                            if len(kodo) < len(partoj):
                                kodo = kodo + '?' * (len(partoj) - len(kodo))
                            elif len(kodo) > len(partoj):
                                kodo = kodo[:len(partoj)]
                            for i, parto in enumerate(partoj):
                                ch = kodo[i] if i < len(kodo) else '?'
                                if ch == 'r':  # rradiko
                                    kolora_vorto.append(f'[color=107C10]{parto}[/color]')
                                elif ch == 't':  #terminaĵoj
                                    kolora_vorto.append(f'[color=FF0000]{parto}[/color]')
                                elif ch == 'q': #pronomo
                                    kolora_vorto.append(f'[color=0000FF]{parto}[/color]')
                                elif ch == 'v':  # korelativo  kiu, kiel ktp
                                    kolora_vorto.append(f'[color=80FF00]{parto}[/color]')
                                elif ch == 's': # sufikso
                                    kolora_vorto.append(f'[color=FF8000]{parto}[/color]')
                                elif ch == 'z': # prepozicio
                                    kolora_vorto.append(f'[color=00BFFF]{parto}[/color]')
                                elif ch == 'x': # konjunkcio
                                    kolora_vorto.append(f'[color=007FFF]{parto}[/color]')
                                elif ch == 'p': #prefikso
                                    kolora_vorto.append(f'[color=00FFFF]{parto}[/color]')
                                else:
                                    kolora_vorto.append(f'[color=000000]{parto}[/color]')
                        else:
                            kolora_vorto.append(f'[color=000000]{vorto}[/color]')
            except Exception as e:
                kolora_vorto.append(f'[color=000000]{vorto}[/color]')
            if kolora_vorto:
                rezulto.append('-'.join(kolora_vorto))
            else:
                rezulto.append('-')
            if interpunkcio:
                rezulto.append(f'[color=000000]{interpunkcio}[/color]')
            rezulto.append('  ')
            index=index+1
        print ("transdonita teksto",' '.join(vortoj))
        print ("transdonita teksto",' '.join(rezulto))
        print ("transdonita teksto",' '.join(kolora_vorto))
        fina = '  '.join(rezulto).rstrip(' ')
        return fina,' '.join(vortoj)




    def konstrui_sonon_por_frazo(self, frazo):
        """
        METU ĈI TIE VIAN KOMPLEKSAN FUNKCION
        kiu konstruas sonon el frazo.

        ENIRON: frazo (string)
        ELIRON: numpy array (int16) kun la sono, aŭ None se malsukcesis
        """
        print(f"  🔨 Konstruas sonon por: '{frazo[:30]}...'")
        print(frazo)
        global silab_memoro
        # Analizu vortojn kaj skribu rezultojn ''
        import re
        parts = re.split(r'(["\';:+\-/*=_)({}\[\]&°#@£$µ§><^|~%¨\\ ]|\n\r)', frazo)
        parts = [p for p in parts if p != ' '] # Formeti spacan karaktron eble malriĉigas analizon
        print ("parts",parts)
        parts = self.anstataŭigi_streketon(parts)
        print(parts)

        global vortoj
        vortoj = [r for r in parts if r != ""]

        print("Teksto:",  vortoj )
        # print("teksto studata   ",vortoj)
        analizo = []

        # print(silaboj)
        # Aŭtomate eligu la ekziston de silab_memoro
        if not self.silab_memoro:
            print("Averto: silab_memoro estas malplena!")
            return

        unua_silabo = next(iter(self.silab_memoro))
        sampla_rapido, _ = self.silab_memoro[unua_silabo]

        #
        nombrazono = ""
        self.jamcitilo = False
        aŭdio_segmentoj = []

        def disigu_interpunkcion(vorto):
            # Serĉas vortojn aŭ la specifajn interpunkciajn signojn
            return re.findall(r'\w+|[€,!°&#%§?;\.\n\r]', vorto)

        global index
        index = 0
        interpunkcio = ""
        print("KOMENCO ĈEFA BUKLO")
        print("dismeto de vortoj ", vortoj)
        while index < len(vortoj):
            vorto = vortoj[index]  # sorted(vortoj, key=esperanta_klavo):
            print("iniciala vorto",vorto)
            if vorto in self.silab_memoro:
                sr, datumoj = self.silab_memoro[vorto]
                aŭdio_segmentoj.append(datumoj)
                if vorto =="ktp":
                    self._aldoni_silenton(aŭdio_segmentoj, sampla_rapido, self.silento_komo)
                else:
                    L=len(vorto)
                    print (self.silento_intervalo,"*",self.silento_progreso[L])
                    intervalo=self.silento_progreso[L]*self.silento_intervalo
                    print(vorto,L,intervalo)
                    self._aldoni_silenton(aŭdio_segmentoj, sampla_rapido, intervalo)

                index=index+1
                continue

            silaboj = []
            # print(" antau +++++++++++++++++++++++++++++++++++++++++++++++++++",vorto)
            if index< len(vortoj)-1 and vortoj[index+1]=='\uE000':
                self.salti_intervalon=True
            if index < len(vortoj)-1 and (vortoj[index+1])[0] in "0123456789" :
                self.last_nombroflago= False


            if vorto == "\n" or vorto == "\r":
               # print ("lini_finio")
               pass
            self.nombroflago, tradukitanombro = self._testo_traduko_nombro(vorto)  # serĉas kaj tradukas literen nombron
            if self.akcepti_vorton(vorto):  # detektas AKRONIMOJ
                akronimoflago = True
                self.last_nombroflago = False
            else:
                akronimoflago = False

            # print("KIO ESTAS    +++++++++++  ",akronimoflago,nombroflago,tradukitanombro)

            if akronimoflago == True:
                vorto = re.sub(r'[.\',/]', "", vorto)
                akronimo = list(vorto)
                # print (vortoj)
                n = 0
                for vorto in akronimo:
                    vorto = vorto.lower()
                    # print(vorto)
                    if vorto in self.konsonantoj:
                        vorto = vorto+"o"
                    akronimo[n] = vorto
                    n = n+1

                n = 0
                while n < len(akronimo):
                    vorto = akronimo[n]
                    # print("nombro buklo ",vorto)
                    analizo = self.radikanalizo(vorto)
                    # print("analizo     ",analizo)
                    silaboj, analizo = self._kompletigo_por_legado(analizo)
                    # print("analizo     ",analizo,"silabo", silaboj)
                    jamcitilo = self._ludu_vorton_el_memoro(
                        aŭdio_segmentoj,       # 1
                        self.jamcitilo,        # 2
                        interpunkcio,          # 3
                        silaboj,               # 4
                        self.silab_memoro,     # 5
                        self.laŭteco_faktoro,  # 6
                        self.lasta_malplifortigo,
                        self.pika_maks,        # 7
                        self.fade_proporcio,    # 8
                        self.fade_fino,        # 9
                        self.silento_sojlo    # 10
                    )
                    self._aldoni_silenton(
                        aŭdio_segmentoj, sampla_rapido, self.silento_akronimo)
                    # print("n ",n)
                    n = n+1

            elif self.nombroflago == True:
               nombrazono = tradukitanombro
               print("nombrezono",nombrazono)
               x = index+1
               if x < len(vortoj)-1:
                    if vortoj[x] in ',-+/*=':
                       self.nombroflago, tradukitanombro = self._testo_traduko_nombro(
                           vortoj[x+1])
                       print("NOMBRO",self.nombroflago,self.last_nombroflago)
                       if self.nombroflago == True:
                           if vortoj[x] == ",":
                               nombrazono = nombrazono+" komo "+tradukitanombro
                           elif vortoj[x] == "-":
                               nombrazono = nombrazono+" minus "+tradukitanombro
                           elif vortoj[x] == "+":
                               nombrazono = nombrazono+" plus"+tradukitanombro
                           elif vortoj[x] == "*":
                               nombrazono = nombrazono+" oble "+tradukitanombro
                           elif vortoj[x] == "/":
                               nombrazono = nombrazono+" one "+tradukitanombro
                           elif vortoj[x] == "=":
                               nombrazono = nombrazono+" egalas "+tradukitanombro

                           #self.last_nombroflago = True
                           # print("nombro kun komo", nombrazono)
                           index = index+2
                           # legado de nombrazono
                       else:
                          print("nombro sen komo", nombrazono)
                          # legado de nombrazono

               nombro_grupoj = nombrazono.split()
               # print("nombro_grupoj ",nombro_grupoj)
               n = 0
               while n < len(nombro_grupoj):
                   vorto = nombro_grupoj[n]
                   # print("nombro buklo ",vorto)
                   # if vorto!='komo':
                   #     nombro_al_vortoj(vorto)
                   if vorto not in self.silab_memoro:
                       analizo = self.radikanalizo(vorto)
                       analizo = self._flatigi_liston(analizo)
                       # print("NE ĈESTA EN SILAB_MEMORO")
                       silaboj, analizo = self._kompletigo_por_legado(analizo)
                       # print("analizo     ",an_alizo,"silabo", silaboj)
                   else:
                       silaboj = [vorto]
                       # print("SILABOJ",silaboj)
                   self.jamcitilo = self._ludu_vorton_el_memoro(
                       aŭdio_segmentoj,       # 1
                       self.jamcitilo,        # 2
                       interpunkcio,          # 3
                       silaboj,               # 4
                       self.silab_memoro,     # 5
                       self.laŭteco_faktoro,  # 6
                       self.lasta_malplifortigo,
                       self.pika_maks,        # 7
                       self.fade_proporcio,    # 8
                       self.fade_fino,        # 9
                       self.silento_sojlo    # 10
                   )

                   if vorto in ["dek", "cent", "mil", "miliono", "milionoj", " miliardo", "miliardoj"]:
                       self._aldoni_silenton(
                           aŭdio_segmentoj, sampla_rapido, self.silento_cifero)
                   else:
                       self._aldoni_silenton(
                           aŭdio_segmentoj, sampla_rapido, self.silento_intervalo)
                   # print("n ",n)
                   n = n+1

            else:
                # print("traktata vorto ",vorto)
                vorto = vorto.lower()
                print("Ĝi NE ESTAS NOMBRO",vorto)

                #vorto = self._flatigi_liston(vorto)
                #print("post disigo de interpunkcio", vorto) #, vorto[-1])
                print("2",vorto)
                if len(vorto) > 1:
                    vorto = disigu_interpunkcion(vorto)
                    print("3",vorto)
                    if vorto[-1] in ",.!?\n\r" and len(vorto) > 1:
                        interpunkcio = vorto[-1]
                        # print("filrilo de punkto",vorto)
                        vorto = vorto[:-1]
                        delimiter = ""  # Define a delimiter
                        vorto = delimiter.join(vorto)
                        # print("filrilo de punkcio",vorto)
                    else:
                        interpunkcio = " "  # eble okazigos tro dasilento?
                        vorto = vorto.pop() # ĉar vorto iĝi tabelon en funkcio diigu_interpunkcio
                    # print ("sen,interpunkcio",vorto,interpunkcio)
                     # redonas simplan katenon
                print("Vorto ", vorto)
                if vorto not in self.silab_memoro:
                    # print("ebla komo")
                    if vorto == "," or vorto == ";":
                        print("komo punkto komo")
                        self._aldoni_silenton(
                            aŭdio_segmentoj, sampla_rapido, self.silento_komo)
                        print("reveno de aldoni silenton")

                    else:
                        analizo = self.radikanalizo(vorto)
                        analizo = self._flatigi_liston(analizo)
                        print("analizo     ",analizo)
                        silaboj, analizo = self._kompletigo_por_legado(analizo)
                        self.jamcitilo = self._ludu_vorton_el_memoro(
                            aŭdio_segmentoj,       # 1
                            self.jamcitilo,        # 2
                            interpunkcio,          # 3
                            silaboj,               # 4
                            self.silab_memoro,     # 5
                            self.laŭteco_faktoro,  # 6
                            self.lasta_malplifortigo,
                            self.pika_maks,        # 7
                            self.fade_proporcio,    # 8
                            self.fade_fino,        # 9
                            self.silento_sojlo    # 10
                        )
                        # print("silento")
                        if self.salti_intervalon == False:
                            print("kun silento",self.silento_intervalo)
                            L=len(vorto)
                            intervalo=self.silento_intervalo*self.silento_progreso[L]

                            print(vorto,L,self.silento_progreso[L],intervalo)
                            self._aldoni_silenton(aŭdio_segmentoj, sampla_rapido, intervalo)
                        else:
                            print("sen silento")
                            self.salti_intervalon = False
                        #
                else:
                    silaboj = [vorto]
                    # print("atentu")
                    # print(self.jamcitilo)
                    self.jamcitilo = self._ludu_vorton_el_memoro(
                        aŭdio_segmentoj,       # 1
                        self.jamcitilo,        # 2
                        interpunkcio,          # 3
                        silaboj,               # 4
                        self.silab_memoro,     # 5
                        self.laŭteco_faktoro,  # 6
                        self.lasta_malplifortigo,
                        self.pika_maks,        # 7
                        self.fade_proporcio,    # 8
                        self.fade_fino,        # 9
                        self.silento_sojlo    # 10
                    )
                    # print("silento")
                    if self.salti_intervalon == False:
                        print("kun silento")
                        L=len(vorto)
                        intervalo=self.silento_intervalo*self.silento_progreso[L]
                        print(vorto,L,self.silento_progreso[L],intervalo)
                        self._aldoni_silenton(aŭdio_segmentoj, sampla_rapido, intervalo)
                    else:
                        print("sen silento")
                        self.salti_intervalon = False
                    # Aldoni silenton laŭ interpunkcio
                print("mi estas tie",interpunkcio, " fina longo", len(aŭdio_segmentoj))
                print("INTERPUNKCIO", interpunkcio)
            if interpunkcio != "":
                if interpunkcio in ",;":
                    if interpunkcio == "," and len(aŭdio_segmentoj) > 1:
                        lastaj_du = np.concatenate([aŭdio_segmentoj[-2], aŭdio_segmentoj[-1]])
                        modifita = self.piĉo_laŭgrada_rapida(lastaj_du, sampla_rapido, 1.1)
                        aŭdio_segmentoj = aŭdio_segmentoj[:-2] + [modifita]
                        print ("estis ,")
                    self._aldoni_silenton(aŭdio_segmentoj, sampla_rapido, self.silento_komo)
                elif interpunkcio ==".":
                    if interpunkcio == "." and len(aŭdio_segmentoj) >1:
                        lastaj_du = np.concatenate([aŭdio_segmentoj[-2], aŭdio_segmentoj[-1]])
                        modifita = self.piĉo_laŭgrada_rapida(lastaj_du, sampla_rapido, 0.9)
                        aŭdio_segmentoj = aŭdio_segmentoj[:-2] + [modifita]
                        print("estis .")
                    self._aldoni_silenton(aŭdio_segmentoj, sampla_rapido, self.silento_punkto)
                elif interpunkcio in"!?":
                    self._aldoni_silenton(aŭdio_segmentoj, sampla_rapido, self.silento_punkto)
            print ("***************",len(aŭdio_segmentoj))
            index += 1

                # KONSTRUI LA FINAN SONON POR ĈI TIU FRAZO
        print(" fina longo", len(aŭdio_segmentoj))
        if aŭdio_segmentoj and len(aŭdio_segmentoj) > 0:
            # kunigi ĉiuj segmentojn kun fin-ek-mikso
            #tuto = self._prepari_aŭdion_simple(aŭdio_segmentoj, sampla_rapido)
            tuto = np.concatenate(aŭdio_segmentoj) if aŭdio_segmentoj else np.array([])

        if tuto.dtype != np.int16:
            # Normigi al intervalo [-1, 1]
            max_val = np.max(np.abs(tuto))
            if max_val > 0:
                tuto = tuto / max_val * 0.5
            tuto = np.int16(tuto * 32767)

        if len(tuto) > 0:
            # print("registrenda frazo", frazo)
            self.ringo.peti_ludon(tuto, is_parolado=True)
            aŭdio_segmentoj = []
            return True  # ✅ Sukcesis

        else:
            print(f"  ⚠ Neniu sono konstruita por ĉi tiu frazo")

        print("mankantaj =", self.mankantaj, "lastavorto traktata", vorto)
        return False  # La sono jam estas sendita al ringo-buffer




    def legi_tekston(self, text):
        if disvolvo:     # man-ŝaltitita regilo por reŝargi silabaron je ĉiu lego-peto
            self._ŝargi_datumojn()
        frazoj = [s.strip() + "" for s in text.split('\n') if s.strip()]
        if not frazoj:
            frazoj = [text]
        for i, frazo in enumerate(frazoj):
            self.ringo.semaphore.acquire()
            sukcesis = self.konstrui_sonon_por_frazo(frazo)
            if not sukcesis:
                self.ringo.semaphore.release()

# ======================== KIVY-INTERFACO ========================
# (Ĉi tie metu la klason DosierElektiloKrom_Kadro – vi jam havas ĝin.)
# Pro koncizeco mi ne republikas ĝin, sed ĝi restas sama.
class DosierElektiloKrom_Kadro(Krom_Kadro):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Elektu dosieron"
        self.size_hint = (0.95, 0.7)
        self.auto_dismiss = False
        krado = KadroAranĝo(orientation='vertical', spacing=5, padding=10)
        self.vojo_Etikedo = Etikedo(text="Ŝarganta vojon...", size_hint_y=None, height=30, font_size='12sp', color=[0.5,0.5,0.5,1], halign='left')
        self.vojo_Etikedo.bind(size=self.vojo_Etikedo.setter('text_size'))
        krado.add_widget(self.vojo_Etikedo)
        uzu_kivy_filechooser = (platformo != 'android' or PYDROID3 or not PLYER_DISPONEBLA)
        if uzu_kivy_filechooser:
            self._krei_kivy_interfacon(krado)
        else:
            self._krei_android_interfacon(krado)
        self.add_widget(krado)

    def _krei_android_interfacon(self, krado):
        msg = Etikedo(text="La sistema dosierelektilo malfermiĝos.", size_hint_y=None, height=40, font_size='14sp')
        krado.add_widget(msg)
        btn_krado = KadroAranĝo(size_hint_y=None, height=50, spacing=10)
        btn_malfermi = Butono(text="📁 Malfermi", font_size='16sp')
        btn_malfermi.bind(on_press=self._lanĉi_android_elektilon)
        btn_krado.add_widget(btn_malfermi)
        btn_nuligi = Butono(text="❌ Nuligi", font_size='16sp')
        btn_nuligi.bind(on_press=self.fermi_Krom_Kadro)
        btn_krado.add_widget(btn_nuligi)
        krado.add_widget(btn_krado)

    def _krei_kivy_interfacon(self, krado):
        start_path = self._trovi_startan_vojon()
        self.filechooser = Dosier_Elektejo(filters=['*.txt', '*.TXT', '*.wav', '*.WAV'], path=start_path, size_hint_y=1)
        self.filechooser.bind(path=self._ĝisdatigi_vojon)
        krado.add_widget(self.filechooser)
        nav_krado = KadroAranĝo(size_hint_y=None, height=40, spacing=5)
        btn_hejmo = Butono(text="🏠 Hejmo", font_size='12sp')
        btn_hejmo.bind(on_press=lambda x: self._ŝanĝi_vojon(os.path.expanduser('~')))
        nav_krado.add_widget(btn_hejmo)
        btn_sd = Butono(text="💾 SD-Karto", font_size='12sp')
        btn_sd.bind(on_press=lambda x: self._ŝanĝi_vojon('/sdcard'))
        nav_krado.add_widget(btn_sd)
        btn_docs = Butono(text="📄 Documents", font_size='12sp')
        btn_docs.bind(on_press=lambda x: self._ŝanĝi_vojon('/sdcard/Documents'))
        nav_krado.add_widget(btn_docs)
        krado.add_widget(nav_krado)
        btn_krado = KadroAranĝo(size_hint_y=None, height=50, spacing=10)
        btn_elekti = Butono(text="✅ Elekti", font_size='16sp')
        btn_elekti.bind(on_press=self._elekti_dosieron)
        btn_krado.add_widget(btn_elekti)
        btn_nuligi = Butono(text="❌ Nuligi", font_size='16sp')
        btn_nuligi.bind(on_press=self.fermi_Krom_Kadro)
        btn_krado.add_widget(btn_nuligi)
        krado.add_widget(btn_krado)
        Kronometro.schedule_once(lambda dt: self._ĝisdatigi_vojon(None, start_path), 0.1)

    def _trovi_startan_vojon(self):
        if platformo == 'android':
            eblaj_vojoj = ['/sdcard/Documents', '/sdcard/Documents/Android', '/sdcard/Android/data/ru.iiec.pydroid3/files/', '/storage/emulated/0/Documents', '/sdcard', os.path.expanduser('~')]
            for vojo_test in eblaj_vojoj:
                if os.path.exists(vojo_test):
                    return vojo_test
            return '/sdcard'
        else:
            return os.path.expanduser('~')

    def _ŝanĝi_vojon(self, nova_vojo):
        if hasattr(self, 'filechooser') and os.path.exists(nova_vojo):
            self.filechooser.path = nova_vojo

    def _ĝisdatigi_vojon(self, instance, nova_vojo):
        if hasattr(self, 'vojo_Etikedo'):
            self.vojo_Etikedo.text = f"📁 {nova_vojo}"

    def _lanĉi_android_elektilon(self, instance):
        if not PLYER_DISPONEBLA:
            return
        try:
            from plyer import filechooser
            filechooser.choose_file(on_success=self._prilabori_sukceson, on_cancel=self._prilabori_nuligon, on_failure=self._prilabori_eraron, filters=[('Tekstaj dosieroj', '*.txt'), ('Ĉiuj dosieroj', '*')], multiple=False)
        except Exception as e:
            self.dismiss()
            Kronometro.schedule_once(lambda dt: self._malfermi_kiel_kivy(), 0.5)

    def _malfermi_kiel_kivy(self):
        Krom_Kadro = DosierElektiloKrom_Kadro(self.callback)
        Krom_Kadro.open()

    def _elekti_dosieron(self, instance):
        if self.filechooser.selection:
            vojo = self.filechooser.selection[0]
            self.fermi_Krom_Kadro()
            if self.callback:
                self.callback(vojo)

    def _prilabori_sukceson(self, elekto):
        if elekto:
            self.fermi_Krom_Kadro()
            if self.callback:
                self.callback(elekto[0])

    def _prilabori_nuligon(self):
        self.fermi_Krom_Kadro()

    def _prilabori_eraron(self, eraro):
        self.fermi_Krom_Kadro()

    def fermi_Krom_Kadro(self, instance=None):
        self.dismiss()



class Esperanto_voĉigiloApp(App):
    def build(self):
        #Window.fullscreen = 'auto'
        self.ringo = Esperanto_voĉigiloAudio()
        if os.path.exists(frazoj_bufro):
            print("frazoj_bufro++",frazoj_bufro)
            for f in os.listdir(frazoj_bufro):
                if f.endswith(".wav"):
                    try:
                        print(os.path.join(frazoj_bufro, f))
                        os.remove(os.path.join(frazoj_bufro, f))
                    except:
                        pass
        print("frazoj_bufro+-+",frazoj_bufro)
        self.parolilo = ViaKompleksaParolilo(self.ringo)
        self.current_sound = None
        self._legado_aktiva = False
        self._sku_detekto_dum_legado = False
        self.sku_detektilo = None
        self.sku_aktivigita = False
        self.uz_maniero = "uzanto"
        self.paŭzita = False

        krado = KadroAranĝo(orientation='vertical', spacing=5, padding=5)
        # info_krado = KadroAranĝo(size_hint=(1, 0.03), spacing=2)
        # self.ringo.buffer_Etikedo = Etikedo(text="[⬜⬜⬜⬜]", markup=True, font_size='18sp', size_hint=(0.5,1))
        # info_krado.add_widget(self.ringo.buffer_Etikedo)
        # self.ringo.stats_Etikedo = Etikedo(text=f"G:{self.ringo.generita_count} L:{self.ringo.ludita_count}", font_size='14sp', size_hint=(0.5,1))
        # info_krado.add_widget(self.ringo.stats_Etikedo)
        # krado.add_widget(info_krado)

        vidrulejo = VidRulejo(size_hint=(1,0.7), do_scroll_x=False, do_scroll_y=True, bar_width=10)
        self.eniraĵo = Tekstejo(text="Saluton! Ĉi tio estas testa teksto. Ni provu per pluraj frazoj. Ĉu vi aŭdas la tonojn?", multiline=True, size_hint_y=None, height=1000, font_size='18sp', background_color=[0.8,0.8,0.8,0.8], foreground_color=[0,0,0,1], padding=[10,10], selection_color=[0.3,0.6,1,0.5])
        self.eniraĵo.bind(minimum_height=self.eniraĵo.setter('height'))
        vidrulejo.add_widget(self.eniraĵo)
        krado.add_widget(vidrulejo)

        btn_krado1 = KadroAranĝo(size_hint=(1,0.04), spacing=5)
        btn_test = Butono(text="🎵 Testo", font_size='16sp', background_normal='', background_color=[0.1,0.5,0.1,1])
        btn_test.bind(on_press=self.test_tone)
        btn_krado1.add_widget(btn_test)
        btn_legado = Butono(text="🔊 Legi", font_size='16sp', background_normal='', background_color=[0.1,0.3,0.7,1])
        btn_legado.bind(on_press=self.legado)
        btn_krado1.add_widget(btn_legado)
        krado.add_widget(btn_krado1)

        btn_krado2 = KadroAranĝo(size_hint=(1,0.04), spacing=5)
        btn_ŝargi = Butono(text="📂 Malfermi", font_size='16sp', background_normal='', background_color=[0.6,0.3,0,1])
        btn_ŝargi.bind(on_press=self.ekran_elekti_dosieron)
        btn_krado2.add_widget(btn_ŝargi)
        btn_viŝi = Butono(text="🗑️ Viŝi", font_size='16sp', background_normal='', background_color=[0.6,0.1,0.1,1])
        btn_viŝi.bind(on_press=self.viŝi_tekston)
        btn_krado2.add_widget(btn_viŝi)
        btn_sku = Butono(text="🔀 Sku", font_size='14sp', background_normal='', background_color=[0.5,0.2,0.7,1])
        btn_sku.bind(on_press=lambda b: self.ŝalti_sku_detekton(not self.sku_aktivigita))
        btn_krado2.add_widget(btn_sku)
        krado.add_widget(btn_krado2)

        btn_reĝimo_krado = KadroAranĝo(size_hint=(1,0.04), spacing=5)
        btn_lernanto = Butono(text="📖 Lernanto", font_size='14sp', background_normal='', background_color=[0.2,0.6,0.2,1])
        btn_lernanto.bind(on_press=lambda b: self.ŝanĝi_uz_manieron("lernanto"))
        btn_reĝimo_krado.add_widget(btn_lernanto)
        btn_komencanto = Butono(text="🌱 Komencanto", font_size='14sp', background_normal='', background_color=[0.6,0.6,0.1,1])
        btn_komencanto.bind(on_press=lambda b: self.ŝanĝi_uz_manieron("komencanto"))
        btn_reĝimo_krado.add_widget(btn_komencanto)
        btn_uzanto = Butono(text="👤 Uzanto", font_size='14sp', background_normal='', background_color=[0.3,0.3,0.7,1])
        btn_uzanto.bind(on_press=lambda b: self.ŝanĝi_uz_manieron("uzanto"))
        btn_reĝimo_krado.add_widget(btn_uzanto)
        krado.add_widget(btn_reĝimo_krado)

        self.sku_status_Etikedo = Etikedo(text="[color=FF6666]Sku: ✗[/color]", markup=True, size_hint=(1,0.03), font_size='11sp')
        krado.add_widget(self.sku_status_Etikedo)
        self.dosiero_Etikedo = Etikedo(text="[i]Neniu dosiero[/i]", markup=True, size_hint=(1,0.03), font_size='12sp', color=[0.6,0.6,0.6,1])
        krado.add_widget(self.dosiero_Etikedo)
        self.paŭza_Etikedo = Etikedo(text="", markup=True, size_hint=(1,0.03), font_size='12sp')
        krado.add_widget(self.paŭza_Etikedo)
        #legend = Etikedo(text="⬜ malplena | 🟢 testa | 🔵 parolado | ▶️ ludanta", size_hint=(1,0.03), font_size='11sp', color=[0.6,0.6,0.6,1])
        #krado.add_widget(legend)

        Kronometro.schedule_interval(self.ludi_sekvan, 0.2)
        return krado

    def on_start(self):
        Window.bind(on_key_down=self._sur_klavo)

    def _sur_klavo(self, window, key, scancode, codepoint, modifier):
        if self._legado_aktiva and codepoint == ' ':
            if self.uz_maniero == "lernanto":
                self.paŭzita = not self.paŭzita
                if self.paŭzita:
                    self.paŭza_Etikedo.text = "[color=FFFF00]⏸ PAŬZITA (premu spac-klavon por rekomenci)[/color]"
                else:
                    self.paŭza_Etikedo.text = "[color=00FF00]▶ Legado rekomencita[/color]"
                    Kronometro.schedule_once(lambda dt: setattr(self.paŭza_Etikedo, 'text', ''), 2)
                return True
            else:
                if not self.paŭzita:
                    self.paŭzi_legadon()
                else:
                    self.rekomenci_legadon()
                return True
        return False

    def paŭzi_legadon(self):
        if self.paŭzita:
            return
        self.paŭzita = True
        if hasattr(self, 'current_sound') and self.current_sound:
            if self.current_sound.state == 'play':
                self.current_sound.stop()
        if hasattr(self, 'paŭza_Etikedo'):
            self.paŭza_Etikedo.text = "[color=FFFF00]⏸ PAŬZITA (premu spac-klavon por rekomenci)[/color]"
        print("⏸ Legado paŭzita")

    def rekomenci_legadon(self):
        if not self.paŭzita:
            return
        self.paŭzita = False
        if hasattr(self, 'paŭza_Etikedo'):
            self.paŭza_Etikedo.text = "[color=00FF00]▶ Legado rekomencita[/color]"
            Kronometro.schedule_once(lambda dt: setattr(self.paŭza_Etikedo, 'text', ''), 2)
        print("▶ Legado rekomencita")
        self.ludi_sekvan(0)

    def ŝanĝi_uz_manieron(self, nova_reĝimo):
        self.uz_maniero = nova_reĝimo
        self.parolilo.uz_maniero = nova_reĝimo
        self._finu_legadon()
        self.ringo.reset()
        print(f"🔄 Reĝimo ŝanĝita al: {nova_reĝimo}")

    def ekran_elekti_dosieron(self, btn):
        Krom_Kadro = DosierElektiloKrom_Kadro(self.ŝargi_dosieron)
        Krom_Kadro.open()

    def ŝargi_dosieron(self, dosierpath):
        try:
            print(f"📂 Ŝargas: {dosierpath}")
            teksto = ""
            if platformo == 'android' and str(dosierpath).startswith('content://'):
                pass
            else:
                with open(dosierpath, 'r', encoding='utf-8') as f:
                    teksto = f.read()
                    print("####", teksto)
            teksto = unicodedata.normalize('NFC', teksto)
            Kronometro.schedule_once(lambda dt: self._montri_tekston(teksto, dosierpath), 0)
        except Exception as e:
            print(f"❌ Eraro: {e}")
            Kronometro.schedule_once(lambda dt: self._montri_eraron(str(e)), 0)

    def _montri_tekston(self, teksto, dosierpath):
        teksto = unicodedata.normalize('NFC', teksto)
        self.eniraĵo.text = teksto
        dosiernomo = os.path.basename(dosierpath)
        self.dosiero_Etikedo.text = f"[b]{dosiernomo[:20]}[/b]"

    def _montri_eraron(self, eraro):
        kromkadro = Krom_Kadro(title='Eraro', content=Etikedo(text=f"{eraro[:100]}", text_size=(280,None)), size_hint=(0.8,0.3))
        kromkadro.open()

    def viŝi_tekston(self, btn):
        self.eniraĵo.text = ""
        self.dosiero_Etikedo.text = "[i]Neniu dosiero[/i]"
        if platformo == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                vibrator = autoclass('android.os.Vibrator')
                context = PythonActivity.mActivity
                vibrator = context.getSystemService(context.VIBRATOR_SERVICE)
                if vibrator:
                    vibrator.vibrate(30)
            except:
                pass

    def test_tone(self, btn):
        print("\n🔊 Testa tono")
        t = np.linspace(0, 0.3, int(SAMPLE_RATE * 0.3), False)
        tone = 0.8 * np.sin(2 * np.pi * 440 * t)
        fade = int(0.005 * SAMPLE_RATE)
        if len(tone) > 2*fade:
            tone[:fade] *= np.linspace(0,1,fade)
            tone[-fade:] *= np.linspace(1,0,fade)
        int16_tone = np.int16(tone * 32767)
        self.ringo.peti_ludon(int16_tone, is_parolado=False)

    def ŝalti_sku_detekton(self, aktivigi=True):
        if aktivigi and not self.sku_aktivigita:
            if not ACCEL_DISPONEBLA:
                print("⚠ Plyer ne disponebla - sku-detekto ne funkcios")
                self.sku_status_Etikedo.text = "[color=FF6666]Sku: ✗ (ne disponebla)[/color]"
                return
            self.sku_detektilo = AccelMezurilo(sojlo=0.3, callback=self._sku_callback)
            self.sku_aktivigita = True
            print("✅ Sku-detekto AKTIVIGITA - skuu por legi!")
            self.sku_status_Etikedo.text = "[color=00FF00]Sku: ✓ (sojlo=0.3)[/color]"
            if platformo == 'android':
                try:
                    vibrator.vibrate(50)
                except:
                    pass
        elif not aktivigi and self.sku_aktivigita:
            if self.sku_detektilo:
                self.sku_detektilo.haltigi()
            self.sku_aktivigita = False
            print("✅ Sku-detekto MALAKTIVIGITA")
            self.sku_status_Etikedo.text = "[color=FF6666]Sku: ✗[/color]"

    def _sku_callback(self, detektita):
        print(f"🎯 _sku_callback: detektita={detektita}")
        if detektita:
            print("🎯 SKU DETEKTITA - lanĉas legadon!")
            Kronometro.schedule_once(lambda dt: self.legado(None))
            if platformo == 'android':
                try:
                    vibrator.vibrate(100)
                except:
                    pass
        else:
            print("❌ Neniu gesto detektita")
            self.sku_status_Etikedo.text = "[color=FFFF00]Sku: ✗ (provu denove)[/color]"
            Kronometro.schedule_once(lambda dt: setattr(self.sku_status_Etikedo, 'text', "[color=00FF00]Sku: ✓ (sojlo=0.3)[/color]"), 2)

    def _ŝalti_butonojn(self, aktiva=True):
        for child in self.root.walk() if hasattr(self,'root') else []:
            if isinstance(child, Butono):
                child.disabled = not aktiva
        try:
            for child in self.root.walk():
                if isinstance(child, Butono) and "Legi" in child.text:
                    if aktiva:
                        child.background_color = [0.2,0.4,0.8,1]
                        child.text = "🔊 Legi"
                    else:
                        child.background_color = [0.5,0.5,0.5,1]
                        child.text = "⏳ Legas..."
                    break
        except:
            pass

    def ĉerpu_tekston(self):
        dosierujo = "legendaĵoj"
        dosieroj = glob.glob(os.path.join(dosierujo, "*"))
        dosieroj = [d for d in dosieroj if os.path.isfile(d)]
        if not dosieroj:
            return "", ""
        plej_maljuna = min(dosieroj, key=os.path.getmtime)
        _, dosiersufikso = os.path.splitext(plej_maljuna)
        tipo = dosiersufikso[1:] if dosiersufikso else ""
        with open(plej_maljuna, 'r', encoding='utf-8') as f:
            enhavo = f.read()
        if tipo == "html":
            doc = mal_htmlo(enhavo)
            enhavo = doc.summary()
            enhavo = trafilatura.extract(enhavo)
        os.remove(plej_maljuna)
        return enhavo, tipo

    def legado(self, btn):
        if self._legado_aktiva:
            print("⚠ Legado jam aktiva - ignoras peton")
            return
        text = self.eniraĵo.text.strip()
        if not text:
            if len(os.listdir("legendaĵoj")) != 0:
                text, tipo = self.ĉerpu_tekston()
            else:
                self.dosiero_Etikedo.text = "[color=FF6666]Enigu tekston unue![/color]"
                Kronometro.schedule_once(lambda dt: setattr(self.dosiero_Etikedo, 'text', "[i]Neniu dosiero[/i]"), 2)
                return

        if self.uz_maniero == "lernanto":
            try:
                kolora_teksto,text = self.parolilo.akiri_koloritan_tekston(text)
                print("text",text)
                print("kolora_teksto",kolora_teksto)
                popup_content = KadroAranĝo(orientation='vertical', spacing=10, padding=10)
                with popup_content.canvas.before:
                    Color(0.6,0.6,0.6,1) # iomete griza
                    rect = Rectangle(size=popup_content.size, pos=popup_content.pos)
                def update_rect(instance, value):
                    rect.size = instance.size
                    rect.pos = instance.pos
                popup_content.bind(pos=update_rect, size=update_rect)
                label = Etikedo(text=kolora_teksto, markup=True, font_size='25sp',
                                size_hint_y=None, text_size=(self.root.width-200, None),
                                color=[0,0,0,1])
                label.bind(texture_size=label.setter('size'))
                scroll = VidRulejo(size_hint=(1,1))
                scroll.add_widget(label)
                popup_content.add_widget(scroll)
                ferm_btn = Butono(text="Fermi", size_hint_y=0.1)
                ferm_btn.bind(on_press=lambda x: popup.dismiss())
                popup_content.add_widget(ferm_btn)
                popup = Krom_Kadro(title="Analizo de la teksto (Lernanto reĝimo)",
                                   content=popup_content, size_hint=(0.9,0.7), auto_dismiss=False)
                popup.open()
            except Exception as e:
                print(f"Eraro dum kreado de lernanta fenestro: {e}")

        self._legado_aktiva = True
        self.paŭzita = False
        if hasattr(self, 'paŭza_Etikedo'):
            self.paŭza_Etikedo.text = ""
        self._ŝalti_butonojn(False)

        if self.sku_aktivigita:
            self._sku_detekto_dum_legado = True
            self.ŝalti_sku_detekton(False)

        if hasattr(self, 'current_sound') and self.current_sound:
            if self.current_sound.state == 'play':
                self.current_sound.stop()
            try:
                self.current_sound.unload()
            except:
                pass
        self.ringo.reset()
        self.dosiero_Etikedo.text = "[b]Legas...[/b]"

        if self.uz_maniero == "lernanto":
            threading.Thread(target=self.parolilo.legi_lernanto_sinsekve, args=(text, self), daemon=True).start()
        else:
            threading.Thread(target=self._legi_en_fadeno, args=(text,), daemon=True).start()

    def _legi_en_fadeno(self, text):
        text = unicodedata.normalize('NFC', text)
        self.parolilo.legi_tekston(text)
        Kronometro.schedule_once(lambda dt: self._finu_legadon(), 0)

    def _finu_legadon(self):
        self._legado_aktiva = False
        self.paŭzita = False
        if hasattr(self, 'paŭza_Etikedo'):
            self.paŭza_Etikedo.text = ""
        Kronometro.schedule_once(lambda dt: self._ŝalti_butonojn(True), 0)
        if hasattr(self, '_sku_detekto_dum_legado') and self._sku_detekto_dum_legado:
            Kronometro.schedule_once(lambda dt: self.ŝalti_sku_detekton(True), 0.5)
            self._sku_detekto_dum_legado = False
        if self.dosiero_Etikedo.text == "[b]Legas...[/b]":
            self.dosiero_Etikedo.text = "[i]Finita[/i]"
            Kronometro.schedule_once(lambda dt: self._restarigi_dosiernomon(), 2)

    def _restarigi_dosiernomon(self):
        if hasattr(self, 'dosiero_Etikedo') and self.dosiero_Etikedo.text == "[i]Finita[/i]":
            self.dosiero_Etikedo.text = "[i]Neniu dosiero[/i]"

    def ludi_sekvan(self, dt):
        if self.paŭzita:
            return
        if hasattr(self, 'current_sound') and self.current_sound:
            if self.current_sound.state == 'play':
                return
            else:
                self.current_sound.unload()
                self.current_sound = None
        filename = self.ringo.sekva_por_ludi()
        if filename and os.path.exists(filename):
            try:
                self.current_sound = SonTraktilo.load(filename)
                if self.current_sound:
                    self.current_sound.bind(on_stop=self.sound_finished)
                    self.current_sound.play()
                    self.ringo._montri_staton()
                    print(f"🔊 LUDATA: {os.path.basename(filename)}")
            except Exception as e:
                print(f"⚠ Eraro ludante: {e}")
                self.ringo.marki_kiel_ludita()

    def sound_finished(self, sound):
        self.ringo.marki_kiel_ludita()
        if hasattr(self, 'current_sound') and self.current_sound:
            try:
                self.current_sound.unload()
            except:
                pass
        self.current_sound = None

    def on_pause(self):
        return True

    def on_stop(self):
        if hasattr(self, 'sku_detektilo') and self.sku_detektilo:
            self.sku_detektilo.haltigi()


#--------------------------------------------------

if __name__ == "__main__":
    print("="*70)
    print("RINGO-BUFFER (4 LOKOJ) kun SEMAFORO-SINKRONIGO + SKU-DETEKTO")
    print("="*70)
    print(f"✅ Platformo: {platformo}")
    print(f"✅ Pydroid 3: {PYDROID3}")
    print(f"✅ Plyer: {PLYER_DISPONEBLA}")
    print(f"✅ Akcelometro: {ACCEL_DISPONEBLA}")
    print("="*70)
    Esperanto_voĉigiloApp().run()