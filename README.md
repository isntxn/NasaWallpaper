# NasaWallpaper

Change automatiquement le fond d'écran de votre machine avec les images de l'**Astronomy Picture of the Day (APOD)** de la NASA — via l'API officielle ou depuis l'archive HTML locale.

---

## Structure du projet

```
changeWallpaper/
├── changeWallpaperApod_API.py        # Récupération via l'API NASA (image du jour ou aléatoire)
├── changeWallpaperApod_Archive.py    # Récupération depuis l'archive HTML locale (mode offline)
├── convertHTMLtoJSON.py              # Conversion de l'archive HTML APOD en JSON
├── dislike.py                        # Bannit le fond d'écran actuel et en applique un nouveau
├── ArchiveAPOD.html                  # Archive HTML de l'APOD (téléchargée depuis la NASA)
├── ArchiveAPOD.json                  # Archive convertie en JSON (généré par convertHTMLtoJSON.py)
├── image/                            # Dossier de stockage des images téléchargées
└── logs/
    ├── horodatage.csv                # Liste des images bannies (ignorées lors du choix)
    └── name_wallpaper.txt            # Nom de la dernière image appliquée en fond d'écran
```

---

## Fonctionnement

Le projet propose **deux modes** de récupération d'image :

### Mode API (`changeWallpaperApod_API.py`)
- Interroge l'API NASA APOD pour récupérer l'image du jour.
- Si l'image du jour ne respecte pas les critères (mauvaises dimensions, GIF etc...), on récupère une image aléatoire via l'API.
- L'image est téléchargée localement, tourner correctement si nécessaire, puis définie comme fond d'écran.

### Mode Archive (`changeWallpaperApod_Archive.py`)
- Fonctionne sans appel à l'API, à partir du fichier `ArchiveAPOD.json` généré localement (à partir du script `ConvertHTMLtoJSON.py`.
- Sélectionne une image au hasard parmi les archives disponibles, en excluant les images bannies (celles ne respectant pas les critères pour éviter de boucler sur les mêmes images).
- Récupère l'image directement sur le site APOD de la NASA.


### Conversion Archive (`convertHTMLtoJSON.py`)
- Ce script permet le téléchargement de la page d'archive de l'APOD (`archivepix.html`) et la sauvegarde en local.
- Convertit le HTML en un dictionnaire JSON structuré utilisable par le mode Archive.

### Dislike (`dislike.py`)
- Lit le nom du fond d'écran actuellement appliqué (depuis `logs/name_wallpaper.txt`).
- Ajoute cette image à la liste des bannis (`horodatage.csv`).
- Applique immédiatement un nouveau fond d'écran via le mode API.

---

## Critères de sélection d'une image

Une image est retenue comme fond d'écran uniquement si :
- Le média est bien une **image** (pas de vidéo etc.)
- Le format n'est **pas un GIF**
- Les **dimensions sont suffisantes** : au moins **1200×2300 px** ou **2300×1200 px** (portrait ou paysage) (Modifiable directement dans le code source, sera natif dans le futur)
- L'image **ne figure pas dans la liste des bannis**

---

## Compatibilité OS

Pour l'instant les OS supportés sont : 

| OS | Support |
|---|---|
| Windows | ✅ Complet |
| Linux (GNOME) | 🔧 Partiel (en cours) |
| Linux (XFCE) | 🔧 Partiel (en cours) |

Cette liste est non exhaustive et pourra augmenter et s'adapter au fur et à mesure du temps.

---

## Prérequis

- Python 3.x
- Les bibliothèques listées dans `requirements.txt` : `requests`, `Pillow`, `beautifulsoup4`, `python-dotenv` (seront automatiquement installées)

  
Pour cela clonez le dépôt puis lancez le script de configuration. Il installe automatiquement les dépendances et crée le fichier `.env` avec votre clé API :

```bash
git clone https://github.com/isntxn/NasaWallpaper.git
cd NasaWallpaper
python setup.py
```
> Le script vous demandera de coller votre clé API NASA (à obtenir gratuitement sur [https://api.nasa.gov](https://api.nasa.gov)) et s'occupe du reste : installation des dépendances, création du `.env` et mise à jour du `.gitignore`.
---

## Utilisation

### Mode API (image du jour NASA)

Ce mode interroge l'API officielle NASA pour récupérer l'image du jour ou une image aléatoire.

> Si vous avez déjà exécuté `python setup.py`, la clé API est déjà configurée. Passez directement à l'étape 2.

**Étape 1 — Configurer la clé API manuellement** *(si vous n'avez pas utilisé `setup.py`)*

Rendez-vous sur [https://api.nasa.gov](https://api.nasa.gov), remplissez le formulaire et récupérez votre clé API gratuite. Créez ensuite un fichier `.env` à la racine du projet :

```
NASA_API_KEY=votre_clé_api_ici
```

**Étape 2 — Lancer le changement de fond d'écran**

```bash
python changeWallpaperApod_API.py
```

---

### Mode Archive

Ce mode fonctionne entièrement en local à partir de l'archive HTML de la NASA. À suivre dans l'ordre :

**Etape 1 - Télécharger et convertir l'archive APOD**

```bash
python convertHTMLtoJSON.py
```
> Télécharge la page d'archive de la NASA et génère `ArchiveAPOD.json`. À exécuter une seule fois (ou pour mettre à jour l'archive).

**Étape 2 — Lancer le changement de fond d'écran**

```bash
python changeWallpaperApod_Archive.py
```
> Sélectionne une image au hasard dans l'archive, la télécharge et l'applique comme fond d'écran.

---

### Dislike — Bannir le fond d'écran actuel

Quelle que soit la méthode utilisée, vous pouvez bannir le fond d'écran actuellement appliqué et en obtenir un nouveau automatiquement :

```bash
python dislike.py
```

---

## Notes

- Le fichier `horodatage.csv` grandit au fil du temps avec les images bannies (mauvaises dimensions ou dislikées manuellement). Il peut être vidé si vous souhaitez réinitialiser la liste.
- Le dossier `image/` stocke la dernière image téléchargée. Les anciennes images ne sont pas supprimées automatiquement.
- Vous pouvez ajouter un ou plusieurs des scripts en tâches planifiées ou bien en application a executer au démarrage afin de ne pas avoir à lancer le script tous les jours.
- Ou encore, il est possible d'installer Rainmeter (ou autres) si vous voulez intégrer des boutons sur votre écran principal pour executer ces scripts plus facilement.

---

## Licence

Ce projet est open-source et libre d'utilisation.

### Auteur

Xenon.