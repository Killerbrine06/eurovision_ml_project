import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore') # Ascundem avertismentele de formatare Pandas

def test_eurovision_2024():
    # 1. RE-ANTRENĂM MODELUL PE TOATE DATELE ISTORICE (2004-2023)
    df = pd.read_csv('../../data/processed/eurovision_master_dataset.csv')
    for col in ['bpm', 'place', 'running_order']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df_ml = df.dropna(subset=['bpm', 'running_order', 'region', 'place']).copy()
    df_ml['target_top10'] = (df_ml['place'] <= 10).astype(int)
    
    # Pregătim atributele de antrenament
    X_train_raw = df_ml[['bpm', 'running_order', 'region']]
    X_train = pd.get_dummies(X_train_raw, drop_first=True)
    y_train = df_ml['target_top10']
    
    # Antrenăm modelul (folosind class_weight='balanced' pentru o mică calibrare!)
    model = RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    # 2. DATELE CONCURENȚILOR NOI (Ediția 2024)
    concurenti_2024 = [
        {'country': 'Croatia', 'artist': 'Baby Lasagna', 'region': 'Balkan', 'bpm': 160, 'running_order': 23},
        {'country': 'Switzerland', 'artist': 'Nemo', 'region': 'Western', 'bpm': 152, 'running_order': 21},
        {'country': 'France', 'artist': 'Slimane', 'region': 'Big 5', 'bpm': 65, 'running_order': 25},
        {'country': 'Italy', 'artist': 'Angelina Mango', 'region': 'Big 5', 'bpm': 105, 'running_order': 15},
        {'country': 'Austria', 'artist': 'Kaleen', 'region': 'Western', 'bpm': 150, 'running_order': 26}
    ]
    
    df_test = pd.DataFrame(concurenti_2024)
    X_test_raw = df_test[['bpm', 'running_order', 'region']]
    
    # Aplicăm One-Hot Encoding pe datele noi
    X_test_encoded = pd.get_dummies(X_test_raw)
    
    # ALINIERE CRITICĂ: Ne asigurăm că datele noi au exact aceleași coloane ca datele de antrenament
    X_test_final = X_test_encoded.reindex(columns=X_train.columns, fill_value=0)

    # 3. FACEM PREDICȚIILE
    predictii = model.predict(X_test_final)
    probabilitati = model.predict_proba(X_test_final)

    print("\nPREDICȚIILE INTELIGENȚEI ARTIFICIALE PENTRU 2024")
    print("==========================================================")
    
    for i, row in df_test.iterrows():
        sansa_top10 = probabilitati[i][1] * 100 # Probabilitatea pentru clasa 1 (Succes)
        rezultat = "✅ INTRĂ ÎN TOP 10" if predictii[i] == 1 else "❌ RATEAZĂ TOP 10"
        
        print(f"🎤 {row['country']} ({row['artist']})")
        print(f"   Context: {row['bpm']} BPM | Ordinea: {row['running_order']} | Regiune: {row['region']}")
        print(f"   Verdict ML: {rezultat} (Șanse calculate: {sansa_top10:.1f}%)")
        print("-" * 58)

if __name__ == "__main__":
    test_eurovision_2024()