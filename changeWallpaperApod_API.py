from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import subprocess
import os
import ctypes
import csv
import platform

load_dotenv()

API_KEY = os.getenv('API_KEY')
URL_APOD = f'https://api.nasa.gov/planetary/apod?api_key={API_KEY}'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PATH_IMAGE = os.path.join(BASE_DIR, 'image')
PATH_LOGS = os.path.join(BASE_DIR, 'logs')
JSON_FILE = os.path.join(BASE_DIR, 'ArchiveAPOD.json')
CSV_FILE = os.path.join(BASE_DIR, 'logs', 'horodatage.csv')

### RECUPERATION IMAGE VIA SITE APOD (PAS API) 
def url_nasa_image(name_page):
    url = 'https://apod.nasa.gov/apod/'

    data = requests.get(f'{url}/{name_page}').text
    soup = BeautifulSoup(data, features='html.parser')

    content_a = soup.find_all('a')
    for a in content_a:
        if a['href'][0:5] == 'image':
            url += a['href']
    
    return url

### MINIMUM 1300x2300 POUR GARDER IMAGE
def condition_dimension(url):
    response = requests.get(url, stream=True)

    try:
        image = Image.open(BytesIO(response.content))
        longueur, largeur = image.size
        print(f"Dimensions: {longueur}x{largeur}")

        return (longueur > 2300 and largeur > 1200) or (longueur > 1200 and largeur > 2300)
    
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")
        return False

### ON LIT LE FICHIER horodatage.csv POUR RECUP LES BANS
def horodatage():
    bans = []
    with open(CSV_FILE, 'r', encoding='utf-8') as fcr:
        reader = csv.reader(fcr)
        for row in reader:
            bans.append(row)
        
    return bans

### ON ECRIT DANS LE CSV LES NOUVEAUX BANNIS
def write_in_bans(page):
    csv_file = horodatage() # on récupère le contenu actuel
    csv_file.append([page, 'always'])
    print(csv_file)

    with open(CSV_FILE, 'w', newline='') as fcw:
        writer = csv.writer(fcw)
        writer.writerows(csv_file)
    
    fcw.close()

### RETOURNE LE NOM DU FICHIER DE L'URL AU FORMAT 'apYYMMDD.html'
def func_name_url(data):
    date = data['date']
    name_url = 'ap'
    for elm in date.split('-'):
        name_url += elm[-2:]
    name_url += '.html'
    
    return name_url

### LE FICHIER DOIT ETRE UNE IMAGE, PAS DE GIF et NE PAS FIGURE DANS LES BANS 
def condition_url(data, bans):
    if (data['media_type'] == 'image' and not data['hdurl'].endswith('.gif')) and func_name_url(data) not in bans:
        return True
    else:
        # ecrit le nom du fichier dans les bans
        write_in_bans(func_name_url(data))
        return False

### RECUPERATION IMAGE VIA API NASA
def claim_nasa_image(bans):
    data = requests.get(URL_APOD, stream=True).json()

    if condition_url(data, bans) and condition_dimension(data['hdurl']):
        print('APOD PÄRT')
        url_nasa = data['hdurl']
        nom_fich = url_nasa.split('/')[-1]
        print(nom_fich)

    else:
        print('RANDOM PART')
        url_random = f'{URL_APOD}&count=1'
        data = requests.get(url_random, stream=True).json()[0]

        while not ((condition_url(data, bans)) and condition_dimension(data['hdurl'])):
            data = requests.get(url_random, stream=True).json()[0]
        
        url_nasa = data['hdurl']
        nom_fich = url_nasa.split('/')[-1]
        print(nom_fich)
    
    return data, nom_fich

### ON VERIFIE LES DIMENSIONS DE L'IMAGE EN LOCAL
def download_image(url, nom_fich):
    response = requests.get(url)

    with open(f'{PATH_IMAGE}{nom_fich}', 'wb') as f:
        f.write(response.content)

    image = Image.open(f'{PATH_IMAGE}{nom_fich}')
    longueur, largeur = image.size

    if largeur > longueur:
        image = image.rotate(90, expand=True)
        image.save(f'{PATH_IMAGE}{nom_fich}')

def add_name_wallpaper(name_fich):
    with open(f'{PATH_LOGS}/name_wallpaper.txt', 'w', encoding='utf-8') as f:
        f.write(name_fich)
    f.close()

### CHANGE LE FOND D'ECRAN DANS UN ENV GNOME
def set_wallpaper_gnome(nom_fich):
    subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://home/lpasur/{nom_fich} [file://home/lpasur/%7Bnom_fich%7D]"], check=True)
    subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-options", "zoom"], check=True)
    print(f"Fond d'écran mis à jour avec l'image : {nom_fich}")

### CHANGE LE FOND D'ECRAN DANS UN ENV XFCE
def set_wallpaper_xfce(nom_fich):
    abs_path = os.path.abspath(f"file://home/lpasur/{nom_fich} [file://home/lpasur/%7Bnom_fich%7D]")
    monitors = ["/backdrop/screen0/monitor0/image-path","/backdrop/screen0/monitor0/last-image"]
    for prop in monitors:
        subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", abs_path], check=True)
        print(f"Fond d'écran mis à jour avec l'image : {nom_fich}")

### CHANGE LE FOND D'ECRAN DANS UN ENV WINDOWS
def set_wallpaper_win(nom_fich):
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, f"{PATH_IMAGE}{nom_fich}", 0)
        print(f"Fond d'écran mis à jour avec l'image : {nom_fich}")
    except:
        return -1

### ON RECUPERE LE NOM DE CHAQUE BANNI QU'ON MET DANS UN TABLEAU
def claim_all_bans(bans):
    return [row[0] for row in bans]

### APPEL DES FONCTIONS
def main():
    csv_file = horodatage() # format : [[banni1,date1], [banni2,date2], [banni3,date3]...]
    bans = claim_all_bans(csv_file) # format : [nom_banni1, nom_banni2, nom_banni3...]

    # on recupere toutes les infos sur la page
    data, nom_fich = claim_nasa_image(bans)
    
    # on télécharge l'image (et on la retourne au besoin)
    url = data['hdurl']
    download_image(url, nom_fich)

    # on inscrit le nom dans le fichier temporaire 
    add_name_wallpaper(func_name_url(data))

    if platform.system() == 'Windows':
        set_wallpaper_win(nom_fich)

    ''' Suite pour Kali et Ubuntu '''    

if __name__ == "__main__":
    main()
