import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

def train_and_save_rf():
    print("Antrenăm Random Forest Classifier...")
    df = pd.read_csv('../../data/processed/eurovision_master_dataset.csv')
    
    for col in ['bpm', 'place', 'running_order']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df_ml = df.dropna(subset=['bpm', 'running_order', 'region', 'place']).copy()
    # df_ml.info()
    df_ml['target_top10'] = (df_ml['place'] <= 10).astype(int)
    
    X_features = pd.get_dummies(df_ml[['bpm', 'running_order', 'region']], drop_first=True)
    y = df_ml['target_top10']

    # === NOU: SEPARARE PENTRU EVALUARE ===
    X_train, X_test, y_train, y_test = train_test_split(X_features, y, test_size=0.2, random_state=42, stratify=y)

    print("Evaluăm Random Forest pe datele de test ascunse (20%)...")
    model_eval = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=5, class_weight='balanced')
    model_eval.fit(X_train, y_train)
    
    predictii_test = model_eval.predict(X_test)
    acuratete = accuracy_score(y_test, predictii_test)
    
    print("\n" + "="*50)
    print(f"📊 PERFORMANȚĂ RANDOM FOREST (Date Test): {acuratete * 100:.2f}%")
    print("="*50)
    print(classification_report(y_test, predictii_test, target_names=['Eșec', 'Succes']))

    # === RE-ANTRENARE PENTRU PRODUCȚIE ===
    print("\nRe-antrenăm modelul final pe 100% din date pentru 2026...")
    model_final = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=5, class_weight='balanced')
    model_final.fit(X_features, y) # Antrenăm pe TOATE datele înainte de salvare

    # Acum salvăm 'model_final' în loc de 'model'
    os.makedirs('../../models', exist_ok=True)
    pachet = {
        'model': model_final,
        'coloane': X_features.columns
    }
    cale_salvare = '../../models/rf_model.joblib'
    joblib.dump(pachet, cale_salvare)

if __name__ == "__main__":
    train_and_save_rf()