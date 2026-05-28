import pandas as pd
import os
import joblib
import xgboost as xgb
import numpy as np
from sklearn.metrics import ndcg_score

def train_and_save_advanced_ltr():
    print("Încărcăm dataset-ul master pentru noul model LTR Avansat...")
    df = pd.read_csv('../../data/processed/eurovision_master_dataset.csv')
    
    coloane_necesare = ['country', 'bpm', 'danceability', 'acousticness', 'genres', 'place', 'points', 'running_order', 'region', 'anul']
    
    # 1. Conversia numerică
    for col in ['bpm', 'danceability', 'acousticness', 'place', 'points', 'running_order', 'anul']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    print(f"Rânduri totale găsite în CSV: {len(df)}")
    
    # 2. Ștergem rândurile incomplete 
    df_ml = df.dropna(subset=coloane_necesare).copy()
    print(f"Rânduri valide reținute (set complet de metrici Spotify + Geopolitică): {len(df_ml)}")
    
    df_ml = df_ml.sort_values('anul')
    
    # 3. MĂIESTRIA DATELOR: Descompunerea genurilor muzicale multiple ("pop, rock")
    # Creează automat coloane separate (ex: genre_pop = 1, genre_rock = 1)
    df_genres = df_ml['genres'].str.get_dummies(sep=', ')
    df_genres = df_genres.add_prefix('genre_')
    
    # 4. Procesarea variabilelor categoriale
    df_categorical = pd.get_dummies(df_ml[['country', 'region']])
    
    # 5. Variabilele numerice
    df_numeric = df_ml[['bpm', 'danceability', 'acousticness', 'running_order']]
    
    # Construim X și y
    X_features = pd.concat([df_numeric, df_categorical, df_genres], axis=1)
    y = df_ml['points']
    
    # ============================================================
    # EVALUAREA ACURATEȚEI (Testare 2019-2023)
    # ============================================================
    train_mask = df_ml['anul'] <= 2018
    test_mask = df_ml['anul'] > 2018
    
    X_train, y_train = X_features[train_mask], y[train_mask]
    X_test, y_test = X_features[test_mask], y[test_mask]
    group_train = df_ml[train_mask].groupby('anul').size().values
    
    print("\nAntrenăm modelul temporar pe datele istorice până în 2018...")
    ranker_eval = xgb.XGBRanker(
        tree_method="hist", objective="rank:ndcg", ndcg_exp_gain=False,
        n_estimators=200, max_depth=5, learning_rate=0.05, random_state=42
    )
    ranker_eval.fit(X_train, y_train, group=group_train)
    
    df_test_results = df_ml[test_mask].copy()
    df_test_results['scor_ai'] = ranker_eval.predict(X_test)
    
    ndcg_scores = []
    for an in df_test_results['anul'].unique():
        df_an = df_test_results[df_test_results['anul'] == an]
        y_adevarat = np.asarray([df_an['points'].values])
        y_prezis = np.asarray([df_an['scor_ai'].values])
        if y_adevarat.shape[1] > 1:
            scor_an = ndcg_score(y_adevarat, y_prezis)
            ndcg_scores.append(scor_an)

    scor_mediu_ndcg = np.mean(ndcg_scores)
    print("\n" + "="*60)
    print(f"📊 ACURATEȚE LTR AVANSAT (Date Test 2019-2023)")
    print("="*60)
    print(f"Scor NDCG Mediu obținut: {scor_mediu_ndcg:.4f} ({scor_mediu_ndcg * 100:.1f}%)")
    print("="*60 + "\n")

    # ============================================================
    # ANTRENAREA ȘI SALVAREA MODELULUI PENTRU 2026
    # ============================================================
    print("Re-antrenăm pe toate datele disponibile (Premium Data) pentru salvare...")
    grupuri_totale = df_ml.groupby('anul').size().values
    
    ranker_final = xgb.XGBRanker(
        tree_method="hist", objective="rank:ndcg", ndcg_exp_gain=False, 
        n_estimators=200, max_depth=5, learning_rate=0.05, random_state=42
    )
    ranker_final.fit(X_features, y, group=grupuri_totale)
    
    os.makedirs('../../models', exist_ok=True)
    pachet = {
        'model': ranker_final,
        'coloane': X_features.columns
    }
    cale_salvare = '../../models/ltr_advanced_model.joblib'
    joblib.dump(pachet, cale_salvare)
    print(f"✓ Modelul LTR Avansat a fost salvat în {cale_salvare}")

if __name__ == "__main__":
    train_and_save_advanced_ltr()