#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 09:12:40 2026

@author: clopeau
"""
"""
Son-Registrilo por Android kaj Linux
Kreas kaj konservas WAV/OGG-dosierojn (44100Hz, 16-bit, mono)
Aŭtomate detektas kio funkcias en via sistemo
"""

import os
import wave
import numpy as np
from kivy.app import App as Apo
from kivy.uix.boxlayout import BoxLayout as SkatolaAranĝo
from kivy.uix.button import Button as Butono
from kivy.uix.label import Label as Markilo
from kivy.uix.textinput import TextInput as TekstaEnigo
from kivy.uix.popup import Popup as Ŝprucfenestro
from kivy.core.audio import SoundLoader as SonoŜargilo
from kivy.clock import Clock
from kivy.utils import platform

# Detekti platformon
ESTAS_ANDROID = platform == 'android'

# Por Android, provi importi permesojn
if ESTAS_ANDROID:
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE
        ])
        from android.storage import primary_external_storage_path
        print("Android-permesoj petitaj")
    except:
        print("Ne eblis peti Android-permesojn")

# Provu importi soundfile por OGG-subteno
HAVAS_SOUNDFILE = False
OGG_SUBTENATA = False
OGG_FLOAT_FUNKCIAS = False
OGG_INT16_FUNKCIAS = False

try:
    import soundfile as sf
    HAVAS_SOUNDFILE = True
    print("✓ soundfile trovita - testas OGG-subtenon...")
    
    # Testu ĉu OGG + float funkcias (plej ofta)
    try:
        test_datenoj = np.zeros(100, dtype=np.float32)
        sf.write('/dev/null' if os.name != 'nt' else 'nul', test_datenoj, 44100, format='ogg')
        OGG_FLOAT_FUNKCIAS = True
        print("  ✓ OGG + float (Vorbis) funkcias")
    except Exception as e:
        print(f"  ✗ OGG + float ne funkcias: {e}")
    
    # Testu ĉu OGG + int16 funkcias (malpli ofta)
    try:
        test_datenoj = np.zeros(100, dtype=np.int16)
        sf.write('/dev/null' if os.name != 'nt' else 'nul', test_datenoj, 44100, 
                 format='ogg', subtype='PCM_16')
        OGG_INT16_FUNKCIAS = True
        print("  ✓ OGG + int16 (PCM_16) funkcias")
    except Exception as e:
        print(f"  ✗ OGG + int16 ne funkcias: {e}")
    
    OGG_SUBTENATA = OGG_FLOAT_FUNKCIAS or OGG_INT16_FUNKCIAS
    
except ImportError:
    print("✗ soundfile NE instalita - nur WAV havebla")

class SonRegistriloApo(Apo):
    def build(self):
        self.title = 'Son-Registrilo (WAV/OGG)'
        self.son_datenoj = None
        self.lastaj_dosieroj = []
        
        # Ĉefa aranĝo
        aranĝo = SkatolaAranĝo(
            orientation='vertical', 
            padding=20, 
            spacing=10
        )
        
        # Statusa markilo
        self.stato = Markilo(
            text='Pretas',
            size_hint_y=0.15,
            halign='center'
        )
        
        # Informo pri platformo kaj formatoj
        if ESTAS_ANDROID:
            platformo_info = "Android-telefono"
            self.konserva_vojo = self.get_android_path()
        else:
            platformo_info = "Labortablo"
            self.konserva_vojo = os.path.join(os.getcwd(), 'konservitaj_sonoj')
            if not os.path.exists(self.konserva_vojo):
                os.makedirs(self.konserva_vojo)
        
        # Krei format-informon
        if HAVAS_SOUNDFILE and OGG_SUBTENATA:
            formatoj = []
            if OGG_FLOAT_FUNKCIAS:
                formatoj.append("OGG (float)")
            if OGG_INT16_FUNKCIAS:
                formatoj.append("OGG (int16)")
            formato_info = f"✓ OGG havebla: {', '.join(formatoj)}"
        elif HAVAS_SOUNDFILE:
            formato_info = "⚠ OGG instalita sed ne funkcias - uzu WAV"
        else:
            formato_info = "ℹ NUR WAV havebla"
        
        self.info = Markilo(
            text=f'Platformo: {platformo_info}\n{formato_info}\nKonserva vojo: {self.konserva_vojo}',
            size_hint_y=0.2,
            font_size='11sp',
            halign='center'
        )
        
        # Butonoj por krei tonojn
        butonujo_tonoj = SkatolaAranĝo(
            orientation='horizontal', 
            size_hint_y=0.15, 
            spacing=5
        )
        
        butono_440 = Butono(
            text='440Hz',
            on_press=lambda x: self.krei_tonon(440)
        )
        butono_880 = Butono(
            text='880Hz',
            on_press=lambda x: self.krei_tonon(880)
        )
        butono_bruo = Butono(
            text='Blank bruo',
            on_press=self.krei_bruon
        )
        
        butonujo_tonoj.add_widget(butono_440)
        butonujo_tonoj.add_widget(butono_880)
        butonujo_tonoj.add_widget(butono_bruo)
        
        # Butono por konservi
        self.butono_konservi = Butono(
            text='KONSERVI SONON',
            size_hint_y=0.15,
            on_press=self.montri_konservan_ŝprucfenestron,
            background_color=(0.2, 0.7, 0.3, 1),
            disabled=True
        )
        
        # Listo de konservitaj dosieroj
        self.listo_markilo = Markilo(
            text='Konservitaj dosieroj:\n(neniu)',
            size_hint_y=0.25,
            font_size='10sp',
            halign='left'
        )
        
        # Aldoni ĉiujn elementojn
        aranĝo.add_widget(self.stato)
        aranĝo.add_widget(self.info)
        aranĝo.add_widget(butonujo_tonoj)
        aranĝo.add_widget(self.butono_konservi)
        aranĝo.add_widget(self.listo_markilo)
        
        # Ĝisdatigi liston de dosieroj
        Clock.schedule_once(self.ĝisdatigi_liston, 1)
        
        return aranĝo
    
    def get_android_path(self):
        """Akiri taŭgan vojon por Android."""
        try:
            if ESTAS_ANDROID:
                # Provu eksteran stokadon
                ext_path = primary_external_storage_path()
                if ext_path:
                    # Kreu dosierujon por nia apliko
                    app_path = os.path.join(ext_path, 'SonRegistrilo')
                    if not os.path.exists(app_path):
                        os.makedirs(app_path)
                    return app_path
        except:
            pass
        
        # Defaŭlta vojo
        return os.getcwd()
    
    def krei_tonon(self, frekvenco):
        """Krei testan tonon."""
        sample_frekvenco = 44100
        daŭro = 2
        t = np.linspace(0, daŭro, int(sample_frekvenco * daŭro), endpoint=False)
        self.son_datenoj = (32767 * 0.5 * np.sin(2 * np.pi * frekvenco * t)).astype(np.int16)
        self.stato.text = f"{frekvenco}Hz tono kreita (44100Hz, 16-bit)"
        self.butono_konservi.disabled = False
    
    def krei_bruon(self, instance):
        """Krei blankan bruon."""
        sample_frekvenco = 44100
        daŭro = 2
        bruo = np.random.normal(0, 32767/4, int(sample_frekvenco * daŭro))
        self.son_datenoj = np.clip(bruo, -32768, 32767).astype(np.int16)
        self.stato.text = "Blank bruo kreita"
        self.butono_konservi.disabled = False
    
    def montri_konservan_ŝprucfenestron(self, instance):
        """Montri ŝprucfenestron por eniri dosiernomon."""
        if self.son_datenoj is None:
            self.stato.text = "Unue kreu tonon!"
            return
        
        enhavo = SkatolaAranĝo(orientation='vertical', padding=20, spacing=10)
        
        # Markilo
        markilo = Markilo(
            text='Eniru dosiernomon:',
            size_hint_y=0.15
        )
        enhavo.add_widget(markilo)
        
        # Teksta enigo kun rekomendata nomo
        self.enigo = TekstaEnigo(
            text='sono.wav',
            multiline=False,
            size_hint_y=0.15
        )
        enhavo.add_widget(self.enigo)
        
        # Informo pri haveblaj formatoj
        formatoj_info = "Haveblaj formatoj:\n"
        formatoj_info += "• .wav (ĉiam funkcias)\n"
        
        if HAVAS_SOUNDFILE:
            if OGG_FLOAT_FUNKCIAS:
                formatoj_info += "• .ogg (float/Vorbis) ✓\n"
            if OGG_INT16_FUNKCIAS:
                formatoj_info += "• .ogg (int16/PCM) ✓\n"
            if not OGG_SUBTENATA:
                formatoj_info += "• .ogg (instalita sed ne funkcias - uzu WAV)\n"
        else:
            formatoj_info += "• .ogg (bezonas: pip install soundfile)\n"
        
        formatoj_info += f"\nKonservos en:\n{self.konserva_vojo}"
        
        formatoj_markilo = Markilo(
            text=formatoj_info,
            size_hint_y=0.4,
            font_size='10sp',
            halign='left'
        )
        enhavo.add_widget(formatoj_markilo)
        
        # Butonoj
        butonujo = SkatolaAranĝo(
            orientation='horizontal',
            size_hint_y=0.15,
            spacing=10
        )
        
        butono_konservi = Butono(
            text='Konservi',
            on_press=self.konservi_dosieron
        )
        butono_nuligi = Butono(
            text='Nuligi',
            on_press=self.fermi_ŝprucfenestron
        )
        
        butonujo.add_widget(butono_konservi)
        butonujo.add_widget(butono_nuligi)
        enhavo.add_widget(butonujo)
        
        # Krei kaj malfermi ŝprucfenestron
        self.ŝprucfenestro = Ŝprucfenestro(
            title='Konservi sonon',
            content=enhavo,
            size_hint=(0.9, 0.7),
            auto_dismiss=False
        )
        self.ŝprucfenestro.open()
    
    def konservi_dosieron(self, instance):
        """Konservi la sonon al dosiero - subtenas .wav kaj .ogg."""
        dosiernomo = self.enigo.text.strip()
        
        if not dosiernomo:
            self.stato.text = "Neniu dosiernomo enigita"
            self.fermi_ŝprucfenestron(None)
            return
        
        # Plena vojo
        plena_vojo = os.path.join(self.konserva_vojo, dosiernomo)
        
        try:
            # Decidi laŭ etendo
            if dosiernomo.lower().endswith('.ogg'):
                self.konservi_kiel_ogg(plena_vojo)
            elif dosiernomo.lower().endswith('.wav'):
                self.konservi_kiel_wav(plena_vojo)
            else:
                # Neniu etendo - demandi la uzanton
                self.stato.text = "Dosiernomo devas finiĝi per .wav aŭ .ogg"
                return
            
            self.stato.text = f"Konservita: {os.path.basename(plena_vojo)}"
            
            # Ĝisdatigi liston
            self.ĝisdatigi_liston()
            
            # Fermi ŝprucfenestron
            self.fermi_ŝprucfenestron(None)
            
            # Provi ludi la sonon
            Clock.schedule_once(lambda dt: self.ludi_sonon(plena_vojo), 0.5)
            
        except Exception as e:
            self.stato.text = f"Eraro: {str(e)}"
    
    def konservi_kiel_wav(self, plena_vojo):
        """Konservi kiel WAV (pura Python, ĉiam funkcias)."""
        with wave.open(plena_vojo, 'wb') as wav:
            wav.setnchannels(1)  # Mono
            wav.setsampwidth(2)  # 16-bit = 2 bajtoj
            wav.setframerate(44100)
            wav.writeframes(self.son_datenoj.tobytes())
    
    def konservi_kiel_ogg(self, plena_vojo):
        """Konservi kiel OGG - uzas soundfile se havebla."""
        if not HAVAS_SOUNDFILE:
            raise Exception("OGG ne havebla: soundfile ne instalita")
        
        if OGG_FLOAT_FUNKCIAS:
            # Metodo 1: Float32 (denaska Vorbis)
            datenoj_float = self.son_datenoj.astype(np.float32) / 32767.0
            sf.write(plena_vojo, datenoj_float, 44100, format='ogg')
            print("Konservita kiel OGG (float/Vorbis)")
            
        elif OGG_INT16_FUNKCIAS:
            # Metodo 2: Int16 (PCM en OGG-kontejno)
            sf.write(plena_vojo, self.son_datenoj, 44100, 
                    format='ogg', subtype='PCM_16')
            print("Konservita kiel OGG (int16/PCM)")
            
        else:
            # Provu ambaŭ metodojn
            try:
                # Unue provu float
                datenoj_float = self.son_datenoj.astype(np.float32) / 32767.0
                sf.write(plena_vojo, datenoj_float, 44100, format='ogg')
                print("Konservita kiel OGG (float/Vorbis - provizore)")
            except:
                # Due provu int16
                sf.write(plena_vojo, self.son_datenoj, 44100,
                        format='ogg', subtype='PCM_16')
                print("Konservita kiel OGG (int16/PCM - provizore)")
    
    def ludi_sonon(self, plena_vojo):
        """Ludi sonon por konfirmi."""
        sono = SonoŜargilo.load(plena_vojo)
        if sono:
            sono.play()
            self.lastaj_dosieroj.append(plena_vojo)
    
    def fermi_ŝprucfenestron(self, instance):
        """Fermi la ŝprucfenestron."""
        if hasattr(self, 'ŝprucfenestro'):
            self.ŝprucfenestro.dismiss()
    
    def ĝisdatigi_liston(self, dt=None):
        """Ĝisdatigi liston de konservitaj dosieroj."""
        try:
            if os.path.exists(self.konserva_vojo):
                wav_dosieroj = [f for f in os.listdir(self.konserva_vojo) 
                               if f.endswith('.wav')]
                ogg_dosieroj = [f for f in os.listdir(self.konserva_vojo) 
                               if f.endswith('.ogg')]
                ĉiuj_dosieroj = wav_dosieroj + ogg_dosieroj
                
                if ĉiuj_dosieroj:
                    ĉiuj_dosieroj.sort(reverse=True)
                    plej_novaj = ĉiuj_dosieroj[:5]  # Lastaj 5
                    teksto = "Lastaj konservitaj dosieroj:\n"
                    for f in plej_novaj:
                        ikono = "🔊" if f.endswith('.ogg') else "🎵"
                        teksto += f"{ikono} {f}\n"
                    self.listo_markilo.text = teksto
                else:
                    self.listo_markilo.text = "Konservitaj dosieroj:\n(neniu)"
        except Exception as e:
            print(f"Eraro dum ĝisdatigo de listo: {e}")

if __name__ == '__main__':
    print("="*60)
    print("SON-REGISTRILO - Plena versio kun OGG-subteno")
    print("="*60)
    print(f"Platformo: {'Android' if ESTAS_ANDROID else 'Labortablo'}")
    print(f"soundfile instalita: {'JES' if HAVAS_SOUNDFILE else 'NE'}")
    if HAVAS_SOUNDFILE:
        print(f"OGG + float: {'FUNKCIAS' if OGG_FLOAT_FUNKCIAS else 'NE FUNKCIAS'}")
        print(f"OGG + int16: {'FUNKCIAS' if OGG_INT16_FUNKCIAS else 'NE FUNKCIAS'}")
    print("="*60)
    
    SonRegistriloApo().run()