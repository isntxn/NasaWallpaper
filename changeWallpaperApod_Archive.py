from bs4 import BeautifulSoup
import requests
import subprocess
import os
import urllib
import ctypes
import json
import csv
import random
import platform
from PIL import Image
from io import BytesIO

JSON_FILE = 'changeWallpaper\\ArchiveAPOD.json'
CSV_FILE = 'changeWallpaper\\logs\\horodatage.csv'
PATH_IMAGE = 'changeWallpaper\\image\\'
PATH_LOGS = 'changeWallpaper\\logs\\'
PATH_PAGE = ['<html>', '<body alink=\"#FF0000\" bgcolor=\"#FFF5FF\" link=\"#0000FF\" text=\"#000000\" vlink=\"#7F0F9F\">', '<b>']

### RECUPERE LE CONTENU D'INDEX COURANT
def recup_dict_path(data):
    for ind in PATH_PAGE:
        data = data[ind]
    return data

### ON LIT LE FICHIER JSON ET ON ECRIT DANS list_page LE CONTENU
def recup_archive_file():
    # ouverture du fichier JSON
    with open(JSON_FILE, 'r', encoding='utf-8') as fj:
        data_json = json.load(fj)
    
    dic_page = recup_dict_path(data_json)
    del dic_page['text']
    del dic_page['balise']

    fj.close()
    return dic_page

### ON LIT LE FICHIER horodatage.csv POUR RECUP LES BANS
def horodatage():
    bans = []
    with open(CSV_FILE, 'r', encoding='utf-8') as fcr:
        reader = csv.reader(fcr)
        for row in reader:
            bans.append(row)
        
    return bans

### ON RECUPERE LE NOM DE CHAQUE BANNI QU'ON MET DANS UN TABLEAU
def claim_all_bans(bans):
    return [row[0] for row in bans]
    
### ON RECUPERE LE NOM DE CHAQUE FICHIER QU'ON MET DANS UN TABLEAU
def claim_all_pages(dic_page):
    return [key[9:-2] for key in dic_page.keys()]

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

### ON ECRIT DANS LE CSV LES NOUVEAUX BANNIS
def write_in_bans(page):
    csv_file = horodatage() # on récupère le contenu actuel
    csv_file.append([page, 'always'])

    with open(CSVfile, 'w', newline='') as fcw:
        writer = csv.writer(fcw)
        writer.writerows(csv_file)
    
    fcw.close()

### MINIMUM 1300x2300 POUR GARDER IMAGE
# Dimensions qui peuvent dépendre mais pour l'instant FIXE
def condition_dimension(page):
    url = url_nasa_image(page)
    response = requests.get(url, stream=True)

    try:
        image = Image.open(BytesIO(response.content))
        longueur, largeur = image.size
        print(f"Dimensions: {longueur}x{largeur}")
        return (longueur > 2300 and largeur > 1200) or (longueur > 1200 and largeur > 2300)
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")
        return False


### ON PREND UNE PAGE AU HASARD
def random_page(list_pages, bans):
    available_pages = [p for p in list_pages if p not in bans]

    if not available_pages:
        raise ValueError("Aucune page disponible (toutes bannies)")
    
    max_attempts = min(50, len(available_pages))

    for i in range(max_attempts):
        page = random.choice(available_pages)

        print('PAGE: ', page)
        if condition_dimension(page):
            return page
        else:
            write_in_bans(page)
            available_pages.remove(page)
    
    raise ValueError("Impossible de trouver une image avec les bonnes dimensions")


### ON VERIFIE LES DIMENSIONS DE L'IMAGE EN LOCAL
def traite_image(nom_fich):
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
    try:
        subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://home/lpasur/{nom_fich} [file://home/lpasur/%7Bnom_fich%7D]"], check=True)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-options", "zoom"], check=True)
        print(f"Fond d'écran mis à jour avec l'image : {nom_fich}")
    except:
        return -1


### CHANGE LE FOND D'ECRAN DANS UN ENV XFCE
def set_wallpaper_xfce(nom_fich):
    try:
        abs_path = os.path.abspath(f"file://home/lpasur/{nom_fich} [file://home/lpasur/%7Bnom_fich%7D]")
        monitors = ["/backdrop/screen0/monitor0/image-path","/backdrop/screen0/monitor0/last-image"]
        for prop in monitors:
            subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", abs_path], check=True)
            print(f"Fond d'écran mis à jour avec l'image : {nom_fich}")
    except:
        return -1
    

### CHANGE LE FOND D'ECRAN DANS UN ENV WINDOWS
def set_wallpaper_win(nom_fich):
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, f"{PATH_IMAGE}{nom_fich}", 0)
        print(f"Fond d'écran mis à jour avec l'image : {nom_fich}")
    except:
        return -1


### APPEL DES FONCTIONS
def main():
    dic_page = recup_archive_file()

    csv_file = horodatage() # format : [[banni1,date1], [banni2,date2], [banni3,date3]...]
    bans = claim_all_bans(csv_file) # format : [nom_banni1, nom_banni2, nom_banni3...]
    
    # recupération des pages des archives
    list_pages = claim_all_pages(dic_page) # format : [nom_page1, nom_page2, nom_page3...]
    # choix d'une page pour le fond d'ecran
    page_choice = random_page(list_pages, bans)
    #print(page_choice)

    # on recupère l'url de la page choisie ainsi que le nom du fichier
    url = url_nasa_image(page_choice)
    nom_fich = url.split('/')[-1]

    # on recupère le contenu de l'image
    response = requests.get(url)
    # on ecrit le contenu de l'image dans le fichier en question
    with open(f'{PATH_IMAGE}{nom_fich}', 'wb') as f:
        f.write(response.content)

    traite_image(nom_fich) # retourne l'image si elle est plus grande en largeur qu'en longueur

    add_name_wallpaper(page_choice)

    if platform.system() == 'Windows':
        set_wallpaper_win(nom_fich)

    ''' Suite pour Kali et Ubuntu'''
    

if __name__ == "__main__":
    main()
