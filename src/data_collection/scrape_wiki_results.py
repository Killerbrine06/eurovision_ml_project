import pandas as pd
import requests
import time
import io

def clean_and_deduplicate_columns(columns):
    """Uniformizează numele coloanelor și elimină duplicatele pentru a evita InvalidIndexError"""
    clean_cols = []
    
    # Pasul 1: Curățare standard
    for col in columns:
        c = str(col).lower().strip()
        if c in ['r/o', 'draw', 'order']:
            clean_cols.append('running_order')
        elif c in ['place', 'rank']:
            clean_cols.append('place')
        elif c in ['points', 'score']:
            clean_cols.append('points')
        elif c == 'country':
            clean_cols.append('country')
        else:
            clean_cols.append(c)
            
    # Pasul 2: De-duplicare (ex: dacă avem două coloane 'points', le facem 'points' și 'points_1')
    seen = {}
    dedup_cols = []
    for col in clean_cols:
        if col in seen:
            seen[col] += 1
            dedup_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            dedup_cols.append(col)
            
    return dedup_cols

def run_scraper():
    ani = [year for year in range(2004, 2024) if year != 2020]
    toate_rezultatele = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    print("Începem extragerea securizată a datelor de pe Wikipedia (2004-2023)...")
    
    for an in ani:
        url = f"https://en.wikipedia.org/wiki/Eurovision_Song_Contest_{an}"
        print(f"Procesăm anul {an}...", end=" ")
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Eroare HTTP {response.status_code}")
                continue
                
            html_io = io.StringIO(response.text)
            tables = pd.read_html(html_io)
            tabele_salvate = 0
            
            for df in tables:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(-1)
                    
                # Aplicăm noua funcție care garantează index unic
                df.columns = clean_and_deduplicate_columns(df.columns)
                
                # Verificăm existența coloanelor de bază (vor face match pe primele instanțe unice)
                if 'country' in df.columns and 'place' in df.columns and 'points' in df.columns:
                    df = df.dropna(subset=['country', 'place'])
                    
                    temp_df = df[['country', 'place', 'points']].copy()
                    
                    if 'running_order' in df.columns:
                        temp_df['running_order'] = df['running_order']
                    else:
                        temp_df['running_order'] = pd.NA
                        
                    temp_df['anul'] = an
                    toate_rezultatele.append(temp_df)
                    tabele_salvate += 1
            
            print(f"Găsit {tabele_salvate} tabele valide.")
            time.sleep(1)
            
        except Exception as e:
            print(f"Eroare la procesare: {e}")
            
    if not toate_rezultatele:
        print("Nu s-a putut extrage niciun tabel.")
        return
        
    df_final = pd.concat(toate_rezultatele, ignore_index=True)
    
    # Curățăm notele de subsol de pe Wikipedia (ex: "Moldova[b]" devine "Moldova")
    df_final['country'] = df_final['country'].astype(str).str.replace(r'\[.*\]', '', regex=True).str.strip()
    
    # Eliminăm eventuale rânduri totale sau invalide rătăcite prin tabele
    df_final = df_final[df_final['country'].str.lower() != 'total']
    
    cale_out = '../../data/raw/wiki_results.csv'
    df_final.to_csv(cale_out, index=False)
    print(f"\nExtragere completă cu succes! S-au salvat {len(df_final)} rânduri în {cale_out}.")

if __name__ == "__main__":
    run_scraper()