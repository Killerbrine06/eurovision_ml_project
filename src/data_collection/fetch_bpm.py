import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

# Încărcăm cheia API din fișierul .env
load_dotenv()
API_KEY = os.getenv("GETSONGBPM_API_KEY")

def get_bpm(artist, song):
    """
    Caută piesa folosind GetSongBPM API și returnează valoarea BPM-ului.
    """
    # Pasul A: Căutăm piesa pentru a obține ID-ul
    search_url = f"https://api.getsongbpm.com/search/?type=both&api_key={API_KEY}&lookup={artist} {song}"
    
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            
            # Verificăm dacă am primit rezultate valide
            if data.get("search"):
                # Luăm primul rezultat relevant
                song_id = data["search"][0]["song_id"]
                
                # Pasul B: Cerem detaliile piesei folosind ID-ul
                song_url = f"https://api.getsongbpm.com/song/?api_key={API_KEY}&id={song_id}"
                song_response = requests.get(song_url)
                
                if song_response.status_code == 200:
                    song_data = song_response.json()
                    if song_data.get("song"):
                        # Extragem și returnăm BPM-ul ca număr întreg
                        return int(song_data["song"]["tempo"])
                        
    except Exception as e:
        print(f"Eroare la conectarea cu API-ul pentru {artist} - {song}: {e}")
        
    return pd.NA # Returnăm NaN (Not a Number) dacă piesa nu este găsită

def enrich_with_bpm():
    cale_csv_raw = '../../data/raw/eurovision_base_data.csv'
    cale_csv_processed = '../../data/raw/eurovision_with_bpm.csv'
    
    print("Încărcăm setul de date istoric...")
    df = pd.read_csv(cale_csv_raw)
    
    # Inițializăm noua coloană
    df['bpm'] = pd.NA
    piese_gasite = 0
    
    print(f"Începem interogarea GetSongBPM pentru {len(df)} piese...")
    
    for index, row in df.iterrows():
        # Curățăm numele artistului pentru o căutare mai eficientă
        artist = str(row['artist']).split(' feat')[0].split(' ft')[0].strip()
        song = str(row['song']).strip()
        
        print(f"[{index+1}/{len(df)}] Caut BPM: {artist} - {song}...", end="")
        
        bpm_value = get_bpm(artist, song)
        
        if pd.notna(bpm_value):
            df.at[index, 'bpm'] = bpm_value
            piese_gasite += 1
            print(f" Găsit! ({bpm_value} BPM)")
        else:
            print(" Nu a fost găsit.")
            
        # Pauză esențială pentru a respecta limitele API-ului gratuit
        time.sleep(1)
        
    print(f"\nFinalizat! S-a găsit BPM-ul pentru {piese_gasite} din {len(df)} piese.")
    
    df.to_csv(cale_csv_processed, index=False)
    print(f"Dataset-ul actualizat a fost salvat în {cale_csv_processed}")

if __name__ == "__main__":
    if not API_KEY:
        print("Eroare: Cheia GETSONGBPM_API_KEY nu a fost găsită în fișierul .env!")
    else:
        enrich_with_bpm()