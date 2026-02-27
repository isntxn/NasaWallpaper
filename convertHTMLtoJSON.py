########################################################################################
#         CODE QUI PERMET DE CONVERTIR LA PAGE HTML DE l'ARCHIVE DE LA NASA            #
#         EN FICHIER JSON POUR ACCES AUX DONNEES EN CAS D'INDISPONIBLITE DE            #
#         L'API. CREER LES FICHIERS "ArchiveAPOD.html" et "ArchiveAPOD.json"           #
########################################################################################

from bs4 import BeautifulSoup
import re
import requests
import json

HTML_FILE = 'ArchiveAPOD.html'
JSON_FILE = 'ArchiveAPOD.json'
dict_json = {}
path = []

### RECUPERATION ARCHIVES APOD 
def func_apod():
    global HTML_FILE
    url = 'https://apod.nasa.gov/apod/archivepix.html'

    data = requests.get(url).text
    soup = BeautifulSoup(data, features='html.parser')
    temp = []

    for line in soup:
        temp.append(str(line))

    with open(HTML_FILE, 'a', encoding='utf-8') as f:
        f.writelines(temp)


### CHAQUE LIGNE EST TRANSFORMEE EN TABLEAU
def transform_line_to_elm(line):
    # (<[^>]+>) → capture une balise HTML
    # |&[^;\s] → capture une entité HTML
    # |[^<>&]+ → capture le texte brut (tout sauf <, > et &)
    pattern = r'(<[^>]+>|&[^;\s]|[^<>&]+)'  
    tab_elm = re.findall(pattern, line)
    # Les chaines de cractères distinctes (qui sont a coté) sont fusionnées
    for ind in range(0,len(tab_elm)-1):
        if tab_elm[ind][0] != '<' and tab_elm[ind][-1] != '>' and len(tab_elm) > ind+1 and tab_elm[ind+1][0] != '<':
            tab_elm[ind] += f"{tab_elm[ind+1]}"
            tab_elm.remove(tab_elm[ind+1])
    
    return tab_elm


### ON TRANSFORME LE TABLEAU DE TABLEAU EN 1 SEUL TABLEAU POUR LE TRAITEMENT
def transform_in_one_tab(fich):
    tab = []
    for line in fich:
        for elm in line:
            if elm != ' ':
                tab.append(elm)
    return tab


def convert_tab_to_dic(elm, dict_temp):
    if True:
        ### EN CAS D'OUVERTURE DE BALISE
        if elm[0] == '<' and elm[1] != '/' and elm[-2] != '/' and elm[:4] != '<!--':
            # si une balise du meme nom existe deja, on ajout un indice
            if elm in dict_temp.keys():
                index = str(elm[:-1]) + ' ind=' + str([elm[:-1] for elm in dict_temp.keys()].count(elm[:-1])) + '>'
                dict_temp[index] = {}
                return index
            else:
                dict_temp[elm] = {}
                return elm

        ### EN CAS DE TEXTE
        elif elm[0] != '<' and elm[-1] != '>': 
            if 'text' not in dict_temp.keys():
                dict_temp['text'] = elm
            else:
                dict_temp['text'] += elm
            return 'text'
        
        ### EN CAS DE COMMENTAIRE
        elif elm[:4] == '<!--' and elm[-3:] == '-->':
            if 'com' not in dict_temp.keys():
                dict_temp['com'] = [elm]
            else:
                dict_temp['com'].append(elm)
            return 'com'
        
        ### EN CAS DE BALISE
        elif elm[0] == '<' and elm[-2:] == '/>':
            if 'balise' not in dict_temp.keys():
                dict_temp['balise'] = [elm]
            else:
                dict_temp['balise'].append(elm)
            return 'balise'

        ### EN CAS DE FERMETURE DE BALISE
        elif elm[:2] == '</' and elm[-1] == '>':
            return -1
        

### MODIFIE LE CHEMIN DE L'INDEX COURANT, QU'ON NOTE DANS 'PATH'
def modify_path(elm):
    while path[-1][:len(elm)-1] != elm[:-1]:
        path.pop()
    path.pop()


### RECUPERE LE CONTENU D'INDEX COURANT
def create_dict_path():
    dict_path = dict_json
    for ind in path:
        dict_path = dict_path[ind]
    return dict_path


def main():
    # importation html dans ArchiveAPOD
    #func_apod()

    # ouverture du fichier
    with open (HTML_FILE, 'r') as fh:
        fich = fh.readlines()

    tab_fich = []
    # on enleve les \n
    for line in fich:
        tab_fich.append(transform_line_to_elm(line.replace('\n', '')))

    fich = transform_in_one_tab(tab_fich)

    # parcourt tous les elements
    for elm in fich:
        dict_path = create_dict_path()
        ind = convert_tab_to_dic(elm, dict_path)
        
        # si ind n'est pas une fermeture de balise
        if ind != -1:
            # et si ind est bien une balise et pas un texte
            if ind[0] == '<' and ind[-1] == '>':
                path.append(ind)
            else:
                pass
        # sinon on modifie le chemin
        else:
            print(elm)
            elm_temp = elm.replace('/', '')
            modify_path(elm_temp)
    
    # mise en forme du json pour un print
    #data = json.dumps(dict_json, indent=2)
    #print(data)

    with open (JSON_FILE, 'w') as fj:
        json.dump(dict_json, fj, indent=2)
    
if __name__ == "__main__":
    main()
