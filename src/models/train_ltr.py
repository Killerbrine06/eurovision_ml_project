import pandas as pd
import os
import joblib
import xgboost as xgb
import numpy as np
from sklearn.metrics import ndcg_score

def train_and_save_ltr():
    print("Pregătim datele pentru XGBoost Ranker...")
    df = pd.read_csv('../../data/processed/eurovision_master_dataset.csv')
    
    for col in ['bpm', 'place', 'points', 'running_order', 'anul']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df_ml = df.dropna(subset=['bpm', 'running_order', 'region', 'place', 'points', 'anul']).copy()
    df_ml = df_ml.sort_values('anul')
    
    X_features = pd.get_dummies(df_ml[['bpm', 'running_order', 'region']], drop_first=True)
    y = df_ml['points']
    
    # ============================================================
    # 1. IMPĂRȚIREA DATELOR PENTRU EVALUARE (Antrenăm <= 2018, Testăm > 2018)
    # ============================================================
    train_mask = df_ml['anul'] <= 2018
    test_mask = df_ml['anul'] > 2018
    
    X_train, y_train = X_features[train_mask], y[train_mask]
    X_test, y_test = X_features[test_mask], y[test_mask]
    
    group_train = df_ml[train_mask].groupby('anul').size().values
    
    print("Antrenăm temporar și evaluăm modelul pe datele de test (2019-2023)...")
    ranker_eval = xgb.XGBRanker(
        tree_method="hist",
        objective="rank:ndcg",
        ndcg_exp_gain=False,
        n_estimators=150,
        max_depth=4,
        learning_rate=0.1
    )
    
    ranker_eval.fit(X_train, y_train, group=group_train)
    predictii_scoruri = ranker_eval.predict(X_test)
    
    # ============================================================
    # 2. CALCUL METRICA NDCG (Acuratețea ierarhizării)
    # ============================================================
    df_test_results = df_ml[test_mask].copy()
    df_test_results['scor_ai'] = predictii_scoruri
    
    ndcg_scores = []
    for an in df_test_results['anul'].unique():
        df_an = df_test_results[df_test_results['anul'] == an]
        y_adevarat = np.asarray([df_an['points'].values])
        y_prezis = np.asarray([df_an['scor_ai'].values])
        
        if y_adevarat.shape[1] > 1:
            scor_an = ndcg_score(y_adevarat, y_prezis)
            ndcg_scores.append(scor_an)

    scor_mediu_ndcg = np.mean(ndcg_scores)
    
    print("\n" + "="*50)
    print(f"📊 PERFORMANȚĂ XGBoost RANKER (Anii 2019-2023)")
    print("="*50)
    print(f"Scor NDCG Mediu: {scor_mediu_ndcg:.4f} (1.0 înseamnă clasament perfect)")
    print(f"Interpretare: Acuratețea de ierarhizare este de {scor_mediu_ndcg * 100:.1f}%")
    print("="*50 + "\n")

    # ============================================================
    # 3. RE-ANTRENARE PE 100% DIN DATE PENTRU PRODUCȚIE
    # ============================================================
    print("Re-antrenăm modelul final pe 100% din istoric pentru predicția 2026...")
    grupuri_totale = df_ml.groupby('anul').size().values
    
    ranker_final = xgb.XGBRanker(
        tree_method="hist",
        objective="rank:ndcg",
        ndcg_exp_gain=False, 
        n_estimators=150,
        max_depth=4,
        learning_rate=0.1
    )
    
    ranker_final.fit(X_features, y, group=grupuri_totale)
    
    # ============================================================
    # 4. SALVAREA MODELULUI FINAL
    # ============================================================
    os.makedirs('../../models', exist_ok=True)
    pachet = {
        'model': ranker_final,
        'coloane': X_features.columns
    }
    cale_salvare = '../../models/ltr_model.joblib'
    joblib.dump(pachet, cale_salvare)
    print(f"✓ Modelul LTR de producție a fost salvat în {cale_salvare}")

if __name__ == "__main__":
    train_and_save_ltr()