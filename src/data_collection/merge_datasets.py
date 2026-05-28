import pandas as pd

def get_geopolitical_blocks():
    """Dicționar pentru maparea țărilor în blocuri culturale/regionale"""
    return {
        # Big 5 (Țările fondatoare/principalii finanțatori)
        'united kingdom': 'Big 5', 'france': 'Big 5', 'germany': 'Big 5', 
        'spain': 'Big 5', 'italy': 'Big 5',
        
        # Țările Nordice (Tradițional susținute puternic între ele)
        'sweden': 'Nordic', 'norway': 'Nordic', 'denmark': 'Nordic', 
        'finland': 'Nordic', 'iceland': 'Nordic',
        
        # Blocul Balcanic & Ex-Iugoslav
        'serbia': 'Balkan', 'croatia': 'Balkan', 'bosnia and herzegovina': 'Balkan', 
        'montenegro': 'Balkan', 'north macedonia': 'Balkan', 'albania': 'Balkan', 
        'slovenia': 'Balkan', 'romania': 'Balkan', 'bulgaria': 'Balkan',
        
        # Blocul Ex-Sovietic (Estic)
        'ukraine': 'Ex-Soviet', 'russia': 'Ex-Soviet', 'belarus': 'Ex-Soviet', 
        'moldova': 'Ex-Soviet', 'georgia': 'Ex-Soviet', 'armenia': 'Ex-Soviet', 
        'azerbaijan': 'Ex-Soviet',
        
        # Blocul Baltic
        'estonia': 'Baltic', 'latvia': 'Baltic', 'lithuania': 'Baltic',
        
        # Europa Centrală
        'poland': 'Central Europe', 'czechia': 'Central Europe', 
        'slovakia': 'Central Europe', 'hungary': 'Central Europe',
        
        # Blocul Mediteranean
        'greece': 'Mediterranean', 'cyprus': 'Mediterranean', 'malta': 'Mediterranean', 
        'san marino': 'Mediterranean',
        
        # Europa de Vest (Altele)
        'ireland': 'Western', 'netherlands': 'Western', 'belgium': 'Western', 
        'switzerland': 'Western', 'austria': 'Western', 'portugal': 'Western',
        
        # Restul lumii / Invitați speciali
        'australia': 'Other', 'israel': 'Other'
    }

def run_final_merge():
    print("Încărcăm fișierele...")
    try:
        df_audio = pd.read_csv('../../data/raw/eurovision_audio_complete.csv')
        df_wiki = pd.read_csv('../../data/raw/wiki_results.csv')
    except FileNotFoundError as e:
        print(f"Eroare la citire: {e}")
        return
    
    # 1. Standardizăm cheile de legătură
    df_audio['country_match'] = df_audio['country'].astype(str).str.lower().str.strip()
    df_wiki['country_match'] = df_wiki['country'].astype(str).str.lower().str.strip()
    
    # Rezolvăm manual cele mai comune discrepanțe
    dictionar_corectii = {
        'the netherlands': 'netherlands',
        'f.y.r. macedonia': 'north macedonia',
        'macedonia': 'north macedonia',
        'czech republic': 'czechia'
    }
    df_audio['country_match'] = df_audio['country_match'].replace(dictionar_corectii)
    df_wiki['country_match'] = df_wiki['country_match'].replace(dictionar_corectii)
    
    # 2. Fuziunea datelor
    print("Unificăm datele...")
    df_final = pd.merge(
        df_audio,
        df_wiki[['anul', 'country_match', 'place', 'points', 'running_order']],
        on=['anul', 'country_match'],
        how='left'
    )
    
    # 3. Adăugăm blocul geopolitic pe baza numelui standardizat
    print("Aplicăm afinitățile geopolitice...")
    blocuri = get_geopolitical_blocks()
    # Mapăm regiunea; dacă o țară nu e în dicționar, primește 'Other'
    df_final['region'] = df_final['country_match'].map(blocuri).fillna('Other')
    
    # 4. Verificare erori de potrivire la merge
    lipsuri = df_final[df_final['place'].isna()]
    if len(lipsuri) > 0:
        print(f"\nATENȚIE: {len(lipsuri)} piese nu și-au găsit rezultatele de pe Wikipedia.")
        print("Exemple:")
        print(lipsuri[['anul', 'country']].drop_duplicates().head())
    else:
        print("\nSUCCES: Toate piesele au fost potrivite perfect!")
        
    # Curățăm coloana temporară de matching și salvăm Master Dataset-ul
    df_final = df_final.drop(columns=['country_match'])
    
    cale_out = '../../data/processed/eurovision_master_dataset.csv'
    
    import os
    # Creăm folderul processed dacă nu există
    os.makedirs('../../data/processed', exist_ok=True)
    
    df_final.to_csv(cale_out, index=False)
    print(f"\nDataset-ul Master a fost salvat în: {cale_out}")
    print(f"Structura finală: {df_final.shape[0]} rânduri, {df_final.shape[1]} coloane.")
    print("Coloanele sunt:", list(df_final.columns))

if __name__ == "__main__":
    run_final_merge()