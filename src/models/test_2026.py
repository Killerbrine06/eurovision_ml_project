import pandas as pd
import joblib
import argparse
import warnings
warnings.filterwarnings('ignore')

# Datele complete 2026 (împărțite pe semifinale pentru a putea aplica LTR corect)
semifinala_1 = [
    {'country': 'Moldova', 'artist': 'Satoshi', 'region': 'Ex-Soviet', 'bpm': 130, 'running_order': 1},
    {'country': 'Sweden', 'artist': 'FELICIA', 'region': 'Nordic', 'bpm': 115, 'running_order': 2},
    {'country': 'Croatia', 'artist': 'Lelek', 'region': 'Balkan', 'bpm': 100, 'running_order': 3},
    {'country': 'Greece', 'artist': 'Akylas', 'region': 'Balkan', 'bpm': 95, 'running_order': 4},
    {'country': 'Portugal', 'artist': 'Bandidos do Cante', 'region': 'Western', 'bpm': 85, 'running_order': 5},
    {'country': 'Georgia', 'artist': 'Bzikebi', 'region': 'Ex-Soviet', 'bpm': 125, 'running_order': 6},
    {'country': 'Finland', 'artist': 'Linda Lampenius x Pete Parkkonen', 'region': 'Nordic', 'bpm': 140, 'running_order': 7},
    {'country': 'Montenegro', 'artist': 'Tamara Živković', 'region': 'Balkan', 'bpm': 110, 'running_order': 8},
    {'country': 'Estonia', 'artist': 'Vanilla Ninja', 'region': 'Baltic', 'bpm': 150, 'running_order': 9},
    {'country': 'Israel', 'artist': 'Noam Bettan', 'region': 'Other', 'bpm': 120, 'running_order': 10},
    {'country': 'Belgium', 'artist': 'ESSYLA', 'region': 'Western', 'bpm': 128, 'running_order': 11},
    {'country': 'Lithuania', 'artist': 'Lion Ceccah', 'region': 'Baltic', 'bpm': 105, 'running_order': 12},
    {'country': 'San Marino', 'artist': 'Senhit', 'region': 'Mediterranean', 'bpm': 135, 'running_order': 13},
    {'country': 'Poland', 'artist': 'ALICJA', 'region': 'Central Europe', 'bpm': 75, 'running_order': 14},
    {'country': 'Serbia', 'artist': 'LAVINA', 'region': 'Balkan', 'bpm': 90, 'running_order': 15}
]

semifinala_2 = [
    {'country': 'Bulgaria', 'artist': 'DARA', 'region': 'Balkan', 'bpm': 128, 'running_order': 1},
    {'country': 'Azerbaijan', 'artist': 'JIVA', 'region': 'Ex-Soviet', 'bpm': 110, 'running_order': 2},
    {'country': 'Romania', 'artist': 'Alexandra Căpitănescu', 'region': 'Balkan', 'bpm': 130, 'running_order': 3},
    {'country': 'Luxembourg', 'artist': 'Eva Marija', 'region': 'Western', 'bpm': 85, 'running_order': 4},
    {'country': 'Czechia', 'artist': 'Daniel Zizka', 'region': 'Central Europe', 'bpm': 140, 'running_order': 5},
    {'country': 'Armenia', 'artist': 'SIMÓN', 'region': 'Ex-Soviet', 'bpm': 115, 'running_order': 6},
    {'country': 'Switzerland', 'artist': 'Veronica Fusaro', 'region': 'Western', 'bpm': 70, 'running_order': 7},
    {'country': 'Cyprus', 'artist': 'Antigoni', 'region': 'Mediterranean', 'bpm': 120, 'running_order': 8},
    {'country': 'Latvia', 'artist': 'Atvara', 'region': 'Baltic', 'bpm': 95, 'running_order': 9},
    {'country': 'Denmark', 'artist': 'Søren Torpegaard Lund', 'region': 'Nordic', 'bpm': 100, 'running_order': 10},
    {'country': 'Australia', 'artist': 'Delta Goodrem', 'region': 'Other', 'bpm': 85, 'running_order': 11},
    {'country': 'Ukraine', 'artist': 'LELÉKA', 'region': 'Ex-Soviet', 'bpm': 105, 'running_order': 12},
    {'country': 'Albania', 'artist': 'Alis', 'region': 'Balkan', 'bpm': 90, 'running_order': 13},
    {'country': 'Malta', 'artist': 'AIDAN', 'region': 'Mediterranean', 'bpm': 125, 'running_order': 14},
    {'country': 'Norway', 'artist': 'Jonas Lovv', 'region': 'Nordic', 'bpm': 145, 'running_order': 15}
]

def prepara_datele(date_brute, coloane_model):
    df = pd.DataFrame(date_brute)
    X_raw = df[['bpm', 'running_order', 'region']]
    X_encoded = pd.get_dummies(X_raw)
    # Aliniem structura cu modelul antrenat
    X_final = X_encoded.reindex(columns=coloane_model, fill_value=0)
    return df, X_final

def evalueaza_random_forest(model_data):
    print("\n" + "="*60)
    print("🌲 MODEL: RANDOM FOREST (Evaluare Independentă - Prag 40%)")
    print("="*60)
    model = model_data['model']
    coloane = model_data['coloane']
    
    toate_datele = semifinala_1 + semifinala_2
    df, X = prepara_datele(toate_datele, coloane)
    
    probabilitati = model.predict_proba(X)
    
    calificati = 0
    for i, row in df.iterrows():
        sansa = probabilitati[i][1]
        if sansa >= 0.40:
            print(f"✅ {row['country']:<15} ({row['artist']}) -> Șanse: {sansa*100:.1f}%")
            calificati += 1
        else:
            print(f"❌ {row['country']:<15} ({row['artist']}) -> Șanse: {sansa*100:.1f}%")
            
    print(f"\nConcluzie Random Forest: A vrut să califice {calificati} din 30 de piese (Regula ignorată).")

def evalueaza_ltr(model_data):
    print("\n" + "="*60)
    print("🏆 MODEL: XGBoost RANKER (Evaluare prin Ierarhizare - Fix 10 Calificați)")
    print("="*60)
    model = model_data['model']
    coloane = model_data['coloane']
    
    for num, semi in enumerate([semifinala_1, semifinala_2], 1):
        print(f"\n--- REZULTATE SEMIFINALA {num} ---")
        df, X = prepara_datele(semi, coloane)
        
        # LTR dă un "scor de forță", nu un procent!
        scoruri = model.predict(X)
        df['scor_ai'] = scoruri
        
        # Aici e magia LTR: sortăm descrescător după scor
        df_sortat = df.sort_values('scor_ai', ascending=False).reset_index(drop=True)
        
        for i, row in df_sortat.iterrows():
            locul = i + 1
            status = "✅ CALIFICAT" if locul <= 10 else "❌ ELIMINAT"
            print(f"{locul:2d}. {status} | {row['country']:<15} ({row['artist']}) | Scor: {row['scor_ai']:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluează Eurovision 2026")
    parser.add_argument('--model', type=str, choices=['rf', 'ltr', 'both'], default='both', 
                        help='Alege modelul: rf (Random Forest), ltr (Ranker), sau both (ambele)')
    args = parser.parse_args()

    if args.model in ['rf', 'both']:
        try:
            rf_data = joblib.load('../../models/rf_model.joblib')
            evalueaza_random_forest(rf_data)
        except FileNotFoundError:
            print("Eroare: Nu găsesc modelul RF. Rulează train_rf.py mai întâi.")
            
    if args.model in ['ltr', 'both']:
        try:
            ltr_data = joblib.load('../../models/ltr_model.joblib')
            evalueaza_ltr(ltr_data)
        except FileNotFoundError:
            print("Eroare: Nu găsesc modelul LTR. Rulează train_ltr.py mai întâi.")