import subprocess
import sys
import os

print("=" * 50)
print("       Configuration de NasaWallpaper")
print("=" * 50)

# Installation des dépendances
print("\n📦 Installation des dépendances...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
print("✅ Dépendances installées avec succès.")

# Création du fichier .env
print("\n🔑 Configuration de la clé API NASA")
print("   Rendez-vous sur https://api.nasa.gov pour obtenir votre clé API gratuite.")
print("   Renseignez votre prénom, nom et email — vous recevrez la clé immédiatement.")

api_key = input("\n   Collez votre clé API NASA ici : ").strip()

if not api_key:
    print("❌ Aucune clé saisie. Relancez le script et renseignez votre clé.")
    sys.exit(1)

with open(".env", "w") as f:
    f.write(f"NASA_API_KEY={api_key}\n")

print("✅ Fichier .env créé avec succès.")

# Vérification que .env est bien dans le .gitignore
gitignore_path = ".gitignore"
env_ignored = False

if os.path.exists(gitignore_path):
    with open(gitignore_path, "r") as f:
        content = f.read()
    if ".env" in content:
        env_ignored = True
    else:
        with open(gitignore_path, "a") as f:
            f.write("\n.env\n")
        env_ignored = True
else:
    with open(gitignore_path, "w") as f:
        f.write(".env\n")
    env_ignored = True

print("✅ Fichier .env ajouté au .gitignore.")

print("\n🚀 Configuration terminée ! Vous pouvez lancer :")
print("   python changeWallpaperApod_API.py      → Mode API (image du jour)")
print("   python changeWallpaperApod_Archive.py  → Mode Archive (local)")
print("   python dislike.py                      → Bannir et changer l'image")
print("=" * 50)
