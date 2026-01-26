#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 14 07:06:21 2025

@author: clopeau
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 13:17:44 2025

@author: clopeau
tiu programo konstruas vortaron kiu kunligas radikoj ( sen afiksoj kaj finaĵoj) ĉerpiataj el vortar.txtraktas tekston, kaj ties silabo-vicoj 
                                 
 (fakte por memoro, estas pluraj ebloj ĉu apartigi moneme ĉu silabike
arb·ar·o 	arb-ar-o    ar-ba-ro
bon·aĵ·o 	bon-aĵ-o    bo-na-ĵo
mal·amik·o 	mal-amik-o  ma-la-mi-ko)


"""


import re
import time
import json
import pickle
   # FUNKCIAS  BONE POR KREADO DE SILABIGITA VORTARO
# ne traktas prefiksojn nek sufiksojn ĉar analizas radikoj  el vortaro
vortaro_analizo = True


print(" ATENTU VORTARO ESTOS TRAKTATA ->  ", vortaro_analizo)
print('-------------------------------------------------')
print("ŝanĝu permane valoron de variablo vortaro_analizo por via celo")

time.sleep(3)

ek = 0
silabo = ""
silabo_komenco = ""
i = 0
konsonanto_sekvo = []
trovita_finajxo = "toto"

konsonantoj = [
    'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'z',
    'ĉ', 'ĝ', 'ĥ', 'ĵ', 'ŝ', 'ŭ']  # Aldonis ĉapelitajn konsonantojn]
vokaloj = ['a', 'e', 'i', 'o', 'u', 'ŭ']
"""
Splitas Esperantajn vortojn kaj returnas simplan liston de partoj en ĝusta ordo
"""
# Listo de komunaj prefiksoj (ordigita de plej longa al plej mallonga)
prefiksoj = ['al', 'ali', 'eks', 'dis', 'mal', 'pra', 'bo', 'ge', 'ek', 're', 'mis', 'trans', 'preter', 'en', 'ĉirkaŭ', 'super', 'sub','tra', 'sur', 'preskaŭ', 'antaŭ', 'anstataŭ', 'apenaŭ', 'malgraŭ', 'kontraŭ', 'ambaŭ', 'pri', 'ĉi', 'almenaŭ', 'ĝis', 'per', 'pli','tuj','inter']

# listo de senfinĵoj
vortujo=['plus', 'minus' , 'egalas', 'kiam']

# Listo de komunaj sufiksoj (ordigita de plej longa al plej mallonga)
sufiksoj = [
    'estr', 'aĉ', 'aĵ', 'ad', 'an', 'ar', 'ebl', 'ec', 'eg', 'ej', 'em',
    'end', 'er', 'et', 'id', 'ig', 'iĝ', 'il', 'in', 'iv', 'ind', 'ing', 'ism', 'ist', 'obl', 'on', 'op', 'uj', 'ul', 'um', 'ĉj', 'nj', 'iz'
]

# Finaĵoj por trakti
finajxoj = ['ajn', 'ojn', 'aj', 'oj', 'an', 'on', 'en', 'jn', 'j', 'n', 'a',
            'o', 'e', 'i', 'u', 'as', 'is', 'os', 'us', 'int', 'ant', 'ont', 'unt']

# Permesataj duopoj
permesatajduopoj = ['sk', 'fr', 'str', 'ŝtr', 'dr', 'dv', 'st', 'ŝt', 'tr', 'pr', 'ps', 'pl', 'spl', 'lpt', 'bl', 'br', 'skr', 'gl', 'kr', 'fl',
                    'ft', 'gr', 'gv', 'kl', 'kn', 'kv', 'sc', 'skl', 'skv', 'ŝl', 'sl', 'ŝm', 'sm', 'ŝn', 'sp', 'ŝp', 'spr', 'ŝpr', 'ŝr', 'sv', 'ŝv', 'sk', 'vr']


# JEN KAPA KUNKCIO POR TRAKTADO DE VORTARAJ RADIKOJ
# Tiu kaze teksto estas tuta listo el la radika vortaro ######

def split_esperanto_vortaro(teksto):
    rezulta_listo = []

    # if not purigita_vorto:
    #     rezulta_listo.append([vorto])
    #     continue

    partoj = []
    restanta_vorto = teksto

    # Traktu finaĵojn
    trovita_finajxo = ""   # en votar.txt    finaĵoj estas jam formetitaj  rilate  vortaro
    # ili estos aldonitaj per la ĉi supra listo same kiel afiksoj

    # Aldonu la radikon
    if restanta_vorto:
        restanta_vorto, trovita_finajxo = silabigo(
            restanta_vorto, partoj, trovita_finajxo)
        # silabigi radikojn
        # print(restanta_vorto, "----- trovita_finajxo =", trovita_finajxo,"----------", )
        partoj.append(restanta_vorto)

    rezulta_listo.append(partoj)
    print(rezulta_listo, "  ++")
    return rezulta_listo

# Funkcio por montri rezultojn bele


def montri_rezultojn(rezultoj):
    for i, partoj in enumerate(rezultoj):
        if isinstance(partoj, list):
            pass
            # print(f"Vorto {i+1}: {' + '.join(partoj)}")
        else:
            pass
            # print(f"Vorto {i+1}: {partoj}")

# Funkcio por disponi ĉiun analizon por plua silabigo


def liveri_rezultojn(rezultoj):
    for i, partoj in enumerate(rezultoj):
        if isinstance(partoj, list):
            ĉeno = partoj  # por posta trakto
            # print(ĉeno)
        else:
            pass
            # print(f"Vorto {i+1}: {partoj}")

# --------------------------------------------------------------------------


def silabigo(vorto, partoj, trovita_finajxo):
    i = 0
    silabo = ""
    silabo_komenco = ""
    konsonanto_sekvo = ""
    silabaro = []
    temp_sufiksoj = []

    while i < len(vorto):
        print(":::", vorto, i, vorto[i])
        if vorto[i] in vokaloj and i != 0:  # vokalo
            silabo_komenco += vorto[i]
            if i+1 <= len(vorto)-1:
                if vorto[i+1] in "ŭaeiou":  # por el trovi diftongoj eŭ  aŭ
                    silabo_komenco += vorto[i+1]
                    # if i+1 >= len(vorto)-1:
                    #     break
                    i = i+1

            silabo = silabo_komenco
            silabo_komenco = ""
            konsonanto_sekvo = ""

        else:
            # foje estas vokalo komence de vorto
            konsonanto_sekvo = konsonanto_sekvo+(vorto[i])
            silabo_komenco += vorto[i]
            if i == len(vorto) - 1:  # tiu konsonanto estas lasta litero de radiko !
                silabo = silabo_komenco
                print("######", i, silabo)
            if i == 1 and silabo_komenco[0] in vokaloj:
                silabo = silabo_komenco
                # silabo_komenco=""
                # konsonanto_sekvo=""

        # print("unua trakto  ", silabo, silabaro, konsonanto_sekvo)
        if silabo != "":
            print(" silabo x,", silabo)
            if all(litero in konsonantoj for litero in silabo):
                print("nur konsonantoj en silabo !")
                print("TRAKTENDA ", silabaro, silabo, "-*-")

                if len(silabaro) >= 1:  # tiam kunligo kun antaua silabo
                    if silabo not in permesatajduopoj:
                        # print(i,len(vorto)-1)

                        if i == len(vorto)-1:  # estas je fino de radiko
                            if len(silabaro[-1]) > 1:
                                # finiĝas per 2 vokaloj
                                if silabaro[-1][-1] in vokaloj and silabaro[-1][-2] in vokaloj:
                                    print("COUCOU ", silabo)

                                    if silabaro[-1][1] == 'ŭ':
                                        silabaro[-1] = silabaro[-1]+silabo
                                        silabo_komenco = ""
                                        silabo = ""

                                    else:
                                        silabo = silabaro[-1][-1]+silabo
                                        print("1", silabo, silabo[0])
                                        if silabo[0] == 'ŭ':
                                            silabaro[-1] = silabaro[-1] + \
                                                silabo[-1]
                                            print(silabaro[-1], "ĝi funkcias")
                                            silabo = ""
                                        else:
                                            silabaro[-1] = silabaro[-1][:-1]
                                            print("2", silabaro[-1])
                                            silabaro.append(silabo)
                                        silabo_komenco = ""
                                else:
                                    silabaro[len(silabaro)-1] += silabo
                                    print(" nura konsontaro algluo 1 *",
                                          silabaro, silabo, silabo_komenco)
                            else:
                                silabaro[len(silabaro)-1] += silabo
                        else:
                            silabaro[len(silabaro)-1] += silabo[0]
                            # print("kompleksa  ",silabaro[len(silabaro)-1],silabo[0])
                            # divido de konsonanto_sekvo malpermesita
                            silabo_komenco = silabo[1:]
                            # silabo_komenco =""
                            # print( " nura konsontaro algluo 1", silabaro,silabo,silabo_komenco)

                    else:
                        silabaro[len(silabaro)-1] += silabo
                        print(" nura konsontaro algluo 2", silabaro)
                        silabo = ""
                else:  # tiam celas fonetikeblan solvon kun plej proksima prefikso au sufikso ĉar estas nur unu silabo en radiko. tio rezultas pro erara malkovro de prefikso au sufikso
                    print("KLOMPLXAĴO")
                    # en tiu stato partoj entenas prefiksoj
                    if len(partoj) >= 1 and len(temp_sufiksoj) == 0:
                        # print(silabo, (i+len(konsonanto_sekvo)+1),len(vorto))  #tiam endas dividi konsonantoj
                        # tiam endas dividi konsonantoj
                        if (silabo not in permesatajduopoj) and (i+len(konsonanto_sekvo) == len(vorto)):
                            silabo = partoj[-1] + silabo_komenco[0]
                            partoj.pop()
                            # print(silabo,"////1  ", temp_sufiksoj)
                            silabaro.append(silabo)
                            silabo = ""
                        else:
                            silabo = partoj[-1] + silabo_komenco
                            partoj.pop()
                            # print(silabo,"////1+  ", temp_sufiksoj)
                            silabaro.append(silabo)
                            silabo = ""
                    else:
                        if len(temp_sufiksoj) >= 1:
                            silabo = silabo_komenco + temp_sufiksoj[0]
                            # print(silabo,"////2", temp_sufiksoj)
                            temp_sufiksoj.pop(0)
                            silabaro.append(silabo)
                            silabo = ""
                        else:
                            if trovita_finajxo:
                                silabo = silabo_komenco + trovita_finajxo
                                # print(silabaro, silabo)
                                silabaro.append(silabo)
                                silabo = ""
                                trovita_finajxo = ""
                                # print("trovita_finajxo = ''")
                            else:
                                print("Kazo de nura konsonanto")
                                silabaro.append(silabo)
                                silabo=""
            else:
                print("kruco  ", silabo)
                if len(silabo) > 2:  # almenau tri literoj kun fina vokalo
                    print("ĉu vokalo", silabo[0].lower(), silabo)
                    if silabo[0].lower() in vokaloj:
                        # kiam estas prefikso , ne povas tie okazi ĉar afiksoj jam tranĉitaj
                        if len(partoj) > 0:
                            pass
                        else:  # kreado de unuvokala silabo kaj normala silabo
                            print(i, silabaro)
                            silabaro.append(silabo[0])
                            print(i, silabaro)
                            silabaro.append(silabo[1:])
                            print(i, silabaro)

                    else:
                        print("kunteksto", silabo[-1], silabo[:-1])
                        # konsonanto duopo malpermesata
                        if silabo[:-1].lower() not in permesatajduopoj and silabo[-1] not in "ŭaeiou":
                            print(silabo[:-1], " lasta karaktro", silabo[-1])
                            retropuŝaĵo = silabo[0]
                            print("retropus^jo ", retropuŝaĵo, silabaro)
                            silabaro[len(
                                silabaro)-1] = silabaro[len(silabaro)-1]+retropuŝaĵo
                            silabo = silabo[1:]
                            silabaro.append(silabo)
                            # print("tuj",silabo,silabaro)
                            silabo = ""
                        # kazo KV? konsonanto vokalo kaj indiferenta aux vere malpermesata konsonantoj-duopo
                        elif silabo[:-1].lower() not in permesatajduopoj:
                            # print(silabo[:-1], " lasta konsonanto" ,silabo[-1])
                            if len(silabaro) >= 1 and silabo[0] in vokaloj:
                                # do ekzistas unu au pli da silabo antaue
                                # tiam oni puŝu unuan literon de tiu malpermesata al
                                # antaua silabo
                                silabaro[len(
                                    silabaro)-1] = silabaro[len(silabaro)-1]+silabo[0]
                                print("A", silabaro[len(silabaro)-1])
                                silabo = silabo[1:]
                                print("A", silabo)
                                silabaro.append(silabo)
                            elif len(silabaro) >= 1 and silabo[-1] in vokaloj and silabo[-2] not in vokaloj:
                                silabaro[len(
                                    silabaro)-1] = silabaro[len(silabaro)-1]+silabo[0]
                                print("B", silabaro[len(silabaro)-1])
                                silabo = silabo[1:]
                                silabaro.append(silabo)
                                silabo = ""
                                print("B", silabo)
                            else:
                                pass
                                print("C", silabo)
                                # silabo_koemenco=silabo
                                silabaro.append(silabo)
                                silabo = ""
                        else:
                            silabaro.append(silabo)
                            silabo = ""
                else:
                    print("komenco ***", silabo_komenco, silabo)
                    # silabo_komenco[0] in vokaloj:
                    if i == 1 and silabo[0] in vokaloj:
                        print("detekto ekz por  'esper' kaj 'aer' ")
                        silabaro.append(silabo)
                        silabo = ""
                        silabo_komenco = ""

                    else:
                        silabaro.append(silabo)
                        silabo = ""
                        print("nenia problemo ", silabaro)

        else:  # momento por kontroli ĉu silabo_komenco ne arigas malpermesataj
            if len(silabo_komenco) > 1 and silabo_komenco not in permesatajduopoj:
                print("jen fuŝa komenco", silabo_komenco)
                if len(silabaro) > 0:
                    silabaro[-1] = silabaro[-1]+silabo_komenco[0]
                    silabo_komenco = silabo_komenco[1:]
                pass
            else:
                pass

        print(i, vorto[i], "silabo", silabo, "komenco",
              silabo_komenco, "silabaro", silabaro)
        if "ŭl" in silabaro:
            print("FIN")
            break
        i = i+1

    return silabaro, trovita_finajxo
#


# --------------------------------------------------------------------------


def flatigi_liston(nesta_listo):
    simpla_listo = []
    for elemento in nesta_listo:
        if isinstance(elemento, list):
            simpla_listo.extend(flatigi_liston(elemento))
        else:
            simpla_listo.append(elemento)
    return simpla_listo


def trovi_multoblajxojn(vortoj):
    """
    Trovas vortojn kiuj aperas pli ol unu fojon en la listo
    """
    multoblajxoj = {}

    for vorto in vortoj:
        if vorto in multoblajxoj:
            multoblajxoj[vorto] += 1
        else:
            multoblajxoj[vorto] = 1

    # Filtras nur tiujn vortojn kiuj aperas pli ol unu fojon
    rezulto = {vorto: count for vorto, count in multoblajxoj.items()
               if count > 1}

    return rezulto, trovita_finajxo


def disigi_frazon(frazo):
    return ("\n".join(frazo.split()))


def savi_vortaron(vortaro, dosiernomo, formato='json'):
    """
    Savas vortaron en dosieron.

    Parametroj:
    vortaro (dict): La vortaro por savi
    dosiernomo (str): Nomo de la dosiero
    formato (str): 'json' aŭ 'pickle' - formato por savi
    """
    try:
        if formato == 'json':
            with open(dosiernomo + '.json', 'w', encoding='utf-8') as f:
                json.dump(vortaro, f, ensure_ascii=False, indent=2)
        elif formato == 'pickle':
            with open(dosiernomo + '.pkl', 'wb') as f:
                pickle.dump(vortaro, f)
        else:
            raise ValueError("Formato devas esti 'json' aŭ 'pickle'")
        print(f"Vortaro sukcese savita al {dosiernomo}.{formato}")
    except Exception as e:
        print(f"Eraro dum savado: {e}")


def ŝargi_vortaron(dosiernomo, formato='json'):
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
            with open(dosiernomo + '.json', 'r', encoding='utf-8') as f:
                vortaro = json.load(f)
        elif formato == 'pickle':
            with open(dosiernomo + '.pkl', 'rb') as f:
                vortaro = pickle.load(f)
        else:
            raise ValueError("Formato devas esti 'json' aŭ 'pickle'")

        print(f"Vortaro sukcese ŝargita el {dosiernomo}.{formato}")
        return vortaro
    except Exception as e:
        print(f"Eraro dum ŝargado: {e}")
        return {}
  # ""


def silabojlisto(vortaro):
    """
    Ricevas vortaron kun strukturo:
    { vorto1: [silabo1, silabo2, ...], vorto2: [silaboX, ...], ... }
    kaj redonas liston de unikaj silaboj, alfabete ordigitaj, sen oblaĵoj.
    """
    # Uzu 'set' por aŭtomate forigi oblaĵojn
    unikaj_silaboj = set()
    for silablisto in vortaro.values():
        unikaj_silaboj.update(silablisto)

    # Konvertu la 'set' al listo kaj ordigu alfabete
    return sorted(list(unikaj_silaboj))

# Ekzemploj de uzo:


if __name__ == "__main__":
    if vortaro_analizo:
        formato = "pickle"
        silaba_vortaro_dosiero = "/home/clopeau/lingvaprogramado/silaba_vortaro"
        silabaro_dosiero = "/home/clopeau/lingvaprogramado/silabaro"
        temp_sufikso = []  # malplena
        radikaj_silaboj = []
        f = open("vortar.txt", "r")
        teksto = f.read()
        # print(teksto1)
        print("*****************************************************")
 
        silaba_vortaro = {}
        vortoj = teksto.split() # teksto (vortar.txt) iĝas tabelon
        vortoj = vortoj + finajxoj + prefiksoj + sufiksoj + vokaloj + konsonantoj
        # print(type(vortoj))
        # print(vortoj)

# POR TESTO
# POR TESTO
        #silaba_vortaro_dosiero="/home/clopeau/lingvaprogramado/essai"
        # vortoj=['vulkan'  , ' esper', 'babil'  ,'aer', ' bien', 'vektor', 'viand', 'izrael', 'trakt','abort' ,'abak', 'aŭgust' , 'standard', 'nuanc']
        #vortoj=['ali' , 'kiam' , 'aliel' ]
        #vortoj=['internaci']
        # print("vortoj listo", vortoj)
        # print()

        for vorto in vortoj:
            # Forigu ne-leterajn signojn komence/fine
            vorto = re.sub(r'^[^a-zA-Zĉĝĥĵŝŭ]+|[^a-zA-Zĉĝĥĵŝŭ]+$', '', vorto)

            rezultoj = split_esperanto_vortaro(vorto)
            rezultoj = flatigi_liston(rezultoj)
            # if vorto =="preter":
            #      print (" +++++++++++++++++++   ", vorto)
            #      print("totototo",str(rezultoj))
            #      break

            silaba_vortaro.update({vorto: rezultoj})
            print("kontrolo", silaba_vortaro.get(vorto))

        print("silba vortaro ***********",silaba_vortaro)

# savi vortaron kun silaba analizo , estas dic strukturo pyhton
        savi_vortaron(silaba_vortaro, silaba_vortaro_dosiero, formato)
        rezultoj = []
        rezultoj = silabojlisto(silaba_vortaro)
        print("tipo de rezultoj", type(rezultoj), rezultoj)
        silabarotuta = rezultoj + prefiksoj + sufiksoj + \
            finajxoj + vokaloj + konsonantoj + vortujo # ĉiuj registrendaj silaboj
        # print("por vidi  ",silabarotuta)
# savi liston silabaro en pkl dosiero
        # silabaro = trovi_multoblajxojn(silabarotuta)
        silabaro = silabarotuta
        print("silabaro  +++++++++++++++  ",silabaro)
        savi_vortaron(silabaro, silabaro_dosiero, formato)

# Savi  en txt dosiero alfabete oridigita sinsekvo de silaboj
        silabarotuta = str(silabarotuta)
        silabarotuta = silabarotuta.replace(",", "")
        silabarotuta = silabarotuta.lower()  # transskribi minusklen
        silabarotuta = silabarotuta.replace("'", "")
        silabarotuta = silabarotuta[1:-1]
        # donas po unu silabo en ĉiu linio
        silabarotuta = disigi_frazon(silabarotuta)
        file = open("silabaro.txt", "w+")
# POR TESTO
        #file = open("votaro_silabaro_essai .txt", "w+")
        ## silabaro = str(silabarotuta)
        file.write(silabarotuta)
        file.close()
