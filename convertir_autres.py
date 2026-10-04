#!/usr/bin/env python3
# Convertit les packs de 0_others/ en MP3 mono légers, nommés par hauteur réelle, et complète strudel.json.
# Lancer depuis le dossier 256OrchestralSamples : python3 strudel-leger/convertir_autres.py
import glob, json, math, os, re, subprocess, tempfile
import numpy as np
SRC = '0_others'; DST = 'strudel-github'
NAMES = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
def midi_de(nom):
    m = re.match(r'([a-g])(s|#)?(-?\d)$', nom.lower()); return NAMES.index(m.group(1)) + (1 if m.group(2) else 0) + 12 * (int(m.group(3)) + 1)
def nom_de(m): return NAMES[m % 12] + str(m // 12 - 1)
def fichier_de(m): return nom_de(m).replace('#', 's')
def charger(path, ss, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '22050', '-ss', str(ss), '-t', str(t), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32); return x - x.mean()
def f0(path):  # fréquence fondamentale (YIN simplifié), sur un passage stable
    x = charger(path, 0.3, 0.4); sr = 22050; W = 4096; tmax = min(int(sr / 25), len(x) - W - 1); tmin = int(sr / 2100)
    d = np.array([np.sum((x[:W] - x[t:t + W]) ** 2) for t in range(tmax)])
    cm = d.copy(); cm[0] = 1; cm[1:] = d[1:] * np.arange(1, tmax) / np.maximum(np.cumsum(d[1:]), 1e-12)
    for t in range(tmin, tmax):
        if cm[t] < .12:
            while t + 1 < tmax and cm[t + 1] < cm[t]: t += 1
            return sr / t
    return sr / (tmin + np.argmin(cm[tmin:]))
def midi_mesure(path): return round(69 + 12 * math.log2(f0(path) / 440))
def pic(cmd_in):
    out = subprocess.run(['ffmpeg', '-hide_banner'] + cmd_in + ['-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.search(r'max_volume: (-?[\d.]+) dB', out).group(1))
def justesse(path, m):  # écart en cents entre l'enregistrement et la note m (médiane des harmoniques 1 à 4)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '44100', '-ss', '0.05', '-t', '0.8', '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32); x = x - x.mean(); N = 1 << 19
    sp = np.abs(np.fft.rfft(x * np.hanning(len(x)), n=N)); fr = np.fft.rfftfreq(N, 1 / 44100); f = 440 * 2 ** ((m - 69) / 12); ec = []
    for h in (1, 2, 3, 4):
        lo, hi = np.searchsorted(fr, h * f * .97), np.searchsorted(fr, h * f * 1.03)
        if hi > lo and h * f < 8000: ec.append(1200 * math.log2(fr[lo + np.argmax(sp[lo:hi])] / (h * f)))
    return float(np.median(ec)) if ec else 0.0
def convertir(srcs, dst, duree, cents=0.0):
    entree = sum((['-i', s] for s in srcs), [])
    melange = f'amix=inputs={len(srcs)}:normalize=0,' if len(srcs) > 1 else ''
    fondu = min(0.8, duree / 3)
    accord = f'aresample=44100,asetrate={44100 * 2 ** (-cents / 1200):.2f},aresample=44100,' if abs(cents) > 15 else ''  # corrige les notes fausses de plus de 15 cents
    chaine = f'{melange}aformat=channel_layouts=mono,{accord}silenceremove=start_periods=1:start_threshold=-60dB,atrim=0:{duree},afade=t=out:st={duree - fondu}:d={fondu}'
    tmp = os.path.join(tempfile.gettempdir(), 'strudel_conversion.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + entree + ['-filter_complex', chaine, '-ar', '44100', tmp], check=True)
    gain = -9 - pic(['-i', tmp])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', f'volume={gain}dB', '-c:a', 'libmp3lame', '-b:a', '96k', os.path.join(DST, dst)], check=True)
    os.remove(tmp)
def nom_fichier(path): return re.sub(r'^\d+__[^_]+__', '', os.path.basename(path))
def par_nom_avec_doublons(paths, extraire, decalage):
    # fichiers du même nom = la note et son dièse (Freesound a retiré les #) : le plus aigu des deux est le dièse
    groupes = {}
    for p in paths: groupes.setdefault(extraire(nom_fichier(p)), []).append(p)
    notes = {}
    for nom, ps in groupes.items():
        m = midi_de(nom) + decalage
        if len(ps) > 1:  # le naturel est celui dont le spectre colle le mieux à la note naturelle plutôt qu'au dièse
            ps = sorted(ps, key=lambda p: -(energie(p, m) - energie(p, m + 1)))
        for k, p in enumerate(ps): notes[m + k] = p
    return notes
def energie(path, m):  # énergie (en dB) autour des 4 premiers harmoniques de la note m, à ±30 cents
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '44100', '-ss', '0.1', '-t', '0.6', '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32); x = x - x.mean(); N = 1 << 18
    sp = np.abs(np.fft.rfft(x * np.hanning(len(x)), n=N)); fr = np.fft.rfftfreq(N, 1 / 44100); f = 440 * 2 ** ((m - 69) / 12); e = 0
    for h in (1, 2, 3, 4):
        lo, hi = np.searchsorted(fr, h * f * 2 ** (-.025)), np.searchsorted(fr, h * f * 2 ** (.025))
        if hi > lo: e += sp[lo:hi].max()
    return 20 * math.log10(e + 1e-9)
def alleger(notes, pas=3):  # une note sur trois (tierce mineure) suffit : Strudel transpose la plus proche
    ms = sorted(notes); garde = {m for m in ms if m % pas == 0} | {ms[0], ms[-1]}
    return {m: notes[m] for m in ms if m in garde}
g = lambda motif: sorted(glob.glob(os.path.join(SRC, motif)))
INSTRUMENTS = {}
# guitare électro-acoustique Sherwood SH887 (Project16, CC BY 3.0) : nuance moyenne v3, hauteurs mesurées
INSTRUMENTS['guitare'] = (alleger({midi_mesure(p): p for p in g('15407*/*v3.flac')}), 4)
# Fender Rhodes Mark II (tim.kahn, CC BY 4.0) : noms une octave trop bas
INSTRUMENTS['rhodes'] = (alleger(par_nom_avec_doublons(g('3957*/*.aif*'), lambda n: re.search(r'[-_]([a-g]\d)(aif)?\.aiff$', n).group(1), 12)), 5)
# Wurlitzer 200a (OldBassMan, CC BY 4.0) : noms faux, hauteurs mesurées (ré, fa#, la# de chaque octave)
INSTRUMENTS['wurlitzer'] = ({midi_mesure(p): p for p in g('5726*/*.wav')}, 5)
# marimba (sgossner, CC BY 4.0) : noms justes
CORRECTIONS = {'marimba-g4': 'g5'}  # mesuré à 783 Hz : c'est un sol 5 (la série monte par tierces : mi 5, sol 5, si 5)
def note_marimba(p):
    n = re.search(r'(marimba-[a-g]\d)', nom_fichier(p)).group(1); return midi_de(CORRECTIONS.get(n, n.split('-')[1]))
INSTRUMENTS['marimba2'] = ({note_marimba(p): p for p in g('15684*/*.wav')}, 3)
# cuivres FM (Terry93D, CC0) : noms justes (s = dièse)
INSTRUMENTS['cuivres_fm'] = (alleger({midi_de(re.search(r'full-brass-([a-g]s?\d)', nom_fichier(p)).group(1)): p for p in g('21486*/*.wav')}), 4)
# contrebasse (pjcohen, CC0) : noms justes, doublons = dièses
INSTRUMENTS['contrebasse'] = (alleger(par_nom_avec_doublons(g('21521*/*normal_*.wav'), lambda n: re.search(r'_([a-g]\d)\.wav$', n).group(1), 0)), 4)
INSTRUMENTS['contrebasse_courte'] = (alleger(par_nom_avec_doublons(g('21521*/*stop_finger_*.wav'), lambda n: re.search(r'_([a-g]\d)\.wav$', n).group(1), 0)), 2)
# point de départ : l'orchestre déjà converti (dossier strudel-leger), copié tel quel
import shutil
os.makedirs(DST, exist_ok=True)
leger = json.load(open(os.path.join('strudel-leger', 'strudel.json')))
NOUVEAUX = ['guitare', 'rhodes', 'wurlitzer', 'marimba2', 'cuivres_fm', 'contrebasse', 'contrebasse_courte', 'orgue_drawbar', 'orgue_percussif', 'orgue_rock', 'contrebasse_effets']
leger = {k: v for k, v in leger.items() if k not in NOUVEAUX}
for k, v in leger.items():
    if k != '_base':
        for f in (v.values() if isinstance(v, dict) else v): shutil.copy(os.path.join('strudel-leger', f), DST)
shutil.copy(os.path.join('strudel-leger', 'convertir.py'), DST)
if not os.path.exists(os.path.join(DST, 'README.md')): shutil.copy(os.path.join('strudel-leger', 'README.md'), DST)  # le README complet n'est pas écrasé
shutil.copy(__file__, DST)
corrections = []
for son, (notes, duree) in INSTRUMENTS.items():
    leger[son] = {}
    for m, p in sorted(notes.items()):
        # pas de correction pour le marimba : ses harmoniques ne sont pas des multiples exacts, la mesure le croirait faux
        c = 0.0 if son == 'marimba2' else justesse(p, m); corrections.append((son, nom_de(m), round(c)))
        dst = f'{son}_{fichier_de(m)}.mp3'; convertir([p], dst, duree, c); leger[son][nom_de(m)] = dst
    print(son, len(notes), nom_de(min(notes)), '-', nom_de(max(notes)), 'corrigées :', [(n, c) for s2, n, c in corrections if s2 == son and abs(c) > 15])
# orgues FreePats (CC0) : hauteurs du fichier SFZ (C2 = do 2), canaux gauche et droit mélangés
for son, motif in [('orgue_drawbar', 'Drawbar*'), ('orgue_percussif', 'Percussive*'), ('orgue_rock', 'Rock*')]:
    leger[son] = {}
    fichiers = g(motif + '/samples/*.wav'); noms = sorted({re.sub(r'[LR]?\.wav$', '', os.path.basename(f)) for f in fichiers})
    for n in noms:
        srcs = [f for f in fichiers if re.sub(r'[LR]?\.wav$', '', os.path.basename(f)) == n]
        m = midi_de(n); dst = f'{son}_{fichier_de(m)}.mp3'; convertir(srcs, dst, 4); leger[son][nom_de(m)] = dst
    print(son, len(noms))
# effets de contrebasse (frappe, slap, glissé)
leger['contrebasse_effets'] = []
for k, p in enumerate(sorted(g('21521*/*effects_*.wav'), key=nom_fichier)):  # knock1-6, slap1-6, slide1-6
    dst = f'contrebasse_effets_{k}.mp3'; convertir([p], dst, 2); leger['contrebasse_effets'].append(dst)
json.dump(leger, open(os.path.join(DST, 'strudel.json'), 'w'), indent=1)
print('total', sum(len(v) for k, v in leger.items() if k != '_base'))
