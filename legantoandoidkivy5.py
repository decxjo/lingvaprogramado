#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 09:51:48 2026

@author: clopeau
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 09:18:09 2026

@author: clopeau
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legilo Kivy - Stabilaj versio
Created on Thu Feb 12 2026
@author: clopeau
"""
import os as os
from pathlib import Path as Vojo
from pathlib import Path
import numpy as np
import platform as platformo
import re
import soundfile as sf
import pickle
import time

from kivy.app import App as Appo
from kivy.uix.boxlayout import BoxLayout as Boxo
from kivy.uix.textinput import TextInput as TekstoIn
from kivy.uix.label import Label as Etikedo
from kivy.uix.button import Button as Butono
from kivy.uix.popup import Popup as Popupo
from kivy.uix.scrollview import ScrollView as Rulilo
from kivy.uix.gridlayout import GridLayout as GridO
from kivy.clock import Clock as Horloĝo
from konfiguro import KONFIGURO as KONFIGURO

# ======= AUDIO FUNKCIO ======

from threading import Thread
from ffpyplayer import MediaPlayer as Sonilo
ludilo = Pla()

# ======= LEGU TEKSTON =======
def legi_tekston(teksto):
    print("teksto transdonita",teksto)
    """Simula legado de teksto"""
    # litero_valoro = [ord(c) % 256 / 256 for c in teksto]
    # signalo = np.array(litero_valoro * 2000)  # pli longa por aŭdi
    # ludi_sonon(signalo)
        
    global jamcitilo,finpunkto,last_nombroflago,neciferaj,nombroflago
    print ("Valoru  mane  dauro de silentoj")
    silento_komo=KONFIGURO.get("silento_komo")
    silento_punkto=KONFIGURO.get("silento_punkto")
    silento_cifero=KONFIGURO.get("silento_cifero")
    silento_akronimo=KONFIGURO.get("silento_akronimo")
    jamcitilo=False
    finpunkto=False
    last_nombroflago=False
    neciferaj=0
    
    
    global mankantaj
    mankantaj=""
    # starti fadenon de son-ludilo
    # Komenci unufoje ĉe programo-lanĉo:

  
    #
    dosierujo = Path(__file__).parent.absolute()
    os.chdir(dosierujo)  # Tio solvos viajn relative vojo-problemojn
    dosierujo=str(dosierujo)+"/"
    print(dosierujo)
    #dosierujo = os.path.dirname(os.path.abspath(__file__))+"/"
    # === FONEMOJ ===
    
    if os.path.isdir( dosierujo+"fonemoj") ==False and platformo.system() != "Android":
        print("BLOKADO mankas dosiero fonemoj kreu ĝi kaj registru fonemoj per registilo eventuale kopiu dosierujon zip transdonita")
    if os.path.isdir( dosierujo+"fonemojx") ==False:
         os.mkdir(dosierujo+"/fonemojx")
         normalilo = "/home/clopeau/lingvaprogramado/SOX.sh"
         eliga_averto = os.system(normalilo)
         print(eliga_averto)
         print("AKTIVADO DE OPCION por produkti filtritajn fonemoj")
    #dosierujo = ''  # Dosieruja vojo
    #tekstodosiero =  KONFIGURO.get(dosierujo+'tekstodosiero') #dosierujo + 'texte3.jsb'
    vortarodosiero = KONFIGURO.get("vortarodosiero")   #dosierujo + '1.csv'
    print("****************vortarodosiero*************************")
    #eligodosiero = KONFIGURO.get("avirer.jsb")
    silaba_vortaro_dosiero =KONFIGURO.get("silaba_vortaro_dosiero")
    silabaro_dosiero = KONFIGURO.get("silabaro_dosiero")
    eliga_dosiero = KONFIGURO.get("eliga_dosiero")

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
        print(dosieronomo)
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



    def kombinu(x, y):
        """Kreu ĉiujn kombinaĵojn de elementoj el du listoj"""
        return [v + w for v in x for w in y]

    def nombru_silabojn(vorto):
        """Kalkulu nombron de silaboj (vokaloj) en vorto"""
        return sum([v in "aeiou" for v in vorto])

    


    def fortranĉu_finaĵon_detale(vorto, finaĵolisto):
        """Fortranĉu finaĵon kaj redonu ambaŭ partojn"""
        for finaĵo in finaĵolisto:
            if vorto[-len(finaĵo):] == finaĵo:
                return (vorto[:-len(finaĵo)], finaĵo)
        return (vorto, "")



    def silaboj(n):
        """Trovu ĉiujn vortojn kun n silaboj"""
        return [v for v in vortaro.keys() if nombru_silabojn(v) == n]

    def akiru_kategoriojn(vorto):
        """Trovu ĉiujn kategoriojn por vorto en vortaro"""
        return [v for v in vortaro.keys() if vortaro[v][0] in vorto]



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
        ikompletigo=0
        analizo=flatigi_liston(analizo)
        print ("PRITRAKTO DE KATEGORIO",analizo)
        silaboj=[]
        ĉiujsilaboj=[]
        while ikompletigo <= len(analizo[-1])-1: # per sinsekva legado de lasta elemento de 'analizo'
                                        # kiu entenas po unu litero kalifikanta ĉiu elemento
                                        # cû r-> radiko   s-> sunstantivo t-> finaĵo
            
            print("registaĵo",silaba_vortaro.get(analizo[ikompletigo]))
            if analizo[-1][ikompletigo]=="r":
                print (ikompletigo,"JES radiko  ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))
                if silaba_vortaro.get(analizo[ikompletigo]) != None:
                    if str(analizo[ikompletigo]) in silab_memoro:
                        print( "KAZO REKTA")
                        silaboj=[analizo[ikompletigo]]
                        #print(silaboj)
                    else:
                        analizo[ikompletigo]=silaba_vortaro.get(analizo[ikompletigo])
                        silaboj=list(analizo[ikompletigo])
                else:
                    silaboj=[analizo[ikompletigo]]
                    # se ne listo de literoj estos unope vicigitaj


            elif analizo[-1][ikompletigo]=="s":
                print (ikompletigo,"JES sufikso  ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))
                if silaba_vortaro.get(analizo[ikompletigo]) != None:
                    analizo[ikompletigo]=silaba_vortaro.get(analizo[ikompletigo])
                    # tie eblo enkonduki funkciojn
                    silaboj=list(analizo[ikompletigo])
                else:
                    silaboj=[analizo[ikompletigo]]
                    # se ne listo de literoj estos unope vicigitaj            


            elif analizo[-1][ikompletigo]=="p":
                print (ikompletigo,"JES prefikso ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))
                if silaba_vortaro.get(analizo[ikompletigo]) != None:
                    analizo[ikompletigo]=silaba_vortaro.get(analizo[ikompletigo])
                    # tie eblo enkonduki funkciojn
                    silaboj=list(analizo[ikompletigo])
                else:
                    silaboj=[analizo[ikompletigo]]
                    # se ne listo de literoj estos unope vicigitaj
            elif analizo[-1][ikompletigo]=="q":
                print (ikompletigo,"JES pronomo ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))
                if silaba_vortaro.get(analizo[ikompletigo]) != None:
                    analizo[ikompletigo]=silaba_vortaro.get(analizo[ikompletigo])
                    # tie eblo enkonduki funkciojn
                    silaboj=list(analizo[ikompletigo])
                else:
                    silaboj=[analizo[ikompletigo]]
                    # se ne listo de literoj estos unope vicigitaj
            elif analizo[-1][ikompletigo]=="t":
                print (ikompletigo,"JES finaĵo  ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))
                if silaba_vortaro.get(analizo[ikompletigo]) != None:
                    analizo[ikompletigo]=silaba_vortaro.get(analizo[ikompletigo])
                # se ne listo de literoj estos unope vicigitaj
                # tie eblo enkonduki funkciojn
                print("kio endos dirita",analizo[ikompletigo])
                silaboj=list(analizo[ikompletigo])     
            elif analizo[-1][ikompletigo]=="y":
                print (ikompletigo,"JES y  ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))            
                if silaba_vortaro.get(analizo[ikompletigo]) != None:
                    analizo[ikompletigo]=silaba_vortaro.get(analizo[ikompletigo])
                    silaboj=analizo[ikompletigo]
                else:
                    silaboj=[analizo[ikompletigo]]
                # se ne listo de literoj estos unope vicigitaj
                #silaboj=list(analizo[ikompletigo])                
            elif analizo[-1][ikompletigo]=="n":
                print (ikompletigo,"JES n  ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))            
                if silaba_vortaro.get(analizo[ikompletigo]) != None:
                    analizo[ikompletigo]=silaba_vortaro.get(analizo[ikompletigo])
                    silaboj=analizo[ikompletigo]
                else:
                    silaboj=[analizo[ikompletigo]]
                # se ne listo de literoj estos unope vicigitaj
                #silaboj=list(analizo[ikompletigo]) 
            elif analizo[-1][ikompletigo]=="z":
                print (ikompletigo,"JES Z  ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))            
                if silaba_vortaro.get(analizo[ikompletigo]) != None:
                    analizo[ikompletigo]=silaba_vortaro.get(analizo[ikompletigo])
                    # tie eblo enkonduki funkciojn
                    silaboj=list(analizo[ikompletigo])
                else:
                    silaboj=[analizo[ikompletigo]]
                    # se ne listo de literoj estos unope vicigitaj
                print("kion ci faras",silaboj) #,silaba_vortaro)
                
            elif analizo[-1][ikompletigo]=="x":
                print (ikompletigo,"JES X  ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))
                if silaba_vortaro.get(analizo[ikompletigo]) != None:
                    analizo[ikompletigo]=silaba_vortaro.get(analizo[ikompletigo])
                    # tie eblo enkonduki funkciojn
                    silaboj=list(analizo[ikompletigo])
                else:
                    silaboj=[analizo[ikompletigo]]
                    # se ne listo de literoj estos unope vicigitaj
            elif analizo[-1][ikompletigo]=="v":
                print (ikompletigo,"JES V  ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))
                if silaba_vortaro.get(analizo[ikompletigo]) != None:
                    analizo[ikompletigo]=silaba_vortaro.get(analizo[ikompletigo])
                    # tie eblo enkonduki funkciojn
                    silaboj=[analizo[ikompletigo]]
                else:
                    silaboj=[analizo[ikompletigo]]
                    # se ne listo de literoj estos unope vicigitaj

            elif analizo[-1][ikompletigo]=="?":
                print (ikompletigo,"JES ?  ", analizo[ikompletigo], silaba_vortaro.get(analizo[ikompletigo]))
                print (analizo[ikompletigo])
                if   analizo[ikompletigo]  not in silabaro:
                    print("analizenda")
                # tie eblo enkonduki funkciojn
                silaboj=[analizo[ikompletigo]]
                print(silaboj)
              
            ikompletigo +=1
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
            print(vojo)
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
            #print(silabo)
        #print(silab_memoro)    
        return silab_memoro

    def aldoni_silenton(aŭdio_segmentoj, sampla_rapido, silento_daŭro=0.2):
        # Unue kunmeti ĉiujn segmentojn en unu array
        #global aŭdio_segmentoj
        silento_longeco = int(silento_daŭro * sampla_rapido)    
        silento = np.zeros(silento_longeco, dtype=np.float32)
        silento = np.atleast_1d(silento).astype(np.float32)   
        return aŭdio_segmentoj.append(silento) #np.concatenate((aŭdio_segmentoj, silento), axis=0)

    def ludu_vorton_el_memoro(jamcitilo,interpunkcio,
        silaboj,
        silab_memoro,
        laŭteco_faktoro,
        pika_maks,
        fade_proporcio=0.8,
        fade_fino=0.30,
        silento_sojlo=0.005
    ):
    ########   por kapti datumoj de silabo
        def ŝargu_sekure(ŝlosilo):
            test1=""
            test2=""
            #print("serĉado de  ",ŝlosilo
            global jamcitilo, mankantaj,neciferaj,last_nombroflago
            print("tioma silabo",index)
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
                if ŝlosilo in "1234567890+-/*()[]{}€.,=": 
                    print("kontrolo  ",index, vortoj[index+1],testo_traduko_nombro(vortoj[index+1]))
                    test1, test2 = testo_traduko_nombro(vortoj[index+1])
                    if ŝlosilo == "-" and last_nombroflago == False and  test1==False :# and :
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
                    elif ŝlosilo =="\n":
                        sr, datumoj = silab_memoro['paragrafo']
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
        i=0
        print("silaboj   ", silaboj)

        for i, sil in enumerate(silaboj):
            #print("sil", sil)
            segmentoj = []  # reŝargu por ĉiu silabo
            
            ##### testo por nure po-litera legado !  kiu povas funciigi kun plej maldika silab_memoro  nur literoj ! utilas por kontrolo de litero-registraĵo        #k=0
            print("SIL******",sil)
            temp_sil = sil
            while len(temp_sil)>0:
                if KONFIGURO.get("testo_po_litera") ==True:   
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
          
    # def aldoni(dosiero, tuto):
    #     #SAMPLA_RAPIDO = 32000
    #     try:
    #         sr, malnova = wavfile.read(dosiero, mmap=False)
    #         if sr == sampla_rapido:
    #             kombinitaj = np.concatenate([malnova.flatten(), tuto])
    #             wavfile.write(dosiero, sampla_rapido, kombinitaj.astype(np.int16))
    #         else:
    #             wavfile.write(dosiero, sampla_rapido, tuto)
    #     except Exception as e:
    #         print(f"Eraro dum legado: {e}")
    #         wavfile.write(dosiero, sampla_rapido, tuto)
    #     #print("SAVADO")   
        
        
    def aldoni(dosiero,tuto):
        if os.path.exists(dosiero):
            # 2. Legi ekzistantan dosieron
            sr_ekzista, datumoj_ekzistaj = wavfile.read(dosiero)
            
            # 3. Kontroli kongruecon
            if sr_ekzista != sampla_rapido:
                raise ValueError(f"Malsamaj samplaj rapidecoj: {sr_ekzista} vs {sampla_rapido}")
            
            # 4. Kunmeti datumojn (alglui je la fino)
            tuto = np.concatenate([datumoj_ekzistaj, tuto])
            
        # 5. Skribi (aŭ reskribi) la dosieron kun la nova enhavo
        wavfile.write(dosiero, sampla_rapido, tuto.astype(datumoj_ekzistaj.dtype if os.path.exists(dosiero) else tuto.dtype))
       
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



 
    # **************************************  NOMBROJ

    def testo_traduko_nombro (vorto):
        # return a Boolean if the match was met
        global nombroflago,last_nombroflago
        print("vorto nombro " ,vorto)
    # Serĉas iun ajneturn not bool(re.search(r'[a-zA-Zà-ÿÀ-ß]', teksto, re.UNICODE))
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


    
    interpunkcio = ",.;?!\n"
    
    
    # Legu kaj ŝargu la n
    vortarolinioj = legu(vortarodosiero).lower().split("\n")
    vortaro = {}
    for linio in vortarolinioj:
        if len(linio) > 0:
            [vorto, kategorio] = linio.split(",")
            vortaro[vorto] = (kategorio)
    print("VORTARO     ",vortaro)
    
    
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
    #sufiksoj = akiru_kategoriojn("s")
    
    # Prefiksoj
    prefiksoj = akiru_kategoriojn("pz")
    prefiksoj.append("ne")
    print("Prefiksoj",prefiksoj) 
    
    
    laŭteco_faktoro=KONFIGURO.get("laŭteco_faktoro")
    pika_maks=KONFIGURO.get("pika_maks")
    lasta_malplifortigo=KONFIGURO.get("lasta_malplifortigo")
         
    if KONFIGURO.get('uzi_fontajn')==True:
        fonemujo=dosierujo+"fonemoj"
    else:
        fonemujo=dosierujo+"fonemojx"

    silab_memoro={}
    print("fonemujo",fonemujo)
    silab_memoro=ŝargi_kaj_normaligi_silabojn(fonemujo, celo_rms=0.08)
    #print(silab_memoro)
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
    print (teksto)
    time.sleep(5)
    # Analizu vortojn kaj skribu rezultojn
    parts = re.split(r'(["\';+\-/*=)\( ]|\n)', teksto)
    parts = [p for p in parts if p != ' ']
    print (parts)
    # Forigu malplenajn/nul-signajn erojn (ekz. spacoj, se ne bezonataj)
    #result = [part for part in parts if part and not part.isspace()]
    #print("Traktado de aportrofo kaj citiloj kaj komo kaj blankoj",result)
    result = parts
    vortoj = result
    
    #print("Teksto:", len(vortoj), "vortoj - Vortaro:", len(vortaro), "morfemoj")
    print("teksto studata   ",vortoj)
    analizo=[]   
    
    
    #print(silaboj)
    # Aŭtomate eligu la ekziston de silab_memoro
    if not silab_memoro:
        print("Averto: silab_memoro estas malplena!")
    
    unua_silabo = next(iter(silab_memoro))
    sampla_rapido, _ = silab_memoro[unua_silabo]
    
    #
    nombrazono=""
    interpunkcioflago=False    
    aŭdio_segmentoj = []
    plena_aŭdio=[]
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
        return re.findall(r'\w+|[€,!?;\.\n]', vorto)
    
    global index
    index=0
    print("KOMENCO ĈEFA BUKLO")
    while index<len(vortoj):
        vorto = vortoj[index] # sorted(vortoj, key=esperanta_klavo):
        silaboj=[]        
        #print(" antau +++++++++++++++++++++++++++++++++++++++++++++++++++",vorto)
        if vorto== "\n" :
           print ("lini_finio") 
        
        if akcepti_vorton(vorto): # detektas AKRONIMOJ
            akronimoflago=True
            last_nombroflago=False
        else:
            akronimoflago=False
            
        nombroflago,tradukitanombro= testo_traduko_nombro(vorto)  # serĉas kaj tradukas literen nombron
        print("KIO ESTAS    +++++++++++  ",akronimoflago,nombroflago,tradukitanombro)
    
        if akronimoflago == True :
            vorto = re.sub(r'[.\',/]', "", vorto)
            #vorto=re.sub(r'[.'',''/]',"",vorto)
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
                jamcitilo=ludu_vorton_el_memoro(jamcitilo,interpunkcio,
                    silaboj,
                    silab_memoro,
                    laŭteco_faktoro,
                    pika_maks,
                    fade_proporcio=0.8,
                    fade_fino=0.30,
                    silento_sojlo=0.005
                )
                aldoni_silenton(aŭdio_segmentoj, sampla_rapido, silento_akronimo)
                #print("n ",n)    
                n=n+1
    
        elif nombroflago == True :
           nombrazono=tradukitanombro
           x=index+1
           if x<len(vortoj)-1:
               if vortoj[x]in',-+/*=':
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
                       index=index+2
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
               jamcitilo=ludu_vorton_el_memoro(jamcitilo,interpunkcio,
                   silaboj,
                   silab_memoro,
                   laŭteco_faktoro,
                   pika_maks,
                   fade_proporcio=0.8,
                   fade_fino=0.30,
                   silento_sojlo=0.005
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
                #vorto=disigu_interpunkcion(vorto)            
                if vorto[-1] in ",.!?\n" and len(vorto)>1:
                    interpunkcio=vorto[-1]
                    #print("filrilo de punkto",vorto)
                    vorto = vorto[:-1]
                    delimiter = "" # Define a delimiter
                    vorto = delimiter.join(vorto)     
                    print("filrilo de punkcio",vorto)                    
                else:
                    interpunkcio=" " # eble okazigos tro dasilento?        
                    #vorto=vorto.pop()
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
           
            plena_aŭdio,jamcitilo=ludu_vorton_el_memoro(jamcitilo,interpunkcio,
                silaboj,
                silab_memoro,
                laŭteco_faktoro,
                pika_maks,
                fade_proporcio=0.8,
                fade_fino=0.30,
                silento_sojlo=0.005
            )
            #last_nombroflago=False
                    ############################## Konverto
        if interpunkcio in ",;":
            aldoni_silenton(aŭdio_segmentoj, sampla_rapido, silento_komo)  
                     
        if interpunkcio in ".!?" or index==len(vortoj)-1: #legado frazo post frazo
            # En via ĉefa kodo:
            aldoni_silenton(aŭdio_segmentoj, sampla_rapido, silento_punkto)
            tuto = prepari_aŭdion_simple(aŭdio_segmentoj, sampla_rapido)
            if len(tuto) > 0:
                print(tuto.dtype)
                print(np.min(tuto), np.max(tuto))
                print("nova frazo")
                aldoni_frazon(tuto)
              

                aŭdio_segmentoj =[]
                # Savi
            if KONFIGURO.get('registri_finan_rezulton')==True:                 
                aldoni(eliga_dosiero,tuto)
                        ########################
        
            
        index=index+1
    print ("mankantaj = ",mankantaj)
    return True
##############################################
class SonoLudilo:
    def __init__(self):
        self.son_vico = []
        self.ludilo = Sonilo()
        self.vico_lock = Lock()
        self.vico_plena = Event()
        self.max_vico = 4
        self.atendi_liberigon = Event()

    def aldoni_sonon(self, sono):
        with self.vico_lock:
            if len(self.son_vico) < self.max_vico:
                self.son_vico.append(sono)
                self.vico_plena.clear()
                if not self.ludilo.is_playing():
                    self.ludi_sekvencajn_sonojn()
            else:
                self.vico_plena.set()  # Signalas ke vico estas plena
                self.atendi_liberigon.wait()  # Atendas liberiĝon

    def ludi_sekvencajn_sonojn(self):
        with self.vico_lock:
            if self.son_vico:
                sono = self.son_vico.pop(0)
                self.atendi_liberigon.clear()  # Resetas eventon
                self.ludilo.play(
                    sono,
                    on_finish=lambda: self.sono_finis()
                )

    def sono_finis(self):
        with self.vico_lock:
            if self.son_vico:
                self.ludi_sekvencajn_sonojn()
            else:
                self.atendi_liberigon.set()  # Signalas ke vico liberiĝis


    def analizi_frazojn(self, frazoj):
        for frazo in frazoj:
            sono = traduku_frazon_al_sono(frazo)  # Via ekzistanta funkcio
            self.aldoni_sonon(sono)
            if self.vico_plena.is_set():
                self.atendi_liberigon.wait()  # Atendas liberiĝon

# ======= KIVY GUI =======
class LegiloGUI(Boxo):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # Statuso
        self.statuso = Etikedo(text="Preta", size_hint=(1, 0.1))
        self.add_widget(self.statuso)

        # Teksto-fenestro (redaktebla)
        self.teksta_ingo = TekstoIn(multiline=True, size_hint=(1, 0.6))
        self.add_widget(self.teksta_ingo)

        # Butonpanelo
        buton_kadro = Boxo(size_hint=(1, 0.2))
        self.add_widget(buton_kadro)

        # Legi butono
        btn_legi = Butono(text="Legi")
        btn_legi.bind(on_press=self.legi)
        buton_kadro.add_widget(btn_legi)

        # Malplenigi butono
        btn_malplenigi = Butono(text="Malplenigi")
        btn_malplenigi.bind(on_press=lambda x: self.malplenigi())
        buton_kadro.add_widget(btn_malplenigi)

        # Ŝargi dosieron butono
        btn_schargi = Butono(text="Ŝargi .txt")
        btn_schargi.bind(on_press=lambda x: self.montri_schargi_popup())
        buton_kadro.add_widget(btn_schargi)

        # Placeholder agordoj
        btn_agordoj = Butono(text="Agordoj")
        btn_agordoj.bind(on_press=lambda x: self.statuso.text("Fenestro Agordoj (demo)"))
        buton_kadro.add_widget(btn_agordoj)

        # Android-fringo-glito placeholder
        if platformo.system() == 'Android':
            self.statuso.text += " | Android-glito aktivita (L por legi)"

    # ======= EVENTOJ =======
    def legi(self, instance):
        sonigu = SonoLudilo()
        frazo_listo = []
        teksto = self.teksta_ingo.text.strip()
        if not teksto:
            self.statuso.text = "Bonvolu enigi tekston por legi."
            return
        self.statuso.text = "Leganta..."        
       # Startu analizon en fadeno
        Thread(target=sonigu.analizi_frazojn, args=(frazo_listo,)).start()
       
       
       ##########################################

    def malplenigi(self):
        self.teksta_ingo.text = ""
        self.statuso.text = "Preta"

    # ======= DOSIERO ŜARGO =======
    def montri_schargi_popup(self):
        dosiero_listo = self.listigi_txt_dosierojn()
        if not dosiero_listo:
            self.statuso.text = "Neniu .txt trovebla en nuna dosierujo"
            return

        layout = GridO(cols=1, spacing=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for dos in dosiero_listo:
            btn = Butono(text=dos.name, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btnx: self.schargi_dosieron(btnx.text))
            layout.add_widget(btn)

        rulilo = Rulilo(size_hint=(1, 1))
        rulilo.add_widget(layout)
        popup = Popupo(title="Elektu .txt", content=rulilo, size_hint=(0.9,0.8))
        popup.open()
        self.popup = popup  # konservi referencon

    def listigi_txt_dosierojn(self):
        nuna = Vojo('.')
        return list(nuna.glob('*.txt'))

    def schargi_dosieron(self, nomo):
        with open(nomo, 'r', encoding='utf-8') as f:
            enhavo = f.read()
        self.teksta_ingo.text = enhavo
        self.statuso.text = f"Ŝargita {nomo}"
        if hasattr(self, 'popup'):
            self.popup.dismiss()

# ======= ĈEFA APP =======
class LegiloApp(Appo):
    def build(self):
        return LegiloGUI()

# ======= KOMENCU =======
if __name__ == "__main__":
    LegiloApp().run()











