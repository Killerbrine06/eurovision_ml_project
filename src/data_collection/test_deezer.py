import requests

def test_deezer():
    # 1. Căutăm piesa (simplu, fără filtre stricte care să blocheze request-ul)
    query = "Celebrate the MusicStars"
    print(f"Căutăm: {query}...")
    
    search_res = requests.get("https://api.deezer.com/search", params={"q": query}).json()
    
    if search_res.get('data') and len(search_res['data']) > 0:
        # 2. Luăm ID-ul primului rezultat și cerem metadatele piesei
        track_id = search_res['data'][0]['id']
        track_res = requests.get(f"https://api.deezer.com/track/{track_id}").json()
        
        print("\n=== REZULTATE API DEEZER ===")
        print(f"Titlu  : {track_res.get('title')}")
        print(f"Artist : {track_res.get('artist', {}).get('name')}")
        print(f"BPM    : {track_res.get('bpm')}")
        print(f"Gain   : {track_res.get('gain')} (Metrica de energie acustică)")
        print(f"Audio  : {track_res.get('preview')}")
    else:
        print("Piesa nu a fost găsită.")

if __name__ == "__main__":
    test_deezer()