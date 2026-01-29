# -*- coding: utf-8 -*-
"""
Created on Sun Nov 30 13:35:14 2025

@author: clopeau 
programo de legado
se  morfemo ne konita en 1.CSV   ĝi eldiras "ĉu" (eble ne plu)
se silabo ne estas jam registrita  ĝi dira 'bof'  (eble ne plu)

traktas ciferoj  êc komplikaj   (12.5-10)*8=toto
traktas citiloj
traktas akronimoj  ĝi aldona ^psy konsonantoj "o" por eldiri akronimojn
post traktado de '-' muns en nombro_zono revenas al sekreto en telsta zono

havas plurajn opciojn komence

oni povas plie ĝustigi temp variabloj per mane

"""
#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import os
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from scipy.fft import fft, ifft
from scipy.signal import butter, filtfilt,lfilter,firwin2
import pickle
import soundfile as sf
import time
import re
import librosa
# === KONFIGURO DE DOSIEROJ ===
"""
Simpla GUI-interfaco por la Esperanta legilo.
Uzas tkinter (inkluzivita en Python).
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
from konfiguro import KONFIGURO

class LegiloGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Esperanta Legilo")
        self.root.geometry("800x600")
        
        # Krei GUI-elementojn
        self.krei_interfacon()
        
    def krei_interfacon(self):
        # Ĉefa kadro
        ĉefa_kadro = ttk.Frame(self.root, padding=10)
        ĉefa_kadro.pack(fill=tk.BOTH, expand=True)
        
        # Teksta enigaĵo
        ttk.Label(ĉefa_kadro, text="Teksto por legi:").pack(anchor=tk.W)
        self.teksta_ingo = scrolledtext.ScrolledText(ĉefa_kadro, height=10, wrap=tk.WORD)
        self.teksta_ingo.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Butonpanelo
        buton_kadro = ttk.Frame(ĉefa_kadro)
        buton_kadro.pack(fill=tk.X, pady=5)
        
        ttk.Button(buton_kadro, text="Legi", command=self.legi).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_kadro, text="Malplenigi", command=self.malplenigi).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_kadro, text="Ŝargi dosieron", command=self.ŝargi_dosieron).pack(side=tk.LEFT, padx=5)
        ttk.Button(buton_kadro, text="Agordoj", command=self.montri_agordojn).pack(side=tk.RIGHT, padx=5)
        
        # Statusa strio
        self.statuso = tk.StringVar(value="Preta")
        ttk.Label(ĉefa_kadro, textvariable=self.statuso, relief=tk.SUNKEN).pack(fill=tk.X, pady=(10, 0))
    
    def legi(self):
        teksto = self.teksta_ingo.get("1.0", tk.END).strip()
        if not teksto:
            messagebox.showwarning("Averto", "Bonvolu enigi tekston por legi.")
            return
        
        self.statuso.set("Leganta...")
        self.root.update()
        
        #Ruli en fadeno por ne bloki la GUI
        def fono_legado():
            try:
                legi_tekston(teksto)
                self.statuso.set("Preta")
            except Exception as e:
                self.statuso.set(f"Eraro: {str(e)}")
        
        threading.Thread(target=fono_legado, daemon=True).start()
    
    def malplenigi(self):
        self.teksta_ingo.delete("1.0", tk.END)
    
    def ŝargi_dosieron(self):
        dosiero = filedialog.askopenfilename(
            title="Elekti tekstan dosieron",
            filetypes=[("Tekstaj dosieroj", "*.txt *.jsb"), ("Ĉiuj dosieroj", "*.*")]
        )
        if dosiero:
            try:
                with open(dosiero, 'r', encoding='utf-8') as f:
                    enhavo = f.read()
                self.teksta_ingo.delete("1.0", tk.END)
                self.teksta_ingo.insert("1.0", enhavo)
            except Exception as e:
                messagebox.showerror("Eraro", f"Ne povis ŝargi dosieron: {e}")
    
    def montri_agordojn(self):
        agord_fenestro = tk.Toplevel(self.root)
        agord_fenestro.title("Agordoj")
        agord_fenestro.geometry("400x500")
        
        kadro = ttk.Frame(agord_fenestro, padding=10)
        kadro.pack(fill=tk.BOTH, expand=True)
        
        # Reĝimoj
        ttk.Label(kadro, text="Reĝimoj:").pack(anchor=tk.W, pady=(10, 5))
        self.testo_var = tk.BooleanVar(value=KONFIGURO.get('testo_po_litera'))
        ttk.Checkbutton(kadro, text="Po-litera testreĝimo", variable=self.testo_var,
                       command=self.ĝisdatigi_agordojn).pack(anchor=tk.W)
        
        self.fontaj_var = tk.BooleanVar(value=KONFIGURO.get('uzi_fontajn'))
        ttk.Checkbutton(kadro, text="Uzi fontajn fonemojn (ne normaligitajn)", 
                       variable=self.fontaj_var, command=self.ĝisdatigi_agordojn).pack(anchor=tk.W)
        
        self.registri_var = tk.BooleanVar(value=KONFIGURO.get('registri_finan_rezulton'))
        ttk.Checkbutton(kadro, text="Registri finan rezulton", variable=self.registri_var,
                       command=self.ĝisdatigi_agordojn).pack(anchor=tk.W)
        
        self.normaligisilaboj_var = tk.BooleanVar(value=KONFIGURO.get('normaligisilaboj'))
        ttk.Checkbutton(kadro, text="re-normalgi silaboj post novaj registroj", variable=self.normaligisilaboj_var,
                       command=self.ĝisdatigi_agordojn).pack(anchor=tk.W)
        # Aŭdi-parametroj
        ttk.Label(kadro, text="Aŭdi-parametroj:").pack(anchor=tk.W, pady=(15, 5))
        
        # Korektita buklo kun ĝusta variablo-nomo kaj lambda-kaptado
        parametroj = [
            ("Laŭteco-faktoro", "laŭteco_faktoro", 0.5, 2.0),
            ("Pika maksimumo", "pika_maks", 0.3, 1.0),
            ("Malfortigo de lasta silabo", "lasta_malplifortigo", 0.5, 1.0)
        ]
        
        for etikedo, ŝlosilo, minv, maxv in parametroj:
            ttk.Label(kadro, text=etikedo).pack(anchor=tk.W)
            skalo = ttk.Scale(
                kadro, 
                from_=minv, 
                to=maxv, 
                orient=tk.HORIZONTAL,
                length=300,
                command=lambda v, k=ŝlosilo: self.ŝanĝi_parametron(k, v)
            )
            # Uzi la ĝustan ŝlosilon por akiri la valoron el KONFIGURO
            skalo.set(KONFIGURO[ŝlosilo])
            skalo.pack(pady=2)
        
        ttk.Button(agord_fenestro, text="Fermi", command=agord_fenestro.destroy).pack(pady=10)
    
    def ŝanĝi_parametron(self, ŝlosilo, valoro):
        """Ŝanĝi numeran parametron en KONFIGURO."""
        KONFIGURO[ŝlosilo] = float(valoro)
    
    def ĝisdatigi_agordojn(self):
        """Ĝisdatigi buleajn parametrojn en KONFIGURO."""
        KONFIGURO['testo_po_litera'] = not self.testo_var.get()
        KONFIGURO['uzi_fontajn'] = not self.fontaj_var.get()
        KONFIGURO['registri_finan_rezulton'] = not self.registri_var.get()
        KONFIGURO['normaligisilaboj']=not self.normaligisilaboj_var.get()
    def elŝuti_agordojn(self):
        pass  # Eble aldoni konservadon en estonteco

def lanĉi_gui():
    root = tk.Tk()
    app = LegiloGUI(root)
    root.mainloop()


# 



def legi_tekston(teksto):
    
    global jamcitilo,finpunkto,last_nombroflago,neciferaj,nombroflago
    print ("Valoru  mane  dauro de silentoj")
    silento_komo = 0.7
    silento_punkto = 2
    silento_cifero= 0.3
    silento_akronimo=0.3
    jamcitilo=False
    finpunkto=False
    last_nombroflago=False
    neciferaj=0
    
    
    global mankantaj
    mankantaj=""
  
    #
    dosierujo = os.path.dirname(os.path.abspath(__file__))+"/"
    #dosierujo = ''  # Dosieruja vojo
    #tekstodosiero =  KONFIGURO.get(dosierujo+'tekstodosiero') #dosierujo + 'texte3.jsb'
    vortarodosiero = KONFIGURO.get("vortarodosiero")   #dosierujo + '1.csv'
    print("****************vortarodosiero*************************")
    #eligodosiero = KONFIGURO.get("avirer.jsb")
    silaba_vortaro_dosiero =KONFIGURO.get("silaba_vortaro_dosiero")
    silabaro_dosiero = KONFIGURO.get("silabaro_dosiero")
    eliga_dosiero = KONFIGURO.get("eliga_dosiero")

    # permesatajopoj=['sk','fr','str', 'ŝtr', 'dr', 'dv', 'st', 'ŝt', 'tr', 'pr','ps','pl','spl','lpt','bl','br','skr','gl','kr','fl','ft','gr','gv','kl','kn','kv','sc','skl','skv','ŝl','sl','ŝm','sm','ŝn','sp','ŝp','spr','ŝpr','ŝr','sv','ŝv','sk','vr']
    konsonantoj = [
        'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'z',
        'ĉ', 'ĝ', 'ĥ', 'ĵ', 'ŝ', 'ŭ']  

    cifero={"1":"unu","2":"du","3":"tri","4"
    :"kvar","5":"kvin","6":"ses","7":"sep","8":"ok","9":"naŭ","0":"nul","(":"ekparentezo",")":"finparentezo","[":"ekkrampo","]":"finkrampo","{":"ekakolado","}":"finakolado",':':'kolono','+':'plus','-':'minus','*':'oble','/':'one','\n':'subenoblikvo','-':'minus','=':'egalas','€':"euro",".":"punkto","'":"aspostrofo","\"":"citilo" }
    grekaj_literoj = {
        'α': 'alfa',
        'β': 'beta',
        'γ': 'gamo',
        'δ': 'delta',
        'ε': 'epsilono',
        'ζ': 'zeto',
        'η': 'eto',
        'θ': 'teto',
        'ι': 'joto',
        'κ': 'kapa',
        'λ': 'lambda',
        'μ': 'mu',
        'ν': 'nu',
        'ξ': 'ksi',
        'ο': 'omikrono',
        'π': 'pi',
        'ρ': 'ro',
        'σ': 'sigma',
        'τ': 'taŭ',
        'υ': 'ipsilono',
        'φ': 'fi',
        'χ': 'ĥi',
        'ψ': 'psi',
        'ω': 'omego'
    }
    #### nomaligo de fonemoj  ->  fonemojx   per bash SOX.sh

    if KONFIGURO.get('normaligisilaboj')==True :
            
        normalilo = "/home/clopeau/lingvaprogramado/SOX.sh"
        eliga_averto = os.system(normalilo)
        print(eliga_averto)



    def ŝargi_vortaron(dosieronomo, formato='pickle'):
        """
        Ŝargas vortaron el dosiero.
        
        Parametroj:
        dosiernomo (str): Nomo de la dosiero (sen etendo)
        formato (str): 'json' aŭ 'pickle' - formato de la dosiero
        
        Revenas:
        dict: La ŝargita vortaro
        """
        try:
            if formato == 'json':
                with open(dosieronomo , 'r', encoding='utf-8') as f:
                    vortaro = json.load(f)
            elif formato == 'pickle':
                print("vortaro //////", dosieronomo)
                with open(dosieronomo , 'rb') as f:
                    vortaro = pickle.load(f)
                    #print(vortaro)
            else:
                raise ValueError("Formato devas esti 'json' aŭ 'pickle'")
            
            print(f"Vortaro sukcese ŝargita el {dosieronomo}")
            return vortaro
        except Exception as e:
            print(f"Eraro dum ŝargado: {e}")
            return {}


    # === UTILAJ FUNKCIOJ ===

    def legu(dosiernomo):
        """Legu la enhavon de dosiero"""
        print(dosiernomo)
        enigo = open(dosiernomo, 'r')
        enhavo = enigo.read()
        enigo.close()
        return enhavo

    # savo de sonigaĵojn


    def skribu(dosiernomo, enhavo):
        """Skribu enhavon al dosiero"""
        print (dosiernomo)
        elig = open(dosiernomo, 'w')
        elig.write(enhavo)
        elig.close()

    def kio_estas(x):
        """Montru tipon, longon kaj reprezenton de variablo (por sencimigo)"""
        print("$", type(x), len(x), repr(x))

    def kombinu(x, y):
        """Kreu ĉiujn kombinaĵojn de elementoj el du listoj"""
        return [v + w for v in x for w in y]

    def nombru_silabojn(vorto):
        """Kalkulu nombron de silaboj (vokaloj) en vorto"""
        return sum([v in "aeiou" for v in vorto])

    def fortranĉu_finon(vorto, finaĵo):
        """Fortranĉu finaĵon se ĝi ekzistas"""
        return vorto[:len(vorto)-len(finaĵo)*(vorto[-len(finaĵo):] == finaĵo)]

    def fortranĉu_komencon(vorto, komenco):
        """Fortranĉu komencon se ĝi ekzistas"""
        return vorto[len(komenco)*(vorto[:len(komenco)] == komenco):]

    def fortranĉu_finaĵon(vorto, finaĵolisto):
        """Fortranĉu unu el eblaj finaĵoj"""
        for finaĵo in finaĵolisto:
            if vorto[-len(finaĵo):] == finaĵo:
                return vorto[:-len(finaĵo)]
        return vorto

    def fortranĉu_finaĵon_detale(vorto, finaĵolisto):
        """Fortranĉu finaĵon kaj redonu ambaŭ partojn"""
        for finaĵo in finaĵolisto:
            if vorto[-len(finaĵo):] == finaĵo:
                return (vorto[:-len(finaĵo)], finaĵo)
        return (vorto, "")

    def fortranĉu_komencon_listo(vorto, komencolisto):
        """Fortranĉu unu el eblaj komencoj"""
        for komenco in komencolisto:
            if vorto[:len(komenco)] == komenco:
                return vorto[len(komenco):]
        return vorto

    def akiru_kategoriojn(vorto):
        """Trovu ĉiujn kategoriojn por vorto en vortaro"""
        return [v for v in vortaro.keys() if vortaro[v][0] in vorto]

    def akiru_kategoriojn_silabajn(kategorio, silabnombro):
        """Trovu vortojn en specifa kategorio kun specifa nombro de silaboj"""
        return [v for v in vortaro.keys()
                if vortaro[v][0] == kategorio and nombru_silabojn(v) == silabnombro]

    def helpaj_vortoj():
        """Trovu ĉiujn helpajn vortojn (finaĵo 'aŭ')"""
        u = akiru_kategoriojn("x")
        v = 'aŭ'
        return [w for w in u if v == w[-2:]]

    def dividu(vorto):
        """Dividu vorton en eblajn radikojn"""
        return [(vorto[:j], vorto[j:]) for j in range(2, len(vorto))
                if vortaro.has_key(vorto[:j])]  # Ekskluzivas finaĵojn

    def ĉiuj_kombinaĵoj(x, y):
        """Kreu ĉiujn kombinaĵojn de listo kun alia listo"""
        return [x[:-1] + [v] for v in y]

    def nivelo(x):
        """Trovu maksimuman nivelon de vortolisto"""
        return max([int(vortaro[v][1]) for v in x])

    def kategorioj():
        """Montru ĉiujn ekzistantajn kategoriojn"""
        s = set([v[0] for v in vortaro.values()])
        return "".join(list(s))

    def silaboj(n):
        """Trovu ĉiujn vortojn kun n silaboj"""
        return [v for v in vortaro.keys() if nombru_silabojn(v) == n]

    # === SPECIALAJ KARAKTEROJ POR ORDIGADO ===
    ĉapelkarakteroj = {
        "ĉ": "c|", "ĝ": "g|", "ĥ": "h|", 
        "ĵ": "j|", "ŝ": "s|", "ŭ": "u|"
    }

    def esperanta_klavo(x):
        """Konvertu Esperantajn literojn por ĝusta ordigo"""
        return "".join([ĉapelkarakteroj.get(v, v) for v in x])

    def nombru_diferencojn(x, y):
        """Kalkulu nombron de malsamaj karakteroj inter du vortoj"""
        return sum([x[i] != y[i] for i in range(min(len(x), len(y)))])

    def minimumaj_paroj(x):
        """Trovu minimumajn parojn (vortojn kiuj diferencas per unu litero)"""
        w = [v for v in vortaro.keys() if len(v) == len(x)]
        u = [v for v in w if 1 == nombru_diferencojn(v, x)]
        return u

    def utilaj_paroj(litero):
        """Montru utilajn minimumajn parojn por donita litero"""
        for v in vortaro.keys():
            if litero in v:
                w = minimumaj_paroj(v)
                print("==>", v)
                for vv in w:
                    if litero not in vv:
                        print(vv)

    # === ĈEFA PROGRAMO ===
    def radikanalizo(vorto):
        """
        Ĉefa funkcio por analizi vorton en radikojn
        Redonas: (radiklisto, finaĵo, kodo)
        """
        if vorto in senfinaĵaj:
            return ([vorto], "", "y")  # 'y' por senfinaĵaj vortoj
        
        elif nombru_silabojn(vorto) < 2:
            print ("kazo ?  1")
            
            return ([vorto], "", "?")  # '?' por unu-silabaj vortoj
        
        else:  # Du aŭ pli da silaboj
            (radiko, finaĵo) = fortranĉu_finaĵon_detale(vorto, finaĵoj)
            finaĵokodo = (len(finaĵo) != 0) * "t"
            print("radiko ",radiko)
            if radiko in silab_memoro :  # antaue vortaro:
               print("trovita rekte ") 
               return (radiko, finaĵo, "r" + finaĵokodo)
            if len(radiko) > 0:
                analizrezultoj = algoritmo4(radiko)            
                if len(analizrezultoj) == 0:
                    print ("kazo ?  2")
                    return ([radiko], finaĵo, "?" + finaĵokodo)
                
                # Ordigi laŭ longo (pli mallongaj kombinaĵoj estas preferataj)
                print("analizrezultoj ",analizrezultoj)
                ordigitaj = sorted([(len(kombinaĵo), kombinaĵo) 
                                   for kombinaĵo in analizrezultoj])
                print("ordigitaj   ",ordigitaj)
                
                i=0
                kategoriokodo=[]
                plejbona=[]
                ordigitaj=ordigitaj[-1]
                j= ordigitaj[0]
                ordigitaj=ordigitaj[1]
                print ("reduktita ordigita  ",i, ordigitaj)
                ordigitaj=flatigi_liston(ordigitaj)
                kategoriokodo=""
                for i in range(j):
                    kategoriokodo = kategoriokodo+vortaro.get(ordigitaj[i])
                print (ordigitaj,kategoriokodo)
                i=0                       
                print(type(ordigitaj))
                ordigitaj.append(finaĵo)
                print("JEN1", ordigitaj)
                print(kategoriokodo, finaĵo)
                kategoriokodo=kategoriokodo+finaĵokodo
                ordigitaj.append(kategoriokodo)
                print("JEN2", ordigitaj)  
                    
                #kategoriokodo = "".join([vortaro[radiko][0] for radiko in plejbona])
                print("kazo 2")
                return (ordigitaj)#, finaĵo, kategoriokodo + finaĵokodo)
            else:
                print ("kazo ?  3")
                return ([vorto], finaĵo, "?" + finaĵokodo)

    def aldonu_elementon(listo, elemento):
        """Aldonu elementon al listo (kreante novan liston)"""
        nova_listo = listo[:]
        nova_listo.append(elemento)
        return nova_listo

    def algoritmo4(vorto):
        """
        Algoritmo por trovi ĉiujn eblajn radikkombinaĵojn
        Uzas profund-unuan serĉadon
        """
        #print(vortaro)
        trovitaj = []
        pritraktotaj = [([], vorto)]  # (jam faritaj, restantaj)
        
        while len(pritraktotaj) > 0:
            #print("pritraktoaj   ",pritraktotaj)
            (faritaj, restantaj) = pritraktotaj.pop()
            #print(restantaj)
            if restantaj in vortaro:
                #print(silaba_vortaro.get(restantaj))
                trovitaj.append(aldonu_elementon(faritaj, restantaj))
                #print("trovitaj * ",trovitaj)
                pritraktotaj=trovitaj  
                break
            # Provu ĉiujn eblajn dividojn
            for i in range(1, len(restantaj) - 1):  # por akcepti finaĵon en komenco
                print("restantaj ",restantaj[:i])
                if restantaj[:i] in vortaro:
                    pritraktotaj.append((aldonu_elementon(faritaj, restantaj[:i]), restantaj[i:]))                
                #print("pritraktotaj eble nur vortara ",pritraktotaj)
        return pritraktotaj  #trovitaj


    # === STATISTIKAJ FUNKCIOJ ===

    def regulo(vorto):
        """Ricevu la kodon de vorto"""
        return radikanalizo(vorto)[2]

    def statistikoj():
        """Kalkulu kaj montru statistikojn pri vortanalizoj"""
        statistikoj_dict = {}
        
        for vorto in vortoj:
            kodo = regulo(vorto)
            statistikoj_dict[kodo] = statistikoj_dict.get(kodo, 0) + 1
        
        histogramo = [(frekvenco, kodo) for kodo, frekvenco in statistikoj_dict.items()]
        
        for (frekvenco, kodo) in sorted(histogramo, key=lambda x: x[1]):
            procento = (100.0 * frekvenco) / len(vortoj)
            print(kodo, frekvenco, "%.2f" % procento)

    def esceptoj():
        """Trovu kaj montru ĉiujn vortojn kiuj ne povis esti analizitaj"""
        esceptlisto = []
        
        for vorto in vortoj:
            analizo = radikanalizo(vorto)
            if analizo[2][0] == "?":
                esceptlisto.append(analizo[0][0])
        
        unikaj_esceptoj = set(esceptlisto)
        ordigitaj_esceptoj = sorted(list(unikaj_esceptoj), key=esperanta_klavo)
        
        print(len(ordigitaj_esceptoj), 'esceptoj')
        for escepto in ordigitaj_esceptoj:
            print(escepto)

    # === ELIGA PRETIGADO ===

    def apartigu_interpunkcioj( teksto): # por ke interpunkcioj ne tuŝu vortojn
        for signo in interpunkcio:
            novasigno=" "+str(signo)+" "
            #print(signo,novasigno)
            teksto = teksto.replace(signo, novasigno)
        #print(teksto)
        return (teksto)
        

    def vort_vicigado (teksto):# Kreu liston de vortoj (nur alfabetaj vortoj)
        vorto=""
        i=0
        vortoj= [vorto for vorto in teksto.split() if vorto]
        print (vortoj)
        while i<len(vortoj):     
            vorto = spacigu_operatoroj(vortoj[i])
            #print (type(vorto),vorto)
            vortoj[i]=vorto
            i=i+1
        vortoj= flatigi_liston(vortoj)
        print(vortoj)
        return  vortoj

    def formatu(analizo):
        """Formatu analizrezulton por eligado"""
        radikoj = "+".join(analizo[0])
        return radikoj + "/" + analizo[1] + " : " + analizo[2]

    def purigu(teksto):
        """Forigu nenecesajn signojn el teksto"""
        teksto = teksto.replace("],", "=")
        for signo in "[']":
            teksto = teksto.replace(signo, "")
        return teksto

    def flatigi_liston(nesta_listo):
        simpla_listo = []
        for elemento in nesta_listo:
            if isinstance(elemento, list):
                simpla_listo.extend(flatigi_liston(elemento))
            else:
                simpla_listo.append(elemento)
        return simpla_listo

    ##################   tiu sekvanta parto interplektiĝas kun parolilo !
    def kompletigo_por_legado(analizo):
        # por dismeti silabojn de plur silabaj vortoj kaj eventuale envicigi funkcioj por  enkonduki  silentetoj antau sufikso , au ŝanĝi  kaj frekvenco kaj lauto-surfaco por esprimi interpunkcioj.
        i=0
        analizo=flatigi_liston(analizo)
        print ("PRITRAKTO DE KATEGORIO",analizo)
        silaboj=[]
        ĉiujsilaboj=[]
        while i <= len(analizo[-1])-1: # per sinsekva legado de lasta elemento de 'analizo'
                                        # kiu entenas po unu litero kalifikanta ĉiu elemento
                                        # cû r-> radiko   s-> sunstantivo t-> finaĵo
            
            print("registaĵo",silaba_vortaro.get(analizo[i]))
            if analizo[-1][i]=="r":
                print (i,"JES radiko  ", analizo[i], silaba_vortaro.get(analizo[i]))
                if silaba_vortaro.get(analizo[i]) != None:
                    if str(analizo[i]) in silab_memoro:
                        print( "KAZO REKTA")
                        silaboj=[analizo[i]]
                        print(silaboj)
                    else:
                        analizo[i]=silaba_vortaro.get(analizo[i])
                        silaboj=list(analizo[i])
                else:
                    silaboj=[analizo[i]]
                    # se ne listo de literoj estos unope vicigitaj


            elif analizo[-1][i]=="s":
                print (i,"JES sufikso  ", analizo[i], silaba_vortaro.get(analizo[i]))
                if silaba_vortaro.get(analizo[i]) != None:
                    analizo[i]=silaba_vortaro.get(analizo[i])
                    # tie eblo enkonduki funkciojn
                    silaboj=list(analizo[i])
                else:
                    silaboj=[analizo[i]]
                    # se ne listo de literoj estos unope vicigitaj            


            elif analizo[-1][i]=="p":
                print (i,"JES prefikso ", analizo[i], silaba_vortaro.get(analizo[i]))
                if silaba_vortaro.get(analizo[i]) != None:
                    analizo[i]=silaba_vortaro.get(analizo[i])
                    # tie eblo enkonduki funkciojn
                    silaboj=list(analizo[i])
                else:
                    silaboj=[analizo[i]]
                    # se ne listo de literoj estos unope vicigitaj
            elif analizo[-1][i]=="q":
                print (i,"JES pronomo ", analizo[i], silaba_vortaro.get(analizo[i]))
                if silaba_vortaro.get(analizo[i]) != None:
                    analizo[i]=silaba_vortaro.get(analizo[i])
                    # tie eblo enkonduki funkciojn
                    silaboj=list(analizo[i])
                else:
                    silaboj=[analizo[i]]
                    # se ne listo de literoj estos unope vicigitaj

            elif analizo[-1][i]=="t":
                print (i,"JES finaĵo  ", analizo[i], silaba_vortaro.get(analizo[i]))
                if silaba_vortaro.get(analizo[i]) != None:
                    analizo[i]=silaba_vortaro.get(analizo[i])
                # se ne listo de literoj estos unope vicigitaj
                # tie eblo enkonduki funkciojn
                print("kio endos dirita",analizo[i])
                silaboj=list(analizo[i])
     
            elif analizo[-1][i]=="y":
                print (i,"JES y  ", analizo[i], silaba_vortaro.get(analizo[i]))            
                if silaba_vortaro.get(analizo[i]) != None:
                    analizo[i]=silaba_vortaro.get(analizo[i])
                    silaboj=analizo[i]
                else:
                    silaboj=[analizo[i]]
                # se ne listo de literoj estos unope vicigitaj
                #silaboj=list(analizo[i])
                
            elif analizo[-1][i]=="n":
                print (i,"JES n  ", analizo[i], silaba_vortaro.get(analizo[i]))            
                if silaba_vortaro.get(analizo[i]) != None:
                    analizo[i]=silaba_vortaro.get(analizo[i])
                    silaboj=analizo[i]
                else:
                    silaboj=[analizo[i]]
                # se ne listo de literoj estos unope vicigitaj
                #silaboj=list(analizo[i]) 



            elif analizo[-1][i]=="z":
                print (i,"JES Z  ", analizo[i], silaba_vortaro.get(analizo[i]))            
                if silaba_vortaro.get(analizo[i]) != None:
                    analizo[i]=silaba_vortaro.get(analizo[i])
                    # tie eblo enkonduki funkciojn
                    silaboj=list(analizo[i])
                else:
                    silaboj=[analizo[i]]
                    # se ne listo de literoj estos unope vicigitaj
                print("kion ci faras",silaboj) #,silaba_vortaro)
                
            elif analizo[-1][i]=="x":
                print (i,"JES X  ", analizo[i], silaba_vortaro.get(analizo[i]))
                if silaba_vortaro.get(analizo[i]) != None:
                    analizo[i]=silaba_vortaro.get(analizo[i])
                    # tie eblo enkonduki funkciojn
                    silaboj=list(analizo[i])
                else:
                    silaboj=[analizo[i]]
                    # se ne listo de literoj estos unope vicigitaj
            elif analizo[-1][i]=="v":
                print (i,"JES V  ", analizo[i], silaba_vortaro.get(analizo[i]))
                if silaba_vortaro.get(analizo[i]) != None:
                    analizo[i]=silaba_vortaro.get(analizo[i])
                    # tie eblo enkonduki funkciojn
                    silaboj=[analizo[i]]
                else:
                    silaboj=[analizo[i]]
                    # se ne listo de literoj estos unope vicigitaj

            elif analizo[-1][i]=="?":
                print (i,"JES ?  ", analizo[i], silaba_vortaro.get(analizo[i]))
                print (analizo[i])
                if   analizo[i]  not in silabaro:
                    print("analizenda")
                # tie eblo enkonduki funkciojn
                silaboj=[analizo[i]]
                print(silaboj)
              
            i +=1
            print(silaboj)
            ĉiujsilaboj=ĉiujsilaboj+silaboj
            #ĉiujsilaboj=ĉiujsilaboj.append(silaboj)
            print(" ***    ", ĉiujsilaboj)
            
        if analizo[-1]=="?"  :  #nur unu karaktro kaj kodo ?.. temas pri interpunkcio
            if analizo[0] == "." : # pritakto de punkto do ioma silento post kas voĉo falanta     
                pass
            elif analizo[0]== ",":
                pass
            elif analizo[0]=='(':
                print("PARENTEZE")
        print("kompletigo    ", ĉiujsilaboj, "     ", analizo)
        #ĉiujsilaboj=prepari_silabojn_kun_finaĵo(ĉiujsilaboj, silab_memoro)
        return ĉiujsilaboj,analizo
    # -------------------------------------------------
    # Viaj funkcioj (senŝanĝaj)
    # -------------------------------------------------


    # -------------------------------------------------
    # Help-funkcioj
    # -------------------------------------------------

    def _kalkuli_rms(data):
        return np.sqrt(np.mean(data**2))

    def ŝargi_kaj_normaligi_silabojn(dosierujo, celo_rms=0.12):
        silab_memoro = {}
        sampla_rapido = None
        if not os.path.isdir(dosierujo):
            raise FileNotFoundError(f"Dosierujo ne ekzistas: {dosierujo}")
        
        for dosiero in os.listdir(dosierujo):
            if not dosiero.endswith(".wav"):
                continue
            silabo = dosiero[:-4]
            vojo = os.path.join(dosierujo, dosiero)
            try:
                data, sr = sf.read(vojo)
            except Exception as e:
                continue
                
            if data.size == 0:
                continue
                
            if sampla_rapido is None:
                sampla_rapido = sr
            elif sr != sampla_rapido:
                raise ValueError(f"Ĉiuj dosieroj devas havi la saman sample rate! Malsamas en {dosiero}.")
                
            if np.issubdtype(data.dtype, np.integer):
                data = data.astype(np.float32) / np.iinfo(data.dtype).max
            else:
                data = data.astype(np.float32)

            # Forigu silenton ĉe komenco/fino (nedeviga, sed helpas RMS)
            data = data[np.abs(data) > 0.001]  # simpla tranĉo; anstataŭe uzu sox.trim en praktiko
            
            if len(data) == 0:
                continue
                
            rms = _kalkuli_rms(data)
            if rms > 1e-8:
                data = data * (celo_rms / rms)
                
            # Sekura limigo por eviti saturadon
            piko = np.max(np.abs(data))
            if piko > 0.6:
                data = data / piko * 0.5
            if silabo=="silentokomo":
                exit()
            silab_memoro[silabo] = (sampla_rapido, data)
            
        return silab_memoro









    def prepari_silabojn_kun_finaĵo(partoj, silab_memoro):
        """
        Aŭtomate disfendas la lastan radik-silabon se eblas,
        por kunmeti ĝian lastan konsonanton kun la finaĵo.
        Ekz: ["es", "per", "ant", "o"] → ["es", "per", "an", "to"]
        """
        if len(partoj) < 2:
            return partoj

        finaĵoj = {
            "o", "a", "e", "i", "u",
            "n", "j",
            "on", "an", "en", "in", "un",
            "oj", "aj", "ej", "ij", "uj",
            "ojn", "ajn", "ejn", "ijn", "ujn"
        }

        lasta = partoj[-1]
        if lasta not in finaĵoj:
            return partoj

        radik_partoj = partoj[:-1]
        lasta_radiko = radik_partoj[-1]

        vokaloj = "aeiou"
        # Nur se lasta_radiko havas ≥2 literojn kaj finiĝas per konsonanto
        if len(lasta_radiko) >= 2 and lasta_radiko[-1] not in vokaloj:
            prefix = lasta_radiko[:-1]
            lasta_fono = lasta_radiko[-1]
            # Se la 'prefix' jam ekzistas en via memoro, uzu la dividon
            if prefix in silab_memoro:
                nova_lasta_silabo = lasta_fono + lasta  # "t" + "o" → "to"
                antaŭaj = radik_partoj[:-1]
                print ("traktitaj", antaŭaj, prefix ,  nova_lasta_silabo)
                return antaŭaj + [prefix, nova_lasta_silabo]

        # Se ne eblas dividado, lasu kiel estas (ekz. "ver o" → ["ver", "o"])
        return partoj


    def varmigi_se_bezone():
        sampla_rapido, _ = silab_memoro['e'] 
        # Praŝargi per 300ms da silento
        silento = np.zeros(int(0.3 * sampla_rapido), dtype=np.float32)
        sd.play(silento, samplerate=sampla_rapido, blocking=False)
        sd.wait()
        #sd.stop()    
        #time.sleep(0.05)
    def aldoni_silenton(aŭdio_segmentoj, sampla_rapido, silento_daŭro=0.2):
        # Unue kunmeti ĉiujn segmentojn en unu array
        #global aŭdio_segmentoj
        silento_longeco = int(silento_daŭro * sampla_rapido)    
        silento = np.zeros(silento_longeco, dtype=np.float32)
        silento = np.atleast_1d(silento).astype(np.float32)   
        return aŭdio_segmentoj.append(silento) #np.concatenate((aŭdio_segmentoj, silento), axis=0)

    def ekbruon (dauxro):
        # Generi sinusoidan ondon
        t = np.linspace(0, dauxro, int(32000 * dauxro), False)
        audio = np.sin(2 * np.pi * 32000 * t)
        # Ludigi
        sd.play(audio, 32000)
        sd.wait()  # atendi ĝis fino (ne deviga, sed ofte utila)    

    def ludu_vorton_el_memoro(jamcitilo,_segmentoj,interpunkcio,
        silaboj,
        silab_memoro,
        eliga_dosiero="registraĵo",
        laŭteco_faktoro=3,
        pika_maks=0.60,
        lasta_malplifortigo=0.85,
        fade_proporcio=0.8,
        fade_fino=0.30,
        silento_sojlo=0.005,
        varmigu_sonon=True,
        praŝarga_temp_sojlo=0.5
    ):
    
    ########   por kapti datumoj de silabo
        def ŝargu_sekure(ŝlosilo):
            #print("serĉado de  ",ŝlosilo
            global jamcitilo, mankantaj,neciferaj,last_nombroflago

            if ŝlosilo in silab_memoro:
                print("registrita", ŝlosilo, silab_memoro[ŝlosilo])
                #print("kontrolo de streketo",last_nombroflago,neciferaj)
                if last_nombroflago==True:
                    neciferaj=neciferaj+1
                    if neciferaj>2:
                        neciferaj=0
                        last_nombroflago=False
                sr, datumoj = silab_memoro[ŝlosilo]
                print("PLU")
            else:
                #print("ne registrita fonemo", ŝlosilo)
                if ŝlosilo in "1234567890+-/*()[]{}€.=": 
                    if ŝlosilo == "-" and last_nombroflago == False  :
                        ŝlosilo ="streketo"
                    else:
                        ŝlosilo=cifero.get(ŝlosilo)
                        last_nombroflago=True
                    print("ciferosigno",ŝlosilo, "nombroflago", nombroflago, "last_nombroflago  ",last_nombroflago)
                    
                    #print(ŝlosilo)
                elif ŝlosilo in "αβγδεζηθικλμνξοπρστυφχψω":
                    ŝlosilo=grekaj_literoj.get(ŝlosilo)
                    print("greka ŝlosilo ",ŝlosilo)
                elif ŝlosilo in "\"\'":
                    if ŝlosilo=="'":
                       ŝlosilo="apostrofo"
                       sr, datumoj = silab_memoro[ŝlosilo] 
                    elif ŝlosilo=='"': #  temas pri  "  citilo
                        print (jamcitilo,"citilo, apostrofo")
                        if jamcitilo==True:
                            ŝlosilo="fincitilo"
                            jamcitilo=False
                        else:
                            ŝlosilo="ekcitilo"
                            jamcitilo=True
                        sr, datumoj = silab_memoro[ŝlosilo]        
                    
                if ŝlosilo in silab_memoro:
                    sr, datumoj = silab_memoro[ŝlosilo]
                    print(ŝlosilo, datumoj)
                else:
                    if ŝlosilo == " ":
                        datumoj = np.zeros(int(0.5*32000), dtype=np.float32)
                    else:    
                        sr, datumoj = silab_memoro['bof']
                        mankantaj=mankantaj+ ŝlosilo 
            # Ĉi tie ni certigas ke datumoj estas almenaŭ 1d
                datumoj = np.atleast_1d(datumoj).astype(np.float32)
            #silento(0.05)
            return sr, datumoj,jamcitilo
    ###################################
        #print(type(silaboj),silaboj)
        #global aŭdio_segmentoj 
        n = len(silaboj)
        lasta_silabo_i = n - 1 # kiu estas ĝenerale finaĵo
        antaŭlasta_silabo_i = n - 2 if n >= 2 else None
       
        print("silaboj   ", silaboj)

        for i, sil in enumerate(silaboj):
            #print("sil", sil)
            segmentoj = []  # reŝargu por ĉiu silabo
            
            ##### testo por nure po-litera legado !  kiu povas funciigi kun plej maldika silab_memoro  nur literoj ! utilas por kontrolo de litero-registraĵo        #k=0
            print("SIL******",sil)
            temp_sil = sil
            while len(temp_sil)>0:
                if KONFIGURO.get("testo") ==True:   
                    fono = temp_sil[0]
                    print("FONO   ",fono)
                    _, fon_datumoj,jamcitilo = ŝargu_sekure(fono)
                    segmentoj.append([fon_datumoj])
                    temp_sil = temp_sil[1:]
                    continue
                # fino de testo
                else :        
            ##### Jen  ĉiukaza proceduro  plej evoluinta necesas plenan silab_memoro 
                    
                    if sil in silab_memoro:                        
                        _, datumoj,jamcitilo = ŝargu_sekure(sil,)
                        segmentoj.append([datumoj])
                        print("tuj trovita ", len(temp_sil))
                        break
                    else:
                        temp_sil = sil
                        while len(temp_sil)>0:
                            print("PECO DE SILABO ",temp_sil)
                            # Provu 3-literajn kombinojn unue
                            if len(temp_sil) >= 3 and temp_sil[:3] in silab_memoro:
                                print("triopo")
                                _, fon_datumoj,jamcitilo = ŝargu_sekure(temp_sil[:3])
                                print("blokado ?")
                                segmentoj.append([fon_datumoj])
                                print("ĉu")
                                temp_sil = temp_sil[2:]
                                print("paneo")
                                #print(temp_sil)
                                continue
                            # Poste 2-literajn
                            elif len(temp_sil) >= 2 and temp_sil[:2] in silab_memoro:
                                print("duopo")
                                _, fon_datumoj,jamcitilo = ŝargu_sekure(temp_sil[:2])
                                segmentoj.append([fon_datumoj])
                                temp_sil = temp_sil[2:]
                                continue
                            # Alie unuopo
                            else:
                                print("unuopo")
                                fono = temp_sil[0]
                                print("FONO   ",fono)
                                _, fon_datumoj,jamcitilo = ŝargu_sekure(fono)
                                segmentoj.append([fon_datumoj])
                                temp_sil = temp_sil[1:]
                                continue
                            
            ####### FINO de la plej evoluinta proceduro      
            # Nun traktu ĉiun fonemon en segmentoj
            for j, datumlist in enumerate(segmentoj):
                datumoj = datumlist[0]  # ĉar vi metis [datumoj] antaŭe
                # → Defensiva konverto: eĉ se ŝargu_sekure malsukcesis
                datumoj = np.atleast_1d(datumoj)
                print (i, antaŭlasta_silabo_i)
                if i == antaŭlasta_silabo_i:
                    #print("PLIFORTIGO ", )
                    #print(datumoj)
                    datumoj = datumoj*laŭteco_faktoro
                    #print(datumoj)
                elif i == lasta_silabo_i:
                    if j == len(segmentoj) - 1:  # lasta fono de lasta silabo
                        sojlo = silento_sojlo
                        datumoj = np.atleast_1d(datumoj)  # ← ĉi tie estas la ĉefa korekto
                        abs_datumoj = np.abs(datumoj)
                        start_idxs = np.where(abs_datumoj > sojlo)[0]
                        start_trim = start_idxs[0] if len(start_idxs) > 0 else 0
                        datumoj = datumoj[start_trim:]
                        datumoj = datumoj * 0.5#lasta_malplifortigo
                        if len(datumoj) > 10:
                            fade_len = max(1, int(len(datumoj) * fade_proporcio))
                            if fade_len < len(datumoj):
                                fade_kurbo = np.linspace(1.0, fade_fino, fade_len)
                                datumoj[-fade_len:] *= fade_kurbo
                                print("trakto de vortfino")
                else:
                    print("NORMALA SILABO")

                datumoj = np.clip(datumoj, -pika_maks, pika_maks)
                aŭdio_segmentoj.append(datumoj)


        if not aŭdio_segmentoj:
            return

        
        if interpunkcio != "":
            #plena_aŭdio=modifi_ondformon_simple(plena_aŭdio, 32000, interpunkcio, progreso=0.5)
            
            #plena_aŭdio=modifi_spektron_dinamike(plena_aŭdio, sampla_rapido, interpunkcio, progreso=0.5)
            
            #plena_aŭdio=drasta_fino_efekto(plena_aŭdio, sampla_rapido)
            pass
            
            #plena_aŭdio=modifi_spektron_simpla(plena_aŭdio, 32000, interpunkcio, progreso=0.5)

            #plena_aŭdio=modifi_spektron(plena_aŭdio, 32000,interpunkcio)
            
            #ludu_kun_efiko(plena_aŭdio, ".", 3.0)  # 3-sekunda sono kun punkto
            
            interpunkcio=""
            
        return plena_aŭdio ,jamcitilo
          
    def aldoni(dosiero, registraĵo):
        SAMPLA_RAPIDO = 32000

        try:
            sr, malnova = wavfile.read(dosiero, mmap=False)
            if sr == SAMPLA_RAPIDO:
                kombinitaj = np.concatenate([malnova.flatten(), registraĵo])
                wavfile.write(dosiero, SAMPLA_RAPIDO, kombinitaj.astype(np.int16))
            else:
                wavfile.write(dosiero, SAMPLA_RAPIDO, registraĵo)
        except Exception as e:
            print(f"Eraro dum legado: {e}")
            wavfile.write(dosiero, SAMPLA_RAPIDO, registraĵo)
        #print("SAVADO")
      
       

    # ************************************   AKRONIMOJ

    def akcepti_vorton(vorto):
        """
        Kontrolas ĉu la vorto estas akceptinda laŭ la specifitaj kondiĉoj.
        
        Kondiĉoj:
        - Post forigo de apartigiloj (.,-/* kaj spaco), la restantaĵo komencas per majuskla litero.
        - La ceteraj signoj en la restantaĵo povas esti majusklaj, minusklaj aŭ ciferoj.
        - La vorto ne komencas aŭ finas per apartigilo.
        - Ĉiuj signoj en la vorto devas esti permesataj (literoj, ciferoj aŭ apartigiloj).
        """
        # Difinu la arojn de signoj
        apartigiloj = ".,-/*"" "
        majuskloj = "ABCDEFGHIJKLMNOPQRSTUVWXYZĈĜĤĴŜŬ"
        minuskloj = "abcdefghijklmnopqrstuvwxyzĉĝĥĵŝŭ"
        ciferoj = "0123456789"
        permesataj = majuskloj + minuskloj + ciferoj + apartigiloj
        
        # 1. Ĉu ĉiuj signoj estas permesataj?
        for ch in vorto:
            if ch not in permesataj:
                return False
        
        # 2. Ĉu la vorto komencas aŭ finas per apartigilo?
        # if vorto[0] in apartigiloj or vorto[-1] in apartigiloj:
        #     return False
        
        # 3. Forigu ĉiujn apartigilojn
        restanta = ''.join(ch for ch in vorto if ch not in apartigiloj)
        
        # 4. Restantaĵo ne povas esti malplena
        if not restanta:
            return False
        
        # 5. Unua signo de restantaĵo devas esti majuskla litero
        if restanta[0] not in majuskloj:
            return False
        
        # 6. ĉu estas almenau 2 majuskloj
        #if  len(re.findall(r'[A-ZĈĜĴŜĤ]', restanta))<1 :
            #return False
        
        # 7. Ĉiuj signoj en restantaĵo devas esti literoj aŭ ciferoj
        for ch in restanta:
            if not (ch in majuskloj or ch in ciferoj):
                return False
        
        return True



    def detekti_vortojn_en_teksto(teksto):
        """
        Trovas ĉiujn vortojn en teksto kiuj plenumas la kondiĉojn de akcepti_vorton.
        """
        # Unue, dividu la tekston per spacoj por ricevi vortojn
        vortoj = teksto.split()
        
        # Tiam purigu ĉiun vorton (forigu apartigilojn ĉe la komenco kaj fino)
        purigitaj_vortoj = []
        for vorto in vortoj:
            # Forigu apartigilojn ĉe la komenco kaj fino
            while vorto and vorto[0] in ".,-/* ":
                vorto = vorto[1:]
            while vorto and vorto[-1] in ".,-/* ":
                vorto = vorto[:-1]
            if vorto:
                purigitaj_vortoj.append(vorto)
        
        # Nun kontrolu ĉiun purigitan vorton
        rezultoj = []
        for vorto in purigitaj_vortoj:
            if akcepti_vorton(vorto):
                rezultoj.append(vorto)
        #print("rezultoj de akronimo  ",rezultoj )
        
        return rezultoj

    # **************************************  NOMBROJ

    def testo_traduko_nombro (vorto):
        # return a Boolean if the match was met
        global nombroflago,last_nombroflago
        print("vorto nombro " ,vorto)
        def ĉu_ne_havas_literojn(teksto):
    # Serĉas iun ajn literon (a-z, A-Z, inkluzive akcentitajn)
            return not bool(re.search(r'[a-zA-Zà-ÿÀ-ß]', teksto, re.UNICODE))
        # if vorto[0]=="-" and ĉu_ne_havas_literojn(vorto[1]) :
        #     print("komenco per minus" )
            
        if  bool(re.match(r"^\d+[.,+*/]?\d*$", vorto)):
            vortoj=nombro_al_vortoj(vorto)
            nombroflago=True
            last_nombroflago=True
            #print("456  66", vortoj  )
            print("nombro  ",vortoj)
            return nombroflago,vortoj
        else:
            nombroflago=False
            return nombroflago,None
        
    def spacigu_operatoroj(esprimo):
        """
        Versio kiu traktas ĉiun operatoron aparte, inkluzive de unaraj + kaj -.
        """
        # Listo de operatoroj por anstataŭigi
        operatoroj = ['+', '-', '*', '/', '=']
        rezulto=[]
        # Forigu spacojn
        esprimo = esprimo.replace(' ', '')
        
        # Aldonu spacojn ĉirkaŭ ĉiu operatoro
        for op in operatoroj:
            esprimo = esprimo.replace(op, ' '+op+' ')
        rezulto = esprimo.split()
        
        # Forigu troajn spacojn
        return rezulto
        
    def nombro_al_vortoj(nombro_str):
        """
        Konvertas numeron al vortoj en Esperanto kun apartaj dekaj partoj.
        Ekzemplo: 856423.458 -> "ok cent/ kvin dek/ ses/ mil/ kvar cent/ du dek/ tri/ komo/ kvar cent/ kvin dek/ ok/"
        """    
        # Unuoj
        unuoj = ["nul", "unu", "du", "tri", "kvar", "kvin", "ses", "sep", "ok", "naŭ"]
        nombro_str=nombro_str
        def konvertu_tri_ciferojn(n):
            """Konvertas tri-ciferan nombron (0-999) al vortoj"""
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
                    # 11-19: "dek unu", "dek du", ktp
                    partoj.append("dek " + unuoj[resto-10])
                else:  # 20-99
                    dek = resto // 10
                    unu = resto % 10
                    # Uzu "du dek", "tri dek", ktp
                    partoj.append(unuoj[dek] + " dek")
                    if unu > 0:
                        partoj.append(unuoj[unu])
            
            return partoj
        
        def entjero_al_vortoj(n_str, sufiksoj=True):
            """Konvertas entjeron (kiel string) al vortoj"""
            # Forigi komencajn nulojn
            n_str = n_str.lstrip('0')
            
            # Se la nombro estas 0
            if n_str == "":
                return ["nul"]
            
            # Grupigi en trioj de la fino
            grupetoj = []
            temp = n_str
            while temp:
                if len(temp) <= 3:
                    grupetoj.append(temp)
                    break
                grupetoj.append(temp[-3:])
                temp = temp[:-3]
            grupetoj.reverse()  # nun la unua estas la plej granda grupo
            #print("grupetoj", grupetoj)
            vortoj_partoj = []
            
            for i, grupo_str in enumerate(grupetoj):
                grupo_valoro = int(grupo_str)
                if grupo_valoro == 0:
                    continue
                
                grupo_vortoj = konvertu_tri_ciferojn(grupo_valoro)
                vortoj_partoj.extend(grupo_vortoj)
                
                pozicio = len(grupetoj) - i - 1
                
                if sufiksoj:
                    if pozicio == 1:  # miloj
                        if grupo_valoro == 1:
                            vortoj_partoj.append("mil")
                        else:
                            vortoj_partoj.append("mil")
                    elif pozicio == 2:  # milionoj
                        if grupo_valoro == 1:
                            vortoj_partoj.append("miliono")
                        else:
                            vortoj_partoj.append("milionoj")
                    elif pozicio == 3:  # miliardoj
                        if grupo_valoro == 1:
                            vortoj_partoj.append("miliardo")
                        else:
                            vortoj_partoj.append("miliardoj")
            
            return vortoj_partoj
        
        # Anstataŭigu komon per punkto por faciligi
        signo=[]
        if nombro_str[0] in "+-/*=":
            signo=[cifero.get(nombro_str[0])]    
            nombro_str=nombro_str[1:]
        nombro_str = str(nombro_str).replace(',', '.')
        #print(nombro_str)
        # Dividu en tutan kaj dekuman parton
        partoj = nombro_str.split('.')
        #print("partoj",partoj)
        if len(partoj) == 1:
            tuta_parto = partoj[0]
            dekuma_parto = ""
        else:
            tuta_parto = partoj[0]
            dekuma_parto = partoj[1]
        
        # Konvertu la tutan parton
        if tuta_parto == "" or int(tuta_parto) == 0:
            tuta_vortoj = ["nul"]
        else:
            tuta_vortoj = entjero_al_vortoj(tuta_parto, sufiksoj=True)
        
        # Konvertu la dekuman parton
        if dekuma_parto == "" or int(dekuma_parto) == 0:
            dekuma_vortoj = []
        else:
            # Forigi komencajn nulojn
            dekuma_parto = dekuma_parto.lstrip('0')
            if dekuma_parto == "":
                dekuma_vortoj = []
            else:
                dekuma_vortoj = entjero_al_vortoj(dekuma_parto, sufiksoj=False)
        
        # Kunigi la rezultojn
        if dekuma_vortoj:
             rezulto_listo = tuta_vortoj + ["komo"] + dekuma_vortoj
        else:
            rezulto_listo = tuta_vortoj
        rezulto_listo=signo+rezulto_listo
        #print("rezulto_listo",rezulto_listo[:])
        s=" "
        rezulto=s.join(rezulto_listo)
        #print("rezulto" ,rezulto)
        # Aldoni '/' post ĉiu elemento en la listo
        return   rezulto


    
    interpunkcio = ",.;?!"
    
    
    # Legu kaj ŝargu la n
    vortarolinioj = legu(vortarodosiero).lower().split("\n")
    vortaro = {}
    for linio in vortarolinioj:
        if len(linio) > 0:
            [vorto, kategorio] = linio.split(",")
            vortaro[vorto] = (kategorio)
    #print("VORTARO     ",vortaro)
    
    
    # === DIFINU GRAMATIKAJN KATEGORIOJN ===
    senfinaĵaj=""
    # Senfinaĵaj vortoj (prepozicioj, numeraloj, ktp)
    senfinaĵaj = akiru_kategoriojn("znx")  
    # Plusaj kombinaĵoj
    senfinaĵaj += kombinu(akiru_kategoriojn("qu"), ["", "n"])  # Participoj
    senfinaĵaj += kombinu(akiru_kategoriojn("v"), ["", "n", "j", "jn"])  # Verboj
    #print ("SENFINAJOJ   ",senfinaĵaj)
    # Vortfinaĵoj
    finaĵoj = akiru_kategoriojn("t")
    finaĵoj = [f for f in finaĵoj if f not in ['j', 'n']]
    finaĵoj += kombinu(["o", "a"], ["n", "j", "jn"])
    finaĵoj.append("en")
    #print(type(finaĵoj), finaĵoj)
    # Sufiksoj
    sufiksoj = akiru_kategoriojn("s")
    
    # Prefiksoj
    prefiksoj = akiru_kategoriojn("pz")
    prefiksoj.append("ne")
    #print("Prefiksoj",prefiksoj) 
    
    # === FONEMOJ ===
    if KONFIGURO.get('uzi_fontajn')==True:
        fonemujo=dosierujo+"fonemoj"
    else:
        fonemujo=dosierujo+"fonemojx"
    laŭteco=1.15
    pika_maks=0.60
    varmigu=True
    silab_memoro={}
    silab_memoro=ŝargi_kaj_normaligi_silabojn(fonemujo, celo_rms=0.08)
    
    ############### vortaro de radikoj  de DS clopeau ne la sama de JSB ,kolono 'nivelo' formetita !
    silaba_vortaro=ŝargi_vortaron(silaba_vortaro_dosiero,formato="pickle")
    #print(silaba_vortaro)
    silabaro=[]
    silabaro = ŝargi_vortaron(silabaro_dosiero, formato="pickle")
    #print(silabaro)
    
    enigo = open("/home/clopeau/lingvaprogramado/vortar.txt","r")  # vortaro de radikoj
    radikoj= enigo.read()
    #print("radikoj   ",radikoj)
    radikoj=radikoj.split()
    radikoj=flatigi_liston(radikoj)
    #print("radikoj   ",radikoj)
    radikinit=radikoj
    radikoj=[]
    for radiko in radikinit:
        radiko=radiko.strip("[]")
        radiko=radiko.strip(",")
        radiko=radiko.strip("'")
        radiko=radiko.strip("'")
        #print(radiko)
        radikoj.append(radiko)
    #print( "RADIKOJ ***** ",radikoj[0],radikoj[len(radikoj)-1])
    
    
    # Analizu vortojn kaj skribu rezultojn
    
    antaŭa_vorto = ""
    nombro_de_aparoj = 0
    #teksto = apartigu_interpunkcioj(teksto)
    #print("post apartigo_interpunkcio",teksto)
    parts = re.split(r"([\"',;+\-/*=\)\() ])", teksto)
    # Forigu malplenajn/nul-signajn erojn (ekz. spacoj, se ne bezonataj)
    result = [part for part in parts if part and not part.isspace()]
    print("Traktado de aportrofo kaj citiloj kaj komo kaj blankoj",result)
    vortoj=result
    #vortoj = vort_vicigado (teksto)
    
   
    
    
    #print("Teksto:", len(vortoj), "vortoj - Vortaro:", len(vortaro), "morfemoj")
    print("teksto studata   ",vortoj)
    analizo=[]   
    
    
    #print(silaboj)
    # Aŭtomate eligu la ekziston de silab_memoro
    if not silab_memoro:
        print("Averto: silab_memoro estas malplena!")
    
    unua_silabo = next(iter(silab_memoro))
    sampla_rapido, _ = silab_memoro[unua_silabo]
    varmigi_se_bezone()   #       por aktivigi souddevice ?
    
    #
    i=0
    nombrazono=""
    interpunkcioflago=False
    
    #plena_aŭdio = np.zeros(int(0.3 * sampla_rapido), dtype=np.float32)
    aŭdio_segmentoj = []
    plena_aŭdio=[]
    ekbruon(1)
    def prepari_aŭdion_simple(aŭdio_segmentoj, sampla_rapido):
#"""Simpla antaŭ-preparo - nur mallongigas kaj kunigas"""
    
        if len(aŭdio_segmentoj) <= 1:
            return np.concatenate(aŭdio_segmentoj) if aŭdio_segmentoj else np.array([])
        
        preparitaj_segmentoj = []
        
        for i in range(len(aŭdio_segmentoj)):
            if i == 0:
                preparitaj_segmentoj.append(aŭdio_segmentoj[i])
                continue
                
            antau_last = aŭdio_segmentoj[i-1]
            lasta = aŭdio_segmentoj[i]
            
            # Kontroli daŭron
            dauro_antaulasta = len(antau_last) / sampla_rapido * 1000
            
            if dauro_antaulasta > 200:
                # Kalkuli 20ms
                specimens_20ms = int(0.02 * sampla_rapido)
                
                if len(antau_last) > specimens_20ms:
                    # Mallongigi la antaŭlastan
                    antaulasta_mallongigita = antau_last[:-specimens_20ms]
                    preparitaj_segmentoj[-1] = antaulasta_mallongigita
                    
                    # Aldoni silenton antaŭ la lasta
                    silento = np.zeros((specimens_20ms,) + lasta.shape[1:])
                    lasta_kun_silento = np.concatenate([silento, lasta])
                    preparitaj_segmentoj.append(lasta_kun_silento)
                else:
                    preparitaj_segmentoj.append(lasta)
            else:
                preparitaj_segmentoj.append(lasta)
        
        # Kunigi ĉion
        return np.concatenate(preparitaj_segmentoj)



    def disigu_interpunkcion(vorto):
        # Serĉas vortojn aŭ la specifajn interpunkciajn signojn
        return re.findall(r'\w+|[€,!?;\.]', vorto)
    while i<len(vortoj):
        vorto = vortoj[i] # sorted(vortoj, key=esperanta_klavo):
        silaboj=[]        
        #print(" antau +++++++++++++++++++++++++++++++++++++++++++++++++++",vorto)
        
        if akcepti_vorton(vorto): # detektas AKRONIMOJ
            akronimoflago=True
            last_nombroflago=False
        else:
            akronimoflago=False
            
        nombroflago,tradukitanombro= testo_traduko_nombro(vorto)  # serĉas kaj tradukas literen nombron
        print("KIO ESTAS    +++++++++++  ",akronimoflago,nombroflago,tradukitanombro)
    
        if akronimoflago == True :
            vorto=re.sub('[.'',''/]',"",vorto)
            #print(vorto)
            akronimo=list(vorto)
            #print (vortoj)
            n=0
            for vorto in akronimo:
                vorto=vorto.lower()
                #print(vorto)
                if vorto in konsonantoj:
                    vorto=vorto+"o"
                akronimo[n]=vorto
                n=n+1
            print (vortoj)
            n=0
            while n< len(akronimo):
                vorto=akronimo[n]
                #print("nombro buklo ",vorto)
                analizo = radikanalizo(vorto)
                analizo= flatigi_liston(analizo)
                #print("analizo     ",analizo)
                silaboj, analizo = kompletigo_por_legado (analizo)
                #print("analizo     ",analizo,"silabo", silaboj)
                jamcitilo=ludu_vorton_el_memoro(jamcitilo,aŭdio_segmentoj,interpunkcio,
                    silaboj,
                    silab_memoro,
                    
                    laŭteco_faktoro=1.15,
                    pika_maks=0.60,
                    lasta_malplifortigo=0.85,
                    fade_proporcio=0.30,
                    fade_fino=0.30,
                    silento_sojlo=0.005,
                    varmigu_sonon=True
                )
                aldoni_silenton(aŭdio_segmentoj, sampla_rapido, silento_akronimo)
                #print("n ",n)    
                n=n+1
    
        elif nombroflago == True :
           nombrazono=tradukitanombro
           x=i+1
           if x<len(vortoj)-1:
               if vortoj[x]in',\-+/*=':
                   nombroflago,tradukitanombro=testo_traduko_nombro(vortoj[x+1])
                   if nombroflago==True:
                       if vortoj[x] ==",":
                           nombrazono=nombrazono+" komo "+tradukitanombro
                       elif vortoj[x]=="-":
                            nombrazono=nombrazono+" minus "+tradukitanombro
                       elif vortoj[x]=="*":
                           nombrazono=nombrazono+" oble "+tradukitanombro
                       elif vortoj[x]=="/":
                           nombrazono=nombrazono+" one "+tradukitanombro
                       elif vortoj[x]=="=":
                           nombrazono=nombrazono+" egalas "+tradukitanombro
                       elif vortoj[x]=="(":
                           nombrazono=nombrazono+" ekparentezo "+tradukitanombro
                       elif vortoj[x]==")":
                           nombrazono=nombrazono+" finparentezo "+tradukitanombro
                       last_nombroflago=True
                       print("nombro kun komo", nombrazono) 
                       i=i+2
                       # legado de nombrazono
                   else:
                      print("nombro sen komo",nombrazono) 
                      # legado de nombrazono   
    
           nombro_grupoj = nombrazono.split()
           print("nombro_grupoj ",nombro_grupoj)
           n=0
           while n< len(nombro_grupoj):
               vorto=nombro_grupoj[n]
               #print("nombro buklo ",vorto)
               # if vorto!='komo':
               #     nombro_al_vortoj(vorto)
               if vorto not in silab_memoro:               
                   analizo = radikanalizo(vorto)
                   analizo= flatigi_liston(analizo)
                   print("NE ĈESTA EN SILAB_MEMORO")
                   silaboj, analizo = kompletigo_por_legado (analizo)
                   #print("analizo     ",analizo,"silabo", silaboj)     
               else:  
                   silaboj=[vorto]
                   #print("SILABOJ",silaboj)
               jamcitilo=ludu_vorton_el_memoro(jamcitilo,aŭdio_segmentoj,interpunkcio,
                   silaboj,
                   silab_memoro,
                   
                   laŭteco_faktoro=1.15,
                   pika_maks=0.60,
                   lasta_malplifortigo=0.85,
                   fade_proporcio=0.30,
                   fade_fino=0.30,
                   silento_sojlo=0.005,
                   varmigu_sonon=True
               )
               if vorto in ["dek","cent","mil","miliono","milionoj"," miliardo", "miliardoj"]:
                   aldoni_silenton(aŭdio_segmentoj, sampla_rapido, silento_cifero)              
               else:
                   aldoni_silenton(aŭdio_segmentoj, sampla_rapido, silento_daŭro=0)  
               #print("n ",n)    
               n=n+1
    
        else :    
            print("traktata vorto ",vorto)
            vorto=vorto.lower()        
            
            if len(vorto)>1:
                vorto=disigu_interpunkcion(vorto)            
                if vorto[-1] in ".!?" and len(vorto)>1:
                    interpunkcio=vorto[-1]
                    #print("filrilo de punkto",vorto)
                    vorto = vorto[:-1]
                    delimiter = "" # Define a delimiter
                    vorto = delimiter.join(vorto)     
                    #print("filrilo de punkto",vorto)                    
                else:
                    interpunkcio=" " # eble okazigos tro dasilento?        
                    vorto=vorto.pop()
                    #print ("sen,interpunkcio",vorto,interpunkcio)
                 # redonas simplan katenon           
            print("Vorto ",vorto)       
            if vorto not in silab_memoro:  
                #print("ebla komo")
                if vorto=="," or vorto==";":
                    aldoni_silenton(aŭdio_segmentoj, sampla_rapido, silento_komo)
                   
                else:    
                    analizo = radikanalizo(vorto)
                    analizo= flatigi_liston(analizo)
                    #print("analizo     ",analizo)
                    silaboj, analizo = kompletigo_por_legado (analizo)
                    print("analizo     ",analizo,"silabo", silaboj)     
            else:  
                silaboj=[vorto]
           
            plena_aŭdio,jamcitilo=ludu_vorton_el_memoro(jamcitilo,aŭdio_segmentoj,interpunkcio,
                silaboj,
                silab_memoro,
                
                laŭteco_faktoro=1.2,
                pika_maks=0.60,
                lasta_malplifortigo=0.85,
                fade_proporcio=0.30,
                fade_fino=0.30,
                silento_sojlo=0.005,
                varmigu_sonon=True
            )
            #last_nombroflago=False
                    ############################## Konverto
                             
        if interpunkcio=="." or i==len(vortoj)-1: #legado frazo post frazo
            # En via ĉefa kodo:
            tuto = prepari_aŭdion_simple(aŭdio_segmentoj, sampla_rapido)
            if len(tuto) > 0:
                sd.play(tuto, samplerate=sampla_rapido)
                sd.wait()
            aŭdio_segmentoj =[]


            # Savi
            if KONFIGURO.get('registri_finan_rezulton')==True:                 
                aldoni(eliga_dosiero,tuto)
                    ########################
        
            
        i=i+1
    print ("mankantaj = ",mankantaj)
    
if __name__ == "__main__":
    lanĉi_gui()

    
