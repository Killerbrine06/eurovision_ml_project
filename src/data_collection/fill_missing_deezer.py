import pandas as pd
import requests
import time
import unicodedata
import re

def normalize_text(text):
    """Curăță textul pentru o căutare precisă pe Deezer"""
    if pd.isna(text):
        return ""
    text = str(text).lower().replace('"', '').replace("'", "")
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()

def fetch_from_deezer(artist, song):
    """Caută piesa pe Deezer și previne data poisoning-ul"""
    norm_artist = normalize_text(artist)
    norm_song = normalize_text(song)
    
    # Deezer are un motor de căutare excelent, preferă textul simplu separat prin spațiu
    query = f"{norm_artist} {norm_song}"
    search_url = f"https://api.deezer.com/search?q={query}"
    
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                # Verificăm artiștii pentru a nu lua piesa greșită (anti-poisoning)
                for item in data['data']:
                    api_artist = normalize_text(item['artist']['name'])
                    
                    if norm_artist in api_artist or api_artist in norm_artist:
                        track_id = item['id']
                        
                        # Cerem detaliile complete ale piesei
                        track_url = f"https://api.deezer.com/track/{track_id}"
                        track_res = requests.get(track_url).json()
                        
                        return {
                            'bpm': track_res.get('bpm'),
                            'gain': track_res.get('gain')
                        }
    except Exception as e:
        print(f"Eroare Deezer: {e}")
        
    return None

def run_deezer_fill():
    cale_csv_in = '../../data/raw/eurovision_with_audio_features.csv'
    cale_csv_out = '../../data/raw/eurovision_audio_complete.csv'
    
    print("Încărcăm dataset-ul parțial (236 piese găsite)...")
    try:
        df = pd.read_csv(cale_csv_in)
    except FileNotFoundError:
        print(f"Eroare: Nu găsesc fișierul {cale_csv_in}")
        return
        
    # Adăugăm coloana gain dacă nu există
    if 'gain' not in df.columns:
        df['gain'] = pd.NA
        
    # Filtrăm doar piesele care nu au BPM completat
    lipsuri = df[df['bpm'].isna()]
    total_lipsuri = len(lipsuri)
    
    print(f"Avem {total_lipsuri} piese fără date. Pornim extragerea de pe Deezer...\n")
    
    piese_salvate = 0
    contor = 1
    
    for index, row in lipsuri.iterrows():
        raw_artist = str(row['artist']).split(' feat')[0].split(' ft')[0].strip()
        raw_song = str(row['song']).strip()
        
        print(f"[{contor}/{total_lipsuri}] Caut: {raw_artist} - {raw_song} -> ", end="")
        
        features = fetch_from_deezer(raw_artist, raw_song)
        
        if features and features['bpm'] != 0: # Deezer uneori returnează BPM 0 dacă nu l-a calculat
            df.at[index, 'bpm'] = features['bpm']
            df.at[index, 'gain'] = features['gain']
            piese_salvate += 1
            print(f"GĂSIT! (BPM: {features['bpm']})")
        else:
            print("Nu s-a găsit pe Deezer.")
            
        contor += 1
        time.sleep(0.5) # Deezer permite mult mai multe request-uri, deci putem merge mai repede
        
    print(f"\nFinalizat! Deezer a salvat {piese_salvate} din cele {total_lipsuri} piese lipsă.")
    
    # Verificăm statusul final
    total_complet = df['bpm'].notna().sum()
    print(f"Acum dataset-ul nostru are un total de {total_complet} piese cu BPM.")
    
    df.to_csv(cale_csv_out, index=False)
    print(f"Dataset-ul final salvat în: {cale_csv_out}")

if __name__ == "__main__":
    run_deezer_fill()