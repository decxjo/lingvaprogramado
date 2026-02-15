#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 09:54:43 2026

@author: clopeau
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Globalaj parametroj por la legilo.
Ĉiuj agordoj estas facile ŝanĝeblaj tra la GUI.
"""

KONFIGURO = {
    # Dosieroj
    'tekstodosiero': 'texte3.jsb',
    'vortarodosiero': '1.csv',
    'silaba_vortaro_dosiero': '/home/clopeau/lingvaprogramado/silaba_vortaro.pkl',
    'silabaro_dosiero': '/home/clopeau/lingvaprogramado/silabaro.pkl',
    'fonemujo_fontaj': '/home/clopeau/lingvaprogramado/fonemoj',
    'fonemujo_normaligitaj': '/home/clopeau/lingvaprogramado/fonemojx',
    'eliga_dosiero': '/home/clopeau/lingvaprogramado/registraĵo.wav',
    
    # Reĝimoj
    'testo_po_litera': False,
    'uzi_fontajn': False,
    'registri_finan_rezulton': False,
    'normaligisilaboj': False,
    
    # Silentoj (sekundoj)
    'silento_komo': 0.7,
    'silento_punkto': 1.2,
    'silento_cifero': 0.4,
    'silento_akronimo': 0.4,
    

    # Aŭdi-parametroj
    'celo_rms': 0.08,
    'laŭteco_faktoro': 1.15,
    'pika_maks': 0.60,
    'lasta_malplifortigo': 0.85,
    'fade_proporcio': 0.30,
    'fade_fino': 0.30,
    'silento_sojlo': 0.005,
    
    # Lingvaj datumoj
    'konsonantoj': [
        'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'z',
        'ĉ', 'ĝ', 'ĥ', 'ĵ', 'ŝ', 'ŭ'
    ],
    'cifera_mapo': {
        '1': 'unu', '2': 'du', '3': 'tri', '4': 'kvar', '5': 'kvin',
        '6': 'ses', '7': 'sep', '8': 'ok', '9': 'naŭ', '0': 'nul',
        '(': 'ekparentezo', ')': 'finparentezo', '[': 'ekkrampo', ']': 'finkrampo',
        '{': 'ekakolado', '}': 'finakolado', ':': 'kolono', '+': 'plus',
        '-': 'minus', '*': 'oble', '/': 'one', '€': 'euro', '.': 'punkto',
        "'": 'apostrofo', '"': 'citilo', '=': 'egalas'
    },
    'grekaj_literoj': {
        'α': 'alfa', 'β': 'beta', 'γ': 'gamo', 'δ': 'delta', 'ε': 'epsilono',
        'ζ': 'zeto', 'η': 'eto', 'θ': 'teto', 'ι': 'joto', 'κ': 'kapa',
        'λ': 'lambda', 'μ': 'mu', 'ν': 'nu', 'ξ': 'ksi', 'ο': 'omikrono',
        'π': 'pi', 'ρ': 'ro', 'σ': 'sigma', 'τ': 'taŭ', 'υ': 'ipsilono',
        'φ': 'fi', 'χ': 'ĥi', 'ψ': 'psi', 'ω': 'omego'
    }
}
    # Legu kaj preparu la tekston
    #--------------------------------------------------
    #------------------------------------------------
    ##########    por testi   
    #teksto= "aŭgusto"
    #teksto = " astrero , astriĝi , skulptaĵo " 
    #teksto="mi vidis plian malfrenezulejojn vidis plian interesitaron ĉirkaŭ fonto"
    #teksto="prenita  malkonsentilaĵo"
    #teksto= "skoto"
    #teksto="tabelojn"
    #eksto="malpli kaj malpli"
    #teksto="bitojn  kiam diras nenion"#"kvitetoj ŝuldas bonan guston"#"re kontentas , ke ci aliros en lernejon.  en frenezulejon  lernantotabelo  strato"  
    #teksto="lernejon" 
    #teksto =" legu esperant o"
    #teksto="lernantotabelo"
    
    #teksto="longa "
    #teksto="Do la plejparto de la landoj havas krizon krom se la civitanoj konsentas ricevi malpli kaj malpli da enspezoj sed tio ne povas longtempe daŭri"
    #teksto="long tempe  guto  tempe  longtempe "#" daŭri"
    #teksto="guto, esperanto."
    #teksto = " Mi mem estas ano de Lokaj Interŝanĝaj Sistemoj LIS. Ili uzas, ne mono, sed kontunuoj, kies valoro baziĝas sur la fido, kiun la grupanoj havas unuj al la aliaj. Kompreneble, tio funkcias sur malgranda skalo, kaj la grupanoj konas sin reciproke. "
    #teksto="ne mono sed kontunuo"
    #teksto="En la jaro 2025  LIN Z24  estis Johano."
    #teksto="kiu traktos (pri disvolviĝo de esperanto  22,45 -78"
    #teksto="( 6+6 =12  "
    #teksto=" mi estas esperantistareto  "
    #teksto=" ĝoja kristnasko  2025   en ruĝa  ker  kambr"
    #teksto="2026"
    #teksto="keri   identeco"
    #teksto=" kosto 20,45 "
    #teksto=" banano abonantaro. sablero tuj  tuje estas"
    #teksto='tuje , "estas, " 3,14  [  20.13 €tuto.'
    #teksto=("20")
    #teksto="reciproke"
    #teksto=' plenbrakoj  plenbrakoj.'   #',   plenbrakoj.'
    #teksto="mi amas kontente, ĉiuj. kaj mi atendas 2 sekundoj"
    #teksto="Lokaj  Interŝanĝaj Sistemoj LIS .  La ĝardeno "
    #teksto="LIS"
    #teksto="hodiau mi kontentis restadi en ĝardeno. Mi atendis ĝis la 10 a horo. Bananoj abonantaro. sablero tuj  tuje   estas. En la jaro 2025  LIN Z24  estis Johano datrevenoj. "
    #teksto="dum jaro 2025 la lernantojtabelo  estis Johano belajn dato-revenojn"
    #teksto="jen ĉiutage"
    #teksto="En 2005, ni partoprenis, 75 an kongreson de Esperanto de UEA po 200 euroj persone. Tiam ni estis ankoraŭ  junaj kaj spritaj, tiel ke vojaĝo ne lacigis nin "
    #teksto=" bona vojaĝi."
    #teksto="restadi; tut, alia,"
    #teksto="kiu traktos (pri disvolviĝo; de esperanto  22,45-78 saluton - ."
    #teksto="esp- eranto  (22,45*78)-10=30 , saluton-totoo."