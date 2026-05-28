import pandas as pd
import joblib

def evalueaza_sf2_avansat():
    print("="*75)
    print("🏆 PREDICȚIE LTR AVANSAT (Semifinala 2 - Eurovision 2026)")
    print("="*75)
    
    try:
        model_data = joblib.load('../../models/ltr_advanced_model.joblib')
        model = model_data['model']
        coloane_model = model_data['coloane']
    except FileNotFoundError:
        print("Eroare: Nu găsesc modelul ltr_advanced_model.joblib.")
        return

    # Datele detaliate pentru Semifinala 2 (inclusiv atributele Spotify)
    semifinala_2 = [
        {'country': 'Bulgaria', 'artist': 'DARA', 'song': 'Bangaranga', 'region': 'Balkan', 'running_order': 1, 'bpm': 130, 'danceability': 0.82, 'acousticness': 0.05, 'genres': 'pop, dance'},
        {'country': 'Azerbaijan', 'artist': 'JIVA', 'song': 'Just Go', 'region': 'Ex-Soviet', 'running_order': 2, 'bpm': 110, 'danceability': 0.65, 'acousticness': 0.20, 'genres': 'pop'},
        {'country': 'Romania', 'artist': 'Alexandra Căpitănescu', 'song': 'Choke Me', 'region': 'Balkan', 'running_order': 3, 'bpm': 135, 'danceability': 0.55, 'acousticness': 0.10, 'genres': 'rock, pop'},
        {'country': 'Luxembourg', 'artist': 'Eva Marija', 'song': 'Mother Nature', 'region': 'Western', 'running_order': 4, 'bpm': 90, 'danceability': 0.45, 'acousticness': 0.70, 'genres': 'pop, indie'},
        {'country': 'Czechia', 'artist': 'Daniel Zizka', 'song': 'CROSSROADS', 'region': 'Central Europe', 'running_order': 5, 'bpm': 120, 'danceability': 0.60, 'acousticness': 0.30, 'genres': 'pop, electronic'},
        {'country': 'Armenia', 'artist': 'Simón', 'song': 'Paloma Rumba', 'region': 'Ex-Soviet', 'running_order': 6, 'bpm': 115, 'danceability': 0.85, 'acousticness': 0.40, 'genres': 'pop, latin'},
        {'country': 'Switzerland', 'artist': 'Veronica Fusaro', 'song': 'Alice', 'region': 'Western', 'running_order': 7, 'bpm': 80, 'danceability': 0.50, 'acousticness': 0.80, 'genres': 'soul, pop'},
        {'country': 'Cyprus', 'artist': 'Antigoni', 'song': 'JALLA', 'region': 'Mediterranean', 'running_order': 8, 'bpm': 125, 'danceability': 0.88, 'acousticness': 0.10, 'genres': 'pop, dance'},
        {'country': 'Latvia', 'artist': 'Atvara', 'song': 'Ēnā', 'region': 'Baltic', 'running_order': 9, 'bpm': 95, 'danceability': 0.40, 'acousticness': 0.60, 'genres': 'indie, folk'},
        {'country': 'Denmark', 'artist': 'Søren Torpegaard Lund', 'song': 'Før Vi Går Hjem', 'region': 'Nordic', 'running_order': 10, 'bpm': 75, 'danceability': 0.35, 'acousticness': 0.85, 'genres': 'pop, ballad'},
        {'country': 'Australia', 'artist': 'Delta Goodrem', 'song': 'Eclipse', 'region': 'Other', 'running_order': 11, 'bpm': 100, 'danceability': 0.55, 'acousticness': 0.25, 'genres': 'pop'},
        {'country': 'Ukraine', 'artist': 'Leléka', 'song': 'Ridnym', 'region': 'Ex-Soviet', 'running_order': 12, 'bpm': 105, 'danceability': 0.50, 'acousticness': 0.50, 'genres': 'folk, electronic'},
        {'country': 'Albania', 'artist': 'Alis', 'song': 'Nân', 'region': 'Balkan', 'running_order': 13, 'bpm': 90, 'danceability': 0.45, 'acousticness': 0.65, 'genres': 'pop, ballad'},
        {'country': 'Malta', 'artist': 'AIDAN', 'song': 'Bella', 'region': 'Mediterranean', 'running_order': 14, 'bpm': 128, 'danceability': 0.78, 'acousticness': 0.15, 'genres': 'pop, dance'},
        {'country': 'Norway', 'artist': 'JONAS LOVV', 'song': 'YA YA YA', 'region': 'Nordic', 'running_order': 15, 'bpm': 145, 'danceability': 0.72, 'acousticness': 0.20, 'genres': 'pop, electronic'}
    ]

    df = pd.DataFrame(semifinala_2)
    
    # 1. Procesăm genurile exact ca în antrenament
    df_genres = df['genres'].str.get_dummies(sep=', ').add_prefix('genre_')
    
    # 2. Procesăm variabilele categoriale
    df_categorical = pd.get_dummies(df[['country', 'region']])
    
    # 3. Variabilele numerice
    df_numeric = df[['bpm', 'danceability', 'acousticness', 'running_order']]
    
    # 4. Asamblăm setul de date
    X_raw = pd.concat([df_numeric, df_categorical, df_genres], axis=1)
    
    # 5. ALINIEREA CRITICĂ: 
    # Orice gen sau țară care nu era în istoricul de antrenament primește 0
    X_final = X_raw.reindex(columns=coloane_model, fill_value=0)
    
    # 6. Generăm scorurile AI
    df['scor_ai'] = model.predict(X_final)
    
    # 7. Afișăm clasamentul oficial 
    df_sortat = df.sort_values('scor_ai', ascending=False).reset_index(drop=True)
    
    print(f"{'Loc':<4} | {'Status':<12} | {'Țară':<15} | {'Artist & Piesă':<35} | {'Scor':<5}")
    print("-" * 75)
    
    for i, row in df_sortat.iterrows():
        locul = i + 1
        status = "✅ CALIFICAT" if locul <= 10 else "❌ ELIMINAT"
        print(f"{locul:<4} | {status:<12} | {row['country']:<15} | {row['artist']} - {row['song']:<20} | {row['scor_ai']:.2f}")

if __name__ == "__main__":
    evalueaza_sf2_avansat()