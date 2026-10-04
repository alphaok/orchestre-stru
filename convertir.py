#!/usr/bin/env python3
# Convertit une sélection des 256 Orchestral Samples en MP3 mono légers, nommés par hauteur réelle.
# Lancer depuis le dossier parent : python3 strudel-leger/convertir.py
import json, os, re, subprocess, urllib.parse
SRC = '.'; DST = 'strudel-leger'
carte = json.load(open('strudel.json'))
LONG = {'violons', 'altos', 'violoncelles', 'violons_harmo', 'flute', 'flute_trille', 'cor', 'trompette', 'trombones', 'tuba', 'vibraphone', 'cloches'}
PERC = {  # son : [(fichier, durée max en s)]
 'timbales': [(f'Timpani{i}_Hit_v3_rr{r}_Sum.wav', 3) for i, r in [(1, 4), (2, 3), (3, 5), (4, 4), (5, 4)]],
 'timbales_roulement': [('Timpani1_Roll_v3_rr1_Sum.wav', 5)],
 'caisse_claire': [('Snare2_HitSN_v5_rr6_Sum.wav', 2), ('Snare2_HitSN_v9_rr2_Sum.wav', 2), ('Snare2_rimshot_v2_rr5_Sum.wav', 2), ('Snare3M_flamSN_v5_rr3_Sum.wav', 2)],
 'caisse_claire_roulement': [('Snare2_rollSN_v3_rr1_Sum.wav', 4)],
 'toms': [('TomH_HitS_v3_rr3_Mid.wav', 2.5), ('TomL_HitS_v4_rr6_Mid.wav', 2.5)],
 'cymbale': [('cymbal_crash2_f2.wav', 5)],
 'cymbale_suspendue': [('susCymb1_hit_mp3.wav', 5), ('susCymb1_cresc_3.75s.wav', 5.5)],
 'gong': [('gong_f.wav', 6)],
 'triangle': [('triangle1_hit_mp.wav', 4)],
 'tambourin': [('tambourine_down_3.wav', 1.5), ('tambourine_up_3.wav', 1.5)],
 'darbuka': [('Darbuka_01.wav', 1.5), ('Darbuka_03.wav', 1.5), ('Darbuka_05.wav', 1.5)],
 'clochettes': [('windchimes_asc1.wav', 5), ('sleighbell1_hit_2.wav', 2)],
}
def pic(path):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.search(r'max_volume: (-?[\d.]+) dB', out).group(1))
def convertir(src, dst, duree):
    gain = -9 - pic(src)            # crête ramenée à -9 dBFS (marge pour les notes qui se chevauchent)
    fondu = min(0.8, duree / 3)
    af = (f'silenceremove=start_periods=1:start_threshold=-60dB,atrim=0:{duree},'
          f'afade=t=out:st={duree - fondu}:d={fondu},volume={gain}dB')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', '1', '-ar', '44100', '-af', af,
                    '-c:a', 'libmp3lame', '-b:a', '96k', os.path.join(DST, dst)], check=True)
nom_note = lambda n: n.replace('#', 's')
leger = {'_base': 'orchestre/'}
for son, v in carte.items():
    if son.startswith('_') or not isinstance(v, dict): continue
    duree = 4 if son in LONG else 3
    leger[son] = {}
    for note, f in v.items():
        dst = f'{son}_{nom_note(note)}.mp3'
        convertir(urllib.parse.unquote(f), dst, duree); leger[son][note] = dst
for son, liste in PERC.items():
    leger[son] = []
    for k, (f, duree) in enumerate(liste):
        dst = f'{son}_{k}.mp3'; convertir(f, dst, duree); leger[son].append(dst)
json.dump(leger, open(os.path.join(DST, 'orchestre.json'), 'w'), indent=1)
print('fichiers', sum(len(v) for k, v in leger.items() if k != '_base'))
