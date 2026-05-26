import pandas as pd
import requests
from bs4 import BeautifulSoup
import io
import time
import os

def scrape_old_format(year):
    url = f"https://en.wikipedia.org/wiki/Eurovision_Song_Contest_{year}"
    print(f"[{year}] Extragem singura semifinală de la: {url}")
    
    # Folosim direct User-Agent-ul sincer care ne-a salvat de eroarea 403
    headers = {'User-Agent': 'EurovisionMLProject/1.0 (student data science project)'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"[{year}] Eroare {response.status_code} la accesarea paginii.")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})
    
    for table in tables:
        df = pd.read_html(io.StringIO(str(table)))[0]
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # Căutăm primul tabel care conține țările și piesele
        if 'country' in df.columns and 'song' in df.columns:
            # În acești ani, primul tabel este garantat Semifinala
            df['anul'] = year
            df['stadiu_competitie'] = "Semi-final"
            
            cols_to_keep = ['anul', 'stadiu_competitie', 'country', 'artist', 'song']
            available_cols = [col for col in cols_to_keep if col in df.columns]
            
            # Oprim căutarea și returnăm imediat după ce am găsit primul tabel
            return df[available_cols].copy()
            
    return None

def add_old_years():
    cale_csv = '../../data/raw/eurovision_base_data.csv'
    ani_vechi = range(2004, 2008) # Generează 2004, 2005, 2006, 2007
    date_noi = []
    
    for an in ani_vechi:
        df_an = scrape_old_format(an)
        if df_an is not None:
            date_noi.append(df_an)
        
        # Pauză de politețe pentru serverele Wikipedia
        time.sleep(2)
        
    if date_noi:
        # 1. Citim ce avem deja (cei 609 de rânduri)
        df_vechi = pd.read_csv(cale_csv)
        
        # 2. Unim cu datele noi
        df_complet = pd.concat([df_vechi] + date_noi, ignore_index=True)
        
        # 3. Sortăm frumos și suprascriem
        df_complet = df_complet.sort_values(by=['anul', 'stadiu_competitie'])
        df_complet.to_csv(cale_csv, index=False)
        
        print(f"\nSucces! Am adăugat anii 2004-2007.")
        print(f"Dataset-ul total are acum {len(df_complet)} rânduri.")

if __name__ == "__main__":
    add_old_years()