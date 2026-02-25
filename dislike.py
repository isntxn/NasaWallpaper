import changeWallpaperApod_Archive as cwall_Arch
import changeWallpaperApod_API as cwall

path_logs = 'C:\\Users\\t.adam\\OneDrive - GROUPE SICA ATLANTIQUE\\Documents\\script\\changeWallpaper\\logs\\'

### AJOUT DU FOND D'ECRAN ACTUEL DANS LES BANNIS
def ban_wallpaper():
    with open(f'{path_logs}/name_wallpaper.txt', 'r', encoding='utf-8') as f:
        name_page = f.read()
    
    return name_page
    
if __name__ == "__main__":
    name_page = ban_wallpaper()
    cwall.write_in_bans(name_page)
    cwall.main()
