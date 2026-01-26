"""
Esperanta Parolsinteza Sistemo
Created on Sun Nov 30 13:35:14 2025

@author: clopeau 
Programo de legado kun morfologia analizo kaj parolsintezо
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import pickle
import soundfile as sf
import re

# === KONSTANTOJ ===
SAMPLA_RAPIDO = 32000
CELO_RMS = 0.08
SILENTO_KOMO = 0.6
SILENTO_PUNKTO = 1.0
SILENTO_CIFERO = 0.3
SILENTO_AKRONIMO = 0.3
PIKA_MAKS = 0.5
LAUXTECO_FAKTORO = 1.2

# === KONFIGURO ===
print("=" * 70)
print("ESPERANTA PAROLSINTEZA SISTEMO")
print("=" * 70)

def akiri_bulean_valoron(mesagxo="Enigu 'True' aŭ 'False': "):
    """Akiru bulea valoro de uzanto kun validigo"""
    while True:
        enigo = input(mesagxo).strip().lower()
        if enigo == 'true':
            return True
        elif enigo == 'false':
            return False
        elif enigo=="":
            return False
            print("Nevalida enigo. Bonvolu enigi 'True' aŭ 'False'.")

print("\nPOR TESTI PO-LITERA LEGADO:")
testo = akiri_bulean_valoron("Ĉu testi po-litera legadon? ")
print(f"Testo-reĝimo: {testo}")

print("\nPOR NORMALIGI FONEMOJN:")
normaligo = akiri_bulean_valoron("Ĉu normaligi fonemojn per SOX? ")

print("\nPOR PAROLI KUN FONTAJ REGISTRAĴOJ:")
fontaj_registraĵoj = akiri_bulean_valoron("Ĉu paroli kun fontaj fonemojn ? ")

# === DOSIEROJ ===
dosierujo = os.path.dirname(os.path.abspath(__file__)) + "/"
tekstodosiero = dosierujo + 'texte3.jsb'
vortarodosiero = dosierujo + '1.csv'
silaba_vortaro_dosiero = "/home/clopeau/lingvaprogramado/silaba_vortaro"
silabaro_dosiero = "/home/clopeau/lingvaprogramado/silabaro"
if fontaj_registraĵoj ==True:
    fonemujo = dosierujo + "fonemoj"
else:    
    fonemujo = dosierujo + "fonemojx"

# === VORTAROJ ===
konsonantoj = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 
               'r', 's', 't', 'v', 'z', 'ĉ', 'ĝ', 'ĥ', 'ĵ', 'ŝ', 'ŭ']

cifero = {
    "1": "unu", "2": "du", "3": "tri", "4": "kvar", "5": "kvin",
    "6": "ses", "7": "sep", "8": "ok", "9": "naŭ", "0": "nul",
    "(": "ekparentezo", ")": "finparentezo", "[": "ekkrampo", "]": "finkrampo",
    "{": "ekakolado", "}": "finakolado", ':': 'kolono', '+': 'plus',
    '-': 'minus', '*': 'oble', '/': 'one', '=': 'egalas', '€': "euro",
    ".": "punkto", "'": "apostrofo", "\"": "citilo"
}

grekaj_literoj = {
    'α': 'alfa', 'β': 'beta', 'γ': 'gamo', 'δ': 'delta', 'ε': 'epsilono',
    'ζ': 'zeto', 'η': 'eto', 'θ': 'teto', 'ι': 'joto', 'κ': 'kapa',
    'λ': 'lambda', 'μ': 'mu', 'ν': 'nu', 'ξ': 'ksi', 'ο': 'omikrono',
    'π': 'pi', 'ρ': 'ro', 'σ': 'sigma', 'τ': 'taŭ', 'υ': 'ipsilono',
    'φ': 'fi', 'χ': 'ĥi', 'ψ': 'psi', 'ω': 'omego'
}

# === NORMALIGO DE FONEMOJ ===
if normaligo:
    normalilo = "/home/clopeau/lingvaprogramado/SOX.sh"
    os.system(normalilo)
    print("Fonemoj normigitaj per SOX")

# === BAZAJ FUNKCIOJ ===

def legu(dosiernomo):
    """Legu dosieron sekure"""
    try:
        with open(dosiernomo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERARO: Dosiero ne trovita: {dosiernomo}")
        return ""
    except Exception as e:
        print(f"ERARO dum legado de {dosiernomo}: {e}")
        return ""

def ŝargi_vortaron(dosieronomo, formato='pickle'):
    """Ŝargu vortaron el dosiero"""
    try:
        if formato == 'pickle':
            with open(dosieronomo + '.pkl', 'rb') as f:
                vortaro = pickle.load(f)
        else:
            raise ValueError("Nur 'pickle' formato subtenata")
        
        print(f"✓ Vortaro ŝargita: {dosieronomo}.{formato}")
        return vortaro
    except Exception as e:
        print(f"✗ Eraro dum ŝargado de {dosieronomo}: {e}")
        return {}

def flatigi_liston(nesta_listo):
    """Rekursive flatigi nestan liston"""
    simpla_listo = []
    for elemento in nesta_listo:
        if isinstance(elemento, list):
            simpla_listo.extend(flatigi_liston(elemento))
        else:
            simpla_listo.append(elemento)
    return simpla_listo

def kombinu(x, y):
    """Kreu ĉiujn kombinaĵojn de du listoj"""
    return [v + w for v in x for w in y]

def nombru_silabojn(vorto):
    """Kalkulu nombron de silaboj (vokaloj)"""
    return sum(1 for v in vorto if v in "aeiou")

def akiru_kategoriojn(kategorio_kodo):
    """Trovu vortojn laŭ kategorio"""
    return [v for v in vortaro.keys() if vortaro[v] == kategorio_kodo]

# === MORFOLOGIA ANALIZO ===

def fortranĉu_finaĵon_detale(vorto, finaĵolisto):
    """Fortranĉu finaĵon kaj redonu ambaŭ partojn"""
    for finaĵo in finaĵolisto:
        if vorto.endswith(finaĵo):
            return (vorto[:-len(finaĵo)], finaĵo)
    return (vorto, "")

def aldonu_elementon(listo, elemento):
    """Aldonu elementon al listo (kreante novan)"""
    return listo + [elemento]

def algoritmo4(vorto):
    """Trovu ĉiujn eblajn radikkombinaĵojn per profund-unua serĉado"""
    trovitaj = []
    pritraktotaj = [([], vorto)]
    
    while pritraktotaj:
        faritaj, restantaj = pritraktotaj.pop()
        
        if restantaj in vortaro:
            trovitaj.append(aldonu_elementon(faritaj, restantaj))
            break
            
        for i in range(1, len(restantaj) - 1):
            if restantaj[:i] in vortaro:
                pritraktotaj.append((
                    aldonu_elementon(faritaj, restantaj[:i]), 
                    restantaj[i:]
                ))
                
    return trovitaj

def radikanalizo(vorto):
    """Ĉefa funkcio por analizi vorton en radikojn"""
    if vorto in senfinaĵaj:
        return ([vorto], "", "y")
    
    if nombru_silabojn(vorto) < 2:
        return ([vorto], "", "?")
    
    radiko, finaĵo = fortranĉu_finaĵon_detale(vorto, finaĵoj)
    finaĵokodo = "t" if finaĵo else ""
    
    if radiko in silab_memoro:
        return (radiko, finaĵo, "r" + finaĵokodo)
    
    if not radiko:
        return ([vorto], finaĵo, "?" + finaĵokodo)
    
    analizrezultoj = algoritmo4(radiko)
    
    if not analizrezultoj:
        return ([radiko], finaĵo, "?" + finaĵokodo)
    
    # Elektu plej mallongan kombinaĵon
    ordigitaj = sorted([(len(kombinaĵo), kombinaĵo) 
                       for kombinaĵo in analizrezultoj])
    
    _, plejbona = ordigitaj[-1]
    plejbona = flatigi_liston(plejbona)
    
    # Konstruu kategorian kodon
    kategoriokodo = "".join(vortaro.get(r, "?") for r in plejbona)
    kategoriokodo += finaĵokodo
    
    rezulto = plejbona + [finaĵo, kategoriokodo]
    return rezulto

# === AŬDIO-TRAKTADO ===

def _kalkuli_rms(data):
    """Kalkulu RMS (Root Mean Square)"""
    return np.sqrt(np.mean(data**2))

def ŝargi_kaj_normaligi_silabojn(dosierujo, celo_rms=CELO_RMS):
    """Ŝargu kaj normaligu aŭdio-silabojn"""
    silab_memoro = {}
    sampla_rapido = None
    
    if not os.path.isdir(dosierujo):
        raise FileNotFoundError(f"Dosierujo ne ekzistas: {dosierujo}")
    
    dosieroj = [d for d in os.listdir(dosierujo) if d.endswith(".wav")]
    print(f"\nŜargas {len(dosieroj)} fonemojn...")
    
    for i, dosiero in enumerate(dosieroj, 1):
        if i % 10 == 0:
            print(f"  Progreso: {i}/{len(dosieroj)}")
            
        silabo = dosiero[:-4]
        vojo = os.path.join(dosierujo, dosiero)
        
        try:
            data, sr = sf.read(vojo)
        except Exception:
            continue
            
        if data.size == 0:
            continue
            
        if sampla_rapido is None:
            sampla_rapido = sr
        elif sr != sampla_rapido:
            raise ValueError(f"Malkongrua sample rate en {dosiero}")
            
        # Konvertu al float32
        if np.issubdtype(data.dtype, np.integer):
            data = data.astype(np.float32) / np.iinfo(data.dtype).max
        else:
            data = data.astype(np.float32)

        # Forigu silenton
        data = data[np.abs(data) > 0.001]
        
        if len(data) == 0:
            continue
            
        # Normaligu RMS
        rms = _kalkuli_rms(data)
        if rms > 1e-8:
            data = data * (celo_rms / rms)
            
        # Evitu saturadon
        piko = np.max(np.abs(data))
        if piko > 0.6:
            data = data / piko * 0.5
            
        silab_memoro[silabo] = (sampla_rapido, data)
    
    print(f"✓ {len(silab_memoro)} fonemoj ŝargitaj")
    return silab_memoro

def varmigi_se_bezone():
    """Praŝargu sounddevice per mallonga silento"""
    sampla_rapido, _ = silab_memoro['e']
    silento = np.zeros(int(0.3 * sampla_rapido), dtype=np.float32)
    sd.play(silento, samplerate=sampla_rapido, blocking=False)
    sd.wait()

def aldoni_silenton(aŭdio_segmentoj, sampla_rapido, silento_daŭro=0.2):
    """Aldonu silenton al aŭdio-segmentoj"""
    if silento_daŭro > 0:
        silento_longeco = int(silento_daŭro * sampla_rapido)
        silento = np.zeros(silento_longeco, dtype=np.float32)
        aŭdio_segmentoj.append(silento)

# === KOMPLETIGO POR LEGADO ===

def kompletigo_por_legado(analizo):
    """Dismetu silabojn kaj preparu por ludado"""
    analizo = flatigi_liston(analizo)
    
    if not analizo:
        return [], analizo
    
    ĉiujsilaboj = []
    kategoriokodo = analizo[-1] if analizo else ""
    
    for i, elemento in enumerate(analizo[:-1]):
        if i >= len(kategoriokodo):
            break
            
        kategorio = kategoriokodo[i]
        silaboj = []
        
        # Kontrolu en silaba_vortaro
        if elemento in silaba_vortaro:
            silaboj = list(silaba_vortaro[elemento])
        elif elemento in silab_memoro:
            silaboj = [elemento]
        else:
            silaboj = [elemento]
        
        ĉiujsilaboj.extend(silaboj)
    
    return ĉiujsilaboj, analizo

# === LUDADO DE VORTOJ ===

def ludu_vorton_el_memoro(
    interpunkcio,
    silaboj,
    silab_memoro,
    aŭdio_segmentoj,
    laŭteco_faktoro=LAUXTECO_FAKTORO,
    pika_maks=PIKA_MAKS,
    fade_proporcio=0.30,
    fade_fino=0.30,
    silento_sojlo=0.005
):
    """Ludi vorton el memoro"""
    
    # Variablo por spuri citilojn
    global jamcitilo
    
    def ŝargu_sekure(ŝlosilo):
        """Sekura ŝargado de fonemoj"""
        global jamcitilo
        
        if ŝlosilo in silab_memoro:
            return silab_memoro[ŝlosilo]
        
        # Traktu specialajn signojn
        if ŝlosilo in cifero:
            if ŝlosilo == "-" and not nombroflago:
                ŝlosilo = "streketo"
            else:
                ŝlosilo = cifero.get(ŝlosilo, ŝlosilo)
        elif ŝlosilo in grekaj_literoj:
            ŝlosilo = grekaj_literoj[ŝlosilo]
        elif ŝlosilo in "\"\'":
            if ŝlosilo == "'":
                ŝlosilo = "apostrofo"
            else:
                if jamcitilo:
                    ŝlosilo = "fincitilo"
                    jamcitilo = False
                else:
                    ŝlosilo = "ekcitilo"
                    jamcitilo = True
        
        # Se ankoraŭ ne trovita, uzu defaŭlton
        if ŝlosilo in silab_memoro:
            return silab_memoro[ŝlosilo]
        elif ŝlosilo == " ":
            return (SAMPLA_RAPIDO, np.zeros(int(0.5 * SAMPLA_RAPIDO), dtype=np.float32))
        else:
            return silab_memoro.get('bof', (SAMPLA_RAPIDO, np.zeros(100, dtype=np.float32)))
    
    n = len(silaboj)
    lasta_silabo_i = n - 1
    antaŭlasta_silabo_i = n - 2 if n >= 2 else None
    
    for i, sil in enumerate(silaboj):
        segmentoj = []
        temp_sil = str(sil)
        
        while temp_sil:
            if testo:
                # Po-litera legado
                fono = temp_sil[0]
                _, fon_datumoj = ŝargu_sekure(fono)
                segmentoj.append(fon_datumoj)
                temp_sil = temp_sil[1:]
            else:
                # Inteligenta legado
                if sil in silab_memoro:
                    _, datumoj = ŝargu_sekure(sil)
                    segmentoj.append(datumoj)
                    break
                
                # Provu 3-literajn, 2-literajn, poste 1-literajn
                trovita = False
                for longeco in [3, 2, 1]:
                    if len(temp_sil) >= longeco and temp_sil[:longeco] in silab_memoro:
                        _, fon_datumoj = ŝargu_sekure(temp_sil[:longeco])
                        segmentoj.append(fon_datumoj)
                        temp_sil = temp_sil[longeco:]
                        trovita = True
                        break
                
                if not trovita:
                    fono = temp_sil[0]
                    _, fon_datumoj = ŝargu_sekure(fono)
                    segmentoj.append(fon_datumoj)
                    temp_sil = temp_sil[1:]
        
        # Procesu ĉiun segmenton
        for j, datumoj in enumerate(segmentoj):
            datumoj = np.atleast_1d(datumoj).astype(np.float32)
            
            # Plifortigo de antaŭlasta silabo
            if i == antaŭlasta_silabo_i:
                datumoj = datumoj * laŭteco_faktoro
            
            # Malfortigu lastan silabon
            elif i == lasta_silabo_i and j == len(segmentoj) - 1:
                # Forigu komencan silenton
                abs_datumoj = np.abs(datumoj)
                start_idxs = np.where(abs_datumoj > silento_sojlo)[0]
                start_trim = start_idxs[0] if len(start_idxs) > 0 else 0
                datumoj = datumoj[start_trim:]
                
                # Malfortigu
                datumoj = datumoj * 0.5
                
                # Fade-out
                if len(datumoj) > 10:
                    fade_len = max(1, int(len(datumoj) * fade_proporcio))
                    if fade_len < len(datumoj):
                        fade_kurbo = np.linspace(1.0, fade_fino, fade_len)
                        datumoj[-fade_len:] *= fade_kurbo
            
            # Evitu klipingon
            datumoj = np.clip(datumoj, -pika_maks, pika_maks)
            aŭdio_segmentoj.append(datumoj)

# === AKRONIMOJ ===

def akcepti_vorton(vorto):
    """Kontrolu ĉu vorto estas akronimo (ĉio majuskla)"""
    majuskloj = "ABCDEFGHIJKLMNOPQRSTUVWXYZĈĜĤĴŜŬ"
    ciferoj = "0123456789"
    apartigiloj = ".,-/* "
    
    # Forigu apartigilojn
    restanta = ''.join(ch for ch in vorto if ch not in apartigiloj)
    
    if not restanta:
        return False
    
    # Unua litero devas esti majuskla
    if restanta[0] not in majuskloj:
        return False
    
    # Ĉiuj literoj devas esti majusklaj aŭ ciferoj
    return all(ch in majuskloj or ch in ciferoj for ch in restanta)

# === NOMBROJ ===

def testo_traduko_nombro(vorto):
    """Testi ĉu vorto estas nombro"""
    if re.match(r"^[+-]?\d+[.,]?\d*$", vorto):
        return True, nombro_al_vortoj(vorto)
    return False, None

def nombro_al_vortoj(nombro_str):
    """Konvertu numeron al Esperantaj vortoj"""
    unuoj = ["", "unu", "du", "tri", "kvar", "kvin", "ses", "sep", "ok", "naŭ"]
    
    def konvertu_tri_ciferojn(n):
        """Konvertu 0-999 al vortoj"""
        if n == 0:
            return []
        
        partoj = []
        centoj = n // 100
        resto = n % 100
        
        if centoj > 0:
            partoj.append("cent" if centoj == 1 else unuoj[centoj] + " cent")
        
        if resto > 0:
            if resto < 10:
                partoj.append(unuoj[resto])
            elif resto == 10:
                partoj.append("dek")
            elif 11 <= resto <= 19:
                partoj.append("dek " + unuoj[resto - 10])
            else:
                dek = resto // 10
                unu = resto % 10
                partoj.append(unuoj[dek] + " dek")
                if unu > 0:
                    partoj.append(unuoj[unu])
        
        return partoj
    
    def entjero_al_vortoj(n_str, sufiksoj=True):
        """Konvertu entjeron al vortoj"""
        n_str = n_str.lstrip('0') or "0"
        
        if n_str == "0":
            return ["nul"]
        
        # Grupigi en triojn
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
            
            vortoj_partoj.extend(konvertu_tri_ciferojn(grupo_valoro))
            
            pozicio = len(grupetoj) - i - 1
            
            if sufiksoj:
                if pozicio == 1:
                    vortoj_partoj.append("mil")
                elif pozicio == 2:
                    vortoj_partoj.append("miliono" if grupo_valoro == 1 else "milionoj")
                elif pozicio == 3:
                    vortoj_partoj.append("miliardo" if grupo_valoro == 1 else "miliardoj")
        
        return vortoj_partoj
    
    # Traktu signon
    signo = []
    if nombro_str and nombro_str[0] in "+-/*=":
        signo = [cifero.get(nombro_str[0])]
        nombro_str = nombro_str[1:]
    
    # Anstataŭigu komon per punkto
    nombro_str = str(nombro_str).replace(',', '.')
    
    # Dividu je dekuma punkto
    partoj = nombro_str.split('.')
    
    tuta_parto = partoj[0] if partoj else "0"
    dekuma_parto = partoj[1] if len(partoj) > 1 else ""
    
    # Konvertu tutan parton
    tuta_vortoj = entjero_al_vortoj(tuta_parto, sufiksoj=True)
    
    # Konvertu dekuman parton
    if dekuma_parto and int(dekuma_parto.ljust(len(dekuma_parto), '0')) > 0:
        dekuma_parto = dekuma_parto.lstrip('0') or "0"
        dekuma_vortoj = ["komo"] + entjero_al_vortoj(dekuma_parto, sufiksoj=False)
    else:
        dekuma_vortoj = []
    
    rezulto_listo = signo + tuta_vortoj + dekuma_vortoj
    return " ".join(rezulto_listo)

def disigu_interpunkcion(vorto):
    """Disigu vortojn kaj interpunkciojn"""
    return re.findall(r'\w+|[€,!?;\.]', vorto)

# === ĈEFA PROGRAMO ===

def main():
    """Ĉefa funkcio"""
    global vortaro, senfinaĵaj, finaĵoj, silab_memoro, silaba_vortaro, silabaro
    global jamcitilo, nombroflago
    
    jamcitilo = False
    nombroflago = False
    
    print("\n" + "=" * 70)
    print("ŜARGAS VORTAROJN...")
    print("=" * 70)
    
    # Ŝargu vortaron
    vortarolinioj = legu(vortarodosiero).lower().split("\n")
    vortaro = {}
    for linio in vortarolinioj:
        if linio:
            partoj = linio.split(",")
            if len(partoj) >= 2:
                vortaro[partoj[0]] = partoj[1]
    
    print(f"✓ Morfema vortaro: {len(vortaro)} morfemoj")
    
    # Difinu kategoriojn
    senfinaĵaj = akiru_kategoriojn("z") + akiru_kategoriojn("n") + akiru_kategoriojn("x")
    senfinaĵaj += kombinu(akiru_kategoriojn("q") + akiru_kategoriojn("u"), ["", "n"])
    senfinaĵaj += kombinu(akiru_kategoriojn("v"), ["", "n", "j", "jn"])
    
    finaĵoj = [f for f in akiru_kategoriojn("t") if f not in ['j', 'n']]
    finaĵoj += kombinu(["o", "a"], ["n", "j", "jn"])
    finaĵoj.append("en")
    
    print(f"✓ Senfinaĵaj vortoj: {len(senfinaĵaj)}")
    print(f"✓ Finaĵoj: {len(finaĵoj)}")
    
    # Ŝargu silabajn vortarojn
    silaba_vortaro = ŝargi_vortaron(silaba_vortaro_dosiero, formato="pickle")
    silabaro = ŝargi_vortaron(silabaro_dosiero, formato="pickle")
    
    # Ŝargu fonemojn
    silab_memoro = ŝargi_kaj_normaligi_silabojn(fonemujo, celo_rms=CELO_RMS)
    
    if not silab_memoro:
        print("✗ ERARO: Neniuj fonemoj ŝargitaj!")
        return
    
    # Varmigu aŭdiosistemon
    print("\nVarmigas aŭdiosistemon...")
    varmigi_se_bezone()
    
    # Legu tekston
    print("\n" + "=" * 70)
    print("LEGAS TEKSTON...")
    print("=" * 70)
    
    #teksto = legu(tekstodosiero).lower()
    teksto="mi salutas novan version far Claude. en la jaro 2026 kun ekstera 'temperaturo' je 7,5 gradoj en LIS skalo "
    #teksto='cla.  2024 '
    if not teksto:
        print("✗ ERARO: Teksto malplena!")
        return
    print(teksto)
    # Preparu vortojn
    parts = re.split(r"([\"', ])", teksto)
    vortoj = [part for part in parts if part and not part.isspace()]
    
    print(f"✓ Teksto: {len(vortoj)} eroj")
    print(f"\nLeganta: {' '.join(vortoj[:10])}...")
    
    # === LEGADO ===
    print("\n" + "=" * 70)
    print("KOMENCAS LEGADON...")
    print("=" * 70 + "\n")
    
    aŭdio_segmentoj = []
    interpunkcio = " "
    i = 0
    
    while i < len(vortoj):
        vorto = vortoj[i]
        
        # Detektu tipon de vorto
        akronimoflago = akcepti_vorton(vorto)
        nombroflago, tradukitanombro = testo_traduko_nombro(vorto)
        
        # === TRAKTU AKRONIMOJN ===
        if akronimoflago:
            print(f"  Akronimo: {vorto}")
            vorto = re.sub('[.'',''/]', "", vorto)
            akronimo = [ch.lower() for ch in vorto]
            
            # Aldonu 'o' al konsonantoj
            akronimo = [ch + "o" if ch in konsonantoj else ch for ch in akronimo]
            
            for litero in akronimo:
                analizo = radikanalizo(litero)
                analizo = flatigi_liston(analizo)
                silaboj, _ = kompletigo_por_legado(analizo)
                ludu_vorton_el_memoro(interpunkcio, silaboj, silab_memoro, aŭdio_segmentoj)
                aldoni_silenton(aŭdio_segmentoj, SAMPLA_RAPIDO, SILENTO_AKRONIMO)
    
    # === TRAKTU NOMBROJN ===
        elif nombroflago:
            print(f"  Nombro: {vorto} → {tradukitanombro}")
        
        # Kontrolu por dekuma komo
            if i + 1 < len(vortoj) and vortoj[i + 1] == ',':
                sekvanta_flago, sekvanta_nombro = testo_traduko_nombro(vortoj[i + 2] if i + 2 < len(vortoj) else "")
                if sekvanta_flago:
                    tradukitanombro = tradukitanombro + " komo " + sekvanta_nombro
                    i += 2
            
            print(vortoj[i],tradukitanombro)
            nombro_grupoj = tradukitanombro.split()
            
            for vorto_parto in nombro_grupoj:
                if vorto_parto in silab_memoro:
                    silaboj = [vorto_parto]
                else:
                    analizo = radikanalizo(vorto_parto)
                    analizo = flatigi_liston(analizo)
                    silaboj, _ = kompletigo_por_legado(analizo)
                
                ludu_vorton_el_memoro(interpunkcio, silaboj, silab_memoro, aŭdio_segmentoj)
                
                if vorto_parto in ["dek", "cent", "mil", "miliono", "milionoj", "miliardo", "miliardoj"]:
                    aldoni_silenton(aŭdio_segmentoj, SAMPLA_RAPIDO, SILENTO_CIFERO)
        
        # === TRAKTU NORMALAJN VORTOJN ===
        else:
            vorto = vorto.lower()
            print("VORTO ", vorto)
            # Disigu interpunkcion
            if len(vorto) > 1:
                vorto_partoj = disigu_interpunkcion(vorto)
                if vorto_partoj and vorto_partoj[-1] in ".!?":
                    interpunkcio = vorto_partoj[-1]
                    vorto = "".join(vorto_partoj[:-1])
                else:
                    interpunkcio = " "
                    vorto = "".join(vorto_partoj)
            
            # Traktu komon/punktokomon
            if vorto in [",", ";"]:
                aldoni_silenton(aŭdio_segmentoj, SAMPLA_RAPIDO, SILENTO_KOMO)
            elif vorto:
                print(f"  Vorto: {vorto}")
                
                if vorto in silab_memoro:
                    silaboj = [vorto]
                else:
                    analizo = radikanalizo(vorto)
                    analizo = flatigi_liston(analizo)
                    silaboj, _ = kompletigo_por_legado(analizo)
                
                ludu_vorton_el_memoro(interpunkcio, silaboj, silab_memoro, aŭdio_segmentoj)
        
        # Ludu frazon se punkto aŭ fino
        if interpunkcio in ".!?" or i == len(vortoj) - 1:
            if aŭdio_segmentoj:
                print(f"\n  ► Ludas frazon ({len(aŭdio_segmentoj)} segmentoj)...\n")
                tuto = np.concatenate(aŭdio_segmentoj)
                sd.play(tuto, samplerate=SAMPLA_RAPIDO)
                sd.wait()
                aŭdio_segmentoj = []
                aldoni_silenton(aŭdio_segmentoj, SAMPLA_RAPIDO, SILENTO_PUNKTO)
                interpunkcio = " "
    
        i += 1

print("\n" + "=" * 70)
print("LEGADO FINITA!")
print("=" * 70)
name='main'
if name == "main":
    main()
    # try:
    #     main()
    # except KeyboardInterrupt:
    #     print("\n\n✗ Interrompita de uzanto")
    # except Exception as e:
    #     print(f"\n\n✗ ERARO: {e}")
    # import traceback
    # traceback.print_exc()