import pandas as pd
import requests
import time
import os
import unicodedata
import re
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GETSONGBPM_API_KEY")

def normalize_for_url(text):
    if pd.isna(text):
        return ""
    text = str(text).lower().replace('"', '').replace("'", "")
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', '+', text.strip())
    return text

def extract_artist_name_from_api(features):
    artist_data = features.get("artist")
    if isinstance(artist_data, dict):
        return artist_data.get("name", "")
    elif isinstance(artist_data, list) and len(artist_data) > 0 and isinstance(artist_data[0], dict):
        return artist_data[0].get("name", "")
    return ""

def parse_features(features):
    artist_genres = ""
    artist_data = features.get("artist")
    if isinstance(artist_data, dict) and artist_data.get("genres"):
        artist_genres = ", ".join(artist_data["genres"])
    elif isinstance(artist_data, list) and len(artist_data) > 0 and isinstance(artist_data[0], dict):
        if artist_data[0].get("genres"):
            artist_genres = ", ".join(artist_data[0]["genres"])
            
    return {
        'bpm': features.get("tempo"),
        'danceability': features.get("danceability"),
        'acousticness': features.get("acousticness"),
        'genres': artist_genres
    }

def fetch_from_api(search_type, lookup_string, expected_artist=None):
    search_url = f"https://api.getsong.co/search/?api_key={API_KEY}&type={search_type}&lookup={lookup_string}"
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            search_result = data.get("search")
            
            if isinstance(search_result, dict) and search_result.get("error") == "no result":
                return None
                
            if isinstance(search_result, list) and len(search_result) > 0:
                if not expected_artist:
                    return parse_features(search_result[0])
                
                norm_expected = normalize_for_url(expected_artist).replace("+", "")
                for features in search_result:
                    api_artist = extract_artist_name_from_api(features)
                    norm_api = normalize_for_url(api_artist).replace("+", "")
                    if norm_expected in norm_api or norm_api in norm_expected:
                        return parse_features(features)
    except Exception:
        pass
    return None

def get_song_features_with_fallback(artist, song):
    base_artist = artist.replace('"', '').replace(" ", "+")
    base_song = song.replace('"', '').replace(" ", "+")
    norm_artist = normalize_for_url(artist)
    norm_song = normalize_for_url(song)

    res1 = fetch_from_api("both", f"song:{base_song}+artist:{base_artist}")
    if res1: return res1
    
    time.sleep(0.4)
    res2 = fetch_from_api("both", f"song:{norm_song}+artist:{norm_artist}")
    if res2: return res2
        
    time.sleep(0.4)
    return fetch_from_api("song", norm_song, expected_artist=artist)

def run_full_enrichment():
    cale_csv_raw = '../../data/raw/eurovision_base_data.csv'
    cale_csv_final = '../../data/raw/eurovision_with_audio_features.csv'
    
    print("Încărcăm setul complet de date...")
    df = pd.read_csv(cale_csv_raw)
    
    for col in ['bpm', 'danceability', 'acousticness', 'genres']:
        df[col] = pd.NA
        
    piese_gasite = 0
    total_piese = len(df)
    
    print(f"Lansăm execuția completă pentru toate cele {total_piese} piese. Va dura ~15-18 minute.")
    
    for index, row in df.iterrows():
        raw_artist = str(row['artist']).split(' feat')[0].split(' ft')[0].strip()
        raw_song = str(row['song']).strip()
        
        print(f"[{index+1}/{total_piese}] {raw_artist} - {raw_song} -> ", end="")
        
        features = get_song_features_with_fallback(raw_artist, raw_song)
        
        if features:
            df.at[index, 'bpm'] = features['bpm']
            df.at[index, 'danceability'] = features['danceability']
            df.at[index, 'acousticness'] = features['acousticness']
            df.at[index, 'genres'] = features['genres']
            piese_gasite += 1
            print(f"SUCCES (BPM: {features['bpm']})")
        else:
            print("Lipsă date")
            
        time.sleep(1.2)
        
    print(f"\nGata! Am îmbogățit dataset-ul. Piese găsite: {piese_gasite} din {total_piese}.")
    df.to_csv(cale_csv_final, index=False)
    print(f"Dataset-ul salvat în: {cale_csv_final}")

if __name__ == "__main__":
    if not API_KEY:
        print("Eroare: Lipsă API KEY în .env!")
    else:
        run_full_enrichment()