# Orchestre pour Strudel

Des échantillons libres préparés pour [Strudel](https://strudel.cc/) : l'orchestre des **256 Orchestral Samples** de Sam Gossner (Versilian Studios), plus des claviers, une guitare, une contrebasse, des cuivres FM et trois orgues venus de Freesound et FreePats. 29 instruments jouables à toutes les hauteurs et 13 familles de percussions et d'effets, en 341 fichiers MP3 mono (14 Mo).

## Utilisation

Dans strudel.cc, en tête du code :

```js
samples('github:alphaok/orchestre-stru')

setcpm(72/4)
$Cordes: chord("<Am F C G>").voicing().s("violons").attack(.2).clip(1).release(.6).gain(.35)
$Harpe:  chord("<Am F C G>").voicing().arp("0 1 2 3 2 1").s("harpe").gain(.45)
$Basse:  note("<a1 f1 c2 g1>").struct("x ~ x ~").s("contrebasse_pizz")
$Timbales: s("timbales:0 ~ ~ timbales:2").gain(.8)
```

Pour les instruments, `note()`, `n().scale()` ou `chord().voicing()` choisissent l'enregistrement le plus proche de la note demandée et le transposent. `.clip(1)` coupe chaque note à sa durée : sans lui, une note tenue sonne jusqu'à la fin de l'échantillon (4 secondes). Les percussions se choisissent par numéro : `timbales:0`, `timbales:1`…

## Sons

| Son | Tessiture |
|---|---|
| `violons` | sol 3 – ré 7 |
| `altos` | do 3 – si 5 |
| `violoncelles` | do 2 – si 4 |
| `violons_harmo` | sol 5 – do 7 (harmoniques) |
| `violoncelles_pizz` | do 2 – la 3 (pincé) |
| `contrebasse_pizz` | mi 1 – sol# 3 (pincé) |
| `harpe` | si 1 – la 6 |
| `flute` | do 4 – la 6 |
| `flute_trille` | mi 4 – do 6 (trille d'un ton) |
| `basson` | si♭ 1 – si♭ 4 (court) |
| `cor` | ré 3 – si♭ 4 |
| `trompette` | fa 3 – do 6 |
| `trombones`, `trombones_stac` | fa# 2 – si♭ 4 (tenu, piqué) |
| `tuba`, `tuba_stac` | si♭ 1 – ré 4 (sforzando, piqué) |
| `marimba` | do 3 – do 7 |
| `vibraphone` | la 3 – mi 6 |
| `cloches` | do 4 – mi 5 (cloches tubulaires) |

| `rhodes` | mi 1 – mi 7 (piano électrique Fender Rhodes Mark II) |
| `wurlitzer` | ré 2 – ré 6 (piano électrique Wurlitzer 200A) |
| `guitare` | mi 2 – ré# 5 (guitare électro-acoustique Sherwood SH887) |
| `contrebasse` | mi 1 – fa# 4 (jazz, pincée, sonne longtemps) |
| `contrebasse_courte` | mi 1 – fa# 4 (pincée et étouffée, note courte) |
| `marimba2` | fa 2 – do 7 (17 notes, plus complet que `marimba`) |
| `cuivres_fm` | fa 1 – sol 5 (cuivres de synthé FM, années 80) |
| `orgue_drawbar`, `orgue_percussif`, `orgue_rock` | do 2 – do 7 (orgues électromécaniques façon Hammond) |

Percussions : `timbales` (0 à 4), `timbales_roulement`, `caisse_claire` (0 à 3), `caisse_claire_roulement`, `toms` (0, 1), `cymbale`, `cymbale_suspendue` (0 frappe, 1 crescendo), `gong`, `triangle`, `tambourin` (0, 1), `darbuka` (0 à 2), `clochettes` (0, 1). Effets de contrebasse : `contrebasse_effets` (0 à 5 frappes sur le bois, 6 à 11 slaps, 12 à 17 glissés).

Exemple avec les claviers :

```js
samples('github:alphaok/orchestre-stru')
setcpm(80/4)
$Rhodes: chord("<Dm9 G13 C^9 A7>").voicing().struct("x ~ [~ x] ~").s("rhodes").clip(1).release(.4).gain(.5)
$Basse:  note("<d2 g1 c2 a1>").struct("x ~ ~ [~ x]").s("contrebasse").gain(.9)
$Orgue:  chord("<Dm9 G13 C^9 A7>").voicing().s("orgue_rock").clip(1).gain(.25)
```

## Préparation des fichiers

- **Hauteurs** : chaque fichier est nommé par sa hauteur réelle, avec la convention de Strudel (do 4 = do central, 262 Hz). Dans le pack d'origine, la plupart des fichiers sont nommés une octave trop bas (`LDFlute_susvib_C4` joue un do 5) ; seules la harpe et les cloches suivent déjà cette convention. Les écarts ont été mesurés par détection de la fréquence fondamentale, puis vérifiés par la tessiture de chaque instrument.
- **Compression** : MP3 mono 96 kbit/s, silence du début retiré, coupe à 3 ou 4 secondes avec fondu de sortie, crête à −9 dB pour laisser de la marge quand plusieurs notes se superposent.
- **Autres packs** : mêmes traitements. Les noms de fichiers ont été vérifiés par mesure : ceux du Rhodes sont une octave trop bas, ceux du Wurlitzer et de la guitare ne correspondent pas aux notes jouées (hauteurs mesurées), le fichier « marimba-g4 » joue un sol 5, et Freesound a retiré les dièses des noms (deux fichiers « a1 » = la 1 et la# 1, départagés par leur spectre). Les notes de `contrebasse_courte` étaient enregistrées jusqu'à un demi-ton trop bas ; elles ont été réaccordées. Pour les instruments très complets, une note sur trois est gardée : Strudel transpose la plus proche d'un ou deux demi-tons. Les orgues suivent les hauteurs de leur fichier SFZ ; leur jeu de 16 pieds fait entendre aussi l'octave inférieure.
- **Scripts** : `convertir.py` (orchestre) et `convertir_autres.py` (autres packs) refont la conversion (ils demandent ffmpeg, Python et numpy).

## Crédits et licence

Échantillons : **Sam Gossner / Versilian Studios LLC**, « 256-Sample Pack of Orchestral Sounds » (2016), http://vis.versilstudios.net/

Conditions de l'auteur, reprises du README d'origine :

> All samples herein are supplied as-is, for total and eternal public usage, redistribution, and modification.
> I encourage and welcome all modifications, ports, and derivations, and request but do not require credit.

Cette version compressée et renommée est une dérivation de ce pack.

Autres sons (tous modifiés : convertis en MP3 mono, coupés, volume ajusté, renommés par hauteur, parfois réaccordés) :

| Son | Source | Auteur | Licence |
|---|---|---|---|
| `rhodes` | [C_S Fender Rhodes Mark II](https://freesound.org/people/tim.kahn/packs/3957/) | tim.kahn | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `wurlitzer` | [Wurlitzer 200a](https://freesound.org/people/OldBassMan/packs/5726/) | OldBassMan | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `marimba2` | [Marimba Samples](https://freesound.org/people/sgossner/packs/15684/) | sgossner (Sam Gossner) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `guitare` | [Electro acoustique Sherwood SH887](https://freesound.org/people/Project16/packs/15407/) | Project16 | [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) |
| `contrebasse`, `contrebasse_courte`, `contrebasse_effets` | [Standup Upright Acoustic Double Bass](https://freesound.org/people/pjcohen/packs/21521/) | pjcohen | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) |
| `cuivres_fm` | [FM Synth - Full Brass](https://freesound.org/people/Terry93D/packs/21486/) | Terry93D | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) |
| `orgue_drawbar` | [Drawbar organ emulation](http://freepats.zenvoid.org/Organ/electric-organ.html) (FreePats) | Roberto | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) |
| `orgue_percussif`, `orgue_rock` | [Percussive / Rock organ emulation](http://freepats.zenvoid.org/Organ/electric-organ.html) (FreePats) | Strix SoundFont Team | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) |
